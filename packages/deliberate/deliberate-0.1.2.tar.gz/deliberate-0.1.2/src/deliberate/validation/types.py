"""Types for validation subsystem."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional


class CaseStatus(Enum):
    """Status of an individual test case."""

    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"  # Infrastructure error, not test failure


# Alias for backwards compatibility
TestStatus = CaseStatus


class PerformanceIssue(Enum):
    """Classification of performance issues for auto-tuner.

    Used by the Auto-Tuner to decide whether to trigger evolution mode
    when tests pass but performance is suboptimal.
    """

    NONE = "none"
    SLOW_EXECUTION = "slow_execution"  # Code runs slower than threshold
    HIGH_MEMORY = "high_memory"  # Memory usage exceeds threshold
    TIMEOUT = "timeout"  # Test or execution timed out
    FLAKY = "flaky"  # Test results are inconsistent


@dataclass
class CaseResult:
    """Result of a single test case."""

    name: str
    status: CaseStatus
    duration_seconds: float = 0.0
    message: Optional[str] = None
    file_path: Optional[str] = None
    line_number: Optional[int] = None


# Alias for backwards compatibility
TestCaseResult = CaseResult


@dataclass
class ValidationResult:
    """Aggregate result of a validation run.

    This replaces the simpler ValidationResult in types.py with more
    detailed information for agent feedback and gating decisions.
    """

    passed: bool
    command: str
    exit_code: int
    stdout: str
    stderr: str
    duration_seconds: float
    tests_run: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    tests_skipped: int = 0
    test_cases: list[CaseResult] = field(default_factory=list)
    error: Optional[str] = None  # If the runner itself failed (timeout, missing command, etc.)
    baseline_passed: Optional[bool] = None  # Did tests pass before changes?
    regression_detected: bool = False  # Did we break existing tests?
    artifacts: "RunArtifacts | None" = None

    # Performance analysis fields (for auto-tuner)
    performance_issue: PerformanceIssue = PerformanceIssue.NONE
    needs_optimization: bool = False
    slowest_tests: list[tuple[str, float]] = field(default_factory=list)

    @property
    def correctness_passed(self) -> bool:
        """Check if tests passed without regressions (ignoring performance)."""
        return self.passed and not self.regression_detected

    @property
    def is_slow(self) -> bool:
        """Check if performance is problematic (slow or timed out)."""
        return self.performance_issue in (
            PerformanceIssue.SLOW_EXECUTION,
            PerformanceIssue.TIMEOUT,
        )

    @property
    def summary(self) -> str:
        """Human readable summary."""
        if self.error:
            return f"Validation Error: {self.error}"

        status = "PASSED" if self.passed else "FAILED"
        parts = [status]

        if self.tests_run > 0:
            parts.append(f"{self.tests_passed}/{self.tests_run} passed")
            if self.tests_failed > 0:
                parts.append(f"{self.tests_failed} failed")
            if self.tests_skipped > 0:
                parts.append(f"{self.tests_skipped} skipped")

        if self.exit_code != 0 and self.tests_run == 0:
            parts.append(f"exit code {self.exit_code}")

        if self.regression_detected:
            parts.append("REGRESSION")

        if self.needs_optimization:
            parts.append(f"NEEDS_OPTIMIZATION ({self.performance_issue.value})")

        return " | ".join(parts)

    @property
    def failure_log(self) -> str:
        """Extract relevant failure information for refinement prompts."""
        if self.passed:
            return ""

        lines = []

        # Add failed test case details
        failed_cases = [tc for tc in self.test_cases if tc.status == CaseStatus.FAILED]
        if failed_cases:
            lines.append("## Failed Tests:")
            for tc in failed_cases[:10]:  # Limit to first 10 for prompt size
                lines.append(f"- {tc.name}")
                if tc.message:
                    # Truncate long messages
                    msg = tc.message[:500] + "..." if len(tc.message) > 500 else tc.message
                    lines.append(f"  {msg}")

        # Add stderr if no structured test failures
        if not failed_cases and self.stderr:
            lines.append("## Error Output:")
            if len(self.stderr) > 2000:
                stderr_truncated = self.stderr[:2000] + "..."
            else:
                stderr_truncated = self.stderr
            lines.append(stderr_truncated)

        # Add stdout failures as fallback
        if not lines and self.stdout:
            # Look for common failure patterns
            if len(self.stdout) > 2000:
                stdout_truncated = self.stdout[:2000] + "..."
            else:
                stdout_truncated = self.stdout
            lines.append("## Test Output:")
            lines.append(stdout_truncated)

        return "\n".join(lines)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "passed": self.passed,
            "command": self.command,
            "exit_code": self.exit_code,
            "duration_seconds": self.duration_seconds,
            "tests_run": self.tests_run,
            "tests_passed": self.tests_passed,
            "tests_failed": self.tests_failed,
            "tests_skipped": self.tests_skipped,
            "regression_detected": self.regression_detected,
            "summary": self.summary,
            "error": self.error,
            # Performance fields
            "performance_issue": self.performance_issue.value,
            "needs_optimization": self.needs_optimization,
            "correctness_passed": self.correctness_passed,
            "is_slow": self.is_slow,
            "slowest_tests": self.slowest_tests,
        }


@dataclass
class RunArtifacts:
    """Raw artifacts from a validation run for downstream evaluators/LLMs."""

    command: str
    cwd: Path
    exit_code: int
    duration_seconds: float
    stdout: str = ""
    stderr: str = ""
    junit_xml: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None


@dataclass
class ValidationConfig:
    """Configuration for validation behavior."""

    enabled: bool = False
    command: Optional[str] = None  # Override auto-detection
    timeout_seconds: int = 300
    run_baseline: bool = True  # Run tests before changes to detect regressions
    fail_on_regression: bool = True  # Block candidates that break existing tests
    required_for_winner: bool = True  # Winner must pass validation
