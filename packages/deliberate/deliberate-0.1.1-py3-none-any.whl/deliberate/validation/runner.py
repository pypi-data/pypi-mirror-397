"""Execution logic for running tests."""

import asyncio
import logging
import re
import time
from pathlib import Path
from typing import Optional, TypedDict

from deliberate.config import DevContainerConfig
from deliberate.utils.subprocess_manager import SubprocessManager
from deliberate.validation.devcontainer import (
    DevContainerInfo,
    DevContainerRunner,
    detect_devcontainer,
)
from deliberate.validation.types import (
    CaseResult,
    CaseStatus,
    PerformanceIssue,
    RunArtifacts,
    ValidationResult,
)

logger = logging.getLogger(__name__)


class ParsedTestResult(TypedDict):
    """Parsed test result from command output."""

    tests_run: int
    tests_passed: int
    tests_failed: int
    tests_skipped: int
    test_cases: list[CaseResult]


class ValidationRunner:
    """Runs validation commands in a specific directory.

    Supports running commands either directly on the host or inside a Dev Container
    for isolation.
    """

    def __init__(
        self,
        working_dir: Path,
        command: Optional[str] = None,
        timeout_seconds: int = 300,
        require_tests: bool = False,
        devcontainer_config: Optional[DevContainerConfig] = None,
        latency_threshold_ms: Optional[float] = None,
        memory_threshold_mb: Optional[float] = None,
    ):
        self.working_dir = working_dir
        self.command = command
        self.timeout_seconds = timeout_seconds
        self.require_tests = require_tests
        self.devcontainer_config = devcontainer_config or DevContainerConfig()
        self.latency_threshold_ms = latency_threshold_ms
        self.memory_threshold_mb = memory_threshold_mb

        # DevContainer state
        self._devcontainer_info: Optional[DevContainerInfo] = None
        self._devcontainer_runner: Optional[DevContainerRunner] = None

        # Auto-detect devcontainer if enabled
        if self.devcontainer_config.enabled and self.devcontainer_config.auto_detect:
            self._devcontainer_info = detect_devcontainer(working_dir)
            if self._devcontainer_info:
                logger.info(f"Detected Dev Container: {self._devcontainer_info.name or 'unnamed'}")
                self._devcontainer_runner = DevContainerRunner(
                    self._devcontainer_info,
                    timeout_seconds=timeout_seconds,
                    use_devcontainer_cli=self.devcontainer_config.use_devcontainer_cli,
                )

    async def run(self) -> ValidationResult:
        """Run the validation command.

        Returns:
            ValidationResult with test execution outcome.
        """
        if not self.command:
            passed = not self.require_tests
            return ValidationResult(
                passed=passed,
                command="",
                exit_code=-1 if self.require_tests else 0,
                stdout="",
                stderr="No test command configured or detected.",
                duration_seconds=0.0,
                tests_run=0,
                error="No tests detected" if self.require_tests else None,
            )

        start_time = time.time()

        # Use DevContainer for isolation if available
        if self._devcontainer_runner:
            return await self._run_in_devcontainer(start_time)

        # Otherwise run directly on host
        return await self._run_on_host(start_time)

    async def _run_in_devcontainer(self, start_time: float) -> ValidationResult:
        """Execute validation inside a Dev Container."""
        assert self._devcontainer_runner is not None
        assert self.command is not None

        logger.info(f"Running validation in Dev Container: {self.command}")

        exit_code, stdout, stderr = await self._devcontainer_runner.exec(self.command)
        duration = time.time() - start_time

        if exit_code == -1 and "Failed to start" in stderr:
            return ValidationResult(
                passed=False,
                command=self.command,
                exit_code=exit_code,
                stdout=stdout,
                stderr=stderr,
                duration_seconds=duration,
                error="Dev Container startup failed",
            )

        # Parse output based on command type
        parsed = self._parse_output(stdout, stderr, self.command)

        artifacts = RunArtifacts(
            command=self.command,
            cwd=self.working_dir,
            exit_code=exit_code,
            duration_seconds=duration,
            stdout=stdout,
            stderr=stderr,
        )

        result = ValidationResult(
            passed=(exit_code == 0),
            command=self.command,
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            duration_seconds=duration,
            tests_run=parsed.get("tests_run", 0),
            tests_passed=parsed.get("tests_passed", 0),
            tests_failed=parsed.get("tests_failed", 0),
            tests_skipped=parsed.get("tests_skipped", 0),
            test_cases=parsed.get("test_cases", []),
            artifacts=artifacts,
        )

        # Analyze performance if thresholds configured and tests passed
        self._analyze_performance(result)
        return result

    async def _run_on_host(self, start_time: float) -> ValidationResult:
        """Execute validation directly on the host system."""
        assert self.command is not None

        try:
            result = await SubprocessManager.run(
                ["bash", "-lc", self.command],
                cwd=str(self.working_dir),
                timeout=self.timeout_seconds,
            )
        except asyncio.TimeoutError:
            return ValidationResult(
                passed=False,
                command=self.command,
                exit_code=-1,
                stdout="",
                stderr=f"Timed out after {self.timeout_seconds}s",
                duration_seconds=time.time() - start_time,
                error="Timeout",
            )
        except FileNotFoundError:
            return ValidationResult(
                passed=False,
                command=self.command,
                exit_code=-1,
                stdout="",
                stderr=f"Command not found: {self.command.split()[0]}",
                duration_seconds=time.time() - start_time,
                error="Command not found",
            )
        except Exception as e:
            return ValidationResult(
                passed=False,
                command=self.command,
                exit_code=-1,
                stdout="",
                stderr=str(e),
                duration_seconds=time.time() - start_time,
                error=str(e),
            )

        duration = time.time() - start_time
        stdout = result.stdout.decode("utf-8", errors="replace")
        stderr = result.stderr.decode("utf-8", errors="replace")
        exit_code = result.returncode or 0

        # Parse output based on command type
        parsed = self._parse_output(stdout, stderr, self.command)

        artifacts = RunArtifacts(
            command=self.command,
            cwd=self.working_dir,
            exit_code=exit_code,
            duration_seconds=duration,
            stdout=stdout,
            stderr=stderr,
        )

        result = ValidationResult(
            passed=(exit_code == 0),
            command=self.command,
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            duration_seconds=duration,
            tests_run=parsed.get("tests_run", 0),
            tests_passed=parsed.get("tests_passed", 0),
            tests_failed=parsed.get("tests_failed", 0),
            tests_skipped=parsed.get("tests_skipped", 0),
            test_cases=parsed.get("test_cases", []),
            artifacts=artifacts,
        )

        # Analyze performance if thresholds configured and tests passed
        self._analyze_performance(result)
        return result

    def _analyze_performance(self, result: ValidationResult) -> None:
        """Analyze test performance and flag issues for auto-tuner.

        Checks for:
        - Slow test execution (latency threshold)
        - Timeout during execution
        - Flaky tests (inconsistent results)

        Populates result.performance_issue, result.needs_optimization,
        and result.slowest_tests based on analysis.
        """
        # Skip analysis if not configured or tests failed
        if not result.correctness_passed:
            return

        # Check for timeout (already set by runner)
        if result.error == "Timeout":
            result.performance_issue = PerformanceIssue.TIMEOUT
            result.needs_optimization = True
            return

        # Extract and sort tests by duration
        tests_with_duration = [(tc.name, tc.duration_seconds) for tc in result.test_cases if tc.duration_seconds > 0]
        tests_with_duration.sort(key=lambda x: x[1], reverse=True)
        result.slowest_tests = tests_with_duration[:10]  # Top 10 slowest

        # Check for latency threshold
        if self.latency_threshold_ms is not None:
            threshold_seconds = self.latency_threshold_ms / 1000.0

            # Look for benchmark-marked tests first (pytest markers)
            # If benchmark tests exist, only apply threshold to them
            has_benchmark_tests, benchmark_slow = self._check_benchmark_tests(result, threshold_seconds)

            if benchmark_slow:
                result.performance_issue = PerformanceIssue.SLOW_EXECUTION
                result.needs_optimization = True
                logger.info(f"Benchmark tests exceed threshold: {[t[0] for t in result.slowest_tests[:3]]}")
            elif has_benchmark_tests:
                # Benchmark tests exist but are fast - don't check regular tests
                logger.debug("Benchmark tests within threshold, skipping regular test analysis")
            elif not tests_with_duration:
                # No individual test timings available, check total duration
                if result.duration_seconds > threshold_seconds:
                    logger.warning(
                        f"Total test duration ({result.duration_seconds:.2f}s) "
                        f"exceeds threshold ({threshold_seconds:.2f}s), but no "
                        "individual test timings available. Consider using "
                        "@pytest.mark.benchmark for performance-critical tests."
                    )
                    # Don't flag as needing optimization without granular data
            else:
                # Check if any individual test exceeds threshold
                slow_tests = [(name, dur) for name, dur in tests_with_duration if dur > threshold_seconds]
                if slow_tests:
                    result.performance_issue = PerformanceIssue.SLOW_EXECUTION
                    result.needs_optimization = True
                    logger.info(f"Found {len(slow_tests)} tests exceeding {self.latency_threshold_ms}ms threshold")

    def _check_benchmark_tests(self, result: ValidationResult, threshold_seconds: float) -> tuple[bool, bool]:
        """Check if any benchmark-marked tests exceed threshold.

        Looks for tests with 'benchmark' or 'slow' in their name/path,
        which is a common pattern for performance tests.

        Returns:
            Tuple of (has_benchmark_tests, any_exceed_threshold)
        """
        benchmark_patterns = ["benchmark", "perf", "performance", "slow"]

        benchmark_tests = []
        for tc in result.test_cases:
            name_lower = tc.name.lower()
            if any(p in name_lower for p in benchmark_patterns):
                benchmark_tests.append((tc.name, tc.duration_seconds))

        if not benchmark_tests:
            return (False, False)

        # Check if any benchmark test exceeds threshold
        for name, duration in benchmark_tests:
            if duration > threshold_seconds:
                return (True, True)

        return (True, False)

    def _parse_output(self, stdout: str, stderr: str, command: str) -> ParsedTestResult:
        """Parse test output to extract structured results.

        Supports pytest, cargo test, npm test (jest), and go test.
        """
        cmd_lower = command.lower()

        if "pytest" in cmd_lower:
            return self._parse_pytest(stdout, stderr)
        if "cargo test" in cmd_lower:
            return self._parse_cargo_test(stdout, stderr)
        if "go test" in cmd_lower:
            return self._parse_go_test(stdout, stderr)
        if "npm test" in cmd_lower or "yarn test" in cmd_lower or "jest" in cmd_lower:
            return self._parse_jest(stdout, stderr)

        # Generic parsing: count common patterns
        return self._parse_generic(stdout, stderr)

    def _parse_pytest(self, stdout: str, stderr: str) -> ParsedTestResult:
        """Parse pytest output."""
        result: ParsedTestResult = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "tests_skipped": 0,
            "test_cases": [],
        }

        combined = stdout + stderr

        # Look for summary line: "X passed, Y failed, Z skipped"
        # or "collected X items"
        collected_match = re.search(r"collected (\d+) items?", combined)
        if collected_match:
            result["tests_run"] = int(collected_match.group(1))

        # Parse summary line
        summary_match = re.search(
            r"(\d+) passed",
            combined,
        )
        if summary_match:
            result["tests_passed"] = int(summary_match.group(1))

        failed_match = re.search(r"(\d+) failed", combined)
        if failed_match:
            result["tests_failed"] = int(failed_match.group(1))

        skipped_match = re.search(r"(\d+) skipped", combined)
        if skipped_match:
            result["tests_skipped"] = int(skipped_match.group(1))

        # Update tests_run if we have components
        if result["tests_passed"] or result["tests_failed"] or result["tests_skipped"]:
            result["tests_run"] = result["tests_passed"] + result["tests_failed"] + result["tests_skipped"]

        # Parse individual test failures
        # Pattern: FAILED tests/test_foo.py::test_bar - AssertionError
        failure_pattern = re.compile(r"FAILED\s+([^\s]+::[^\s]+)\s*[-:]?\s*(.*)?")
        for match in failure_pattern.finditer(combined):
            test_name = match.group(1)
            message = match.group(2) or ""
            result["test_cases"].append(
                CaseResult(
                    name=test_name,
                    status=CaseStatus.FAILED,
                    message=message.strip(),
                )
            )

        return result

    def _parse_cargo_test(self, stdout: str, stderr: str) -> ParsedTestResult:
        """Parse cargo test output."""
        result: ParsedTestResult = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "tests_skipped": 0,
            "test_cases": [],
        }

        combined = stdout + stderr

        # Look for "test result: ok. X passed; Y failed; Z ignored"
        summary_match = re.search(
            r"test result:.*?(\d+) passed;?\s*(\d+) failed;?\s*(\d+) ignored",
            combined,
        )
        if summary_match:
            result["tests_passed"] = int(summary_match.group(1))
            result["tests_failed"] = int(summary_match.group(2))
            result["tests_skipped"] = int(summary_match.group(3))
            result["tests_run"] = result["tests_passed"] + result["tests_failed"] + result["tests_skipped"]

        # Parse individual test results
        # Pattern: test module::test_name ... ok/FAILED
        test_pattern = re.compile(r"test\s+(\S+)\s+\.\.\.\s+(ok|FAILED|ignored)")
        for match in test_pattern.finditer(combined):
            test_name = match.group(1)
            status_str = match.group(2)
            status = {
                "ok": CaseStatus.PASSED,
                "FAILED": CaseStatus.FAILED,
                "ignored": CaseStatus.SKIPPED,
            }.get(status_str, CaseStatus.ERROR)

            result["test_cases"].append(CaseResult(name=test_name, status=status))

        return result

    def _parse_go_test(self, stdout: str, stderr: str) -> ParsedTestResult:
        """Parse go test output."""
        result: ParsedTestResult = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "tests_skipped": 0,
            "test_cases": [],
        }

        combined = stdout + stderr

        # Parse individual test results
        # Pattern: --- PASS: TestName (0.00s)
        # Pattern: --- FAIL: TestName (0.00s)
        test_pattern = re.compile(r"---\s+(PASS|FAIL|SKIP):\s+(\S+)\s+\(([0-9.]+)s\)")
        for match in test_pattern.finditer(combined):
            status_str = match.group(1)
            test_name = match.group(2)
            duration = float(match.group(3))

            status = {
                "PASS": CaseStatus.PASSED,
                "FAIL": CaseStatus.FAILED,
                "SKIP": CaseStatus.SKIPPED,
            }.get(status_str, CaseStatus.ERROR)

            result["test_cases"].append(CaseResult(name=test_name, status=status, duration_seconds=duration))

            if status == CaseStatus.PASSED:
                result["tests_passed"] += 1
            elif status == CaseStatus.FAILED:
                result["tests_failed"] += 1
            elif status == CaseStatus.SKIPPED:
                result["tests_skipped"] += 1

        result["tests_run"] = len(result["test_cases"])

        return result

    def _parse_jest(self, stdout: str, stderr: str) -> ParsedTestResult:
        """Parse Jest (npm test) output."""
        result: ParsedTestResult = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "tests_skipped": 0,
            "test_cases": [],
        }

        combined = stdout + stderr

        # Look for "Tests: X passed, Y failed, Z total"
        tests_match = re.search(
            r"Tests:\s*(?:(\d+)\s+passed)?[,\s]*(?:(\d+)\s+failed)?[,\s]*(\d+)\s+total",
            combined,
        )
        if tests_match:
            result["tests_passed"] = int(tests_match.group(1) or 0)
            result["tests_failed"] = int(tests_match.group(2) or 0)
            result["tests_run"] = int(tests_match.group(3))

        # Parse individual failures
        # Pattern: ✕ test description
        fail_pattern = re.compile(r"[✕✗×]\s+(.+?)(?:\s+\(\d+\s*ms\))?$", re.MULTILINE)
        for match in fail_pattern.finditer(combined):
            result["test_cases"].append(CaseResult(name=match.group(1).strip(), status=CaseStatus.FAILED))

        return result

    def _parse_generic(self, stdout: str, stderr: str) -> ParsedTestResult:
        """Generic parsing for unknown test frameworks."""
        result: ParsedTestResult = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "tests_skipped": 0,
            "test_cases": [],
        }

        combined = (stdout + stderr).lower()

        # Count common patterns
        result["tests_passed"] = len(re.findall(r"\bpass(?:ed)?\b", combined))
        result["tests_failed"] = len(re.findall(r"\bfail(?:ed|ure)?\b", combined))
        result["tests_run"] = result["tests_passed"] + result["tests_failed"]

        return result


async def run_validation(
    working_dir: Path,
    command: Optional[str] = None,
    timeout_seconds: int = 300,
    require_tests: bool = False,
    devcontainer_config: Optional[DevContainerConfig] = None,
) -> ValidationResult:
    """Convenience function to run validation.

    Args:
        working_dir: Directory to run tests in.
        command: Test command (auto-detected if None).
        timeout_seconds: Maximum time to wait for tests.
        require_tests: If True, return failure when no tests detected.
        devcontainer_config: Optional Dev Container configuration for isolated execution.

    Returns:
        ValidationResult with test outcome.
    """
    from deliberate.validation.detectors import detect_test_command

    if command is None:
        command = detect_test_command(working_dir)

    runner = ValidationRunner(
        working_dir,
        command,
        timeout_seconds,
        require_tests=require_tests,
        devcontainer_config=devcontainer_config,
    )
    return await runner.run()


def _is_command_not_found(result: ValidationResult) -> bool:
    """Check if validation failed due to command not found.

    Returns True if the failure was likely due to:
    - Exit code 127 (command not found in shell)
    - Exit code 126 (command not executable)
    - Common "command not found" error messages
    """
    if result.exit_code in (126, 127):
        return True

    # Check for common error patterns in stderr
    error_patterns = [
        "command not found",
        "not found",
        "no such file or directory",
        "cannot find",
        "is not recognized",  # Windows
    ]

    stderr = (result.stderr or "").lower()
    for pattern in error_patterns:
        if pattern in stderr:
            return True

    return False


async def run_validation_with_fallback(
    working_dir: Path,
    adapter,  # ModelAdapter - not type-hinted to avoid circular import
    command: Optional[str] = None,
    timeout_seconds: int = 300,
    require_tests: bool = False,
    devcontainer_config: Optional[DevContainerConfig] = None,
) -> ValidationResult:
    """Run validation with LLM fallback if command detection fails.

    If the initial command (heuristic or provided) fails with "command not found",
    this function will:
    1. Use LLM-based detection to find the correct command
    2. Retry with the LLM-detected command

    This handles cases where heuristics fail:
    - Monorepos with custom test scripts
    - Docker-wrapped test runners
    - Non-standard project setups

    Args:
        working_dir: Directory to run tests in.
        adapter: Model adapter for LLM-based command detection.
        command: Test command (auto-detected if None).
        timeout_seconds: Maximum time to wait for tests.
        require_tests: If True, return failure when no tests detected.
        devcontainer_config: Optional Dev Container configuration.

    Returns:
        ValidationResult with test outcome.
    """
    from deliberate.validation.detectors import detect_test_command

    # First attempt with heuristic detection
    if command is None:
        command = detect_test_command(working_dir)

    result = await run_validation(
        working_dir,
        command,
        timeout_seconds,
        require_tests,
        devcontainer_config,
    )

    # If command not found, try LLM detection
    if _is_command_not_found(result) and adapter is not None:
        logger.info(f"Command '{command}' not found (exit {result.exit_code}), trying LLM-based detection...")

        try:
            from deliberate.validation.analyzer import detect_test_command_llm

            llm_command = await detect_test_command_llm(
                working_dir,
                adapter,
                fallback_to_heuristics=False,  # Already tried heuristics
            )

            if llm_command and llm_command != command:
                logger.info(f"LLM detected command: {llm_command}")

                # Retry with LLM-detected command
                result = await run_validation(
                    working_dir,
                    llm_command,
                    timeout_seconds,
                    require_tests,
                    devcontainer_config,
                )

                # Update the command in result for transparency
                if result.command != llm_command:
                    # Result may have a different command if it auto-detected again
                    pass

        except Exception as e:
            logger.warning(f"LLM command detection failed: {e}")
            # Return original result if LLM fallback fails

    return result
