"""Main orchestrator for deliberate workflow."""

import asyncio
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt

from deliberate.adapters.api_adapter import APIAdapter
from deliberate.adapters.base import ModelAdapter
from deliberate.adapters.cli_adapter import CLIAdapter
from deliberate.adapters.fake_adapter import FakeAdapter
from deliberate.adapters.mcp_adapter import MCPAdapter
from deliberate.budget.tracker import BudgetTracker
from deliberate.config import DeliberateConfig, TriggerPolicy
from deliberate.context import JuryContext
from deliberate.git.worktree import Worktree, WorktreeManager
from deliberate.mcp_orchestrator_server import OrchestratorServer, StatusUpdate
from deliberate.phases.execution import ExecutionPhase
from deliberate.phases.planning import PlanningPhase
from deliberate.phases.refinement import RefinementOrchestrator
from deliberate.phases.review import ReviewPhase
from deliberate.review.criteria import generate_review_criteria
from deliberate.review_tui import ReviewTUI
from deliberate.tracing.setup import get_tracer
from deliberate.tracking import get_tracker, record_jury_result
from deliberate.types import DebateMessage, ExecutionResult, JuryResult, Plan, Review, VoteResult
from deliberate.validation.types import PerformanceIssue, ValidationResult
from deliberate.verbose_logger import get_verbose_logger


class Orchestrator:
    """Orchestrates the complete deliberate workflow.

    Coordinates the three phases (planning, execution, review)
    and manages adapters, worktrees, and budget.
    """

    def __init__(
        self,
        config: DeliberateConfig,
        repo_root: Path,
        interactive_review: bool = False,
        console: Console | None = None,
        *,
        budget_tracker: BudgetTracker | None = None,
        worktree_mgr: WorktreeManager | None = None,
        execution_base_ref: str | None = None,
    ):
        """Initialize the orchestrator.

        Args:
            config: The deliberate configuration.
            repo_root: Path to the repository root.
            interactive_review: Enable interactive TUI for reviewing results.
            console: Rich console instance (for interactive mode).
        """
        self.config = config
        self.repo_root = repo_root.resolve()
        self.interactive_review = interactive_review
        self.console = console or Console()
        self.execution_base_ref = execution_base_ref

        # Initialize tracker explicitly
        db_path = None
        if self.config.tracking.db_path:
            db_path = Path(self.config.tracking.db_path)
        self.tracker = get_tracker(db_path)

        # Initialize budget tracker
        self.budget = budget_tracker or BudgetTracker(
            max_total_tokens=config.limits.budget.max_total_tokens,
            max_cost_usd=config.limits.budget.max_cost_usd,
            max_requests_per_agent=config.limits.budget.max_requests_per_agent,
            hard_timeout_seconds=config.limits.time.hard_timeout_minutes * 60,
        )

        # Set up budget warning callback to log via verbose_logger
        def budget_warning_callback(message: str, level: str) -> None:
            verbose_logger = get_verbose_logger()
            verbose_logger.log_event(f"BUDGET: {message}", level)

        self.budget.set_warning_callback(budget_warning_callback)

        # Initialize worktree manager
        worktree_root = repo_root / config.workflow.execution.worktree.root
        self.worktrees = worktree_mgr or WorktreeManager(repo_root, worktree_root)

        # Shared runtime context
        self.context = JuryContext(
            repo_root=self.repo_root,
            budget=self.budget,
            config=self.config,
            worktree_mgr=self.worktrees,
        )

        # Build adapters
        self.adapters = self._build_adapters()

        # Initialize MCP orchestrator server (for agent status updates)
        self.mcp_server: OrchestratorServer | None = None
        self.mcp_server_task: asyncio.Task | None = None

        # Initialize phases
        self.planning = self._build_planning_phase()
        self.execution = self._build_execution_phase()
        self.review = self._build_review_phase()

    def _build_adapters(self) -> dict[str, ModelAdapter]:
        """Build adapters for all configured agents."""
        adapters: dict[str, ModelAdapter] = {}

        for name, agent_cfg in self.config.agents.items():
            adapter: ModelAdapter

            if agent_cfg.type == "fake":
                adapter = FakeAdapter(
                    name=name,
                    behavior=agent_cfg.behavior or "echo",
                )
            elif agent_cfg.type == "cli":
                adapter = CLIAdapter(
                    name=name,
                    command=agent_cfg.command,
                    env=agent_cfg.env,
                    timeout_seconds=agent_cfg.config.timeout_seconds,
                    telemetry_endpoint=agent_cfg.telemetry_endpoint or self.config.telemetry.endpoint,
                    telemetry_exporter=agent_cfg.telemetry_exporter or self.config.telemetry.exporter,
                    telemetry_environment=agent_cfg.telemetry_environment or self.config.telemetry.environment,
                    telemetry_log_user_prompt=agent_cfg.telemetry_log_user_prompt
                    if agent_cfg.telemetry_log_user_prompt is not None
                    else self.config.telemetry.log_user_prompt,
                    permission_mode=agent_cfg.permission_mode,
                    parser_type=getattr(agent_cfg, "parser", None),
                    model_id=agent_cfg.model,
                )
            elif agent_cfg.type == "mcp":
                # Use MCP adapter for JSON-RPC communication
                adapter = MCPAdapter(
                    name=name,
                    command=agent_cfg.command,
                    env=agent_cfg.env,
                    timeout_seconds=agent_cfg.config.timeout_seconds,
                )
            elif agent_cfg.type == "api":
                adapter = APIAdapter(
                    name=name,
                    model=agent_cfg.model or "gpt-5",  # Default if not specified
                    env=agent_cfg.env,
                    timeout_seconds=agent_cfg.config.timeout_seconds,
                    config=agent_cfg.config.model_dump(),
                )
            else:
                # Unknown type, use fake
                adapter = FakeAdapter(name=name, behavior="echo")

            adapters[name] = adapter

        return adapters

    def _select_criteria_agent(self, preferred: str | None) -> ModelAdapter | None:
        """Pick the best available agent for criteria generation."""
        review_agents = self.config.workflow.review.agents
        if preferred and preferred in self.adapters:
            return self.adapters[preferred]

        # Prefer a non-fake review agent if available
        for name in review_agents:
            cfg = self.config.agents.get(name)
            if cfg and cfg.type != "fake":
                return self.adapters.get(name)

        if review_agents:
            return self.adapters.get(review_agents[0])

        return None

    async def _maybe_generate_dynamic_criteria(self, task: str) -> None:
        """Optionally generate task-specific review criteria before planning."""
        cfg = self.config.workflow.review.context_analysis
        if not cfg.enabled:
            return

        adapter = self._select_criteria_agent(cfg.agent)
        if not adapter:
            return

        verbose_logger = get_verbose_logger()

        try:
            result = await generate_review_criteria(
                task,
                self.repo_root,
                adapter,
                cfg.max_criteria,
            )
        except Exception as exc:  # pragma: no cover - defensive
            verbose_logger.log_event(f"Dynamic criteria generation failed: {exc}", "warning")
            return

        if result:
            names, descriptions, tokens = result
            self.review.update_criteria(names, descriptions)
            # Record budget for the criteria agent
            try:
                self.budget.record_usage(
                    adapter.name,
                    tokens,
                    adapter.estimate_cost(tokens),
                    phase="review_criteria",
                )
            except Exception:
                pass
            verbose_logger.log_event(
                f"Using dynamic review criteria from {adapter.name}: {', '.join(names)}",
                "info",
            )

    def _build_planning_phase(self) -> PlanningPhase:
        """Build the planning phase."""
        planning_cfg = self.config.workflow.planning
        return PlanningPhase(
            agents=planning_cfg.agents,
            adapters=self.adapters,
            budget=self.budget,
            debate_enabled=planning_cfg.debate.enabled,
            debate_rounds=planning_cfg.debate.rounds,
            selection_method=planning_cfg.selection.method,
            judge_agent=planning_cfg.selection.judge,
        )

    def _build_execution_phase(self) -> ExecutionPhase:
        """Build the execution phase."""
        execution_cfg = self.config.workflow.execution
        return ExecutionPhase(
            agents=execution_cfg.agents,
            adapters=self.adapters,
            budget=self.budget,
            worktree_mgr=self.worktrees,
            context=self.context,
            use_worktrees=execution_cfg.worktree.enabled,
            timeout_seconds=self.config.limits.time.phase_timeouts.get("execution", 25) * 60,
            parallelism_enabled=execution_cfg.parallelism.enabled,
            max_parallel=execution_cfg.parallelism.max_parallel,
            question_strategy=execution_cfg.questions.strategy,
            max_questions=execution_cfg.questions.max_questions,
            auto_answer_agent=self.adapters.get(execution_cfg.questions.auto_answer_agent)
            if execution_cfg.questions.auto_answer_agent
            else None,
            run_tests=self.config.workflow.require_tests,
            on_worktree_created=None,  # MCP config now written via _write_execution_context()
            get_mcp_config_for_agent=self.get_mcp_server_config_for_agent,
            base_ref=self.execution_base_ref,
        )

    def _build_review_phase(self) -> ReviewPhase:
        """Build the review phase."""
        review_cfg = self.config.workflow.review
        return ReviewPhase(
            agents=review_cfg.agents,
            adapters=self.adapters,
            budget=self.budget,
            criteria_descriptions=None,
            criteria=review_cfg.scoring.criteria,
            scale=review_cfg.scoring.scale,
            aggregation_method=review_cfg.aggregation.method,
            approval_threshold=review_cfg.aggregation.min_approval_ratio,
            reject_is_veto=review_cfg.aggregation.reject_is_veto,
        )

    # -------------------------------------------------------------------------
    # Auto-Tuner Methods
    # -------------------------------------------------------------------------

    def _should_trigger_evolution(
        self,
        execution_results: list[ExecutionResult],
        evolution_attempts: int,
    ) -> tuple[bool, ValidationResult | None]:
        """Check if evolution should be triggered based on validation results.

        The auto-tuner triggers evolution when:
        1. Auto-tuner is enabled
        2. Tests passed (correctness_passed=True)
        3. Performance is suboptimal (needs_optimization=True)
        4. Policy is set to EVOLVE
        5. Haven't exceeded max evolution attempts

        Args:
            execution_results: Results from execution phase.
            evolution_attempts: Number of evolution attempts so far.

        Returns:
            Tuple of (should_trigger, triggering_validation_result).
        """
        auto_tuner = self.config.workflow.auto_tuner
        evolution_cfg = self.config.workflow.evolution

        # Check if auto-tuner is enabled
        if not auto_tuner.enabled:
            return (False, None)

        # Check if evolution is available
        if not evolution_cfg.enabled or not evolution_cfg.agents:
            return (False, None)

        # Check attempt limits
        if evolution_attempts >= auto_tuner.max_evolution_attempts:
            return (False, None)

        # Find execution results that need optimization
        for result in execution_results:
            if not result.validation_result:
                continue

            vr = result.validation_result

            # Must have passed correctness checks
            if not vr.correctness_passed:
                continue

            # Check if optimization is needed
            if not vr.needs_optimization:
                continue

            # Check policy based on performance issue type
            if vr.performance_issue == PerformanceIssue.SLOW_EXECUTION:
                if auto_tuner.on_slow_execution == TriggerPolicy.EVOLVE:
                    return (True, vr)
            elif vr.performance_issue == PerformanceIssue.HIGH_MEMORY:
                if auto_tuner.on_high_memory == TriggerPolicy.EVOLVE:
                    return (True, vr)
            elif vr.performance_issue == PerformanceIssue.TIMEOUT:
                # Timeout is treated as slow execution
                if auto_tuner.on_slow_execution == TriggerPolicy.EVOLVE:
                    return (True, vr)

        return (False, None)

    async def _run_evolution_for_optimization(
        self,
        task: str,
        execution_result: ExecutionResult,
        validation_result: ValidationResult,
    ) -> ExecutionResult | None:
        """Run evolution to optimize a passing but slow execution result.

        Uses the EvolutionController to iteratively improve the code
        with a focus on performance optimization.

        Args:
            task: Original task description.
            execution_result: The execution result to optimize.
            validation_result: The validation result with performance issues.

        Returns:
            Improved ExecutionResult if evolution succeeded, None otherwise.
        """
        from deliberate.evolution.controller import EvolutionController
        from deliberate.evolution.database import ProgramDatabase
        from deliberate.evolution.types import EvolutionConfig

        verbose_logger = get_verbose_logger()
        auto_tuner = self.config.workflow.auto_tuner
        evolution_cfg = self.config.workflow.evolution

        verbose_logger.log_event(
            f"Auto-tuner triggered: {validation_result.performance_issue.value}",
            "info",
        )

        # Build evolution config with optimization focus
        config = EvolutionConfig(
            max_iterations=auto_tuner.max_evolution_attempts,
            target_score=0.95,  # High bar for optimization
            prefer_diffs=evolution_cfg.prefer_diffs,
            max_stagnant_iterations=2,  # Stop quickly if not improving
        )

        # Create program database
        database = ProgramDatabase()

        # Get evolution agents
        evolution_agents = {name: self.adapters[name] for name in evolution_cfg.agents if name in self.adapters}

        if not evolution_agents:
            verbose_logger.log_event("No evolution agents available", "warning")
            return None

        # Build optimization task with performance context
        optimization_task = self._build_optimization_task(
            task,
            validation_result,
            auto_tuner.optimization_target,
        )

        # Create controller
        controller = EvolutionController(
            database=database,
            agents=evolution_agents,
            config=config,
            budget_tracker=self.budget,
        )

        # Get the code to optimize
        seed_code = None
        if execution_result.worktree_path:
            # Try to get the diff content as seed
            seed_code = execution_result.diff

        try:
            # Run evolution
            result = await controller.evolve(
                task=optimization_task,
                seed_program=seed_code,
                working_dir=Path(execution_result.worktree_path) if execution_result.worktree_path else self.repo_root,
            )

            if result.best_program and result.success:
                evolved_code = result.best_program.code
                score = result.best_program.metrics.overall_score
                verbose_logger.log_event(
                    f"Evolution improved solution: score {score:.2f}",
                    "success",
                )

                # Apply evolved code to worktree
                if execution_result.worktree_path and evolved_code:
                    working_dir = Path(execution_result.worktree_path)

                    # Determine target file from task or find Python files
                    target_file = self._find_target_file(task, working_dir)
                    if target_file:
                        target_file.write_text(evolved_code)
                        verbose_logger.log_event(
                            f"Applied evolved code to {target_file.name}",
                            "info",
                        )

                        # Commit the evolution result
                        if self.worktrees:
                            from deliberate.git.worktree import Worktree

                            wt = Worktree(
                                name=working_dir.name,
                                path=working_dir,
                                ref="HEAD",
                            )
                            commit_sha = self.worktrees.commit_changes(
                                wt,
                                f"Deliberate: Evolution optimization (score: {score:.2f})",
                            )
                            if commit_sha:
                                verbose_logger.log_event(
                                    f"Committed evolution: {commit_sha[:8]}",
                                    "info",
                                )

                        # Get updated diff
                        if self.worktrees:
                            updated_diff = self.worktrees.get_diff(wt)
                        else:
                            updated_diff = evolved_code

                        # Return updated execution result
                        return ExecutionResult(
                            id=execution_result.id,
                            agent=execution_result.agent,
                            worktree_path=execution_result.worktree_path,
                            diff=updated_diff,
                            summary=f"Evolved: {execution_result.summary}",
                            success=True,
                            validation_result=execution_result.validation_result,
                            duration_seconds=execution_result.duration_seconds,
                            token_usage=execution_result.token_usage + result.total_tokens,
                        )

                return execution_result

            verbose_logger.log_event("Evolution did not find improvement", "warning")
            return None

        except Exception as e:
            verbose_logger.log_event(f"Evolution failed: {e}", "error")
            return None

    def _find_target_file(self, task: str, working_dir: Path) -> Path | None:
        """Find the target file for evolved code.

        Args:
            task: The original task description.
            working_dir: The working directory to search in.

        Returns:
            Path to the target file, or None if not found.
        """
        import re

        # Look for file references in task
        file_patterns = [
            r"(?:file|in|modify|edit|fix|optimize)\s+[`'\"]?(\S+\.py)[`'\"]?",
            r"(\S+\.py)",
        ]
        for pattern in file_patterns:
            match = re.search(pattern, task, re.IGNORECASE)
            if match:
                candidate = working_dir / match.group(1)
                if candidate.exists():
                    return candidate

        # Fallback: find main Python files (not tests)
        py_files = [
            f
            for f in working_dir.glob("*.py")
            if not f.name.startswith("test_") and f.name != "conftest.py" and f.name != "__init__.py"
        ]
        if py_files:
            # Prefer files with "main", "app", or "solution" in the name
            for keyword in ["solution", "main", "app", "pipeline"]:
                for f in py_files:
                    if keyword in f.name.lower():
                        return f
            # Otherwise return the first non-test file
            return py_files[0]

        return None

    def _build_optimization_task(
        self,
        original_task: str,
        validation_result: ValidationResult,
        target: str,
    ) -> str:
        """Build an optimization-focused task description.

        Args:
            original_task: The original task description.
            validation_result: Validation result with performance details.
            target: Optimization target (latency, memory, token_count).

        Returns:
            Enhanced task description for optimization.
        """
        parts = [
            "# Optimization Task",
            "",
            "## Original Task",
            original_task,
            "",
            "## Performance Issue",
            f"The current implementation has a performance issue: {validation_result.performance_issue.value}",
            "",
            f"## Optimization Target: {target}",
        ]

        if target == "latency":
            parts.extend(
                [
                    "Focus on reducing execution time. Consider:",
                    "- Algorithmic improvements (better time complexity)",
                    "- Caching frequently computed values",
                    "- Avoiding unnecessary operations",
                    "- Using more efficient data structures",
                ]
            )
        elif target == "memory":
            parts.extend(
                [
                    "Focus on reducing memory usage. Consider:",
                    "- Using generators instead of lists",
                    "- Processing data in chunks",
                    "- Avoiding duplicate data storage",
                    "- Using memory-efficient data structures",
                ]
            )
        elif target == "token_count":
            parts.extend(
                [
                    "Focus on reducing token/API usage. Consider:",
                    "- Batching API calls",
                    "- Caching API responses",
                    "- Reducing prompt size",
                    "- Using more efficient prompts",
                ]
            )

        if validation_result.slowest_tests:
            parts.extend(
                [
                    "",
                    "## Slowest Tests",
                    "These tests are the primary bottlenecks:",
                ]
            )
            for name, duration in validation_result.slowest_tests[:5]:
                parts.append(f"- {name}: {duration:.2f}s")

        return "\n".join(parts)

    async def _start_mcp_server(self) -> str | None:
        """Start the MCP orchestrator server for agent status updates.

        Creates tokens for each configured agent. The orchestrator can then
        write .mcp.json files to worktrees with agent-specific auth tokens.

        Returns:
            The server URL if started successfully, None otherwise.
        """
        try:

            def status_callback(update: StatusUpdate):
                """Handle status updates from agents."""
                verbose_logger = get_verbose_logger()
                # Update the agent status in the dashboard
                verbose_logger.update_agent_status(
                    update.agent_name,
                    update.status,
                    update.message[:60] + "..." if len(update.message) > 60 else update.message,
                )
                # Also log the full message
                verbose_logger.log_event(
                    f"[{update.agent_name}] {update.message[:120]}",
                    "info" if update.status != "error" else "error",
                )

            # Get all agent names for token generation
            agent_names = list(self.adapters.keys())

            # Build static tokens from config or environment variable
            static_tokens: dict[str, str] = dict(self.config.mcp.static_tokens)

            # If static_token_env_var is set and has a value, use it for agents
            # that need static tokens (like Codex with global MCP config)
            env_var = self.config.mcp.static_token_env_var
            if env_var:
                import os

                static_token = os.environ.get(env_var)
                if static_token:
                    # Apply static token to agents that use it (those with disable_auth behavior)
                    # For now, add it for any agent not already in static_tokens
                    for agent_name in agent_names:
                        if agent_name not in static_tokens:
                            static_tokens[agent_name] = static_token

            # Use configured host/port or defaults
            self.mcp_server = OrchestratorServer(
                db_connection=self.tracker.get_connection(),
                agent_names=agent_names,
                callback=status_callback,
                host=self.config.mcp.server_host,
                port=self.config.mcp.server_port,
                disable_auth=self.config.mcp.disable_auth,
                static_tokens=static_tokens if static_tokens else None,
            )

            # Start server in background task
            self.mcp_server_task = asyncio.create_task(self.mcp_server.run())

            # Wait a moment for server to start
            await asyncio.sleep(0.5)

            return self.mcp_server.get_url()
        except Exception as e:
            print(f"Warning: Failed to start MCP server: {e}")
            return None

    def get_mcp_server_config_for_agent(self, agent_name: str):
        """Get MCPServerConfig for an agent to pass to run_agentic().

        This returns an MCPServerConfig object that can be injected into the
        agent's execution via extra_mcp_servers parameter.

        Args:
            agent_name: Name of the agent

        Returns:
            MCPServerConfig or None if MCP server not running
        """
        if not self.mcp_server:
            return None
        return self.mcp_server.get_mcp_server_config(agent_name)

    # TODO: shouldn't be here - not an orchestrator concern
    def write_mcp_config_to_path(self, agent_name: str, path: Path) -> bool:
        """Write .mcp.json for an agent to the given path."""
        if not self.mcp_server:
            return False

        config = self.mcp_server.get_mcp_config_for_agent(agent_name)
        if not config:
            return False

        try:
            path = Path(path)
            path.mkdir(parents=True, exist_ok=True)
            config_path = path / ".mcp.json"
            config_path.write_text(json.dumps(config, indent=2))
            return True
        except Exception as exc:  # pragma: no cover - defensive
            verbose_logger = get_verbose_logger()
            verbose_logger.log_event(f"Failed to write .mcp.json: {exc}", "error")
            return False

    async def _stop_mcp_server(self):
        """Stop the MCP orchestrator server."""
        if self.mcp_server:
            await self.mcp_server.shutdown()

        if self.mcp_server_task:
            self.mcp_server_task.cancel()
            try:
                await self.mcp_server_task
            except asyncio.CancelledError:
                pass

    def _collect_status_updates(self) -> list[dict]:
        """Collect status updates from the MCP server if running."""
        if not self.mcp_server:
            return []

        updates = self.mcp_server.get_updates()
        return [
            {
                "agent_name": u.agent_name,
                "phase": u.phase,
                "status": u.status,
                "message": u.message,
                "timestamp": u.timestamp.isoformat(),
                "metadata": u.metadata,
            }
            for u in updates
        ]

    def cleanup_worktrees(self) -> None:
        """Expose worktree cleanup for callers who defer cleanup."""
        if self.config.workflow.execution.worktree.cleanup:
            self.worktrees.cleanup_all()

    def _branch_name_from_worktree(self, worktree: Worktree) -> str:
        """Derive a branch name for applied changes."""
        safe_name = worktree.name.replace(" ", "-")
        return f"deliberate/{safe_name}"

    def _get_current_ref(self) -> str:
        """Return the current branch name or HEAD sha if detached."""
        branch_result = self.worktrees._run_git(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=self.repo_root)
        branch = branch_result.stdout.strip() or "HEAD"
        if branch == "HEAD":
            sha_result = self.worktrees._run_git(["git", "rev-parse", "HEAD"], cwd=self.repo_root)
            return sha_result.stdout.strip()
        return branch

    def _edit_text(self, content: str) -> str | None:
        """Open a temp editor session for the user and return edits."""
        try:
            return click.edit(content, extension=".md")
        except Exception:
            return None

    def _human_plan_gate(self, plan: Plan) -> bool:
        """Ask the user to approve or edit the plan before execution."""
        if not self.interactive_review:
            return True

        self.console.print("\n[bold yellow]Review the plan before execution[/bold yellow]\n")
        self.console.print(Markdown(plan.content))

        while True:
            choice = Prompt.ask(
                "Continue to execution? [y/n/edit]",
                choices=["y", "n", "edit"],
                default="y",
            )

            if choice == "y":
                return True
            if choice == "n":
                return False

            edited = self._edit_text(plan.content)
            if edited is not None:
                plan.content = edited.strip()
                self.console.print("\n[green]Updated plan:[/green]\n")
                self.console.print(Markdown(plan.content))
            else:
                self.console.print("[yellow]No changes applied to the plan.[/yellow]")

    def apply_changes(
        self,
        execution_result: ExecutionResult,
        target_branch: str | None = None,
        base_ref: str | None = None,
    ) -> str:
        """Apply winning worktree contents back into the repo root.

        Uses strategy defined in config (merge or squash).
        Copy strategy is no longer supported for safety reasons.

        Returns:
            Name of the branch where changes were applied.
        """
        if not execution_result.worktree_path:
            raise RuntimeError("No worktree path available for the selected execution result.")

        worktree_path = Path(execution_result.worktree_path)
        if not worktree_path.exists():
            raise RuntimeError(f"Worktree {worktree_path} no longer exists.")

        strategy = self.config.workflow.execution.worktree.apply_strategy
        get_verbose_logger()

        if strategy == "copy":
            raise RuntimeError(
                "The 'copy' apply strategy is deprecated and unsafe. "
                "Please use 'merge' or 'squash' in your configuration."
            )

        # Try to find the Worktree object
        worktree_name = worktree_path.name
        worktree = self.worktrees.get_worktree(worktree_name)

        if worktree:
            return self._apply_via_git(worktree, strategy, branch_name=target_branch, base_ref=base_ref)
        else:
            raise RuntimeError(f"Could not find managed worktree for {worktree_path}")

    def _apply_via_git(
        self, worktree, strategy: str, branch_name: str | None = None, base_ref: str | None = None
    ) -> str:
        """Apply changes using git merge or squash into a dedicated branch."""
        # 1. Ensure worktree is clean (commit if needed)
        status = self.worktrees.get_status(worktree)
        if status.strip():
            self.worktrees.commit_changes(worktree, "Deliberate: Auto-commit of agent changes")

        # 2. Get the commit hash
        head_sha = self.worktrees.get_head_sha(worktree)

        base_ref = base_ref or self._get_current_ref()
        branch_name = branch_name or self._branch_name_from_worktree(worktree)

        checkout = self.worktrees._run_git(
            ["git", "checkout", "-B", branch_name, base_ref],
            cwd=self.repo_root,
            check=False,
        )
        if checkout.returncode != 0:
            raise RuntimeError(
                f"Failed to create or switch to branch {branch_name} from {base_ref}.\nWorktree kept at {worktree.path}"
            )

        if strategy == "squash":
            merge_cmd = ["git", "merge", "--squash", head_sha]
            result = self.worktrees._run_git(merge_cmd, cwd=self.repo_root, check=False)
            if result.returncode != 0:
                self.worktrees._run_git(["git", "merge", "--abort"], cwd=self.repo_root, check=False)
                raise RuntimeError(
                    f"Git merge failed due to conflicts.\n"
                    f"Branch left at {branch_name}\n"
                    f"Worktree kept at {worktree.path}\n"
                    f"Please verify manually."
                )

            commit_msg = f"Deliberate: Apply changes (squash) from {worktree.name}"
            commit = self.worktrees._run_git(
                ["git", "commit", "-m", commit_msg],
                cwd=self.repo_root,
                check=False,
            )
            if commit.returncode != 0:
                raise RuntimeError(
                    f"Git commit failed after squash merge.\n"
                    f"Branch left at {branch_name}\n"
                    f"Worktree kept at {worktree.path}"
                )
        else:
            cmd = ["git", "merge", "--no-edit", head_sha]
            result = self.worktrees._run_git(cmd, cwd=self.repo_root, check=False)

            if result.returncode != 0:
                # If merge failed, abort it to clean up state before raising
                self.worktrees._run_git(["git", "merge", "--abort"], cwd=self.repo_root, check=False)
                raise RuntimeError(
                    f"Git merge failed due to conflicts.\n"
                    f"Branch left at {branch_name}\n"
                    f"Worktree kept at {worktree.path}\n"
                    f"Please verify manually."
                )

        return branch_name

    async def run(
        self,
        task: str,
        preloaded_plan: Plan | dict | None = None,
        *,
        keep_worktrees: bool = False,
    ) -> JuryResult:
        """Run the complete jury workflow.

        Args:
            task: The task description.
            preloaded_plan: Optional pre-loaded plan dict (from --from-plan).
                           If provided, skips planning and uses this plan.

        Returns:
            JuryResult containing the outcome of all phases.
        """
        get_tracer()
        verbose_logger = get_verbose_logger()
        start_timestamp = datetime.now(timezone.utc)
        start_time = time.time()
        planning_cfg = self.config.workflow.planning
        execution_cfg = self.config.workflow.execution
        review_cfg = self.config.workflow.review

        # Log workflow start
        verbose_logger.register_phases(
            {
                "Planning": planning_cfg.enabled,
                "Execution": execution_cfg.enabled,
                "Review": review_cfg.enabled,
                "Refinement": self.config.workflow.refinement.enabled,
            }
        )
        verbose_logger.start_workflow(task)

        # Convert preloaded_plan dict to Plan object if needed
        plan: Plan | None = None
        if preloaded_plan is not None:
            if isinstance(preloaded_plan, Plan):
                plan = preloaded_plan
            else:
                from datetime import datetime as dt

                plan = Plan(
                    id=preloaded_plan.get("id", "plan-preloaded"),
                    agent=preloaded_plan.get("agent", "preloaded"),
                    content=preloaded_plan.get("content", ""),
                    timestamp=dt.fromisoformat(preloaded_plan["timestamp"])
                    if "timestamp" in preloaded_plan
                    else dt.now(),
                    token_usage=preloaded_plan.get("token_usage", 0),
                )

        # Start MCP orchestrator server for agent status updates
        mcp_url = await self._start_mcp_server()
        if mcp_url:
            verbose_logger.log_event(f"MCP orchestrator server started at {mcp_url}", "info")
            # Inject MCP server URL into all CLI adapters' environment
            for adapter in self.adapters.values():
                if isinstance(adapter, CLIAdapter):
                    if adapter.env is None:
                        adapter.env = {}
                    adapter.env["DELIBERATE_MCP_SERVER_URL"] = mcp_url

        try:
            return await self._run_workflow(
                task,
                start_timestamp,
                start_time,
                mcp_url,
                plan,
                keep_worktrees=keep_worktrees,
            )
        finally:
            await self._stop_mcp_server()

    async def _run_workflow(
        self,
        task: str,
        start_timestamp: datetime,
        start_time: float,
        mcp_url: str | None,
        preloaded_plan: Plan | None = None,
        keep_worktrees: bool = False,
    ) -> JuryResult:
        """Run the workflow with MCP server active.

        Args:
            task: The task description.
            start_timestamp: Timestamp when workflow started.
            start_time: Time when workflow started (for duration calculation).
            mcp_url: URL of the MCP orchestrator server for agent communication.
            preloaded_plan: Optional pre-loaded plan dict to use instead of running planning.

        Returns:
            JuryResult containing the outcome of all phases.
        """
        tracer = get_tracer()
        verbose_logger = get_verbose_logger()
        planning_cfg = self.config.workflow.planning
        execution_cfg = self.config.workflow.execution
        review_cfg = self.config.workflow.review

        with tracer.start_as_current_span("workflow.jury") as workflow_span:
            workflow_span.set_attribute("workflow.task", task[:500])
            workflow_span.set_attribute("workflow.planning_enabled", planning_cfg.enabled)
            workflow_span.set_attribute("workflow.execution_enabled", execution_cfg.enabled)
            workflow_span.set_attribute("workflow.review_enabled", review_cfg.enabled)
            workflow_span.set_attribute("gen_ai.application.name", "deliberate")
            workflow_span.set_attribute("gen_ai.operation.name", "workflow")
            workflow_span.set_attribute("gen_ai.workflow.id", str(id(self)))

            try:
                # Phase 1: Planning
                selected_plan = None
                all_plans = []
                debate_messages: list[DebateMessage] = []

                # Optional: dynamic review criteria
                await self._maybe_generate_dynamic_criteria(task)

                # Use preloaded plan if provided
                if preloaded_plan:
                    selected_plan = preloaded_plan
                    all_plans = [selected_plan]
                    verbose_logger.log_event(f"Using preloaded plan from {selected_plan.agent}", "info")
                elif planning_cfg.enabled and planning_cfg.agents:
                    with verbose_logger.phase("Planning", planning_cfg.agents):
                        with tracer.start_as_current_span("phase.planning") as span:
                            span.set_attribute("phase.agents", ",".join(planning_cfg.agents))
                            span.set_attribute("gen_ai.operation.name", "planning")
                            span.set_attribute("gen_ai.application.name", "deliberate")
                            selected_plan, all_plans, debate_messages = await self.planning.run(task)
                            if selected_plan:
                                span.set_attribute("phase.plan_agent", selected_plan.agent)
                                verbose_logger.log_event(f"Selected plan from {selected_plan.agent}", "success")
                            span.set_attribute("phase.plans_generated", len(all_plans))

                # Human gate: allow interactive confirmation before execution
                if selected_plan and self.interactive_review:
                    proceed = self._human_plan_gate(selected_plan)
                    if not proceed:
                        workflow_span.set_attribute("workflow.success", False)
                        workflow_span.set_attribute("workflow.cancelled", True)
                        workflow_span.set_attribute("workflow.error", "User cancelled before execution")
                        workflow_span.set_attribute("workflow.duration_seconds", time.time() - start_time)
                        verbose_logger.log_event("User cancelled after reviewing plan", "warning")
                        totals = self.budget.get_totals()
                        status_updates = self._collect_status_updates()
                        verbose_logger.show_final_summary(
                            success=False,
                            total_duration=time.time() - start_time,
                            total_tokens=totals["tokens"],
                            total_cost=totals["cost_usd"],
                        )
                        return JuryResult(
                            task=task,
                            selected_plan=selected_plan,
                            execution_results=[],
                            reviews=[],
                            vote_result=None,
                            final_diff=None,
                            summary="Run cancelled before execution after plan review.",
                            success=False,
                            all_plans=all_plans,
                            error="Cancelled before execution",
                            total_duration_seconds=time.time() - start_time,
                            total_token_usage=totals["tokens"],
                            total_cost_usd=totals["cost_usd"],
                            refinement_iterations=[],
                            refinement_triggered=False,
                            final_improvement=0.0,
                            started_at=start_timestamp,
                            status_updates=status_updates,
                        )

                # Phase 2: Execution
                execution_results: list[ExecutionResult] = []
                if execution_cfg.enabled and execution_cfg.agents:
                    with verbose_logger.phase("Execution", execution_cfg.agents):
                        with tracer.start_as_current_span("phase.execution") as span:
                            span.set_attribute("phase.agents", ",".join(execution_cfg.agents))
                            span.set_attribute("gen_ai.operation.name", "execution")
                            span.set_attribute("gen_ai.application.name", "deliberate")
                            execution_results = await self.execution.run(task, selected_plan)
                            span.set_attribute("phase.result_count", len(execution_results))
                            successful = sum(1 for e in execution_results if e.success)
                            span.set_attribute("phase.successful_count", successful)
                            verbose_logger.log_event(
                                f"{successful}/{len(execution_results)} agents completed successfully",
                                "success" if successful > 0 else "warning",
                            )

                # Enforce test gating if required
                if self.config.workflow.require_tests and execution_results:
                    for er in execution_results:
                        if not er.validation_result or not er.validation_result.passed:
                            er.success = False
                    execution_results = [er for er in execution_results]

                # Phase 3: Review
                reviews: list[Review] = []
                vote_result: VoteResult | None = None
                if review_cfg.enabled and review_cfg.agents and execution_results:
                    with verbose_logger.phase("Review", review_cfg.agents):
                        with tracer.start_as_current_span("phase.review") as span:
                            span.set_attribute("phase.agents", ",".join(review_cfg.agents))
                            span.set_attribute("gen_ai.operation.name", "review")
                            span.set_attribute("gen_ai.application.name", "deliberate")
                            reviews, vote_result = await self.review.run(task, execution_results)
                            span.set_attribute("phase.review_count", len(reviews))
                            if vote_result:
                                span.set_attribute("phase.winner_id", vote_result.winner_id)
                                span.set_attribute("phase.confidence", vote_result.confidence)
                                verbose_logger.log_event(
                                    f"Winner: {vote_result.winner_id} (confidence: {vote_result.confidence:.2f})",
                                    "success",
                                )

                # Phase 4: Refinement (Iterative Repair)
                refinement_iterations = []
                refinement_triggered = False
                final_improvement = 0.0

                if self.config.workflow.refinement.enabled and vote_result and reviews:
                    with verbose_logger.phase("Refinement", None):
                        with tracer.start_as_current_span("phase.refinement") as span:
                            refinement_orch = RefinementOrchestrator(
                                config=self.config.workflow.refinement,
                                agents=list(self.adapters.values()),
                                budget_tracker=self.budget,
                                worktree_mgr=self.worktrees,
                            )

                            should_refine = await refinement_orch.should_trigger(vote_result, reviews)
                            span.set_attribute("phase.triggered", should_refine)

                            if should_refine:
                                verbose_logger.log_event("Refinement triggered", "info")
                                refinement_triggered = True
                                refinement_iterations = await refinement_orch.run_refinement_loop(
                                    initial_results=execution_results,
                                    initial_reviews=reviews,
                                    initial_vote=vote_result,
                                    task_description=task,
                                )

                                span.set_attribute("phase.iteration_count", len(refinement_iterations))

                                # Use final refined results
                                if refinement_iterations:
                                    final_iteration = refinement_iterations[-1]
                                    vote_result = final_iteration.vote_result
                                    reviews = final_iteration.reviews
                                    final_improvement = sum(it.improvement_delta for it in refinement_iterations)
                                    span.set_attribute("phase.final_improvement", final_improvement)
                                    iters = len(refinement_iterations)
                                    verbose_logger.log_event(
                                        f"Completed {iters} iteration(s), +{final_improvement:.2f}",
                                        "success",
                                    )
                            else:
                                verbose_logger.log_event("Refinement not needed", "info")

                # Phase 5: Auto-Tuner (Performance Optimization via Evolution)
                evolution_attempts = 0

                if execution_results and self.config.workflow.auto_tuner.enabled:
                    with tracer.start_as_current_span("phase.auto_tuner") as span:
                        span.set_attribute("gen_ai.operation.name", "auto_tuner")
                        span.set_attribute("gen_ai.application.name", "deliberate")

                        should_evolve, triggering_vr = self._should_trigger_evolution(
                            execution_results, evolution_attempts
                        )
                        span.set_attribute("phase.triggered", should_evolve)

                        if should_evolve and triggering_vr:
                            perf_issue = triggering_vr.performance_issue.value
                            verbose_logger.log_event(
                                f"Auto-tuner triggering evolution for {perf_issue}",
                                "info",
                            )

                            # Find the execution result to optimize (winner or best passing)
                            target_result = None
                            if vote_result:
                                target_result = next(
                                    (e for e in execution_results if e.id == vote_result.winner_id),
                                    None,
                                )
                            if not target_result:
                                # Use first result with the triggering validation
                                for er in execution_results:
                                    if (
                                        er.validation_result
                                        and er.validation_result.correctness_passed
                                        and er.validation_result.needs_optimization
                                    ):
                                        target_result = er
                                        break

                            if target_result:
                                span.set_attribute("phase.target_execution_id", target_result.id)
                                improved = await self._run_evolution_for_optimization(
                                    task, target_result, triggering_vr
                                )
                                evolution_attempts += 1
                                span.set_attribute("phase.evolution_attempts", evolution_attempts)

                                if improved:
                                    verbose_logger.log_event(
                                        "Auto-tuner evolution completed successfully",
                                        "success",
                                    )
                                else:
                                    verbose_logger.log_event(
                                        "Auto-tuner evolution did not improve performance",
                                        "warning",
                                    )
                        else:
                            verbose_logger.log_event(
                                "Auto-tuner: no optimization needed",
                                "info",
                            )

                # Interactive review (human override)
                if self.interactive_review and execution_results:
                    # Print clear message that interactive mode is starting
                    self.console.print("\n[bold yellow]═══ Interactive Review Mode ═══[/bold yellow]")

                    verbose_logger.log_event("Starting interactive review", "info")

                    # Use the same console instance for TUI
                    tui = ReviewTUI(self.console)
                    try:
                        # Let human override winner selection
                        winner_id = tui.review_and_select_winner(
                            execution_results,
                            vote_result,
                            task,
                        )
                        # Update vote_result to reflect human choice
                        if vote_result:
                            vote_result.winner_id = winner_id
                            vote_result.confidence = 1.0  # Human decision is 100% confident
                        else:
                            # Create new vote_result from human choice
                            vote_result = VoteResult(
                                winner_id=winner_id,
                                rankings=[winner_id],
                                scores={winner_id: 10.0},
                                vote_breakdown={"human": {winner_id: 10.0}},
                                confidence=1.0,
                            )
                        verbose_logger.log_event(f"User selected: {winner_id}", "success")
                    except KeyboardInterrupt:
                        # User cancelled - use jury recommendation or first successful
                        verbose_logger.log_event("Interactive review cancelled", "warning")
                        self.console.print("\n[yellow]Interactive review cancelled[/yellow]")
                        # Ensure we have a vote_result
                        if not vote_result and execution_results:
                            # Use first successful result
                            successful = [e for e in execution_results if e.success]
                            if successful:
                                vote_result = VoteResult(
                                    winner_id=successful[0].id,
                                    rankings=[successful[0].id],
                                    scores={successful[0].id: 10.0},
                                    vote_breakdown={"fallback": {successful[0].id: 10.0}},
                                    confidence=0.5,
                                )

                # Determine final diff
                final_diff = None
                if vote_result and execution_results:
                    winner = next(
                        (e for e in execution_results if e.id == vote_result.winner_id),
                        None,
                    )
                    if winner:
                        final_diff = winner.diff
                elif execution_results:
                    # No review, use first successful result
                    successful = [e for e in execution_results if e.success]
                    if successful:
                        final_diff = successful[0].diff

                # Build summary
                summary = self._build_summary(
                    task,
                    selected_plan,
                    execution_results,
                    vote_result,
                )

                # Calculate totals
                totals = self.budget.get_totals()

                # Collect status updates from MCP server
                status_updates = self._collect_status_updates()

                execution_success = (
                    not execution_cfg.enabled or not execution_cfg.agents or any(e.success for e in execution_results)
                )
                review_success = not review_cfg.enabled or not review_cfg.agents or vote_result is not None

                result = JuryResult(
                    task=task,
                    selected_plan=selected_plan,
                    all_plans=all_plans,
                    execution_results=execution_results,
                    reviews=reviews,
                    vote_result=vote_result,
                    final_diff=final_diff,
                    summary=summary,
                    success=execution_success and review_success,
                    total_duration_seconds=time.time() - start_time,
                    total_token_usage=totals["tokens"],
                    total_cost_usd=totals["cost_usd"],
                    refinement_iterations=refinement_iterations,
                    refinement_triggered=refinement_triggered,
                    final_improvement=final_improvement,
                    started_at=start_timestamp,
                    status_updates=status_updates,
                    debate_messages=debate_messages,
                )

                # Record final metrics
                workflow_span.set_attribute("workflow.success", True)
                workflow_span.set_attribute("workflow.total_tokens", totals["tokens"])
                workflow_span.set_attribute("workflow.total_cost_usd", totals["cost_usd"])
                workflow_span.set_attribute("workflow.duration_seconds", result.total_duration_seconds)

                # Show verbose final summary
                verbose_logger.show_final_summary(
                    success=True,
                    total_duration=result.total_duration_seconds,
                    total_tokens=result.total_token_usage,
                    total_cost=result.total_cost_usd,
                )

                # Record performance tracking
                self._record_tracking(result)

                return result

            except Exception as e:
                totals = self.budget.get_totals()
                workflow_span.set_attribute("workflow.success", False)
                workflow_span.set_attribute("workflow.error", str(e))
                workflow_span.record_exception(e)

                # Collect status updates even on error
                status_updates = self._collect_status_updates()

                return JuryResult(
                    task=task,
                    selected_plan=None,
                    all_plans=[],
                    execution_results=[],
                    reviews=[],
                    vote_result=None,
                    final_diff=None,
                    summary=f"Jury failed: {str(e)}",
                    success=False,
                    error=str(e),
                    total_duration_seconds=time.time() - start_time,
                    total_token_usage=totals["tokens"],
                    total_cost_usd=totals["cost_usd"],
                    started_at=start_timestamp,
                    status_updates=status_updates,
                )

            finally:
                verbose_logger.stop_live()
                # Cleanup worktrees if configured and not deferred
                if self.config.workflow.execution.worktree.cleanup and not keep_worktrees:
                    self.worktrees.cleanup_all()

    def _record_tracking(self, result: JuryResult) -> None:
        """Record result to performance tracker if enabled."""
        if not self.config.tracking.enabled:
            return

        try:
            record_jury_result(result, self.tracker)
        except Exception as e:
            # Don't let tracking failures break the workflow
            print(f"Tracking error: {e}")
            pass

    def _build_summary(
        self,
        task: str,
        plan,
        execution_results,
        vote_result,
    ) -> str:
        """Build a summary of the jury run."""
        lines = []

        lines.append(f"## Task\n{task[:200]}...")

        if plan:
            lines.append(f"\n## Selected Plan (by {plan.agent})\n{plan.content[:500]}...")

        if execution_results:
            successful = [e for e in execution_results if e.success]
            lines.append(f"\n## Execution\n- Total agents: {len(execution_results)}")
            lines.append(f"- Successful: {len(successful)}")

        if vote_result:
            lines.append("\n## Review Results")
            lines.append(f"- Winner: {vote_result.winner_id}")
            lines.append(f"- Confidence: {vote_result.confidence:.2f}")
            lines.append("- Rankings: " + " > ".join(vote_result.rankings[:3]))

        return "\n".join(lines)
