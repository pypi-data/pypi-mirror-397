"""Iterative solver implementing the meta-pattern.

Core concept from poetiq-arc-agi-solver:
"The prompt is an interface, not the intelligence" - The system engages
in an iterative problem-solving loop where it:
1. Generates a potential solution
2. Receives feedback from evaluation
3. Analyzes the feedback
4. Refines the solution based on accumulated history

Self-Auditing: The system autonomously decides when it has enough
information and the solution is satisfactory, allowing early termination.
"""

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Generic, TypeVar

from deliberate.adapters.base import AdapterResponse, ModelAdapter
from deliberate.budget.tracker import BudgetTracker

from .feedback import (
    FeedbackBuilder,
    build_iteration_prompt,
)
from .history import SolutionHistory
from .types import (
    FeedbackContext,
    IterationConfig,
    IterationResult,
    SolutionAttempt,
    TerminationReason,
)

# Type variable for the solution type
S = TypeVar("S")


class SolutionEvaluator(ABC, Generic[S]):
    """Abstract evaluator that determines solution quality.

    Subclass for specific domains:
    - TestEvaluator: runs tests and checks pass/fail
    - ARCEvaluator: compares grid outputs to expected
    - ReviewEvaluator: uses LLM to score quality
    """

    @abstractmethod
    async def evaluate(self, solution: S, context: Any) -> tuple[FeedbackContext, Any]:
        """Evaluate a solution.

        Args:
            solution: The solution to evaluate.
            context: Domain-specific context (e.g., test inputs, expected outputs).

        Returns:
            Tuple of (FeedbackContext for feedback builder, raw evaluation result).
        """
        pass

    @abstractmethod
    def is_success(self, feedback_context: FeedbackContext) -> bool:
        """Determine if the solution passes all success criteria."""
        pass


class SolutionExtractor(ABC, Generic[S]):
    """Extracts solution artifacts from LLM responses.

    Subclass for specific output formats:
    - CodeExtractor: extracts code from markdown blocks
    - JSONExtractor: parses JSON responses
    - PlainExtractor: uses raw response
    """

    @abstractmethod
    def extract(self, response: str) -> S | None:
        """Extract solution from LLM response.

        Args:
            response: Raw LLM response text.

        Returns:
            Extracted solution or None if extraction failed.
        """
        pass


@dataclass
class IterativeSolver(Generic[S]):
    """Main iterative solver implementing the meta-pattern.

    Orchestrates the iterative problem-solving loop:
    1. Generate solution via LLM
    2. Extract solution artifact
    3. Evaluate against criteria
    4. Build feedback
    5. Check for success (self-audit)
    6. Accumulate to history
    7. Repeat with context

    Type parameter S is the solution type (e.g., str for code).
    """

    agent: ModelAdapter
    evaluator: SolutionEvaluator[S]
    extractor: SolutionExtractor[S]
    feedback_builder: FeedbackBuilder
    config: IterationConfig
    budget_tracker: BudgetTracker | None = None

    # Callbacks
    on_iteration_start: Callable[[int], None] | None = None
    on_iteration_end: Callable[[int, SolutionAttempt], None] | None = None
    on_success: Callable[[SolutionAttempt], None] | None = None

    async def solve(
        self,
        task: str,
        evaluation_context: Any,
        working_dir: str | Path | None = None,
        system_prompt: str | None = None,
    ) -> IterationResult:
        """Run the iterative solving loop.

        Args:
            task: The problem to solve (base prompt).
            evaluation_context: Context for evaluating solutions
                (e.g., test cases, expected outputs).
            working_dir: Optional working directory for file operations.
            system_prompt: Optional system prompt for the LLM.

        Returns:
            IterationResult with all attempts and final outcome.
        """
        start_time = time.time()
        history = SolutionHistory()
        total_tokens = 0
        termination_reason = TerminationReason.MAX_ITERATIONS

        for iteration in range(1, self.config.max_iterations + 1):
            iter_start = time.time()

            # Callback: iteration starting
            if self.on_iteration_start:
                self.on_iteration_start(iteration)

            # Check budget limits
            if self._should_stop_for_budget(total_tokens, start_time):
                termination_reason = TerminationReason.BUDGET_EXHAUSTED
                break

            # Build prompt with history context
            selected = history.select_for_context(
                max_solutions=self.config.max_solutions_in_context,
                selection_probability=self.config.selection_probability,
                improving_order=self.config.improving_order,
                seed=self.config.seed + iteration,
            )
            history_context = history.format_for_prompt(
                selected, include_full_feedback=self.config.include_all_feedback
            )
            prompt = build_iteration_prompt(task, history_context)

            # Generate solution via LLM
            try:
                response = await self._call_agent(
                    prompt,
                    working_dir=working_dir,
                    system_prompt=system_prompt,
                )
                total_tokens += response.token_usage
            except Exception as e:
                # Record failed attempt
                attempt = SolutionAttempt(
                    iteration=iteration,
                    code=None,
                    output="",
                    success=False,
                    soft_score=0.0,
                    feedback=f"LLM call failed: {e}",
                    error=str(e),
                    token_usage=0,
                    duration_seconds=time.time() - iter_start,
                )
                history.add(attempt)
                continue

            # Extract solution artifact
            solution = self.extractor.extract(response.content)
            if solution is None:
                # Extraction failed - record and continue
                attempt = SolutionAttempt(
                    iteration=iteration,
                    code=response.content[:500],  # Store partial for debugging
                    output="",
                    success=False,
                    soft_score=0.0,
                    feedback="Failed to extract solution from response",
                    error="Extraction failed",
                    token_usage=response.token_usage,
                    duration_seconds=time.time() - iter_start,
                )
                history.add(attempt)
                continue

            # Evaluate the solution
            feedback_ctx, raw_eval = await self.evaluator.evaluate(solution, evaluation_context)

            # Build structured feedback
            structured_fb = self.feedback_builder.build(raw_eval, feedback_ctx)

            # Create attempt record
            attempt = SolutionAttempt(
                iteration=iteration,
                code=str(solution) if solution else None,
                output=str(raw_eval),
                success=structured_fb.success,
                soft_score=structured_fb.score,
                feedback=structured_fb.text,
                error=None if structured_fb.success else "; ".join(structured_fb.issues[:3]),
                token_usage=response.token_usage,
                duration_seconds=time.time() - iter_start,
            )
            history.add(attempt)

            # Callback: iteration complete
            if self.on_iteration_end:
                self.on_iteration_end(iteration, attempt)

            # Self-audit: Check for success
            if self.evaluator.is_success(feedback_ctx):
                termination_reason = TerminationReason.SUCCESS
                if self.on_success:
                    self.on_success(attempt)
                break

            # Check for stagnation (no improvement)
            if iteration >= 3 and not history.is_improving(window=3, threshold=self.config.min_improvement_threshold):
                # Could add early termination for stagnation
                pass

        # Build final result
        best_attempt = history.get_best()
        success = termination_reason == TerminationReason.SUCCESS
        final_score = best_attempt.soft_score if best_attempt else 0.0

        return IterationResult(
            success=success,
            termination_reason=termination_reason,
            iterations_completed=len(history),
            best_attempt=best_attempt,
            all_attempts=list(history),
            final_score=final_score,
            total_tokens=total_tokens,
            total_duration=time.time() - start_time,
            improvement_trajectory=history.get_score_trajectory(),
        )

    async def _call_agent(
        self,
        prompt: str,
        working_dir: str | Path | None = None,
        system_prompt: str | None = None,
    ) -> AdapterResponse:
        """Call the agent with the given prompt."""
        # Try call() first (for simple completion)
        # If agent supports run_agentic, could use that for tool-enabled execution
        return await self.agent.call(
            prompt=prompt,
            system=system_prompt,
            working_dir=str(working_dir) if working_dir else None,
        )

    def _should_stop_for_budget(self, tokens_used: int, start_time: float) -> bool:
        """Check if we should stop due to budget constraints."""
        if self.config.max_tokens and tokens_used >= self.config.max_tokens:
            return True

        if self.config.max_time_seconds:
            elapsed = time.time() - start_time
            if elapsed >= self.config.max_time_seconds:
                return True

        if self.budget_tracker:
            # Check against global budget tracker
            try:
                self.budget_tracker.check_before_call("iteration_solver")
            except Exception:
                return True

        return False


# Convenience implementations for common use cases


class CodeExtractor(SolutionExtractor[str]):
    """Extracts code from markdown code blocks."""

    def __init__(self, language: str = "python"):
        self.language = language

    def extract(self, response: str) -> str | None:
        """Extract code from ```language ... ``` blocks."""
        import re

        # Try language-specific block first
        pattern = rf"```{self.language}\s*(.*?)```"
        match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()

        # Fall back to generic code block
        pattern = r"```\s*(.*?)```"
        match = re.search(pattern, response, re.DOTALL)
        if match:
            return match.group(1).strip()

        return None


class PlainExtractor(SolutionExtractor[str]):
    """Uses raw response as the solution."""

    def extract(self, response: str) -> str | None:
        return response.strip() if response else None


class TestEvaluator(SolutionEvaluator[str]):
    """Evaluates code by running tests.

    Integrates with deliberate's existing ValidationRunner.
    """

    def __init__(
        self,
        test_command: str | None = None,
        timeout_seconds: int = 300,
        working_dir: Path | None = None,
    ):
        self.test_command = test_command
        self.timeout_seconds = timeout_seconds
        self.working_dir = working_dir

    async def evaluate(self, solution: str, context: Any) -> tuple[FeedbackContext, dict]:
        """Evaluate by running tests.

        Args:
            solution: The code solution (written to working dir).
            context: Dict with 'working_dir' and optionally 'test_command'.

        Returns:
            FeedbackContext and raw test result dict.
        """
        from deliberate.validation.runner import run_validation

        working_dir = context.get("working_dir") or self.working_dir
        test_command = context.get("test_command") or self.test_command

        if not working_dir:
            raise ValueError("working_dir required for test evaluation")

        result = await run_validation(
            working_dir=Path(working_dir),
            command=test_command,
            timeout_seconds=self.timeout_seconds,
        )

        # Convert to FeedbackContext
        ctx = FeedbackContext(
            expected="all tests pass",
            actual=f"{result.tests_passed}/{result.tests_run} passed"
            if hasattr(result, "tests_run")
            else str(result.passed),
            match=result.passed,
            soft_score=self._calculate_soft_score(result),
            diff=result.failure_log if hasattr(result, "failure_log") else None,
            errors=result.stderr.split("\n")[:5] if result.stderr else [],
        )

        raw_result = {
            "passed": result.passed,
            "exit_code": result.exit_code,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "failures": [],  # Would need parsing for detailed failures
        }

        return ctx, raw_result

    def is_success(self, feedback_context: FeedbackContext) -> bool:
        return feedback_context.match

    def _calculate_soft_score(self, result) -> float:
        """Calculate soft score from test results."""
        if result.passed:
            return 1.0
        # Try to get pass ratio if available
        if hasattr(result, "total_tests") and result.total_tests > 0:
            passed = getattr(result, "passed_count", 0)
            return passed / result.total_tests
        return 0.0


async def run_iterative_solver(
    agent: ModelAdapter,
    task: str,
    evaluation_context: Any,
    evaluator: SolutionEvaluator,
    extractor: SolutionExtractor | None = None,
    feedback_builder: FeedbackBuilder | None = None,
    config: IterationConfig | None = None,
    budget_tracker: BudgetTracker | None = None,
    working_dir: str | Path | None = None,
) -> IterationResult:
    """Convenience function to run an iterative solver.

    Args:
        agent: The LLM adapter to use.
        task: The problem to solve.
        evaluation_context: Context for evaluating solutions.
        evaluator: How to evaluate solutions.
        extractor: How to extract solutions from responses (default: CodeExtractor).
        feedback_builder: How to build feedback (default: TestFeedbackBuilder).
        config: Iteration configuration (default: IterationConfig()).
        budget_tracker: Optional budget tracker.
        working_dir: Optional working directory.

    Returns:
        IterationResult with all attempts and final outcome.
    """
    from .feedback import TestFeedbackBuilder

    solver = IterativeSolver(
        agent=agent,
        evaluator=evaluator,
        extractor=extractor or CodeExtractor(),
        feedback_builder=feedback_builder or TestFeedbackBuilder(),
        config=config or IterationConfig(),
        budget_tracker=budget_tracker,
    )

    return await solver.solve(
        task=task,
        evaluation_context=evaluation_context,
        working_dir=working_dir,
    )
