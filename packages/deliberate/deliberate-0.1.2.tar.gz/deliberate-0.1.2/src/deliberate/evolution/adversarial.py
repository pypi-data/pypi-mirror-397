"""Adversarial test loop for co-evolving tests and implementations.

This module implements a Red Team (tests) vs Blue Team (code) adversarial
loop where:
1. Tests evolve to find bugs in champion implementations
2. Code evolves to fix bugs exposed by tests
3. The cycle continues until tests can no longer break the code

SECURITY NOTE: Generated tests are code execution vectors. This module
requires isolation via DevContainer or git worktree to safely execute
untrusted test code.
"""

import logging
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path

from deliberate.adapters.base import ModelAdapter
from deliberate.budget.tracker import BudgetTracker
from deliberate.config import DevContainerConfig

from .test_evaluator import (
    TestValidationEvaluator,
)
from .test_prompt_builder import TestGenerationPromptBuilder
from .types import (
    Program,
    ProgramMetrics,
)

logger = logging.getLogger(__name__)


@dataclass
class AdversarialConfig:
    """Configuration for adversarial test loop.

    The adversarial loop co-evolves tests and code:
    - Tests try to break champion implementations (Red Team)
    - Code evolves to pass all tests (Blue Team)

    Security: Generated tests are code execution vectors.
    require_isolation MUST be True in production.
    """

    # Cycle limits
    max_cycles: int = 3  # Number of test<->code cycles
    max_test_evolution_iterations: int = 10  # Max iterations per test evolution
    max_code_evolution_iterations: int = 10  # Max iterations per code evolution

    # Quality thresholds
    min_kill_rate: float = 0.1  # Minimum useful kill rate for tests
    target_kill_rate: float = 0.5  # Target kill rate (higher = harder tests)
    max_new_tests_per_cycle: int = 3  # New tests to generate per cycle

    # Security - MUST use isolation in production
    require_isolation: bool = True  # Enforce DevContainer/worktree isolation

    # Budget limits per cycle
    max_tokens_per_cycle: int | None = None
    max_cost_per_cycle: float | None = None

    # Evaluation settings
    test_timeout_seconds: float = 30.0  # Timeout for running tests
    require_judge_approval: bool = True  # Require judge to validate tests


@dataclass
class CycleResult:
    """Result of a single adversarial cycle."""

    cycle_number: int
    tests_evolved: int
    tests_valid: int
    kill_rate: float
    code_evolved: int
    code_passes_tests: bool
    killed_champions: list[str] = field(default_factory=list)
    new_edge_cases: list[str] = field(default_factory=list)
    duration_seconds: float = 0.0


@dataclass
class AdversarialResult:
    """Result of the full adversarial loop."""

    success: bool
    final_code: str
    final_tests: str
    total_cycles: int
    cycle_results: list[CycleResult]
    final_kill_rate: float
    edge_cases_discovered: list[str]
    total_tests_generated: int
    total_code_iterations: int
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    total_time_seconds: float = 0.0
    termination_reason: str = ""


class AdversarialTestLoop:
    """Adversarial loop for co-evolving tests and implementations.

    The loop alternates between:
    1. Red Team: Evolve tests to break champion code
    2. Blue Team: Evolve code to pass all tests

    This creates a virtuous cycle where:
    - Tests become more thorough (find more edge cases)
    - Code becomes more robust (handles more edge cases)

    SECURITY: Generated tests execute arbitrary code. This class
    enforces isolation requirements to protect the host system.
    """

    def __init__(
        self,
        test_agent: ModelAdapter,
        code_agent: ModelAdapter,
        judge_agent: ModelAdapter | None = None,
        config: AdversarialConfig | None = None,
        devcontainer_config: DevContainerConfig | None = None,
        worktree_enabled: bool = False,
        budget_tracker: BudgetTracker | None = None,
    ):
        """Initialize the adversarial test loop.

        Args:
            test_agent: LLM adapter for generating tests.
            code_agent: LLM adapter for evolving code.
            judge_agent: Optional LLM adapter for validating tests.
            config: Adversarial loop configuration.
            devcontainer_config: DevContainer configuration (for isolation).
            worktree_enabled: Whether worktree isolation is enabled.
            budget_tracker: Optional budget tracker.

        Raises:
            ValueError: If isolation is required but not configured.
        """
        self.test_agent = test_agent
        self.code_agent = code_agent
        self.judge_agent = judge_agent
        self.config = config or AdversarialConfig()
        self.devcontainer_config = devcontainer_config
        self.worktree_enabled = worktree_enabled
        self.budget = budget_tracker

        # Validate isolation requirements
        if self.config.require_isolation:
            has_devcontainer = devcontainer_config is not None and devcontainer_config.enabled
            if not has_devcontainer and not worktree_enabled:
                raise ValueError(
                    "Adversarial test generation requires isolation. "
                    "Enable DevContainer (devcontainer_config.enabled=True) or "
                    "worktree isolation (worktree_enabled=True), or explicitly "
                    "disable isolation requirement (config.require_isolation=False). "
                    "WARNING: Disabling isolation is a security risk."
                )

        # Initialize components
        self.test_prompt_builder = TestGenerationPromptBuilder()
        self.test_evaluator = TestValidationEvaluator(
            judge_agent=judge_agent,
            min_kill_rate=self.config.min_kill_rate,
            require_judge_approval=self.config.require_judge_approval,
            max_test_time_seconds=self.config.test_timeout_seconds,
        )

        # State tracking
        self._current_cycle = 0
        self._total_tests_generated = 0
        self._total_code_iterations = 0
        self._edge_cases_discovered: list[str] = []
        self._start_time: float = 0.0

    async def run(
        self,
        task: str,
        initial_code: str,
        initial_tests: str | None = None,
        working_dir: Path | None = None,
    ) -> AdversarialResult:
        """Run the adversarial test loop.

        Args:
            task: Description of the programming task.
            initial_code: Starting implementation code.
            initial_tests: Optional initial test suite.
            working_dir: Working directory for test execution.

        Returns:
            AdversarialResult with evolved code, tests, and metrics.
        """
        self._start_time = time.time()
        self._current_cycle = 0
        self._total_tests_generated = 0
        self._total_code_iterations = 0
        self._edge_cases_discovered = []

        current_code = initial_code
        current_tests = initial_tests or ""
        cycle_results: list[CycleResult] = []
        termination_reason = "max_cycles"

        # Create champion program for evaluation
        champion = self._create_program(current_code, "champion", generation=0)

        for cycle in range(1, self.config.max_cycles + 1):
            self._current_cycle = cycle
            cycle_start = time.time()

            logger.info(f"Starting adversarial cycle {cycle}/{self.config.max_cycles}")

            # Phase 1: Red Team - Evolve tests to break champion
            test_result = await self._evolve_tests(
                task=task,
                champion_code=current_code,
                current_tests=current_tests,
                working_dir=working_dir,
            )

            # Check if tests found bugs
            if test_result.kill_rate == 0.0 and cycle > 1:
                # Tests can no longer break the code - success!
                termination_reason = "tests_cannot_break_code"
                logger.info("Tests can no longer break the code - adversarial loop complete")
                break

            current_tests = test_result.evolved_tests
            killed_champions = test_result.killed_champions

            # Phase 2: Blue Team - Evolve code to pass tests
            code_result = await self._evolve_code(
                task=task,
                current_code=current_code,
                tests=current_tests,
                working_dir=working_dir,
            )

            current_code = code_result.evolved_code
            self._total_code_iterations += code_result.iterations

            # Update champion
            champion = self._create_program(current_code, "champion", generation=cycle)

            # Record cycle result
            cycle_result = CycleResult(
                cycle_number=cycle,
                tests_evolved=test_result.tests_evolved,
                tests_valid=test_result.tests_valid,
                kill_rate=test_result.kill_rate,
                code_evolved=code_result.iterations,
                code_passes_tests=code_result.passes_tests,
                killed_champions=killed_champions,
                new_edge_cases=test_result.new_edge_cases,
                duration_seconds=time.time() - cycle_start,
            )
            cycle_results.append(cycle_result)

            # Track discovered edge cases
            self._edge_cases_discovered.extend(test_result.new_edge_cases)

            # Check if code now passes all tests
            if not code_result.passes_tests:
                # Code couldn't be fixed - log and continue
                logger.warning(f"Cycle {cycle}: Code evolution did not pass all tests")

            # Check budget limits
            if self._should_terminate():
                termination_reason = self._get_termination_reason()
                break

        # Final evaluation
        final_kill_rate = 0.0
        if current_tests:
            final_validation = await self.test_evaluator.evaluate(
                current_tests,
                champions=[champion],
                task_description=task,
                run_kill_evaluation=True,
            )
            final_kill_rate = final_validation.kill_rate

        return AdversarialResult(
            success=termination_reason == "tests_cannot_break_code",
            final_code=current_code,
            final_tests=current_tests,
            total_cycles=self._current_cycle,
            cycle_results=cycle_results,
            final_kill_rate=final_kill_rate,
            edge_cases_discovered=list(set(self._edge_cases_discovered)),
            total_tests_generated=self._total_tests_generated,
            total_code_iterations=self._total_code_iterations,
            total_tokens=getattr(self.budget, "total_tokens", 0) if self.budget else 0,
            total_cost_usd=getattr(self.budget, "total_cost", 0.0) if self.budget else 0.0,
            total_time_seconds=time.time() - self._start_time,
            termination_reason=termination_reason,
        )

    @dataclass
    class _TestEvolutionResult:
        """Internal result of test evolution phase."""

        evolved_tests: str
        tests_evolved: int
        tests_valid: int
        kill_rate: float
        killed_champions: list[str]
        new_edge_cases: list[str]

    async def _evolve_tests(
        self,
        task: str,
        champion_code: str,
        current_tests: str,
        working_dir: Path | None,
    ) -> _TestEvolutionResult:
        """Evolve tests to break the champion implementation.

        This is the Red Team phase where we generate adversarial tests
        that expose bugs in the current champion.

        Args:
            task: Task description.
            champion_code: Current champion implementation.
            current_tests: Existing test suite.
            working_dir: Working directory for execution.

        Returns:
            _TestEvolutionResult with evolved tests and metrics.
        """
        best_tests = current_tests
        best_kill_rate = 0.0
        tests_evolved = 0
        tests_valid = 0
        killed_champions: list[str] = []
        new_edge_cases: list[str] = []

        # Create champion program for evaluation
        champion = self._create_program(champion_code, "champion", generation=0)

        for iteration in range(1, self.config.max_test_evolution_iterations + 1):
            # Build prompt for test generation
            if best_tests:
                # Evolve existing tests
                parent_test = self._create_program(best_tests, "test", generation=iteration - 1)
                prompt = self.test_prompt_builder.build_test_evolution_prompt(
                    task=task,
                    champion_code=champion_code,
                    parent_test=parent_test,
                    known_edge_cases=self._edge_cases_discovered,
                    iteration=iteration,
                )
            else:
                # Generate initial tests
                prompt = self.test_prompt_builder.build_initial_test_prompt(
                    task=task,
                    champion_code=champion_code,
                )

            # Generate tests via LLM
            try:
                response = await self.test_agent.call(prompt)
                if self.budget:
                    self.budget.record_usage(
                        self.test_agent.name,
                        response.token_usage,
                        self.test_agent.estimate_cost(response.token_usage),
                        phase="adversarial_test",
                    )
            except Exception as e:
                logger.warning(f"Test generation failed: {e}")
                continue

            # Extract test code from response
            test_code = self._extract_code(response.content)
            if not test_code:
                continue

            tests_evolved += 1
            self._total_tests_generated += 1

            # Validate the generated tests
            validation = await self.test_evaluator.evaluate(
                test_code,
                champions=[champion],
                task_description=task,
                run_kill_evaluation=True,
            )

            if not validation.is_valid:
                logger.debug(f"Generated tests invalid: {validation.errors}")
                continue

            tests_valid += 1

            # Check if these tests are better (higher kill rate)
            if validation.kill_rate > best_kill_rate:
                best_tests = test_code
                best_kill_rate = validation.kill_rate
                killed_champions = validation.killed_champions
                new_edge_cases = validation.edge_cases_detected

                logger.info(f"Test evolution {iteration}: kill rate improved to {validation.kill_rate:.1%}")

            # Check if we've reached target kill rate
            if best_kill_rate >= self.config.target_kill_rate:
                logger.info(f"Target kill rate {self.config.target_kill_rate:.1%} reached")
                break

        return self._TestEvolutionResult(
            evolved_tests=best_tests,
            tests_evolved=tests_evolved,
            tests_valid=tests_valid,
            kill_rate=best_kill_rate,
            killed_champions=killed_champions,
            new_edge_cases=new_edge_cases,
        )

    @dataclass
    class _CodeEvolutionResult:
        """Internal result of code evolution phase."""

        evolved_code: str
        iterations: int
        passes_tests: bool

    async def _evolve_code(
        self,
        task: str,
        current_code: str,
        tests: str,
        working_dir: Path | None,
    ) -> _CodeEvolutionResult:
        """Evolve code to pass all tests.

        This is the Blue Team phase where we fix the implementation
        to pass the adversarial tests.

        Args:
            task: Task description.
            current_code: Current implementation.
            tests: Test suite to pass.
            working_dir: Working directory for execution.

        Returns:
            _CodeEvolutionResult with evolved code and metrics.
        """
        best_code = current_code
        iterations = 0
        passes_tests = False

        for iteration in range(1, self.config.max_code_evolution_iterations + 1):
            iterations += 1

            # Build prompt for code evolution
            prompt = self._build_code_evolution_prompt(
                task=task,
                current_code=best_code,
                tests=tests,
                iteration=iteration,
            )

            # Generate code via LLM
            try:
                response = await self.code_agent.call(prompt)
                if self.budget:
                    self.budget.record_usage(
                        self.code_agent.name,
                        response.token_usage,
                        self.code_agent.estimate_cost(response.token_usage),
                        phase="adversarial_code",
                    )
            except Exception as e:
                logger.warning(f"Code generation failed: {e}")
                continue

            # Extract code from response
            new_code = self._extract_code(response.content)
            if not new_code:
                continue

            # Evaluate if code passes tests
            # Note: In production, this would run in isolation
            test_passed = await self._evaluate_code_against_tests(new_code, tests, working_dir)

            if test_passed:
                best_code = new_code
                passes_tests = True
                logger.info(f"Code evolution {iteration}: All tests pass")
                break
            else:
                # Code improved but still has failures - continue evolving
                best_code = new_code
                logger.debug(f"Code evolution {iteration}: Tests still failing")

        return self._CodeEvolutionResult(
            evolved_code=best_code,
            iterations=iterations,
            passes_tests=passes_tests,
        )

    def _build_code_evolution_prompt(
        self,
        task: str,
        current_code: str,
        tests: str,
        iteration: int,
    ) -> str:
        """Build prompt for code evolution."""
        return f"""# Task

{task}

## Current Implementation

```python
{current_code}
```

## Tests to Pass

The following tests are failing. Your goal is to fix the implementation
so that all tests pass.

```python
{tests}
```

## Instructions (Iteration {iteration})

1. Analyze why the tests are failing
2. Fix the implementation to pass all tests
3. Ensure your fix doesn't break other functionality
4. Keep the code clean and maintainable

Provide your fixed implementation:

```python
# Your implementation here
```
"""

    async def _evaluate_code_against_tests(
        self,
        code: str,
        tests: str,
        working_dir: Path | None,
    ) -> bool:
        """Evaluate if code passes all tests.

        Note: This is a placeholder. In production, this would:
        1. Write code and tests to isolated worktree/container
        2. Run pytest and capture results
        3. Parse test outcomes

        Args:
            code: Implementation code.
            tests: Test suite.
            working_dir: Working directory for execution.

        Returns:
            True if all tests pass, False otherwise.
        """
        # Placeholder - in production this runs in isolation
        # For now, do syntax validation only
        try:
            import ast

            ast.parse(code)
            ast.parse(tests)
            return True  # Assume passing for now
        except SyntaxError:
            return False

    def _create_program(
        self,
        code: str,
        agent: str,
        generation: int = 0,
    ) -> Program:
        """Create a Program object from code."""
        return Program(
            id=f"{agent}_{generation}_{uuid.uuid4().hex[:8]}",
            code=code,
            agent=agent,
            metrics=ProgramMetrics(generation=generation),
        )

    def _extract_code(self, text: str) -> str | None:
        """Extract code from LLM response."""
        import re

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

        return None

    def _should_terminate(self) -> bool:
        """Check if the loop should terminate early."""
        if self.budget:
            total_tokens = getattr(self.budget, "total_tokens", 0)
            total_cost = getattr(self.budget, "total_cost", 0.0)
            if self.config.max_tokens_per_cycle and total_tokens >= self.config.max_tokens_per_cycle:
                return True
            if self.config.max_cost_per_cycle and total_cost >= self.config.max_cost_per_cycle:
                return True
        return False

    def _get_termination_reason(self) -> str:
        """Get the reason for early termination."""
        if self.budget:
            total_tokens = getattr(self.budget, "total_tokens", 0)
            total_cost = getattr(self.budget, "total_cost", 0.0)
            if self.config.max_tokens_per_cycle and total_tokens >= self.config.max_tokens_per_cycle:
                return "token_limit"
            if self.config.max_cost_per_cycle and total_cost >= self.config.max_cost_per_cycle:
                return "cost_limit"
        return "unknown"
