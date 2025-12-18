"""Planning phase for deliberate."""

import asyncio
import re
import warnings
from dataclasses import dataclass, field
from typing import Any

from deliberate.adapters.base import ModelAdapter
from deliberate.budget.tracker import BudgetTracker
from deliberate.iteration.evaluators import PlanReviewEvaluator
from deliberate.iteration.extractors import PlanExtractor
from deliberate.iteration.feedback import PlanFeedbackBuilder
from deliberate.iteration.solver import IterativeSolver
from deliberate.iteration.types import IterationConfig, IterationResult
from deliberate.prompts.planning import DEBATE_PROMPT, JUDGE_PROMPT, PLANNING_PROMPT
from deliberate.types import DebateMessage, Plan
from deliberate.utils.structured_output import extract_tool_call
from deliberate.verbose_logger import get_verbose_logger


@dataclass
class IterativePlanningConfig:
    """Configuration for iterative planning mode."""

    enabled: bool = False
    max_iterations: int = 5
    success_threshold: float = 0.9
    critic_agent: str | None = None  # Agent to use as critic
    require_structure: bool = True
    weights: dict[str, float] | None = None  # Critic criteria weights


@dataclass
class PlanningPhase:
    """Orchestrates the planning phase of the jury workflow.

    Multiple agents propose plans, optionally debate them,
    and a judge (or voting) selects the best plan.

    Supports two modes:
    1. Classic mode: Multiple agents propose, optionally debate, judge selects
    2. Iterative mode: Single agent iterates with critic feedback until threshold met
    """

    agents: list[str]
    adapters: dict[str, ModelAdapter]
    budget: BudgetTracker
    debate_enabled: bool = False
    debate_rounds: int = 1
    selection_method: str = "first"  # first | llm_judge | borda
    judge_agent: str | None = None
    iterative_config: IterativePlanningConfig = field(default_factory=IterativePlanningConfig)

    async def run(self, task: str) -> tuple[Plan | None, list[Plan], list[DebateMessage]]:
        """Run the planning phase.

        Args:
            task: The task description.

        Returns:
            Tuple of (selected plan, all plans, debate messages).
            Selected plan is None if no plans were generated.
        """
        verbose_logger = get_verbose_logger()

        # Use iterative mode if enabled
        if self.iterative_config.enabled:
            verbose_logger.log_event("[Planning] Using iterative planning mode", "info")
            result = await self._run_iterative_planning(task, verbose_logger=verbose_logger)
            if result and result.best_attempt:
                # Convert the best attempt to a Plan
                plan = Plan(
                    id="iterative-plan",
                    agent=self.agents[0] if self.agents else "iterative_planner",
                    content=result.best_attempt.code or "",
                    token_usage=result.total_tokens,
                )
                return plan, [plan], []
            return None, [], []

        # Classic mode: collect plans from multiple agents
        plans = await self._collect_plans(task, verbose_logger=verbose_logger)

        if not plans:
            return None, [], []

        debate_messages: list[DebateMessage] = []
        if self.debate_enabled and len(plans) > 1:
            debate_messages = await self._run_debate(task, plans, verbose_logger=verbose_logger)

        selected = await self._select_plan(task, plans)
        if selected:
            verbose_logger.log_event(f"Selected plan from {selected.agent}", "info")
        return selected, plans, debate_messages

    async def _run_iterative_planning(
        self,
        task: str,
        verbose_logger=None,
    ) -> IterationResult | None:
        """Run iterative planning with critic feedback.

        Uses IterativeSolver[Plan] with PlanReviewEvaluator to iteratively
        improve a plan until it meets the success threshold.

        Args:
            task: The task description.
            verbose_logger: Optional logger.

        Returns:
            IterationResult with all attempts, or None if no agent available.
        """
        verbose_logger = verbose_logger or get_verbose_logger()

        if not self.agents:
            verbose_logger.log_event("[Planning] No agents available", "error")
            return None

        # Get the primary planning agent
        planner_agent = self.agents[0]
        planner_adapter = self.adapters.get(planner_agent)
        if not planner_adapter:
            verbose_logger.log_event(f"[Planning] Adapter not found for {planner_agent}", "error")
            return None

        # Get critic agent if configured
        critic_adapter = None
        if self.iterative_config.critic_agent:
            critic_adapter = self.adapters.get(self.iterative_config.critic_agent)
            if not critic_adapter:
                verbose_logger.log_event(
                    f"[Planning] Critic adapter not found: {self.iterative_config.critic_agent}",
                    "warning",
                )

        # Build the solver components
        evaluator = PlanReviewEvaluator(
            critic_agent=critic_adapter,
            success_threshold=self.iterative_config.success_threshold,
            require_structure=self.iterative_config.require_structure,
            weights=self.iterative_config.weights,
        )
        extractor = PlanExtractor(agent_name=planner_agent)
        feedback_builder = PlanFeedbackBuilder(success_threshold=self.iterative_config.success_threshold)

        config = IterationConfig(
            max_iterations=self.iterative_config.max_iterations,
            max_solutions_in_context=3,
            include_all_feedback=True,
        )

        solver: IterativeSolver[Plan] = IterativeSolver(
            agent=planner_adapter,
            evaluator=evaluator,
            extractor=extractor,
            feedback_builder=feedback_builder,
            config=config,
            budget_tracker=self.budget,
            on_iteration_start=lambda i: verbose_logger.log_event(f"[Planning] Iteration {i} starting", "info"),
            on_iteration_end=lambda i, a: verbose_logger.log_event(
                f"[Planning] Iteration {i} score: {a.soft_score:.2f}", "info"
            ),
        )

        # Evaluation context includes the task for the critic
        evaluation_context = {"task": task}

        try:
            result = await solver.solve(
                task=self._build_iterative_planning_prompt(task),
                evaluation_context=evaluation_context,
            )
            verbose_logger.log_event(
                f"[Planning] Iterative planning complete: "
                f"{result.iterations_completed} iterations, "
                f"score: {result.final_score:.2f}",
                "info",
            )
            return result
        except Exception as e:
            verbose_logger.log_event(f"[Planning] Iterative planning failed: {e}", "error")
            return None

    def _build_iterative_planning_prompt(self, task: str) -> str:
        """Build the prompt for iterative planning.

        Wraps the task with planning-specific instructions.
        """
        return f"""Create an implementation plan for the following task.

## Task
{task}

## Plan Requirements
Your plan must include:
1. **Numbered steps**: Clear implementation steps (minimum 2, ideally 3-5)
2. **Risk section**: Identify potential risks, concerns, or caveats
3. **Affected files**: List files that will be created or modified

## Format
Wrap your plan in <plan> tags:

<plan>
## Implementation Steps
1. First step
2. Second step
...

## Risks and Concerns
- Risk 1
- Risk 2

## Affected Files
- path/to/file1.py
- path/to/file2.py
</plan>
"""

    async def _collect_plans(self, task: str, verbose_logger=None) -> list[Plan]:
        """Collect plans from all planning agents."""
        verbose_logger = verbose_logger or get_verbose_logger()

        async def get_plan(agent_name: str) -> Plan | None:
            adapter = self.adapters.get(agent_name)
            if not adapter:
                return None

            try:
                verbose_logger.log_event(f"[Planning] {agent_name} starting", "info")
                prompt = PLANNING_PROMPT.format(task=task)
                response = await adapter.call(prompt)

                self.budget.record_usage(
                    agent_name,
                    response.token_usage,
                    adapter.estimate_cost(response.token_usage),
                )

                content = response.content
                if "| permission_denials=" in content:
                    content = content.split("| permission_denials=", 1)[0].rstrip()

                return Plan(
                    id=f"plan-{agent_name}",
                    agent=agent_name,
                    content=content,
                    token_usage=response.token_usage,
                )
            except Exception as e:
                verbose_logger.log_event(f"[Planning] {agent_name} failed: {e}", "error")
                return None

        results = await asyncio.gather(*[get_plan(a) for a in self.agents])
        return [p for p in results if p is not None]

    async def _run_debate(
        self,
        task: str,
        plans: list[Plan],
        verbose_logger=None,
    ) -> list[DebateMessage]:
        """Run debate rounds where agents critique each other's plans.

        .. deprecated::
            Use iterative planning mode instead. Set `iterative_config.enabled=True`
            for critic-based plan improvement.
        """
        warnings.warn(
            "Debate mode is deprecated. Use iterative planning mode instead (set iterative_config.enabled=True).",
            DeprecationWarning,
            stacklevel=2,
        )
        verbose_logger = verbose_logger or get_verbose_logger()
        messages: list[DebateMessage] = []

        for round_num in range(self.debate_rounds):
            for i, agent_name in enumerate(self.agents):
                adapter = self.adapters.get(agent_name)
                if not adapter:
                    continue

                # Each agent reviews the next agent's plan (circular)
                other_plan = plans[(i + 1) % len(plans)]
                prompt = DEBATE_PROMPT.format(
                    task=task,
                    plan=other_plan.content,
                )

                try:
                    response = await adapter.call(prompt)
                    self.budget.record_usage(agent_name, response.token_usage)

                    messages.append(
                        DebateMessage(
                            agent=agent_name,
                            content=response.content,
                            round=round_num,
                            reply_to=other_plan.agent,
                        )
                    )
                    verbose_logger.log_event(
                        f"[Planning][Debate] {agent_name} critiqued {other_plan.agent}",
                        "info",
                    )
                except Exception as e:
                    verbose_logger.log_event(f"[Planning][Debate] {agent_name} failed: {e}", "error")

        return messages

    async def _select_plan(self, task: str, plans: list[Plan]) -> Plan:
        """Select the best plan using the configured method."""
        if len(plans) == 1 or self.selection_method == "first":
            return plans[0]

        if self.selection_method == "llm_judge" and self.judge_agent:
            return await self._judge_select(task, plans)

        # Default to first plan
        return plans[0]

    async def _judge_select(self, task: str, plans: list[Plan]) -> Plan:
        """Use an LLM judge to select the best plan."""
        if not self.judge_agent:
            return plans[0]

        adapter = self.adapters.get(self.judge_agent)
        if not adapter:
            return plans[0]

        # Format plans for comparison
        plans_text = "\n\n---\n\n".join(f"## Plan {i + 1} (by {p.agent})\n\n{p.content}" for i, p in enumerate(plans))

        prompt = JUDGE_PROMPT.format(
            task=task,
            plans=plans_text,
            num_plans=len(plans),
        )

        try:
            response = await adapter.call(prompt)
            if self.judge_agent:
                self.budget.record_usage(self.judge_agent, response.token_usage)

            selection = extract_tool_call(response.raw_response, response.content, "select_plan")
            if selection:
                plan_id = selection.get("plan_id") or selection.get("id") or selection.get("plan")
                idx = self._coerce_plan_index(plan_id, plans)
                if idx is not None:
                    return plans[idx]

            # Parse "Plan N" from response
            match = re.search(r"[Pp]lan\s*(\d+)", response.content)
            if match:
                idx = int(match.group(1)) - 1
                if 0 <= idx < len(plans):
                    return plans[idx]

        except Exception as e:
            print(f"Warning: Judge selection failed: {e}")

        return plans[0]

    def _coerce_plan_index(self, plan_id: Any, plans: list[Plan]) -> int | None:
        """Convert a plan_id to a zero-based index if valid."""
        try:
            idx = int(plan_id) - 1
        except (TypeError, ValueError):
            return None

        if 0 <= idx < len(plans):
            return idx
        return None
