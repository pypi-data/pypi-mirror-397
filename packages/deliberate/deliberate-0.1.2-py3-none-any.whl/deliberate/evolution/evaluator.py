"""Evaluators for the evolution module.

Integrates with deliberate's existing validation infrastructure:
- Syntax checking (parse/compile)
- Linting (ruff, flake8, etc.)
- Test execution (pytest, etc.)
- Code coverage
"""

import asyncio
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .controller import EvaluationResult, Evaluator
from .types import EvaluationLevel, Program, ProgramMetrics


@dataclass
class TDDEvaluatorConfig:
    """Configuration for the TDD evaluator."""

    test_command: str | None = None
    lint_command: str | None = "ruff check"
    timeout_seconds: int = 300
    working_dir: Path | None = None
    write_to_file: str = "solution.py"  # File to write code to
    coverage_enabled: bool = False


class TDDEvaluator(Evaluator):
    """Evaluator that uses TDD-style test execution.

    Implements the evaluation cascade:
    1. SYNTAX - Python parse check
    2. LINT - Code style check (ruff, flake8)
    3. UNIT_FAST - Quick unit tests
    4. UNIT_FULL - Full test suite
    5. BENCHMARK - Performance tests

    Integrates with deliberate's existing validation runner.
    """

    def __init__(self, config: TDDEvaluatorConfig | None = None):
        self.config = config or TDDEvaluatorConfig()

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
            context: Optional context (e.g., working_dir, test_command).

        Returns:
            EvaluationResult with metrics and feedback.
        """
        start_time = time.time()
        metrics = ProgramMetrics(
            generation=program.metrics.generation,
            parent_id=program.metrics.parent_id,
            lines_of_code=len(program.code.split("\n")),
        )

        # Extract context
        working_dir = self.config.working_dir
        test_command = self.config.test_command
        if context:
            if isinstance(context, dict):
                working_dir = context.get("working_dir", working_dir)
                test_command = context.get("test_command", test_command)
            elif isinstance(context, Path):
                working_dir = context

        # Evaluate based on level
        if level == EvaluationLevel.SYNTAX:
            result = await self._check_syntax(program)
        elif level == EvaluationLevel.LINT:
            result = await self._check_lint(program, working_dir)
        elif level in (EvaluationLevel.UNIT_FAST, EvaluationLevel.UNIT_FULL):
            result = await self._run_tests(program, working_dir, test_command)
        elif level == EvaluationLevel.INTEGRATION:
            result = await self._run_tests(program, working_dir, test_command, integration=True)
        elif level == EvaluationLevel.BENCHMARK:
            result = await self._run_benchmark(program, working_dir)
        else:
            result = EvaluationResult(
                passed=False,
                level=level,
                metrics=metrics,
                feedback=f"Unknown evaluation level: {level}",
            )

        # Update metrics with duration
        result.metrics.evaluation_time_ms = (time.time() - start_time) * 1000
        result.metrics.highest_level_passed = level if result.passed else EvaluationLevel.SYNTAX

        return result

    async def _check_syntax(self, program: Program) -> EvaluationResult:
        """Check if the program has valid Python syntax."""
        try:
            compile(program.code, "<string>", "exec")
            return EvaluationResult(
                passed=True,
                level=EvaluationLevel.SYNTAX,
                metrics=ProgramMetrics(lint_score=1.0),
                feedback="Syntax check passed",
            )
        except SyntaxError as e:
            return EvaluationResult(
                passed=False,
                level=EvaluationLevel.SYNTAX,
                metrics=ProgramMetrics(lint_score=0.0),
                feedback=f"Syntax error: {e}",
            )

    async def _check_lint(
        self,
        program: Program,
        working_dir: Path | None,
    ) -> EvaluationResult:
        """Run linter on the program."""
        if not self.config.lint_command:
            return EvaluationResult(
                passed=True,
                level=EvaluationLevel.LINT,
                metrics=ProgramMetrics(lint_score=1.0),
                feedback="No lint command configured",
            )

        # Write code to temp file and lint
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
        ) as f:
            f.write(program.code)
            temp_path = f.name

        try:
            cmd = f"{self.config.lint_command} {temp_path}"
            result = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(working_dir) if working_dir else None,
            )
            stdout, stderr = await asyncio.wait_for(
                result.communicate(),
                timeout=30,
            )

            lint_output = stdout.decode() + stderr.decode()

            if result.returncode == 0:
                return EvaluationResult(
                    passed=True,
                    level=EvaluationLevel.LINT,
                    metrics=ProgramMetrics(lint_score=1.0),
                    feedback="Lint check passed",
                    lint_output=lint_output,
                )
            else:
                # Count lint errors to compute score
                error_count = lint_output.count("\n")
                lint_score = max(0.0, 1.0 - (error_count * 0.1))

                return EvaluationResult(
                    passed=False,
                    level=EvaluationLevel.LINT,
                    metrics=ProgramMetrics(lint_score=lint_score),
                    feedback=f"Lint check failed with {error_count} issues",
                    lint_output=lint_output,
                )
        except asyncio.TimeoutError:
            return EvaluationResult(
                passed=False,
                level=EvaluationLevel.LINT,
                metrics=ProgramMetrics(lint_score=0.5),
                feedback="Lint check timed out",
            )
        finally:
            # Cleanup temp file
            Path(temp_path).unlink(missing_ok=True)

    async def _run_tests(
        self,
        program: Program,
        working_dir: Path | None,
        test_command: str | None,
        integration: bool = False,
    ) -> EvaluationResult:
        """Run tests on the program."""
        if not test_command:
            # Try to auto-detect test command
            test_command = "pytest -v"

        if not working_dir:
            return EvaluationResult(
                passed=False,
                level=EvaluationLevel.UNIT_FAST,
                metrics=ProgramMetrics(),
                feedback="No working directory configured for test execution",
            )

        # Write code to working dir
        code_path = working_dir / self.config.write_to_file
        code_path.write_text(program.code)

        try:
            # Import and use deliberate's validation runner
            from deliberate.validation.runner import run_validation

            result = await run_validation(
                working_dir=working_dir,
                command=test_command,
                timeout_seconds=self.config.timeout_seconds,
            )

            # Use structured test counts from ValidationResult
            tests_passed = result.tests_passed
            tests_total = result.tests_run or 1  # Avoid division by zero

            if result.passed:
                return EvaluationResult(
                    passed=True,
                    level=EvaluationLevel.UNIT_FULL if integration else EvaluationLevel.UNIT_FAST,
                    metrics=ProgramMetrics(
                        tests_passed=tests_total,
                        tests_total=tests_total,
                        test_score=1.0,
                    ),
                    feedback="All tests passed",
                    test_output=result.stdout,
                )
            else:
                test_score = tests_passed / tests_total if tests_total > 0 else 0.0

                # Build detailed feedback from artifacts if available
                feedback = f"Tests failed: {tests_passed}/{tests_total} passed"
                if result.artifacts:
                    from deliberate.validation.failure_interpreter import FailureInterpreter

                    interpreter = FailureInterpreter()
                    interpretation = interpreter.interpret(result.artifacts)
                    if interpretation.failed_tests:
                        failed_list = ", ".join(interpretation.failed_tests[:5])
                        if len(interpretation.failed_tests) > 5:
                            failed_list += f" (+{len(interpretation.failed_tests) - 5} more)"
                        feedback = f"Tests failed ({tests_passed}/{tests_total}): {failed_list}"

                return EvaluationResult(
                    passed=False,
                    level=EvaluationLevel.UNIT_FAST,
                    metrics=ProgramMetrics(
                        tests_passed=tests_passed,
                        tests_total=tests_total,
                        test_score=test_score,
                    ),
                    feedback=feedback,
                    test_output=result.stderr or result.stdout,
                )

        except Exception as e:
            return EvaluationResult(
                passed=False,
                level=EvaluationLevel.UNIT_FAST,
                metrics=ProgramMetrics(test_score=0.0),
                feedback=f"Test execution error: {e}",
            )

    async def _run_benchmark(
        self,
        program: Program,
        working_dir: Path | None,
    ) -> EvaluationResult:
        """Run performance benchmark on the program.

        This is a placeholder - real benchmarks would be domain-specific.
        """
        # Simple timing-based benchmark
        start = time.time()
        try:
            # Execute the code to measure runtime
            exec(compile(program.code, "<string>", "exec"), {})
            runtime_ms = (time.time() - start) * 1000

            return EvaluationResult(
                passed=True,
                level=EvaluationLevel.BENCHMARK,
                metrics=ProgramMetrics(runtime_ms=runtime_ms),
                feedback=f"Benchmark complete: {runtime_ms:.2f}ms",
            )
        except Exception as e:
            return EvaluationResult(
                passed=False,
                level=EvaluationLevel.BENCHMARK,
                metrics=ProgramMetrics(runtime_ms=float("inf")),
                feedback=f"Benchmark failed: {e}",
            )


class InMemoryEvaluator(Evaluator):
    """Simple evaluator for testing that doesn't use external tools.

    Useful for unit tests and quick experiments.
    """

    def __init__(
        self,
        expected_outputs: dict[str, Any] | None = None,
        test_function: str | None = None,
    ):
        """Initialize the evaluator.

        Args:
            expected_outputs: Dict mapping inputs to expected outputs.
            test_function: Name of function to test in the code.
        """
        self.expected_outputs = expected_outputs or {}
        self.test_function = test_function or "solve"

    async def evaluate(
        self,
        program: Program,
        level: EvaluationLevel,
        context: Any = None,
    ) -> EvaluationResult:
        """Evaluate by executing code and comparing outputs."""
        start_time = time.time()

        # Check syntax first
        try:
            compiled = compile(program.code, "<string>", "exec")
        except SyntaxError as e:
            return EvaluationResult(
                passed=False,
                level=EvaluationLevel.SYNTAX,
                metrics=ProgramMetrics(),
                feedback=f"Syntax error: {e}",
            )

        if level == EvaluationLevel.SYNTAX:
            return EvaluationResult(
                passed=True,
                level=level,
                metrics=ProgramMetrics(),
                feedback="Syntax OK",
            )

        # Execute and test
        try:
            namespace: dict[str, Any] = {}
            exec(compiled, namespace)

            if self.test_function not in namespace:
                return EvaluationResult(
                    passed=False,
                    level=level,
                    metrics=ProgramMetrics(),
                    feedback=f"Function '{self.test_function}' not found",
                )

            func = namespace[self.test_function]

            # Test all expected outputs
            tests_passed = 0
            tests_total = len(self.expected_outputs)
            failed_tests = []

            for input_val, expected in self.expected_outputs.items():
                try:
                    # Handle tuple inputs
                    if isinstance(input_val, tuple):
                        actual = func(*input_val)
                    else:
                        actual = func(input_val)

                    if actual == expected:
                        tests_passed += 1
                    else:
                        failed_tests.append(f"Input {input_val}: got {actual}, expected {expected}")
                except Exception as e:
                    failed_tests.append(f"Input {input_val}: {e}")

            test_score = tests_passed / tests_total if tests_total > 0 else 0.0
            passed = tests_passed == tests_total

            feedback = f"{tests_passed}/{tests_total} tests passed"
            if failed_tests:
                feedback += "\n" + "\n".join(failed_tests[:5])

            return EvaluationResult(
                passed=passed,
                level=level,
                metrics=ProgramMetrics(
                    tests_passed=tests_passed,
                    tests_total=tests_total,
                    test_score=test_score,
                    runtime_ms=(time.time() - start_time) * 1000,
                ),
                feedback=feedback,
            )

        except Exception as e:
            return EvaluationResult(
                passed=False,
                level=level,
                metrics=ProgramMetrics(),
                feedback=f"Execution error: {e}",
            )
