"""Evolution Controller implementing AlphaEvolve's distributed loop.

Orchestrates the evolutionary code generation process:
1. Sample parent and inspiration programs from database
2. Build prompts for LLM ensemble
3. Generate diffs/code via LLMs
4. Apply diffs to create child programs
5. Evaluate through cascade
6. Add successful programs to database
"""

import asyncio
import re
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from deliberate.adapters.base import AdapterResponse, ModelAdapter
from deliberate.budget.tracker import BudgetTracker

from .database import ProgramDatabase
from .diff_evolution import (
    DiffParser,
    apply_diff,
    count_changes,
    extract_evolve_regions,
    parse_diff,
)
from .prompt_builder import PromptBuilder
from .types import (
    EvaluationLevel,
    EvolutionConfig,
    EvolutionResult,
    Program,
    ProgramMetrics,
)


@dataclass
class EvaluationResult:
    """Result of evaluating a program."""

    passed: bool
    level: EvaluationLevel
    metrics: ProgramMetrics
    feedback: str
    test_output: str | None = None
    lint_output: str | None = None
    duration_ms: float = 0.0


class Evaluator:
    """Base evaluator interface for programs.

    Subclass this for specific evaluation domains:
    - TestEvaluator for running test suites
    - BenchmarkEvaluator for performance evaluation
    - LintEvaluator for code quality
    """

    async def evaluate(
        self,
        program: Program,
        level: EvaluationLevel,
        context: Any = None,
    ) -> EvaluationResult:
        """Evaluate a program at the given cascade level.

        Args:
            program: The program to evaluate.
            level: The evaluation level to run.
            context: Domain-specific evaluation context.

        Returns:
            EvaluationResult with metrics and feedback.
        """
        raise NotImplementedError


class EvolutionController:
    """Main controller for evolutionary code generation.

    Implements AlphaEvolve's distributed controller loop:
    ```
    while not done:
        parent, inspirations = database.sample()
        prompt = prompt_builder.build(parent, inspirations)
        diff = llm.generate(prompt)
        child = apply_diff(parent, diff)
        results = evaluator.evaluate(child)
        database.add(child, results)
    ```
    """

    def __init__(
        self,
        database: ProgramDatabase,
        agents: dict[str, ModelAdapter],
        evaluator: Evaluator | None = None,
        config: EvolutionConfig | None = None,
        budget_tracker: BudgetTracker | None = None,
    ):
        """Initialize the evolution controller.

        Args:
            database: Program database for storage and sampling.
            agents: Dictionary of model name -> adapter.
                    Should include both "fast" and "powerful" models.
            evaluator: Evaluator for programs.
            config: Evolution configuration.
            budget_tracker: Optional budget tracker.
        """
        self.database = database
        self.agents = agents
        self.evaluator = evaluator
        self.config = config or EvolutionConfig()
        self.budget = budget_tracker

        self.prompt_builder = PromptBuilder(
            prefer_diffs=self.config.prefer_diffs,
            include_inspirations=self.config.include_inspirations,
        )
        self.diff_parser = DiffParser()

        # Statistics
        self._iterations = 0
        self._programs_generated = 0
        self._programs_valid = 0
        self._stagnant_iterations = 0
        self._best_score = 0.0
        self._score_trajectory: list[float] = []
        self._start_time: float = 0.0

        # Callbacks
        self.on_iteration: Callable[[int, Program | None], None] | None = None
        self.on_improvement: Callable[[Program], None] | None = None

    async def evolve(
        self,
        task: str,
        seed_program: str | None = None,
        evaluation_context: Any = None,
        working_dir: Path | None = None,
    ) -> EvolutionResult:
        """Run the evolution loop.

        Args:
            task: The problem/task description.
            seed_program: Optional initial program to evolve from.
            evaluation_context: Context for evaluation (e.g., test files).
            working_dir: Working directory for evaluation.

        Returns:
            EvolutionResult with best program and statistics.
        """
        self._start_time = time.time()
        self._iterations = 0
        self._programs_generated = 0
        self._programs_valid = 0
        self._stagnant_iterations = 0
        self._best_score = 0.0
        self._score_trajectory = []

        termination_reason = "max_iterations"

        # Generate initial seed if needed
        if seed_program:
            seed = await self._create_seed_program(seed_program, task, evaluation_context)
            if seed:
                self.database.add(seed)
        elif self.database.size == 0:
            # Generate seeds using LLMs
            await self._generate_initial_seeds(task, evaluation_context)

        # Main evolution loop
        for iteration in range(1, self.config.max_iterations + 1):
            self._iterations = iteration

            # Check termination conditions
            if self._should_terminate():
                termination_reason = self._get_termination_reason()
                break

            # Sample parents and inspirations
            parents, inspirations = self.database.sample(
                n_parents=1,
                n_inspirations=self.config.include_inspirations,
                prefer_champions=True,
            )

            if not parents:
                # No programs in database, generate more seeds
                await self._generate_initial_seeds(task, evaluation_context)
                continue

            parent = parents[0]

            # Select agent (fast vs powerful)
            agent = self._select_agent(parent)

            # Build prompt
            feedback = self.prompt_builder.build_feedback_from_metrics(parent.metrics)
            evolve_regions = None
            if self.config.use_evolve_markers:
                regions = extract_evolve_regions(parent.code)
                if regions:
                    evolve_regions = [(r.start_line, r.end_line, r.content) for r in regions]

            prompt = self.prompt_builder.build_evolution_prompt(
                task=task,
                parent=parent,
                inspirations=inspirations,
                feedback=feedback,
                iteration=iteration,
                evolve_regions=evolve_regions,
            )

            # Generate response
            try:
                response = await self._call_agent(agent, prompt)
            except Exception:
                # Log and continue
                continue

            # Parse and apply diff
            child = await self._create_child_program(parent, response.content)
            if not child:
                continue

            self._programs_generated += 1

            # Evaluate through cascade
            eval_result = await self._evaluate_program(child, evaluation_context)

            # Update metrics
            child.metrics = eval_result.metrics
            child.is_valid = eval_result.passed

            if child.is_valid:
                self._programs_valid += 1

                # Add to database
                if self.database.add(child):
                    # Check for improvement
                    if child.metrics.overall_score > self._best_score:
                        child.metrics.overall_score - self._best_score
                        self._best_score = child.metrics.overall_score
                        self._stagnant_iterations = 0
                        if self.on_improvement:
                            self.on_improvement(child)
                    else:
                        self._stagnant_iterations += 1

            # Track trajectory
            self._score_trajectory.append(self._best_score)

            # Callback
            if self.on_iteration:
                self.on_iteration(iteration, child if child.is_valid else None)

            # Periodic migration
            if iteration % 10 == 0:
                self.database.migrate()

            # Check for target score
            if self._best_score >= self.config.target_score:
                termination_reason = "target_reached"
                break

        # Build result
        return EvolutionResult(
            success=self._best_score >= self.config.target_score,
            best_program=self.database.get_best(),
            all_programs=self.database.get_champions(20),
            iterations_completed=self._iterations,
            programs_generated=self._programs_generated,
            programs_valid=self._programs_valid,
            score_trajectory=self._score_trajectory,
            generation_timeline=[self.database.generation],
            total_tokens=getattr(self.budget, "total_tokens", 0) if self.budget else 0,
            total_cost_usd=getattr(self.budget, "total_cost", 0.0) if self.budget else 0.0,
            total_time_seconds=time.time() - self._start_time,
            termination_reason=termination_reason,
            stagnant_iterations=self._stagnant_iterations,
        )

    async def _generate_initial_seeds(
        self,
        task: str,
        evaluation_context: Any,
        n_seeds: int = 4,
    ) -> None:
        """Generate initial seed programs using LLMs."""
        prompt = self.prompt_builder.build_seed_prompt(task)

        # Generate seeds in parallel using different agents
        tasks = []
        for i, (name, agent) in enumerate(list(self.agents.items())[:n_seeds]):
            tasks.append(self._call_agent(agent, prompt))

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        for i, response in enumerate(responses):
            if isinstance(response, BaseException):
                continue

            code = self._extract_code(response.content)
            if not code:
                continue

            program = Program(
                id=f"seed_{i}_{uuid.uuid4().hex[:8]}",
                code=code,
                agent=list(self.agents.keys())[i % len(self.agents)],
                metrics=ProgramMetrics(generation=0),
            )

            # Evaluate
            eval_result = await self._evaluate_program(program, evaluation_context)
            program.metrics = eval_result.metrics
            program.is_valid = eval_result.passed

            if program.is_valid:
                self.database.add(program)
                self._programs_valid += 1
            self._programs_generated += 1

    async def _create_seed_program(
        self,
        code: str,
        task: str,
        evaluation_context: Any,
    ) -> Program | None:
        """Create a seed program from provided code."""
        program = Program(
            id=f"seed_{uuid.uuid4().hex[:8]}",
            code=code,
            agent="seed",
            metrics=ProgramMetrics(generation=0),
        )

        eval_result = await self._evaluate_program(program, evaluation_context)
        program.metrics = eval_result.metrics
        program.is_valid = eval_result.passed

        self._programs_generated += 1
        if program.is_valid:
            self._programs_valid += 1

        return program if program.is_valid else None

    async def _create_child_program(
        self,
        parent: Program,
        response: str,
    ) -> Program | None:
        """Create a child program from LLM response."""
        # Try to parse as diff first
        diff_blocks = parse_diff(response)

        if diff_blocks:
            # Apply diffs to parent
            try:
                new_code = apply_diff(parent.code, diff_blocks, fuzzy=True)
            except Exception:
                new_code = parent.code
        else:
            # Extract full code from response
            new_code = self._extract_code(response)
            if not new_code:
                return None

        # Check if code actually changed
        if new_code.strip() == parent.code.strip():
            return None

        # Create child program
        child_id = f"prog_{self.database.generation + 1}_{uuid.uuid4().hex[:8]}"
        child = parent.clone(child_id)
        child.code = new_code
        child.diff_applied = response if diff_blocks else None

        # Update code metrics
        changes = count_changes(parent.code, new_code)
        child.metrics.lines_changed = changes["lines_added"] + changes["lines_changed"]
        child.metrics.lines_of_code = len(new_code.split("\n"))

        return child

    async def _evaluate_program(
        self,
        program: Program,
        context: Any,
    ) -> EvaluationResult:
        """Evaluate a program through the cascade."""
        if not self.evaluator:
            # No evaluator - assume valid with default metrics
            return EvaluationResult(
                passed=True,
                level=EvaluationLevel.SYNTAX,
                metrics=program.metrics,
                feedback="No evaluator configured",
            )

        # Evaluate through cascade levels
        current_level = EvaluationLevel.SYNTAX
        final_result = None

        for level in self.config.cascade_levels:
            try:
                result = await self.evaluator.evaluate(program, level, context)
            except Exception as e:
                # Evaluation failed - stop cascade
                return EvaluationResult(
                    passed=False,
                    level=current_level,
                    metrics=program.metrics,
                    feedback=f"Evaluation error at {level.name}: {e}",
                )

            final_result = result

            if not result.passed:
                # Failed this level - stop cascade
                break

            current_level = level

        return final_result or EvaluationResult(
            passed=False,
            level=EvaluationLevel.SYNTAX,
            metrics=program.metrics,
            feedback="No evaluation result",
        )

    def _select_agent(self, parent: Program) -> ModelAdapter:
        """Select which agent (fast vs powerful) to use.

        AlphaEvolve uses:
        - Fast model (Flash) for most iterations (throughput)
        - Powerful model (Pro) for evolving champions
        """
        agent_names = list(self.agents.keys())
        if len(agent_names) == 1:
            return self.agents[agent_names[0]]

        # Check if this is a champion
        is_champion = parent.is_champion or (
            self.config.use_powerful_for_champions and parent.metrics.overall_score >= self._best_score * 0.95
        )

        if is_champion:
            # Use powerful model (prefer "pro", "opus", "sonnet" in name)
            for name in agent_names:
                if any(p in name.lower() for p in ["pro", "opus", "sonnet", "4"]):
                    return self.agents[name]

        # Otherwise use fast model based on ratio
        import random

        if random.random() < self.config.fast_model_ratio:
            # Use fast model (prefer "flash", "haiku", "mini" in name)
            for name in agent_names:
                if any(p in name.lower() for p in ["flash", "haiku", "mini", "3.5"]):
                    return self.agents[name]

        # Fall back to first agent
        return self.agents[agent_names[0]]

    async def _call_agent(
        self,
        agent: ModelAdapter,
        prompt: str,
    ) -> AdapterResponse:
        """Call an agent and track budget."""
        response = await agent.call(prompt=prompt)

        if self.budget:
            self.budget.record_usage(
                agent.name,
                response.token_usage,
                agent.estimate_cost(response.token_usage),
                phase="evolution",
            )

        return response

    def _extract_code(self, text: str) -> str | None:
        """Extract code from a response (markdown code blocks)."""
        # Try language-specific blocks first
        for lang in ["python", "py"]:
            pattern = rf"```{lang}\s*(.*?)```"
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()

        # Try generic code block
        pattern = r"```\s*(.*?)```"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()

        # No code block found
        return None

    def _should_terminate(self) -> bool:
        """Check if evolution should terminate."""
        # Budget limits
        if self.budget:
            total_tokens = getattr(self.budget, "total_tokens", 0)
            total_cost = getattr(self.budget, "total_cost", 0.0)
            if self.config.max_tokens and total_tokens >= self.config.max_tokens:
                return True
            if self.config.max_cost_usd and total_cost >= self.config.max_cost_usd:
                return True

        # Time limit
        if self.config.max_time_seconds:
            elapsed = time.time() - self._start_time
            if elapsed >= self.config.max_time_seconds:
                return True

        # Stagnation
        if self._stagnant_iterations >= self.config.max_stagnant_iterations:
            return True

        return False

    def _get_termination_reason(self) -> str:
        """Get the reason for termination."""
        if self.budget:
            total_tokens = getattr(self.budget, "total_tokens", 0)
            total_cost = getattr(self.budget, "total_cost", 0.0)
            if self.config.max_tokens and total_tokens >= self.config.max_tokens:
                return "token_limit"
            if self.config.max_cost_usd and total_cost >= self.config.max_cost_usd:
                return "cost_limit"

        if self.config.max_time_seconds:
            elapsed = time.time() - self._start_time
            if elapsed >= self.config.max_time_seconds:
                return "time_limit"

        if self._stagnant_iterations >= self.config.max_stagnant_iterations:
            return "stagnation"

        return "unknown"
