"""Unit tests for the validation subsystem."""

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from deliberate.validation import (
    TestCaseResult,
    TestStatus,
    ValidationResult,
    ValidationRunner,
    detect_project_type,
    detect_test_command,
)


class TestTestCommandDetection:
    """Tests for test command detection."""

    def test_detect_python_pytest(self, tmp_path: Path):
        """Should detect pytest for Python project."""
        (tmp_path / "pyproject.toml").write_text("[tool.pytest.ini_options]")
        cmd = detect_test_command(tmp_path)
        assert cmd is not None
        assert "pytest" in cmd

    def test_detect_python_with_uv(self, tmp_path: Path):
        """Should use uv run for project with uv.lock."""
        (tmp_path / "pyproject.toml").write_text("[project]")
        (tmp_path / "uv.lock").write_text("")
        cmd = detect_test_command(tmp_path)
        assert cmd == "uv run pytest"

    def test_detect_rust_cargo(self, tmp_path: Path):
        """Should detect cargo test for Rust project."""
        (tmp_path / "Cargo.toml").write_text("[package]")
        cmd = detect_test_command(tmp_path)
        assert cmd == "cargo test"

    def test_detect_go(self, tmp_path: Path):
        """Should detect go test for Go project."""
        (tmp_path / "go.mod").write_text("module example.com/foo")
        cmd = detect_test_command(tmp_path)
        assert cmd == "go test ./..."

    def test_detect_node_npm(self, tmp_path: Path):
        """Should detect npm test for Node project."""
        (tmp_path / "package.json").write_text('{"scripts": {"test": "jest"}}')
        cmd = detect_test_command(tmp_path)
        assert cmd == "npm test"

    def test_detect_node_yarn(self, tmp_path: Path):
        """Should use yarn for project with yarn.lock."""
        (tmp_path / "package.json").write_text('{"scripts": {"test": "jest"}}')
        (tmp_path / "yarn.lock").write_text("")
        cmd = detect_test_command(tmp_path)
        assert cmd == "yarn test"

    def test_detect_makefile(self, tmp_path: Path):
        """Should detect make test from Makefile."""
        (tmp_path / "Makefile").write_text("test:\n\tpytest")
        cmd = detect_test_command(tmp_path)
        assert cmd == "make test"

    def test_detect_nothing(self, tmp_path: Path):
        """Should return None when no test framework detected."""
        cmd = detect_test_command(tmp_path)
        assert cmd is None

    def test_detect_node_test_unit(self, tmp_path: Path):
        """Should detect npm run test:unit for custom test script."""
        (tmp_path / "package.json").write_text('{"scripts": {"test:unit": "jest --coverage"}}')
        cmd = detect_test_command(tmp_path)
        assert cmd == "npm run test:unit"

    def test_detect_node_skips_placeholder(self, tmp_path: Path):
        """Should skip placeholder test scripts."""
        (tmp_path / "package.json").write_text('{"scripts": {"test": "echo \\"no tests\\""}}')
        cmd = detect_test_command(tmp_path)
        assert cmd is None

    def test_detect_rust_workspace(self, tmp_path: Path):
        """Should detect cargo test --workspace for Rust workspace."""
        (tmp_path / "Cargo.toml").write_text("[workspace]\nmembers = ['crate1']")
        cmd = detect_test_command(tmp_path)
        assert cmd == "cargo test --workspace"

    def test_detect_makefile_check_target(self, tmp_path: Path):
        """Should detect make check target."""
        (tmp_path / "Makefile").write_text("check:\n\tpytest")
        cmd = detect_test_command(tmp_path)
        assert cmd == "make check"

    def test_detect_from_ci_workflow(self, tmp_path: Path):
        """Should extract test command from GitHub Actions workflow."""
        workflows = tmp_path / ".github" / "workflows"
        workflows.mkdir(parents=True)
        (workflows / "test.yml").write_text("jobs:\n  test:\n    steps:\n      - run: uv run pytest tests/")
        cmd = detect_test_command(tmp_path)
        assert cmd == "uv run pytest tests/"


class TestProjectTypeDetection:
    """Tests for project type detection."""

    def test_detect_python(self, tmp_path: Path):
        """Should detect Python project."""
        (tmp_path / "pyproject.toml").write_text("")
        assert detect_project_type(tmp_path) == "python"

    def test_detect_rust(self, tmp_path: Path):
        """Should detect Rust project."""
        (tmp_path / "Cargo.toml").write_text("")
        assert detect_project_type(tmp_path) == "rust"

    def test_detect_node(self, tmp_path: Path):
        """Should detect Node project."""
        (tmp_path / "package.json").write_text("{}")
        assert detect_project_type(tmp_path) == "node"

    def test_detect_go(self, tmp_path: Path):
        """Should detect Go project."""
        (tmp_path / "go.mod").write_text("")
        assert detect_project_type(tmp_path) == "go"

    def test_detect_unknown(self, tmp_path: Path):
        """Should return None for unknown project."""
        assert detect_project_type(tmp_path) is None


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_summary_passed(self):
        """Should generate passed summary."""
        result = ValidationResult(
            passed=True,
            command="pytest",
            exit_code=0,
            stdout="",
            stderr="",
            duration_seconds=1.5,
            tests_run=10,
            tests_passed=10,
            tests_failed=0,
        )
        assert "PASSED" in result.summary
        assert "10/10" in result.summary

    def test_summary_failed(self):
        """Should generate failed summary."""
        result = ValidationResult(
            passed=False,
            command="pytest",
            exit_code=1,
            stdout="",
            stderr="",
            duration_seconds=1.5,
            tests_run=10,
            tests_passed=7,
            tests_failed=3,
        )
        assert "FAILED" in result.summary
        assert "7/10" in result.summary
        assert "3 failed" in result.summary

    def test_summary_error(self):
        """Should show error in summary."""
        result = ValidationResult(
            passed=False,
            command="pytest",
            exit_code=-1,
            stdout="",
            stderr="",
            duration_seconds=0.0,
            error="Command not found",
        )
        assert "Error" in result.summary
        assert "Command not found" in result.summary

    def test_summary_regression(self):
        """Should show regression in summary."""
        result = ValidationResult(
            passed=False,
            command="pytest",
            exit_code=1,
            stdout="",
            stderr="",
            duration_seconds=1.0,
            regression_detected=True,
        )
        assert "REGRESSION" in result.summary

    def test_failure_log_with_test_cases(self):
        """Should include failed test cases in failure log."""
        result = ValidationResult(
            passed=False,
            command="pytest",
            exit_code=1,
            stdout="",
            stderr="",
            duration_seconds=1.0,
            test_cases=[
                TestCaseResult(
                    name="test_foo",
                    status=TestStatus.FAILED,
                    message="AssertionError: expected 1, got 2",
                ),
                TestCaseResult(
                    name="test_bar",
                    status=TestStatus.PASSED,
                ),
            ],
        )
        log = result.failure_log
        assert "test_foo" in log
        assert "AssertionError" in log
        assert "test_bar" not in log  # Passed tests not included

    def test_failure_log_empty_when_passed(self):
        """Should return empty failure log when passed."""
        result = ValidationResult(
            passed=True,
            command="pytest",
            exit_code=0,
            stdout="",
            stderr="",
            duration_seconds=1.0,
        )
        assert result.failure_log == ""

    def test_to_dict(self):
        """Should serialize to dict correctly."""
        result = ValidationResult(
            passed=True,
            command="pytest",
            exit_code=0,
            stdout="output",
            stderr="",
            duration_seconds=1.5,
            tests_run=5,
            tests_passed=5,
            tests_failed=0,
        )
        d = result.to_dict()
        assert d["passed"] is True
        assert d["command"] == "pytest"
        assert d["tests_run"] == 5
        assert "summary" in d

    def test_correctness_passed_property(self):
        """Should return True only when passed and no regression."""
        # Passed with no regression
        result = ValidationResult(
            passed=True,
            command="pytest",
            exit_code=0,
            stdout="",
            stderr="",
            duration_seconds=1.0,
        )
        assert result.correctness_passed is True

        # Failed but no regression
        result.passed = False
        assert result.correctness_passed is False

        # Passed but regression detected
        result.passed = True
        result.regression_detected = True
        assert result.correctness_passed is False

    def test_is_slow_property(self):
        """Should return True for slow execution or timeout."""
        from deliberate.validation.types import PerformanceIssue

        result = ValidationResult(
            passed=True,
            command="pytest",
            exit_code=0,
            stdout="",
            stderr="",
            duration_seconds=1.0,
        )
        assert result.is_slow is False

        result.performance_issue = PerformanceIssue.SLOW_EXECUTION
        assert result.is_slow is True

        result.performance_issue = PerformanceIssue.TIMEOUT
        assert result.is_slow is True

        result.performance_issue = PerformanceIssue.HIGH_MEMORY
        assert result.is_slow is False

        result.performance_issue = PerformanceIssue.FLAKY
        assert result.is_slow is False

    def test_summary_with_needs_optimization(self):
        """Should include optimization info in summary."""
        from deliberate.validation.types import PerformanceIssue

        result = ValidationResult(
            passed=True,
            command="pytest",
            exit_code=0,
            stdout="",
            stderr="",
            duration_seconds=5.0,
            tests_run=10,
            tests_passed=10,
            needs_optimization=True,
            performance_issue=PerformanceIssue.SLOW_EXECUTION,
        )
        assert "NEEDS_OPTIMIZATION" in result.summary
        assert "slow_execution" in result.summary

    def test_to_dict_includes_performance_fields(self):
        """Should include performance fields in serialization."""
        from deliberate.validation.types import PerformanceIssue

        result = ValidationResult(
            passed=True,
            command="pytest",
            exit_code=0,
            stdout="",
            stderr="",
            duration_seconds=1.5,
            performance_issue=PerformanceIssue.HIGH_MEMORY,
            needs_optimization=True,
            slowest_tests=[("test_slow", 2.5), ("test_slower", 3.0)],
        )
        d = result.to_dict()
        assert d["performance_issue"] == "high_memory"
        assert d["needs_optimization"] is True
        assert d["correctness_passed"] is True
        assert d["is_slow"] is False
        assert d["slowest_tests"] == [("test_slow", 2.5), ("test_slower", 3.0)]


class TestValidationRunner:
    """Tests for ValidationRunner."""

    @pytest.mark.asyncio
    async def test_run_no_command(self, tmp_path: Path):
        """Should return vacuous pass when no command."""
        runner = ValidationRunner(tmp_path, command=None)
        result = await runner.run()
        assert result.passed is True
        assert result.tests_run == 0

    @pytest.mark.asyncio
    async def test_run_no_command_when_required(self, tmp_path: Path):
        """If tests are required, missing command should fail."""
        runner = ValidationRunner(tmp_path, command=None, require_tests=True)
        result = await runner.run()
        assert result.passed is False
        assert result.error == "No tests detected"

    @pytest.mark.asyncio
    async def test_run_successful_command(self, tmp_path: Path):
        """Should parse successful test run."""
        runner = ValidationRunner(tmp_path, command="echo 'tests passed'")
        result = await runner.run()
        assert result.passed is True
        assert result.exit_code == 0

    @pytest.mark.asyncio
    async def test_run_failing_command(self, tmp_path: Path):
        """Should report failure for non-zero exit code."""
        runner = ValidationRunner(tmp_path, command="exit 1")
        result = await runner.run()
        assert result.passed is False
        assert result.exit_code == 1

    @pytest.mark.asyncio
    async def test_run_timeout(self, tmp_path: Path):
        """Should handle timeout."""
        runner = ValidationRunner(tmp_path, command="sleep 10", timeout_seconds=1)
        result = await runner.run()
        assert result.passed is False
        assert result.error == "Timeout"

    @pytest.mark.asyncio
    async def test_run_missing_command(self, tmp_path: Path):
        """Should handle missing command."""
        runner = ValidationRunner(tmp_path, command="nonexistent_command_xyz")
        result = await runner.run()
        assert result.passed is False
        # Either error or exit code should indicate failure
        assert result.exit_code != 0 or result.error is not None


class TestValidationRunnerParsing:
    """Tests for test output parsing."""

    def test_parse_pytest_method(self):
        """Test the pytest parser directly."""
        runner = ValidationRunner(Path("."), "pytest")
        parsed = runner._parse_pytest(
            stdout="collected 7 items\n... 5 passed, 2 failed in 1.23s",
            stderr="",
        )
        assert parsed["tests_passed"] == 5
        assert parsed["tests_failed"] == 2
        assert parsed["tests_run"] == 7

    def test_parse_cargo_test_method(self):
        """Test the cargo test parser directly."""
        runner = ValidationRunner(Path("."), "cargo test")
        parsed = runner._parse_cargo_test(
            stdout="test result: ok. 10 passed; 2 failed; 1 ignored",
            stderr="",
        )
        assert parsed["tests_passed"] == 10
        assert parsed["tests_failed"] == 2
        assert parsed["tests_skipped"] == 1
        assert parsed["tests_run"] == 13

    def test_parse_generic_counts_patterns(self):
        """Test the generic parser counts pass/fail patterns."""
        runner = ValidationRunner(Path("."), "unknown_runner")
        parsed = runner._parse_generic(
            stdout="test1 passed\ntest2 passed\ntest3 failed",
            stderr="",
        )
        assert parsed["tests_passed"] == 2
        assert parsed["tests_failed"] == 1

    @pytest.mark.asyncio
    async def test_run_returns_parsed_results(self, tmp_path: Path):
        """Verify parser is called and results are populated."""
        runner = ValidationRunner(tmp_path, command="echo 'test output'")
        result = await runner.run()
        assert result.stdout == "test output\n"
        assert result.exit_code == 0


class TestIsCommandNotFound:
    """Tests for _is_command_not_found helper."""

    def test_exit_code_127(self):
        """Should detect command not found from exit code 127."""
        from deliberate.validation.runner import _is_command_not_found

        result = ValidationResult(
            passed=False,
            command="nonexistent",
            exit_code=127,
            stdout="",
            stderr="bash: nonexistent: command not found",
            duration_seconds=0.1,
        )
        assert _is_command_not_found(result) is True

    def test_exit_code_126(self):
        """Should detect not executable from exit code 126."""
        from deliberate.validation.runner import _is_command_not_found

        result = ValidationResult(
            passed=False,
            command="./script.sh",
            exit_code=126,
            stdout="",
            stderr="bash: ./script.sh: Permission denied",
            duration_seconds=0.1,
        )
        assert _is_command_not_found(result) is True

    def test_command_not_found_in_stderr(self):
        """Should detect from error message even with other exit code."""
        from deliberate.validation.runner import _is_command_not_found

        result = ValidationResult(
            passed=False,
            command="pytest",
            exit_code=1,
            stdout="",
            stderr="pytest: command not found",
            duration_seconds=0.1,
        )
        assert _is_command_not_found(result) is True

    def test_normal_failure(self):
        """Should return False for normal test failures."""
        from deliberate.validation.runner import _is_command_not_found

        result = ValidationResult(
            passed=False,
            command="pytest",
            exit_code=1,
            stdout="FAILED tests/test_foo.py::test_one",
            stderr="",
            duration_seconds=1.0,
            tests_failed=1,
        )
        assert _is_command_not_found(result) is False

    def test_success(self):
        """Should return False for successful runs."""
        from deliberate.validation.runner import _is_command_not_found

        result = ValidationResult(
            passed=True,
            command="pytest",
            exit_code=0,
            stdout="All tests passed",
            stderr="",
            duration_seconds=1.0,
        )
        assert _is_command_not_found(result) is False


class TestRunValidationWithFallback:
    """Tests for run_validation_with_fallback function."""

    @pytest.mark.asyncio
    async def test_success_without_fallback(self, tmp_path: Path):
        """Should work normally when command succeeds."""
        from deliberate.validation.runner import run_validation_with_fallback

        # Create a passing test command
        result = await run_validation_with_fallback(
            tmp_path,
            adapter=None,  # No adapter needed for success
            command="echo 'tests pass'",
        )

        assert result.passed is True
        assert result.exit_code == 0

    @pytest.mark.asyncio
    async def test_fallback_not_triggered_on_normal_failure(self, tmp_path: Path):
        """Should not trigger fallback on normal test failure."""
        from deliberate.validation.runner import run_validation_with_fallback

        mock_adapter = AsyncMock()

        result = await run_validation_with_fallback(
            tmp_path,
            adapter=mock_adapter,
            command="exit 1",  # Normal failure, not command-not-found
        )

        assert result.passed is False
        assert result.exit_code == 1
        # Adapter should not have been used
        mock_adapter.assert_not_called()

    @pytest.mark.asyncio
    async def test_fallback_triggered_on_127(self, tmp_path: Path):
        """Should trigger LLM fallback on exit code 127."""
        from deliberate.validation.runner import run_validation_with_fallback

        # Mock the detect_test_command_llm function at the source module
        with patch("deliberate.validation.analyzer.detect_test_command_llm") as mock_detect:
            # LLM suggests a working command
            mock_detect.return_value = "echo 'llm detected'"

            mock_adapter = AsyncMock()

            result = await run_validation_with_fallback(
                tmp_path,
                adapter=mock_adapter,
                command="nonexistent_command_xyz_127",
            )

            # Should have called LLM detection
            mock_detect.assert_called_once()

            # Result should be from the retry with LLM command
            assert result.passed is True
            assert "llm detected" in result.stdout

    @pytest.mark.asyncio
    async def test_no_fallback_when_adapter_is_none(self, tmp_path: Path):
        """Should not attempt fallback when adapter is None."""
        from deliberate.validation.runner import run_validation_with_fallback

        with patch("deliberate.validation.analyzer.detect_test_command_llm") as mock_detect:
            result = await run_validation_with_fallback(
                tmp_path,
                adapter=None,  # No adapter
                command="nonexistent_command_xyz_127",
            )

            # Should not have called LLM detection
            mock_detect.assert_not_called()

            # Result should be the original failure
            assert result.passed is False

    @pytest.mark.asyncio
    async def test_fallback_handles_llm_exception(self, tmp_path: Path):
        """Should handle LLM detection exceptions gracefully."""
        from deliberate.validation.runner import run_validation_with_fallback

        with patch("deliberate.validation.analyzer.detect_test_command_llm") as mock_detect:
            mock_detect.side_effect = RuntimeError("LLM API error")

            mock_adapter = AsyncMock()

            result = await run_validation_with_fallback(
                tmp_path,
                adapter=mock_adapter,
                command="nonexistent_command_xyz_127",
            )

            # Should return original failure, not crash
            assert result.passed is False
            assert result.exit_code != 0

    @pytest.mark.asyncio
    async def test_fallback_skipped_when_llm_returns_same_command(self, tmp_path: Path):
        """Should not retry if LLM returns the same command."""
        from deliberate.validation.runner import run_validation_with_fallback

        with patch("deliberate.validation.analyzer.detect_test_command_llm") as mock_detect:
            # LLM returns the same failing command
            mock_detect.return_value = "nonexistent_command_xyz_127"

            mock_adapter = AsyncMock()

            result = await run_validation_with_fallback(
                tmp_path,
                adapter=mock_adapter,
                command="nonexistent_command_xyz_127",
            )

            mock_detect.assert_called_once()

            # Should not have retried, just return original failure
            assert result.passed is False

    @pytest.mark.asyncio
    async def test_fallback_skipped_when_llm_returns_none(self, tmp_path: Path):
        """Should not retry if LLM returns None."""
        from deliberate.validation.runner import run_validation_with_fallback

        with patch("deliberate.validation.analyzer.detect_test_command_llm") as mock_detect:
            mock_detect.return_value = None

            mock_adapter = AsyncMock()

            result = await run_validation_with_fallback(
                tmp_path,
                adapter=mock_adapter,
                command="nonexistent_command_xyz_127",
            )

            mock_detect.assert_called_once()

            # Should return original failure
            assert result.passed is False


class TestValidationRunnerPerformanceAnalysis:
    """Tests for performance analysis in ValidationRunner."""

    def test_analyze_performance_no_thresholds(self):
        """Should skip analysis when no thresholds configured."""
        runner = ValidationRunner(Path("."), command="pytest")

        result = ValidationResult(
            passed=True,
            command="pytest",
            exit_code=0,
            stdout="",
            stderr="",
            duration_seconds=10.0,
        )

        runner._analyze_performance(result)

        assert result.performance_issue.value == "none"
        assert result.needs_optimization is False

    def test_analyze_performance_skips_failed_tests(self):
        """Should skip analysis when tests failed."""
        runner = ValidationRunner(Path("."), command="pytest", latency_threshold_ms=100.0)

        result = ValidationResult(
            passed=False,
            command="pytest",
            exit_code=1,
            stdout="",
            stderr="",
            duration_seconds=10.0,
        )

        runner._analyze_performance(result)

        assert result.performance_issue.value == "none"
        assert result.needs_optimization is False

    def test_analyze_performance_detects_slow_tests(self):
        """Should detect slow tests exceeding threshold."""
        from deliberate.validation.types import CaseResult, CaseStatus, PerformanceIssue

        runner = ValidationRunner(Path("."), command="pytest", latency_threshold_ms=500.0)

        result = ValidationResult(
            passed=True,
            command="pytest",
            exit_code=0,
            stdout="",
            stderr="",
            duration_seconds=5.0,
            test_cases=[
                CaseResult(name="test_fast", status=CaseStatus.PASSED, duration_seconds=0.1),
                CaseResult(name="test_slow", status=CaseStatus.PASSED, duration_seconds=2.0),
                CaseResult(name="test_very_slow", status=CaseStatus.PASSED, duration_seconds=5.0),
            ],
        )

        runner._analyze_performance(result)

        assert result.performance_issue == PerformanceIssue.SLOW_EXECUTION
        assert result.needs_optimization is True
        assert len(result.slowest_tests) == 3
        assert result.slowest_tests[0][0] == "test_very_slow"

    def test_analyze_performance_benchmark_tests_prioritized(self):
        """Should apply threshold only to benchmark tests when present."""
        from deliberate.validation.types import CaseResult, CaseStatus, PerformanceIssue

        runner = ValidationRunner(Path("."), command="pytest", latency_threshold_ms=500.0)

        # Regular tests are slow, but benchmark tests are fast
        # Note: avoid using 'slow' in regular test names since that's a benchmark pattern
        result = ValidationResult(
            passed=True,
            command="pytest",
            exit_code=0,
            stdout="",
            stderr="",
            duration_seconds=5.0,
            test_cases=[
                CaseResult(
                    name="test_regular_long_running",
                    status=CaseStatus.PASSED,
                    duration_seconds=2.0,
                ),
                CaseResult(
                    name="test_benchmark_fast",
                    status=CaseStatus.PASSED,
                    duration_seconds=0.1,
                ),
            ],
        )

        runner._analyze_performance(result)

        # Should not flag because benchmark test is fast
        assert result.performance_issue == PerformanceIssue.NONE
        assert result.needs_optimization is False

    def test_analyze_performance_slow_benchmark_test(self):
        """Should flag when benchmark tests are slow."""
        from deliberate.validation.types import CaseResult, CaseStatus, PerformanceIssue

        runner = ValidationRunner(Path("."), command="pytest", latency_threshold_ms=500.0)

        result = ValidationResult(
            passed=True,
            command="pytest",
            exit_code=0,
            stdout="",
            stderr="",
            duration_seconds=5.0,
            test_cases=[
                CaseResult(name="test_regular_slow", status=CaseStatus.PASSED, duration_seconds=2.0),
                CaseResult(
                    name="test_benchmark_slow",
                    status=CaseStatus.PASSED,
                    duration_seconds=1.0,
                ),
            ],
        )

        runner._analyze_performance(result)

        # Should flag because benchmark test exceeds threshold
        assert result.performance_issue == PerformanceIssue.SLOW_EXECUTION
        assert result.needs_optimization is True

    def test_analyze_performance_no_individual_timings(self):
        """Should warn but not flag when no individual test timings available."""
        from deliberate.validation.types import PerformanceIssue

        runner = ValidationRunner(Path("."), command="pytest", latency_threshold_ms=500.0)

        result = ValidationResult(
            passed=True,
            command="pytest",
            exit_code=0,
            stdout="",
            stderr="",
            duration_seconds=10.0,
            test_cases=[],  # No individual test results
        )

        runner._analyze_performance(result)

        # Should NOT flag without granular data
        assert result.performance_issue == PerformanceIssue.NONE
        assert result.needs_optimization is False

    def test_analyze_performance_populates_slowest_tests(self):
        """Should populate slowest_tests sorted by duration."""
        from deliberate.validation.types import CaseResult, CaseStatus

        runner = ValidationRunner(
            Path("."), command="pytest", latency_threshold_ms=10000.0
        )  # High threshold so nothing is flagged

        result = ValidationResult(
            passed=True,
            command="pytest",
            exit_code=0,
            stdout="",
            stderr="",
            duration_seconds=5.0,
            test_cases=[
                CaseResult(name="test_a", status=CaseStatus.PASSED, duration_seconds=0.5),
                CaseResult(name="test_b", status=CaseStatus.PASSED, duration_seconds=1.5),
                CaseResult(name="test_c", status=CaseStatus.PASSED, duration_seconds=0.2),
            ],
        )

        runner._analyze_performance(result)

        # Should be sorted by duration descending
        assert result.slowest_tests[0] == ("test_b", 1.5)
        assert result.slowest_tests[1] == ("test_a", 0.5)
        assert result.slowest_tests[2] == ("test_c", 0.2)

    def test_check_benchmark_tests_patterns(self):
        """Should recognize various benchmark test patterns."""
        from deliberate.validation.types import CaseResult, CaseStatus

        runner = ValidationRunner(Path("."), command="pytest")

        patterns_to_test = [
            "test_benchmark_add",
            "test_performance_critical",
            "test_perf_matrix",
            "test_slow_path",
        ]

        for pattern in patterns_to_test:
            result = ValidationResult(
                passed=True,
                command="pytest",
                exit_code=0,
                stdout="",
                stderr="",
                duration_seconds=1.0,
                test_cases=[
                    CaseResult(name=pattern, status=CaseStatus.PASSED, duration_seconds=1.0),
                ],
            )

            # Should recognize as benchmark test and detect it exceeds threshold
            has_benchmark, exceeds = runner._check_benchmark_tests(result, threshold_seconds=0.5)
            assert has_benchmark is True
            assert exceeds is True

    def test_check_benchmark_tests_returns_tuple(self):
        """Should return correct tuple based on benchmark tests."""
        from deliberate.validation.types import CaseResult, CaseStatus

        runner = ValidationRunner(Path("."), command="pytest")

        # No benchmark tests
        result = ValidationResult(
            passed=True,
            command="pytest",
            exit_code=0,
            stdout="",
            stderr="",
            duration_seconds=1.0,
            test_cases=[
                CaseResult(name="test_regular", status=CaseStatus.PASSED, duration_seconds=1.0),
            ],
        )
        has_benchmark, exceeds = runner._check_benchmark_tests(result, threshold_seconds=0.5)
        assert has_benchmark is False
        assert exceeds is False

        # Benchmark test that's fast
        result.test_cases = [
            CaseResult(name="test_benchmark_fast", status=CaseStatus.PASSED, duration_seconds=0.1),
        ]
        has_benchmark, exceeds = runner._check_benchmark_tests(result, threshold_seconds=0.5)
        assert has_benchmark is True
        assert exceeds is False
