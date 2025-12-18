"""Execution phase for deliberate."""

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Awaitable, Callable, Literal, Optional

from deliberate.adapters.base import ModelAdapter
from deliberate.adapters.cli_adapter import CLIAdapter, MCPServerConfig
from deliberate.agent_context import (
    AgentExecutionContext,
    AgentIdentity,
    ExecutionSettings,
    MCPOrchestratorConfig,
    MCPSettings,
    TaskContext,
)
from deliberate.agent_context import (
    MCPServerConfig as MCPServerContextConfig,
)
from deliberate.budget.tracker import BudgetTracker
from deliberate.context import JuryContext
from deliberate.git.worktree import Worktree, WorktreeManager
from deliberate.prompts.execution import (
    EXECUTION_NO_PLAN,
    EXECUTION_PROMPT,
    EXECUTION_WITH_PLAN,
)
from deliberate.tools.ask_question import AskQuestionTool, QuestionHandler
from deliberate.types import ExecutionResult, Plan
from deliberate.utils.code_block_applier import apply_code_blocks_from_text
from deliberate.validation import (
    ValidationRunner,
)
from deliberate.validation.analyzer import detect_test_command_llm
from deliberate.verbose_logger import get_verbose_logger


def _categorize_error(e: Exception) -> str:
    """Categorize an exception for tracking."""
    error_msg = str(e).lower()
    if isinstance(e, asyncio.TimeoutError) or "timed out" in error_msg:
        return "timeout"
    if "context length" in error_msg or "token limit" in error_msg:
        return "context_length_exceeded"
    if "json" in error_msg or "parse" in error_msg:
        return "json_parse_error"
    return "runtime_error"


def _write_execution_context(
    agent: ModelAdapter,
    result_id: str,
    task: str,
    working_dir: Path,
    timeout_seconds: int,
    extra_mcp_servers: list[MCPServerConfig] | None,
    plan: Optional["Plan"],
) -> Path | None:
    """Write agent execution context to .deliberate/config.json in worktree.

    Args:
        agent: The model adapter being used.
        result_id: Unique execution ID.
        task: The task description (without tool injections).
        working_dir: Path to the worktree.
        timeout_seconds: Execution timeout.
        extra_mcp_servers: MCP servers to inject.
        plan: Optional plan being executed.

    Returns:
        Path to the written config file, or None if writing failed.
    """
    try:
        # Determine parser type and permission mode from adapter
        parser_type = agent.name  # Default to agent name
        permission_mode = "bypassPermissions"
        if isinstance(agent, CLIAdapter):
            parser_type = agent._get_cli_type()
            if agent.permission_mode:
                permission_mode = agent.permission_mode

        # Use default max tokens for execution context
        max_tokens: int = 8000

        # Convert MCP servers to context config format
        mcp_servers: list[MCPServerContextConfig] = []
        orchestrator_config: MCPOrchestratorConfig | None = None

        if extra_mcp_servers:
            for server in extra_mcp_servers:
                # Check if this is the orchestrator server (has SSE URL with token)
                if server.url and server.headers:
                    # Extract token from Authorization header
                    auth_header = server.headers.get("Authorization", "")
                    if auth_header.startswith("Bearer "):
                        token = auth_header[7:]
                        orchestrator_config = MCPOrchestratorConfig(
                            url=server.url,
                            token=token,
                        )
                        continue

                # Regular MCP server
                mcp_servers.append(
                    MCPServerContextConfig(
                        name=server.name,
                        type="sse" if server.url else "stdio",
                        command=server.command,
                        args=server.args or [],
                        url=server.url,
                        env=server.env or {},
                    )
                )

        # Build the context
        context = AgentExecutionContext(
            agent=AgentIdentity(
                name=agent.name,
                parser=parser_type,
                role="executor",
                capabilities=["executor"],
            ),
            task=TaskContext(
                id=result_id,
                description=task,
                plan_id=plan.id if plan else None,
                plan_content=plan.content if plan else None,
            ),
            mcp=MCPSettings(
                orchestrator=orchestrator_config,
                servers=mcp_servers,
            ),
            execution=ExecutionSettings(
                working_dir=str(working_dir),
                timeout_seconds=timeout_seconds,
                permission_mode=permission_mode,
                max_tokens=max_tokens,
            ),
        )

        return context.write_to_worktree(working_dir)

    except Exception as e:
        # Log but don't fail execution if config writing fails
        logging.warning(f"Failed to write execution context: {e}")
        return None


QuestionStrategy = Literal["prompt_user", "auto_answer", "fail"]


def create_question_tool(
    strategy: QuestionStrategy,
    max_questions: int = 5,
    auto_answer_agent: ModelAdapter | None = None,
    user_prompt_callback: Callable[[str], Awaitable[str]] | None = None,
    budget_tracker: BudgetTracker | None = None,
) -> AskQuestionTool:
    """Create an AskQuestionTool configured with the appropriate handler.

    Args:
        strategy: How to handle questions - "fail", "prompt_user", or "auto_answer".
        max_questions: Maximum number of questions to handle before failing.
        auto_answer_agent: Agent to use for auto-answering (required for "auto_answer").
        user_prompt_callback: Async callback to prompt user (required for "prompt_user").
        budget_tracker: Optional budget tracker for recording auto_answer usage.

    Returns:
        Configured AskQuestionTool ready for use.
    """
    handler: QuestionHandler | None = None

    if strategy == "prompt_user" and user_prompt_callback is not None:
        handler = user_prompt_callback

    elif strategy == "auto_answer" and auto_answer_agent is not None:

        async def auto_answer_handler(question: str) -> str:
            """Use another agent to answer the question."""
            response = await auto_answer_agent.call(
                prompt=f"Please answer this question concisely:\n\n{question}",
                system="You are a helpful assistant answering questions from another AI agent. "
                "Be concise and direct. If you don't know, say so.",
                max_tokens=500,
                temperature=0.3,
            )
            # Record usage for auto-answer calls to maintain accurate budget tracking
            if budget_tracker:
                budget_tracker.record_usage(
                    auto_answer_agent.name,
                    response.token_usage,
                    auto_answer_agent.estimate_cost(response.token_usage),
                    phase="auto_answer",
                )
            return response.content

        handler = auto_answer_handler

    return AskQuestionTool(
        strategy=strategy,
        max_questions=max_questions,
        handler=handler,
    )


# Keep legacy function for backwards compatibility
def create_question_handler(
    strategy: QuestionStrategy,
    auto_answer_agent: ModelAdapter | None = None,
    max_questions: int = 5,
    user_prompt_callback: Callable[[str], str] | None = None,
) -> Callable[[str], str] | None:
    """Create a sync question handler callback (legacy).

    Deprecated: Use create_question_tool() instead for async support.

    Args:
        strategy: How to handle questions - "fail", "prompt_user", or "auto_answer".
        auto_answer_agent: Agent to use for auto-answering (required for "auto_answer").
        max_questions: Maximum number of questions to handle before failing.
        user_prompt_callback: Callback to prompt user (required for "prompt_user").

    Returns:
        A callback function for handling questions, or None for "fail" strategy.
    """
    if strategy == "fail":
        return None

    questions_asked: list[str] = []

    def handler(question: str) -> str:
        nonlocal questions_asked

        if len(questions_asked) >= max_questions:
            raise RuntimeError(f"Maximum questions ({max_questions}) exceeded. Questions asked: {questions_asked}")

        questions_asked.append(question)

        if strategy == "prompt_user":
            if user_prompt_callback is None:
                raise RuntimeError("prompt_user strategy requires a user_prompt_callback")
            return user_prompt_callback(question)

        if strategy == "auto_answer":
            if auto_answer_agent is None:
                raise RuntimeError("auto_answer strategy requires an auto_answer_agent")
            raise NotImplementedError("auto_answer strategy requires async support - use create_question_tool()")

        raise ValueError(f"Unknown question strategy: {strategy}")

    return handler


async def execute_single_agent(
    agent: ModelAdapter,
    task: str,
    worktree_path: str | None = None,
    budget_tracker: BudgetTracker | None = None,
    phase: str = "execution",
    worktree_mgr: WorktreeManager | None = None,
    timeout_seconds: int = 1200,
    on_question: Callable[[str], str] | None = None,
    question_tool: AskQuestionTool | None = None,
    on_worktree_created: Callable[[str, Path], None] | None = None,
    run_tests: bool = False,
    test_command: Optional[str] = None,
    test_timeout_seconds: int = 300,
    extra_mcp_servers: list[MCPServerConfig] | None = None,
    base_ref: str | None = None,
    plan: Plan | None = None,
) -> ExecutionResult:
    """Execute single agent, optionally in existing worktree.

    Args:
        agent: The model adapter to use.
        task: The task description/prompt.
        worktree_path: Optional existing worktree path to reuse.
        budget_tracker: Optional budget tracker for recording usage.
        phase: Workflow phase name for budget tracking.
        worktree_mgr: Worktree manager for creating/managing worktrees.
        timeout_seconds: Timeout for agent execution.
        on_question: Optional callback for handling agent questions (legacy).
        question_tool: AskQuestionTool to expose to the agent for asking questions.
        on_worktree_created: Callback(agent_name, path) called after worktree creation,
                            before agent runs. Use to write agent-specific config files.
        run_tests: Whether to run tests after agent execution.
        test_command: Test command to use (auto-detected if None).
        test_timeout_seconds: Timeout for test execution.
        extra_mcp_servers: Additional MCP servers to inject for agent execution.
        base_ref: Git ref to create worktree from.
        plan: Optional plan being executed (for context file).

    Returns:
        ExecutionResult with outcome of execution.
    """
    start = time.time()
    result_id = f"exec-{uuid.uuid4().hex[:8]}"

    worktree: Worktree | None = None
    working_dir: Path

    # Inject question tool into task if enabled
    task_with_tools = task
    if question_tool and question_tool.is_enabled:
        tool_prompt = question_tool.to_prompt_injection()
        if tool_prompt:
            task_with_tools = f"{task}\n\n{tool_prompt}"

    # Encourage tool use over markdown edits
    tool_usage_note = (
        "Use available tools (e.g., fs.write_file via MCP) to apply changes directly. "
        "Do not emit markdown code blocks; write to the filesystem instead."
    )
    task_with_tools = f"{task_with_tools}\n\n{tool_usage_note}"

    try:
        # Determine working directory
        if worktree_path:
            # Reuse existing worktree
            working_dir = Path(worktree_path)
        elif worktree_mgr:
            # Create new worktree based on specified ref (defaults to HEAD)
            worktree = worktree_mgr.create(name=result_id, ref=base_ref or "HEAD")
            working_dir = worktree.path
        else:
            # Use current directory (no worktree)
            working_dir = Path.cwd()

        # Call worktree created callback (e.g., to write MCP config)
        if on_worktree_created:
            on_worktree_created(agent.name, working_dir)

        # Write agent execution context to worktree
        _write_execution_context(
            agent=agent,
            result_id=result_id,
            task=task,
            working_dir=working_dir,
            timeout_seconds=timeout_seconds,
            extra_mcp_servers=extra_mcp_servers,
            plan=plan,
        )

        # Execute the task
        response = await agent.run_agentic(
            task=task_with_tools,
            working_dir=str(working_dir),
            timeout_seconds=timeout_seconds,
            on_question=on_question,
            extra_mcp_servers=extra_mcp_servers,
        )

        # Record budget usage with phase tracking
        if budget_tracker:
            budget_tracker.record_usage(
                agent.name,
                response.token_usage,
                agent.estimate_cost(response.token_usage),
                phase=phase,
            )

        # Only apply markdown code blocks when no worktree is managing output.
        # Capable agents should write to disk via tools rather than emitting patches.
        if not worktree_mgr:
            apply_code_blocks_from_text(response.content, working_dir)

        # Get the diff if using worktrees
        diff = None
        if worktree_mgr and (worktree or worktree_path):
            # For reused worktrees, create temp Worktree object for diff extraction
            target_worktree = worktree
            if worktree_path and not worktree:
                target_worktree = Worktree(
                    name=Path(worktree_path).name,
                    path=Path(worktree_path),
                    ref="HEAD",
                )
            if target_worktree:
                diff = worktree_mgr.get_diff(target_worktree)

                # Commit the changes to preserve them in the worktree
                if diff and diff.strip():
                    commit_sha = worktree_mgr.commit_changes(
                        target_worktree,
                        f"Deliberate: Agent {agent.name} execution",
                    )
                    if commit_sha:
                        logging.info(f"Committed agent changes: {commit_sha[:8]}")

        # Run tests if requested
        validation_result = None
        if run_tests:
            cmd = test_command
            if not cmd:
                cmd = await detect_test_command_llm(working_dir, agent)

            if cmd:
                runner = ValidationRunner(
                    working_dir,
                    cmd,
                    test_timeout_seconds,
                    require_tests=run_tests,
                )
                validation_result = await runner.run()

        # Collect questions asked during execution
        questions = []
        if question_tool:
            questions = [q.question for q in question_tool.questions_asked]

        # Determine error category and success status
        error_category = None
        execution_success = True

        if validation_result and not validation_result.passed:
            error_category = "test_failure"
            execution_success = False

        return ExecutionResult(
            id=result_id,
            agent=agent.name,
            worktree_path=working_dir,
            diff=diff,
            summary=response.content,
            success=execution_success,
            error_category=error_category,
            questions_asked=questions,
            duration_seconds=time.time() - start,
            token_usage=response.token_usage,
            stdout=response.stdout,
            validation_result=validation_result,
        )

    except Exception as e:
        # Collect questions even on failure
        questions = []
        if question_tool:
            questions = [q.question for q in question_tool.questions_asked]

        return ExecutionResult(
            id=result_id,
            agent=agent.name,
            worktree_path=working_dir if "working_dir" in locals() else None,
            diff=None,
            summary="",
            success=False,
            error=str(e),
            error_category=_categorize_error(e),
            questions_asked=questions,
            duration_seconds=time.time() - start,
        )


@dataclass
class ExecutionPhase:
    """Orchestrates the execution phase of the jury workflow.

    Agents execute the task (with optional plan) in isolated
    git worktrees, producing diffs and summaries.
    """

    agents: list[str]
    adapters: dict[str, ModelAdapter]
    budget: BudgetTracker
    worktree_mgr: WorktreeManager
    context: JuryContext | None = None
    use_worktrees: bool = True
    timeout_seconds: int = 1200

    # Question handling configuration
    question_strategy: QuestionStrategy = "fail"
    max_questions: int = 5
    auto_answer_agent: ModelAdapter | None = None
    user_prompt_callback: Callable[[str], Awaitable[str]] | None = None
    # Legacy sync callback (deprecated)
    question_handler: Callable[[str], str] | None = None

    # Parallelism configuration
    parallelism_enabled: bool = False
    max_parallel: int = 1

    # Validation configuration
    run_tests: bool = False
    tests_command: Optional[str] = None  # Auto-detected if None
    test_timeout_seconds: int = 300

    # Worktree setup callback (e.g., for writing MCP config)
    on_worktree_created: Callable[[str, Path], None] | None = None

    # MCP server injection callback (returns agent-specific MCP config)
    get_mcp_config_for_agent: Callable[[str], MCPServerConfig | None] | None = None
    # Base ref to create execution worktrees from (e.g., deliberate/<branch>)
    base_ref: str | None = None

    def __post_init__(self):
        """Backfill dependencies from context when provided."""
        if self.context:
            if not getattr(self, "worktree_mgr", None):
                self.worktree_mgr = self.context.worktree_mgr
            if not getattr(self, "budget", None):
                self.budget = self.context.budget

    async def run(
        self,
        task: str,
        plan: Plan | None = None,
    ) -> list[ExecutionResult]:
        """Run the execution phase.

        Args:
            task: The task description.
            plan: Optional plan to follow.

        Returns:
            List of execution results from all agents.
        """
        verbose_logger = get_verbose_logger()
        for agent_name in self.agents:
            verbose_logger.update_agent_status(agent_name, "pending", "Queued for execution")

        if not self.parallelism_enabled:
            results = []
            for agent_name in self.agents:
                result = await self._execute_single(agent_name, task, plan)
                results.append(result)
            return results

        # Parallel execution
        semaphore = asyncio.Semaphore(self.max_parallel)

        async def _run_limited(name: str):
            async with semaphore:
                return await self._execute_single(name, task, plan)

        return await asyncio.gather(*[_run_limited(name) for name in self.agents])

    async def _execute_single(
        self,
        agent_name: str,
        task: str,
        plan: Plan | None,
    ) -> ExecutionResult:
        """Execute the task with a single agent."""
        verbose_logger = get_verbose_logger()
        adapter = self.adapters.get(agent_name)
        if not adapter:
            verbose_logger.update_agent_status(agent_name, "error", "Adapter not found")
            return ExecutionResult(
                id=f"exec-{uuid.uuid4().hex[:8]}",
                agent=agent_name,
                worktree_path=None,
                diff=None,
                summary="",
                success=False,
                error="Adapter not found",
                duration_seconds=0.0,
            )

        # Build the prompt
        if plan:
            plan_section = EXECUTION_WITH_PLAN.format(plan=plan.content)
        else:
            plan_section = EXECUTION_NO_PLAN

        prompt = EXECUTION_PROMPT.format(
            task=task,
            plan_section=plan_section,
            working_dir="<will be set by executor>",
        )

        # Create question tool for this execution
        question_tool = create_question_tool(
            strategy=self.question_strategy,
            max_questions=self.max_questions,
            auto_answer_agent=self.auto_answer_agent,
            user_prompt_callback=self.user_prompt_callback,
            budget_tracker=self.budget,
        )

        # Use standalone function with phase tracking
        verbose_logger.update_agent_status(agent_name, "running", "Preparing worktree")

        # Get MCP config for this agent (e.g., orchestrator SSE server with agent-specific token)
        mcp_servers: list[MCPServerConfig] | None = None
        if self.get_mcp_config_for_agent:
            mcp_config = self.get_mcp_config_for_agent(agent_name)
            if mcp_config:
                mcp_servers = [mcp_config]

        try:
            result = await execute_single_agent(
                agent=adapter,
                task=prompt,
                worktree_path=None,  # Create new worktree
                budget_tracker=self.budget,
                phase="execution",
                worktree_mgr=self.worktree_mgr if self.use_worktrees else None,
                timeout_seconds=self.timeout_seconds,
                on_question=self.question_handler,
                question_tool=question_tool,
                on_worktree_created=self.on_worktree_created,
                run_tests=self.run_tests,
                test_command=self.tests_command,
                test_timeout_seconds=self.test_timeout_seconds,
                extra_mcp_servers=mcp_servers,
                base_ref=self.base_ref,
                plan=plan,
            )
        except Exception as exc:
            verbose_logger.update_agent_status(agent_name, "error", f"Failed: {exc}")
            raise

        status = "completed" if result.success else "error"
        action = result.error or (
            "Validation failed" if result.validation_result and not result.validation_result.passed else "Finished"
        )
        if result.diff and not result.error:
            action = "Changes ready"
        verbose_logger.update_agent_status(agent_name, status, action)

        return result

    # _run_tests method removed as it's no longer needed
