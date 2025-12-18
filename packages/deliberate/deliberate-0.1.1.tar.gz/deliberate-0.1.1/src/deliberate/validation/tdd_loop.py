"""TDD (Test-Driven Development) inner loop for refinement.

The TDD loop minimizes expensive LLM reviews by using cheap test execution
to validate changes before sending to the jury.

Enhanced with the meta-pattern from poetiq-arc-agi-solver:
- "The prompt is an interface, not the intelligence" - iterative feedback loop
- "Self-auditing" - track progress and best solutions across iterations

Workflow:
1. Pre-Flight: Agent writes a failing test (optional, for new features)
2. Gate 1: Lint/validate the test file
3. Execute: Agent writes/fixes code
4. Gate 2: Run tests - if fail -> feed stderr back -> retry with history
5. Review: Only if tests pass (or max retries) go to LLM Jury
"""

import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

from deliberate.adapters.base import ModelAdapter
from deliberate.budget.tracker import BudgetTracker
from deliberate.validation.failure_interpreter import (
    FailureInterpretation,
    FailureInterpreter,
)
from deliberate.validation.linter import LintResult, lint_directory
from deliberate.validation.runner import run_validation
from deliberate.validation.types import ValidationResult


@dataclass
class TDDConfig:
    """Configuration for the TDD loop."""

    enabled: bool = True
    max_fix_iterations: int = 3  # Max test->fail->fix cycles before giving up
    lint_before_test: bool = True  # Run linter before tests
    lint_patterns: list[str] = field(default_factory=lambda: ["**/*.py"])
    require_tests_pass: bool = True  # Block LLM review until tests pass
    test_command: Optional[str] = None  # Override auto-detection
    test_timeout_seconds: int = 300
    lint_timeout_seconds: int = 60

    # Iterative feedback settings (inspired by poetiq meta-pattern)
    use_iterative_feedback: bool = True  # Include history in prompts
    max_history_in_prompt: int = 3  # Max previous attempts to include
    include_history_scores: bool = True  # Show soft scores for past attempts
    return_best_on_failure: bool = True  # Return best attempt if no success

    # Failure interpretation settings
    use_failure_interpreter: bool = True  # Use FailureInterpreter for analysis
    interpreter_llm_handler: Optional[Callable[[str], str]] = None  # LLM fallback


@dataclass
class TDDIteration:
    """Record of a single TDD fix iteration."""

    iteration_num: int
    lint_result: Optional[LintResult]
    validation_result: Optional[ValidationResult]
    fix_prompt: str  # Prompt sent to agent
    agent_response: str  # Agent's fix attempt
    duration_seconds: float
    tokens_used: int
    # Soft score for partial progress tracking (0.0-1.0)
    soft_score: float = 0.0
    # Structured failure interpretation (when using FailureInterpreter)
    interpretation: Optional[FailureInterpretation] = None


@dataclass
class TDDLoopResult:
    """Result of a complete TDD loop."""

    success: bool  # Did tests eventually pass?
    iterations: list[TDDIteration]
    final_lint: Optional[LintResult]
    final_validation: Optional[ValidationResult]
    total_tokens: int
    total_duration: float
    gave_up: bool = False  # True if we hit max iterations without passing
    best_iteration: Optional[TDDIteration] = None  # Best attempt by soft_score
    score_trajectory: list[float] = field(default_factory=list)  # Scores over time

    @property
    def summary(self) -> str:
        """Human readable summary."""
        if self.success:
            return f"TDD: PASSED after {len(self.iterations)} iteration(s)"
        if self.gave_up:
            best_score = self.best_iteration.soft_score if self.best_iteration else 0.0
            return f"TDD: GAVE UP after {len(self.iterations)} iteration(s), best score: {best_score:.2f}"
        return f"TDD: FAILED ({len(self.iterations)} iteration(s))"

    @property
    def is_improving(self) -> bool:
        """Check if scores are improving over iterations."""
        if len(self.score_trajectory) < 2:
            return True
        return self.score_trajectory[-1] > self.score_trajectory[0]


class TDDLoop:
    """Implements the inner TDD cycle: test -> fail -> fix -> retest.

    Enhanced with the meta-pattern from poetiq-arc-agi-solver:
    - Accumulates solution history with soft scores
    - Includes past attempts in prompts for learning
    - Tracks best solution for return on failure

    This loop is "cheap" - it only uses the agent for fixes and avoids
    expensive LLM reviews until tests pass.
    """

    def __init__(
        self,
        config: TDDConfig,
        agent: ModelAdapter,
        working_dir: Path,
        budget_tracker: Optional[BudgetTracker] = None,
    ):
        self.config = config
        self.agent = agent
        self.working_dir = working_dir
        self.budget = budget_tracker
        self._best_iteration: Optional[TDDIteration] = None
        self._best_score: float = 0.0
        self._score_trajectory: list[float] = []

        # Create failure interpreter if enabled
        self._interpreter: Optional[FailureInterpreter] = None
        if config.use_failure_interpreter:
            self._interpreter = FailureInterpreter(llm_handler=config.interpreter_llm_handler)

    async def run(
        self,
        task_description: str,
        initial_validation: Optional[ValidationResult] = None,
    ) -> TDDLoopResult:
        """Run the TDD loop until tests pass or max iterations.

        Enhanced with iterative feedback pattern:
        - Tracks soft scores for partial progress
        - Includes history of past attempts in prompts
        - Returns best attempt on failure

        Args:
            task_description: The original task/fix description.
            initial_validation: Optional initial test run result.

        Returns:
            TDDLoopResult with all iterations and final state.
        """
        start_time = time.time()
        iterations: list[TDDIteration] = []
        total_tokens = 0

        # Reset tracking state
        self._best_iteration = None
        self._best_score = 0.0
        self._score_trajectory = []

        # Get initial test state if not provided
        current_validation = initial_validation
        if current_validation is None:
            current_validation = await self._run_tests()

        # Pre-flight: Check for broken environment (bad command)
        if self._is_environment_error(current_validation):
            current_validation = await self._attempt_command_fix(current_validation, task_description)
            # If still broken after attempted fix, abort
            if self._is_environment_error(current_validation):
                return TDDLoopResult(
                    success=False,
                    iterations=iterations,
                    final_lint=None,
                    final_validation=current_validation,
                    total_tokens=total_tokens,
                    total_duration=time.time() - start_time,
                    gave_up=True,
                )

        # If tests already pass, we're done (self-audit: immediate success)
        if current_validation.passed:
            return TDDLoopResult(
                success=True,
                iterations=[],
                final_lint=None,
                final_validation=current_validation,
                total_tokens=0,
                total_duration=time.time() - start_time,
                score_trajectory=[1.0],
            )

        # TDD inner loop with iterative feedback
        for i in range(1, self.config.max_fix_iterations + 1):
            iter_start = time.time()

            # Gate 1: Lint check (optional but cheap)
            lint_result = None
            if self.config.lint_before_test:
                lint_result = await self._run_lint()
                if not lint_result.passed:
                    # Syntax errors - feed back to agent immediately
                    fix_prompt = self._build_lint_fix_prompt(task_description, lint_result, i)
                    response = await self._call_agent(fix_prompt)
                    total_tokens += response.token_usage

                    # Lint failure = score 0 (can't even run tests)
                    iteration = TDDIteration(
                        iteration_num=i,
                        lint_result=lint_result,
                        validation_result=None,
                        fix_prompt=fix_prompt,
                        agent_response=response.content,
                        duration_seconds=time.time() - iter_start,
                        tokens_used=response.token_usage,
                        soft_score=0.0,
                    )
                    iterations.append(iteration)
                    self._score_trajectory.append(0.0)

                    # Re-lint after fix
                    lint_result = await self._run_lint()
                    if not lint_result.passed:
                        continue  # Still has lint errors, try again

            # Gate 2: Run tests
            current_validation = await self._run_tests()

            # Calculate soft score for partial progress
            soft_score = self._calculate_soft_score(current_validation)

            if current_validation.passed:
                # Success! Tests pass (self-audit: terminate early)
                self._score_trajectory.append(1.0)
                return TDDLoopResult(
                    success=True,
                    iterations=iterations,
                    final_lint=lint_result,
                    final_validation=current_validation,
                    total_tokens=total_tokens,
                    total_duration=time.time() - start_time,
                    best_iteration=self._best_iteration,
                    score_trajectory=self._score_trajectory,
                )

            # Tests failed - build prompt with history context
            fix_prompt = self._build_test_fix_prompt(task_description, current_validation, lint_result, i, iterations)
            response = await self._call_agent(fix_prompt)
            total_tokens += response.token_usage
            response_text = getattr(response, "summary", response.content)

            # Get structured interpretation if available
            interpretation = self._interpret_validation(current_validation)

            iteration = TDDIteration(
                iteration_num=i,
                lint_result=lint_result,
                validation_result=current_validation,
                fix_prompt=fix_prompt,
                agent_response=response_text,
                duration_seconds=time.time() - iter_start,
                tokens_used=response.token_usage,
                soft_score=soft_score,
                interpretation=interpretation,
            )
            iterations.append(iteration)
            self._score_trajectory.append(soft_score)

            # Track best iteration
            if soft_score >= self._best_score:
                self._best_score = soft_score
                self._best_iteration = iteration

        # Max iterations reached - run final validation
        final_lint = await self._run_lint() if self.config.lint_before_test else None
        final_validation = await self._run_tests()

        return TDDLoopResult(
            success=final_validation.passed,
            iterations=iterations,
            final_lint=final_lint,
            final_validation=final_validation,
            total_tokens=total_tokens,
            total_duration=time.time() - start_time,
            gave_up=not final_validation.passed,
            best_iteration=self._best_iteration,
            score_trajectory=self._score_trajectory,
        )

    def _calculate_soft_score(self, validation: ValidationResult) -> float:
        """Calculate soft score (0.0-1.0) for partial progress.

        Inspired by poetiq's soft scoring for ARC-AGI grids.
        Uses ValidationResult's structured test counts when available.
        """
        if validation.passed:
            return 1.0

        # Use structured test counts from ValidationResult
        if validation.tests_run > 0:
            return validation.tests_passed / validation.tests_run

        # Fall back to exit code heuristic (0 = pass, anything else = fail)
        if validation.exit_code == 0:
            return 1.0
        return 0.0

    def _interpret_validation(self, validation: ValidationResult) -> Optional[FailureInterpretation]:
        """Use FailureInterpreter to extract structured failure info.

        Returns None if interpreter is disabled or no artifacts available.
        """
        if not self._interpreter:
            return None

        # Check if validation has artifacts
        artifacts = validation.artifacts
        if not artifacts:
            # Fall back to constructing minimal artifacts from ValidationResult
            from deliberate.validation.types import RunArtifacts

            artifacts = RunArtifacts(
                command=validation.command,
                cwd=self.working_dir,
                exit_code=validation.exit_code,
                duration_seconds=validation.duration_seconds,
                stdout=validation.stdout,
                stderr=validation.stderr,
            )

        return self._interpreter.interpret(artifacts)

    async def _run_lint(self) -> LintResult:
        """Run lint check on the working directory."""
        return await lint_directory(
            self.working_dir,
            patterns=self.config.lint_patterns,
            timeout_seconds=self.config.lint_timeout_seconds,
        )

    async def _run_tests(self) -> ValidationResult:
        """Run tests in the working directory."""
        return await run_validation(
            self.working_dir,
            command=self.config.test_command,
            timeout_seconds=self.config.test_timeout_seconds,
        )

    def _is_environment_error(self, result: ValidationResult) -> bool:
        """Check if validation failed due to broken environment/command."""
        if result.exit_code in [126, 127]:  # 126=not executable, 127=not found
            return True
        if result.error == "Command not found":
            return True
        if "command not found" in (result.stderr or "").lower():
            return True
        if "no test command configured" in (result.stderr or "").lower():
            return True
        return False

    async def _attempt_command_fix(
        self,
        validation: ValidationResult,
        task: str,
    ) -> ValidationResult:
        """Attempt to fix broken test command by asking agent."""
        print("  -> Detected broken test command. Asking agent to fix...")

        for attempt in range(2):  # Try twice
            prompt = self._build_command_fix_prompt(task, validation)
            response = await self._call_agent(prompt)
            response_text = getattr(response, "summary", response.content)

            # Parse response for code block with command
            # Look for ```bash ... ``` or just ``` ... ```
            match = re.search(r"```(?:bash)?\s*(.+?)\s*```", response_text, re.DOTALL)
            if match:
                new_command = match.group(1).strip()
                # Remove common prefixes like '$ ' if present
                if new_command.startswith("$ "):
                    new_command = new_command[2:]

                print(f"  -> Agent proposed new command: {new_command}")
                self.config.test_command = new_command

                # Verify immediately
                new_validation = await self._run_tests()
                if not self._is_environment_error(new_validation):
                    return new_validation

                # Update validation for next loop (error message might have changed)
                validation = new_validation

        return validation

    async def _call_agent(self, prompt: str):
        """Call the agent with the fix prompt."""
        response = await self.agent.run_agentic(
            task=prompt,
            working_dir=str(self.working_dir),
            timeout_seconds=600,  # 10 min timeout for fixes
        )

        # Record budget usage
        if self.budget:
            self.budget.record_usage(
                self.agent.name,
                response.token_usage,
                self.agent.estimate_cost(response.token_usage),
                phase="tdd_fix",
            )

        return response

    def _build_lint_fix_prompt(
        self,
        task: str,
        lint_result: LintResult,
        iteration: int,
    ) -> str:
        """Build prompt for fixing lint/syntax errors."""
        return f"""# URGENT: Fix Syntax/Lint Errors

Your code has syntax errors that must be fixed before tests can run.

## Original Task
{task}

## Lint Errors (Iteration {iteration}/{self.config.max_fix_iterations})
{lint_result.error_log}

## Full Output
```
{lint_result.stderr[:2000]}
```

## Instructions
1. Fix ALL syntax errors listed above
2. Do not change any logic - only fix syntax
3. The code must compile/parse successfully

Fix the syntax errors now.
"""

    def _build_test_fix_prompt(
        self,
        task: str,
        validation: ValidationResult,
        lint_result: Optional[LintResult],
        iteration: int,
        previous_iterations: Optional[list[TDDIteration]] = None,
    ) -> str:
        """Build prompt for fixing test failures.

        Enhanced with iterative feedback pattern: includes history of
        previous attempts when enabled, so the agent can learn from
        past failures.
        """
        lint_section = ""
        if lint_result and lint_result.warnings:
            lint_section = f"""
## Lint Warnings (non-blocking)
{chr(10).join(f"- {w}" for w in lint_result.warnings[:10])}
"""

        # Build history context if enabled and we have previous iterations
        history_section = ""
        if self.config.use_iterative_feedback and previous_iterations and len(previous_iterations) > 0:
            history_section = self._build_history_context(previous_iterations)

        return f"""# Fix Failing Tests (Iteration {iteration}/{self.config.max_fix_iterations})

Your implementation has failing tests. Fix them WITHOUT waiting for code review.

## Original Task
{task}

## Current Test Results
{validation.summary}
{validation.failure_log}

## Test Command
`{validation.command}`

## Exit Code
{validation.exit_code}
{lint_section}{history_section}
## Instructions
1. Read the test failures carefully
2. Fix your implementation to make the tests pass
3. Do NOT modify the tests unless they are clearly incorrect
4. Focus on the specific errors shown above
5. Learn from previous attempts if shown above - avoid repeating the same mistakes

Fix the code now. The tests will be re-run automatically.
"""

    def _build_history_context(
        self,
        previous_iterations: list[TDDIteration],
    ) -> str:
        """Build history context section for the prompt.

        Inspired by poetiq's FEEDBACK_PROMPT - shows previous attempts
        with their scores and feedback so the agent can learn from mistakes.
        """
        if not previous_iterations:
            return ""

        # Select recent iterations (up to max_history_in_prompt)
        selected = previous_iterations[-self.config.max_history_in_prompt :]

        # Sort by score if we want improving order (worst to best)
        selected = sorted(selected, key=lambda x: x.soft_score)

        blocks = []
        for i, iteration in enumerate(selected, start=1):
            validation = iteration.validation_result
            feedback_text = "No validation result"
            if validation:
                # Build a summary of the test failure
                feedback_text = validation.summary or f"Exit code: {validation.exit_code}"
                if validation.failure_log:
                    # Truncate to avoid huge prompts
                    failure_excerpt = validation.failure_log[:500]
                    if len(validation.failure_log) > 500:
                        failure_excerpt += "... (truncated)"
                    feedback_text += f"\n{failure_excerpt}"

            score_info = ""
            if self.config.include_history_scores:
                score_info = f"\n<attempt_score>{iteration.soft_score:.2f}</attempt_score>"

            blocks.append(f"""<previous_attempt_{i}>
<attempt_iteration>{iteration.iteration_num}</attempt_iteration>
<attempt_feedback>
{feedback_text}
</attempt_feedback>{score_info}
</previous_attempt_{i}>""")

        return f"""
## Previous Attempts (learn from these)

Study these previous attempts and their results. Avoid repeating the same mistakes.

{chr(10).join(blocks)}
"""

    def _build_command_fix_prompt(
        self,
        task: str,
        validation: ValidationResult,
    ) -> str:
        """Build prompt for fixing broken test command."""
        return f"""# URGENT: Fix Test Command

The test command failed to execute (Command Not Found or similar error).
We cannot verify your code until we have a working test command.

## Original Task
{task}

## Failed Command
`{validation.command}`

## Error Output
```
{validation.stderr}
```
Exit Code: {validation.exit_code}

## Instructions
1. Analyze the project structure (you can use tools to list files)
2. Determine the CORRECT command to run tests for this project
3. Return the command inside a BASH code block

Example:
```bash
pytest tests/
```

Provide ONLY the command in the code block.
"""


async def run_tdd_loop(
    agent: ModelAdapter,
    working_dir: Path,
    task: str,
    config: Optional[TDDConfig] = None,
    budget_tracker: Optional[BudgetTracker] = None,
    initial_validation: Optional[ValidationResult] = None,
) -> TDDLoopResult:
    """Convenience function to run a TDD loop.

    Args:
        agent: Model adapter for fix iterations.
        working_dir: Directory containing the code.
        task: Original task description.
        config: TDD configuration (uses defaults if None).
        budget_tracker: Optional budget tracker.
        initial_validation: Optional initial test result.

    Returns:
        TDDLoopResult with outcome.
    """
    if config is None:
        config = TDDConfig()

    loop = TDDLoop(config, agent, working_dir, budget_tracker)
    return await loop.run(task, initial_validation)
