"""Tests for TDD loop and linter modules."""

import asyncio
import tempfile
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from deliberate.validation.linter import (
    LintResult,
    lint_directory,
    lint_file,
    lint_python_file,
)
from deliberate.validation.tdd_loop import (
    TDDConfig,
    TDDLoop,
    TDDLoopResult,
    run_tdd_loop,
)
from deliberate.validation.types import ValidationResult

# =============================================================================
# Linter Tests
# =============================================================================


class TestLintResult:
    """Tests for LintResult dataclass."""

    def test_passed_summary(self):
        """Test summary for passing lint."""
        result = LintResult(
            passed=True,
            command="python -m py_compile test.py",
            exit_code=0,
            errors=[],
            warnings=[],
            stdout="",
            stderr="",
        )
        assert result.summary == "Lint: PASSED"

    def test_failed_summary(self):
        """Test summary for failing lint."""
        result = LintResult(
            passed=False,
            command="python -m py_compile test.py",
            exit_code=1,
            errors=["SyntaxError: invalid syntax", "NameError: undefined"],
            warnings=[],
            stdout="",
            stderr="",
        )
        assert result.summary == "Lint: FAILED (2 errors)"

    def test_error_log_formatting(self):
        """Test error_log property formats errors correctly."""
        result = LintResult(
            passed=False,
            command="lint",
            exit_code=1,
            errors=["Error 1", "Error 2"],
            warnings=[],
            stdout="",
            stderr="",
        )
        assert "## Lint Errors:" in result.error_log
        assert "- Error 1" in result.error_log
        assert "- Error 2" in result.error_log

    def test_error_log_empty_when_no_errors(self):
        """Test error_log is empty when no errors."""
        result = LintResult(
            passed=True,
            command="lint",
            exit_code=0,
            errors=[],
            warnings=[],
            stdout="",
            stderr="",
        )
        assert result.error_log == ""


class TestLintPythonFile:
    """Tests for lint_python_file function."""

    @pytest.mark.asyncio
    async def test_valid_python_file(self):
        """Test linting a valid Python file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def hello():\n    return 'world'\n")
            f.flush()
            path = Path(f.name)

        try:
            result = await lint_python_file(path)
            assert result.passed is True
            assert result.exit_code == 0
            assert len(result.errors) == 0
        finally:
            path.unlink()

    @pytest.mark.asyncio
    async def test_syntax_error_python_file(self):
        """Test linting a Python file with syntax errors."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def broken(\n    return 'missing close paren'\n")
            f.flush()
            path = Path(f.name)

        try:
            result = await lint_python_file(path)
            assert result.passed is False
            assert result.exit_code != 0
            assert len(result.errors) > 0
        finally:
            path.unlink()

    @pytest.mark.asyncio
    async def test_nonexistent_file(self):
        """Test linting a file that doesn't exist."""
        path = Path("/nonexistent/path/to/file.py")
        # py_compile will fail for nonexistent files
        result = await lint_python_file(path)
        assert result.passed is False


class TestLintFile:
    """Tests for lint_file function (extension-based dispatch)."""

    @pytest.mark.asyncio
    async def test_python_file_dispatch(self):
        """Test that .py files use Python linter."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("x = 1\n")
            f.flush()
            path = Path(f.name)

        try:
            result = await lint_file(path)
            assert result.passed is True
            assert "py_compile" in result.command
        finally:
            path.unlink()

    @pytest.mark.asyncio
    async def test_unknown_extension(self):
        """Test that unknown extensions are assumed OK."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xyz", delete=False) as f:
            f.write("random content\n")
            f.flush()
            path = Path(f.name)

        try:
            result = await lint_file(path)
            assert result.passed is True
            assert any("No linter configured" in w for w in result.warnings)
        finally:
            path.unlink()


class TestLintDirectory:
    """Tests for lint_directory function."""

    @pytest.mark.asyncio
    async def test_lint_directory_all_valid(self):
        """Test linting a directory with all valid Python files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            (d / "a.py").write_text("x = 1\n")
            (d / "b.py").write_text("y = 2\n")

            result = await lint_directory(d, patterns=["*.py"])
            assert result.passed is True
            assert result.exit_code == 0
            assert "2 files" in result.command

    @pytest.mark.asyncio
    async def test_lint_directory_with_errors(self):
        """Test linting a directory with some invalid files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            (d / "valid.py").write_text("x = 1\n")
            (d / "invalid.py").write_text("def broken(\n")

            result = await lint_directory(d, patterns=["*.py"])
            assert result.passed is False
            assert len(result.errors) > 0

    @pytest.mark.asyncio
    async def test_lint_directory_default_patterns(self):
        """Test lint_directory uses **/*.py by default."""
        with tempfile.TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            subdir = d / "subdir"
            subdir.mkdir()
            (subdir / "nested.py").write_text("z = 3\n")

            result = await lint_directory(d)  # No patterns = default **/*.py
            assert result.passed is True


# =============================================================================
# TDD Loop Tests
# =============================================================================


class TestTDDConfig:
    """Tests for TDDConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = TDDConfig()
        assert config.enabled is True
        assert config.max_fix_iterations == 3
        assert config.lint_before_test is True
        assert config.require_tests_pass is True
        assert config.test_command is None
        assert config.test_timeout_seconds == 300

    def test_custom_config(self):
        """Test custom configuration."""
        config = TDDConfig(
            enabled=False,
            max_fix_iterations=5,
            lint_before_test=False,
            test_command="pytest -x",
        )
        assert config.enabled is False
        assert config.max_fix_iterations == 5
        assert config.lint_before_test is False
        assert config.test_command == "pytest -x"


class TestTDDLoopResult:
    """Tests for TDDLoopResult dataclass."""

    def test_success_summary(self):
        """Test summary for successful TDD loop."""
        result = TDDLoopResult(
            success=True,
            iterations=[MagicMock(), MagicMock()],
            final_lint=None,
            final_validation=None,
            total_tokens=1000,
            total_duration=10.5,
        )
        assert "PASSED" in result.summary
        assert "2 iteration(s)" in result.summary

    def test_gave_up_summary(self):
        """Test summary when TDD loop gave up."""
        result = TDDLoopResult(
            success=False,
            iterations=[MagicMock(), MagicMock(), MagicMock()],
            final_lint=None,
            final_validation=None,
            total_tokens=3000,
            total_duration=30.0,
            gave_up=True,
        )
        assert "GAVE UP" in result.summary
        assert "3 iteration(s)" in result.summary

    def test_failed_summary(self):
        """Test summary for failed TDD loop."""
        result = TDDLoopResult(
            success=False,
            iterations=[MagicMock()],
            final_lint=None,
            final_validation=None,
            total_tokens=500,
            total_duration=5.0,
            gave_up=False,
        )
        assert "FAILED" in result.summary


class TestTDDLoop:
    """Tests for TDDLoop class."""

    @pytest.fixture
    def mock_agent(self):
        """Create a mock agent adapter."""
        agent = MagicMock()
        agent.name = "test-agent"

        # Create a response object
        @dataclass
        class MockResponse:
            content: str
            token_usage: int

            @property
            def summary(self):
                return self.content

        agent.run_agentic = AsyncMock(return_value=MockResponse(content="Fixed the code", token_usage=100))
        agent.estimate_cost = MagicMock(return_value=0.001)
        return agent

    @pytest.fixture
    def passing_validation(self):
        """Create a passing validation result."""
        return ValidationResult(
            passed=True,
            command="pytest",
            exit_code=0,
            stdout="All tests passed",
            stderr="",
            duration_seconds=1.0,
            tests_run=5,
            tests_passed=5,
        )

    @pytest.fixture
    def failing_validation(self):
        """Create a failing validation result."""
        return ValidationResult(
            passed=False,
            command="pytest",
            exit_code=1,
            stdout="",
            stderr="FAILED test_example.py::test_one",
            duration_seconds=1.0,
            tests_run=5,
            tests_passed=4,
            tests_failed=1,
        )

    @pytest.mark.asyncio
    async def test_already_passing(self, mock_agent, passing_validation):
        """Test TDD loop exits immediately if tests already pass."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = TDDConfig()
            loop = TDDLoop(config, mock_agent, Path(tmpdir))

            result = await loop.run("fix the bug", passing_validation)

            assert result.success is True
            assert len(result.iterations) == 0
            assert result.total_tokens == 0
            # Agent should not have been called
            mock_agent.run_agentic.assert_not_called()

    @pytest.mark.asyncio
    async def test_fix_on_first_iteration(self, mock_agent, failing_validation):
        """Test TDD loop fixes code on first iteration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write a valid Python file so lint passes
            (Path(tmpdir) / "test.py").write_text("x = 1\n")

            config = TDDConfig(lint_before_test=False)
            loop = TDDLoop(config, mock_agent, Path(tmpdir))

            # Mock _run_tests to return passing on second call
            call_count = 0

            async def mock_run_tests():
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    return failing_validation
                return ValidationResult(
                    passed=True,
                    command="pytest",
                    exit_code=0,
                    stdout="OK",
                    stderr="",
                    duration_seconds=1.0,
                )

            loop._run_tests = mock_run_tests

            result = await loop.run("fix the bug", failing_validation)

            assert result.success is True
            assert len(result.iterations) == 1
            mock_agent.run_agentic.assert_called_once()

    @pytest.mark.asyncio
    async def test_max_iterations_exceeded(self, mock_agent, failing_validation):
        """Test TDD loop gives up after max iterations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "test.py").write_text("x = 1\n")

            config = TDDConfig(max_fix_iterations=2, lint_before_test=False)
            loop = TDDLoop(config, mock_agent, Path(tmpdir))

            # Tests always fail
            loop._run_tests = AsyncMock(return_value=failing_validation)

            result = await loop.run("fix the bug", failing_validation)

            assert result.success is False
            assert result.gave_up is True
            assert len(result.iterations) == 2
            assert mock_agent.run_agentic.call_count == 2

    @pytest.mark.asyncio
    async def test_lint_errors_trigger_fix(self, mock_agent, failing_validation):
        """Test that lint errors are fed back to agent for fixing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write invalid Python to trigger lint error
            bad_file = Path(tmpdir) / "broken.py"
            bad_file.write_text("def broken(\n")  # Syntax error

            config = TDDConfig(lint_before_test=True, max_fix_iterations=1)
            loop = TDDLoop(config, mock_agent, Path(tmpdir))

            # After agent "fixes" the code, write valid Python
            async def fix_side_effect(*args, **kwargs):
                bad_file.write_text("def fixed(): pass\n")

                @dataclass
                class MockResponse:
                    content: str = "Fixed syntax"
                    token_usage: int = 100

                    @property
                    def summary(self):
                        return self.content

                return MockResponse()

            mock_agent.run_agentic.side_effect = fix_side_effect

            # Tests pass after fix
            loop._run_tests = AsyncMock(
                return_value=ValidationResult(
                    passed=True,
                    command="pytest",
                    exit_code=0,
                    stdout="OK",
                    stderr="",
                    duration_seconds=1.0,
                )
            )

            await loop.run("fix the bug", failing_validation)

            # Agent should have been called for lint fix
            assert mock_agent.run_agentic.called
            # Check prompt mentioned syntax/lint
            call_args = mock_agent.run_agentic.call_args
            assert (
                "syntax" in call_args.kwargs.get("task", "").lower()
                or "lint" in call_args.kwargs.get("task", "").lower()
            )


class TestRunTDDLoop:
    """Tests for the run_tdd_loop convenience function."""

    @pytest.mark.asyncio
    async def test_convenience_function(self):
        """Test run_tdd_loop creates and runs a TDDLoop."""
        mock_agent = MagicMock()
        mock_agent.name = "agent"

        @dataclass
        class MockResponse:
            content: str = "fixed"
            token_usage: int = 50

            @property
            def summary(self):
                return self.content

        mock_agent.run_agentic = AsyncMock(return_value=MockResponse())

        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "test.py").write_text("x = 1\n")

            passing = ValidationResult(
                passed=True,
                command="pytest",
                exit_code=0,
                stdout="OK",
                stderr="",
                duration_seconds=1.0,
            )

            result = await run_tdd_loop(
                agent=mock_agent,
                working_dir=Path(tmpdir),
                task="fix bug",
                initial_validation=passing,
            )

            assert result.success is True
            assert isinstance(result, TDDLoopResult)

    @pytest.mark.asyncio
    async def test_convenience_function_with_config(self):
        """Test run_tdd_loop accepts custom config."""
        mock_agent = MagicMock()
        mock_agent.name = "agent"

        @dataclass
        class MockResponse:
            content: str = "fixed"
            token_usage: int = 50

            @property
            def summary(self):
                return self.content

        mock_agent.run_agentic = AsyncMock(return_value=MockResponse())

        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "test.py").write_text("x = 1\n")

            passing = ValidationResult(
                passed=True,
                command="pytest",
                exit_code=0,
                stdout="OK",
                stderr="",
                duration_seconds=1.0,
            )

            custom_config = TDDConfig(max_fix_iterations=5)

            result = await run_tdd_loop(
                agent=mock_agent,
                working_dir=Path(tmpdir),
                task="fix bug",
                config=custom_config,
                initial_validation=passing,
            )

            assert result.success is True


class TestTDDPromptBuilding:
    """Tests for TDD prompt building methods."""

    @pytest.fixture
    def tdd_loop(self):
        """Create a TDDLoop instance for testing prompts."""
        mock_agent = MagicMock()
        mock_agent.name = "test-agent"
        config = TDDConfig(max_fix_iterations=3)
        return TDDLoop(config, mock_agent, Path("/tmp"))

    def test_lint_fix_prompt_structure(self, tdd_loop):
        """Test lint fix prompt contains required sections."""
        lint_result = LintResult(
            passed=False,
            command="python -m py_compile test.py",
            exit_code=1,
            errors=["SyntaxError: invalid syntax"],
            warnings=[],
            stdout="",
            stderr="File test.py, line 5: SyntaxError",
        )

        prompt = tdd_loop._build_lint_fix_prompt(
            task="implement feature X",
            lint_result=lint_result,
            iteration=1,
        )

        assert "URGENT" in prompt or "Syntax" in prompt
        assert "Original Task" in prompt
        assert "implement feature X" in prompt
        assert "Lint Errors" in prompt
        assert "Iteration 1/3" in prompt
        assert "SyntaxError" in prompt

    def test_test_fix_prompt_structure(self, tdd_loop):
        """Test test fix prompt contains required sections."""
        validation = ValidationResult(
            passed=False,
            command="pytest tests/",
            exit_code=1,
            stdout="",
            stderr="FAILED test_example::test_add - AssertionError",
            duration_seconds=2.0,
            tests_run=5,
            tests_failed=1,
        )

        prompt = tdd_loop._build_test_fix_prompt(
            task="implement add function",
            validation=validation,
            lint_result=None,
            iteration=2,
        )

        assert "Failing Tests" in prompt
        assert "Iteration 2/3" in prompt
        assert "Original Task" in prompt
        assert "implement add function" in prompt
        assert "Test Results" in prompt
        assert "pytest" in prompt

    def test_test_fix_prompt_includes_lint_warnings(self, tdd_loop):
        """Test that lint warnings are included in test fix prompt."""
        validation = ValidationResult(
            passed=False,
            command="pytest",
            exit_code=1,
            stdout="",
            stderr="FAILED",
            duration_seconds=1.0,
        )
        lint_result = LintResult(
            passed=True,
            command="ruff",
            exit_code=0,
            errors=[],
            warnings=["W001: unused import", "W002: line too long"],
            stdout="",
            stderr="",
        )

        prompt = tdd_loop._build_test_fix_prompt(
            task="fix tests",
            validation=validation,
            lint_result=lint_result,
            iteration=1,
        )

        assert "Lint Warnings" in prompt
        assert "unused import" in prompt


# =============================================================================
# TDD Loop Integration Tests - Retry Logic
# =============================================================================


class TestTDDLoopRetryBehavior:
    """Integration tests for TDD loop retry behavior.

    These tests verify the loop correctly handles scenarios where
    the agent fails multiple times before succeeding.
    """

    @pytest.fixture
    def mock_response_factory(self):
        """Factory for creating mock agent responses."""

        @dataclass
        class MockResponse:
            content: str
            token_usage: int

            @property
            def summary(self):
                return self.content

        def factory(content: str = "Fixed the code", tokens: int = 100):
            return MockResponse(content=content, token_usage=tokens)

        return factory

    @pytest.fixture
    def failing_validation(self):
        """Create a failing validation result."""
        return ValidationResult(
            passed=False,
            command="pytest",
            exit_code=1,
            stdout="",
            stderr="FAILED test_example.py::test_one - AssertionError",
            duration_seconds=1.0,
            tests_run=5,
            tests_passed=4,
            tests_failed=1,
        )

    @pytest.fixture
    def passing_validation(self):
        """Create a passing validation result."""
        return ValidationResult(
            passed=True,
            command="pytest",
            exit_code=0,
            stdout="5 passed in 1.2s",
            stderr="",
            duration_seconds=1.2,
            tests_run=5,
            tests_passed=5,
        )

    @pytest.mark.asyncio
    async def test_succeeds_on_third_attempt(
        self,
        mock_response_factory,
        failing_validation,
        passing_validation,
    ):
        """Test TDD loop succeeds after agent fails 2 times and succeeds on 3rd.

        This verifies:
        1. Loop continues retrying after failures
        2. Loop terminates immediately upon success
        3. Correct number of iterations recorded
        """
        mock_agent = MagicMock()
        mock_agent.name = "test-agent"
        mock_agent.estimate_cost = MagicMock(return_value=0.001)

        # Track calls to verify retry behavior
        fix_attempts = []

        async def mock_run_agentic(task: str, **kwargs):
            fix_attempts.append(task)
            return mock_response_factory(
                content=f"Fix attempt {len(fix_attempts)}",
                tokens=100 * len(fix_attempts),  # Increasing token usage
            )

        mock_agent.run_agentic = mock_run_agentic

        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "test.py").write_text("x = 1\n")

            config = TDDConfig(max_fix_iterations=5, lint_before_test=False)
            loop = TDDLoop(config, mock_agent, Path(tmpdir))

            # Mock _run_tests to fail twice, then pass
            test_call_count = 0

            async def mock_run_tests():
                nonlocal test_call_count
                test_call_count += 1
                if test_call_count <= 2:
                    return failing_validation
                return passing_validation

            loop._run_tests = mock_run_tests

            result = await loop.run("fix the flaky test", failing_validation)

            # Verify success after exactly 2 failed iterations
            assert result.success is True
            assert result.gave_up is False
            assert len(result.iterations) == 2  # 2 failed attempts recorded
            assert len(fix_attempts) == 2  # Agent called twice

            # Verify token tracking: 100 + 200 = 300
            assert result.total_tokens == 300

            # Verify iterations contain correct data
            assert result.iterations[0].iteration_num == 1
            assert result.iterations[0].tokens_used == 100
            assert "Fix attempt 1" in result.iterations[0].agent_response

            assert result.iterations[1].iteration_num == 2
            assert result.iterations[1].tokens_used == 200
            assert "Fix attempt 2" in result.iterations[1].agent_response

    @pytest.mark.asyncio
    async def test_budget_tracking_across_iterations(
        self,
        mock_response_factory,
        failing_validation,
        passing_validation,
    ):
        """Test that budget tracker correctly records all iteration costs.

        This verifies budget tracking accumulates across multiple fix attempts.
        """
        from deliberate.budget.tracker import BudgetTracker

        mock_agent = MagicMock()
        mock_agent.name = "fix-agent"
        mock_agent.estimate_cost = MagicMock(side_effect=lambda t: t * 0.00001)

        call_count = 0

        async def mock_run_agentic(task: str, **kwargs):
            nonlocal call_count
            call_count += 1
            return mock_response_factory(
                content=f"Attempt {call_count}",
                tokens=500,  # Fixed 500 tokens per call
            )

        mock_agent.run_agentic = mock_run_agentic

        budget = BudgetTracker(
            max_total_tokens=100000,
            max_cost_usd=10.0,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "code.py").write_text("pass\n")

            config = TDDConfig(max_fix_iterations=5, lint_before_test=False)
            loop = TDDLoop(config, mock_agent, Path(tmpdir), budget_tracker=budget)

            # Fail 3 times, pass on 4th
            test_calls = 0

            async def mock_run_tests():
                nonlocal test_calls
                test_calls += 1
                if test_calls <= 3:
                    return failing_validation
                return passing_validation

            loop._run_tests = mock_run_tests

            result = await loop.run("fix the bug", failing_validation)

            assert result.success is True
            assert len(result.iterations) == 3  # 3 failed attempts

            # Verify budget tracker recorded all calls
            totals = budget.get_totals()
            assert totals["tokens"] == 1500  # 3 * 500

            # Verify phase tracking
            phase_usage = budget.get_phase_usage("tdd_fix")
            assert phase_usage.tokens == 1500

    @pytest.mark.asyncio
    async def test_loop_terminates_at_max_iterations_even_with_failures(
        self,
        mock_response_factory,
        failing_validation,
    ):
        """Test loop terminates at max_fix_iterations even if still failing.

        This verifies the loop doesn't run forever when fixes never work.
        """
        mock_agent = MagicMock()
        mock_agent.name = "stubborn-agent"
        mock_agent.estimate_cost = MagicMock(return_value=0.001)

        attempt_count = 0

        async def mock_run_agentic(task: str, **kwargs):
            nonlocal attempt_count
            attempt_count += 1
            return mock_response_factory(content=f"Try {attempt_count}", tokens=100)

        mock_agent.run_agentic = mock_run_agentic

        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "test.py").write_text("x = 1\n")

            # Set max iterations to exactly 3
            config = TDDConfig(max_fix_iterations=3, lint_before_test=False)
            loop = TDDLoop(config, mock_agent, Path(tmpdir))

            # Tests always fail
            loop._run_tests = AsyncMock(return_value=failing_validation)

            result = await loop.run("impossible fix", failing_validation)

            # Verify we gave up after exactly 3 attempts
            assert result.success is False
            assert result.gave_up is True
            assert len(result.iterations) == 3
            assert attempt_count == 3  # Agent called exactly 3 times

            # Verify final validation was run
            assert result.final_validation is not None
            assert result.final_validation.passed is False

    @pytest.mark.asyncio
    async def test_iteration_records_contain_validation_results(
        self,
        mock_response_factory,
        failing_validation,
        passing_validation,
    ):
        """Test each iteration record contains the validation result."""
        mock_agent = MagicMock()
        mock_agent.name = "test-agent"
        mock_agent.estimate_cost = MagicMock(return_value=0.001)
        mock_agent.run_agentic = AsyncMock(return_value=mock_response_factory("fixed", 100))

        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "test.py").write_text("x = 1\n")

            config = TDDConfig(max_fix_iterations=3, lint_before_test=False)
            loop = TDDLoop(config, mock_agent, Path(tmpdir))

            # Create different failing validations to track
            call_count = 0

            async def mock_run_tests():
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    return ValidationResult(
                        passed=False,
                        command="pytest",
                        exit_code=1,
                        stdout="",
                        stderr="FAILED test_a - error 1",
                        duration_seconds=1.0,
                        tests_failed=1,
                    )
                if call_count == 2:
                    return ValidationResult(
                        passed=False,
                        command="pytest",
                        exit_code=1,
                        stdout="",
                        stderr="FAILED test_b - error 2",
                        duration_seconds=1.0,
                        tests_failed=1,
                    )
                return passing_validation

            loop._run_tests = mock_run_tests

            result = await loop.run("fix tests", failing_validation)

            assert result.success is True
            assert len(result.iterations) == 2

            # Each iteration should have its validation result
            assert result.iterations[0].validation_result is not None
            assert "error 1" in result.iterations[0].validation_result.stderr

            assert result.iterations[1].validation_result is not None
            assert "error 2" in result.iterations[1].validation_result.stderr

    @pytest.mark.asyncio
    async def test_duration_tracked_per_iteration(
        self,
        mock_response_factory,
        failing_validation,
        passing_validation,
    ):
        """Test each iteration records its own duration."""
        mock_agent = MagicMock()
        mock_agent.name = "test-agent"
        mock_agent.estimate_cost = MagicMock(return_value=0.001)

        # Add a small delay to ensure measurable duration
        async def slow_run_agentic(task: str, **kwargs):
            await asyncio.sleep(0.01)  # 10ms delay
            return mock_response_factory("fixed", 100)

        mock_agent.run_agentic = slow_run_agentic

        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "test.py").write_text("x = 1\n")

            config = TDDConfig(max_fix_iterations=3, lint_before_test=False)
            loop = TDDLoop(config, mock_agent, Path(tmpdir))

            test_count = 0

            async def mock_run_tests():
                nonlocal test_count
                test_count += 1
                return passing_validation if test_count > 1 else failing_validation

            loop._run_tests = mock_run_tests

            result = await loop.run("fix it", failing_validation)

            assert result.success is True
            assert len(result.iterations) == 1

            # Duration should be at least the artificial delay
            assert result.iterations[0].duration_seconds >= 0.01
            assert result.total_duration > 0
