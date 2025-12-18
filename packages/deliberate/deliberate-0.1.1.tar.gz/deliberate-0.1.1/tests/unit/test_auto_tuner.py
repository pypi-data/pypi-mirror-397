"""Tests for auto-tuner logic in Orchestrator."""

import subprocess
from pathlib import Path

from deliberate.budget.tracker import BudgetTracker
from deliberate.config import (
    AutoTunerConfig,
    DeliberateConfig,
    EvolutionWorkflowConfig,
    TriggerPolicy,
)
from deliberate.git.worktree import WorktreeManager
from deliberate.orchestrator import Orchestrator
from deliberate.types import ExecutionResult
from deliberate.validation.types import (
    PerformanceIssue,
    ValidationResult,
)


def _init_repo(tmp_path: Path) -> Path:
    """Initialize a git repo for testing."""
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    (repo / "README.md").write_text("# Test\n")
    subprocess.run(["git", "add", "README.md"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo, check=True, capture_output=True)
    return repo


def _make_orchestrator(
    tmp_path: Path,
    auto_tuner_enabled: bool = True,
    on_slow_execution: TriggerPolicy = TriggerPolicy.EVOLVE,
    evolution_enabled: bool = True,
) -> Orchestrator:
    """Create an orchestrator with test configuration."""
    repo = _init_repo(tmp_path)

    cfg = DeliberateConfig()
    cfg.tracking.enabled = False
    cfg.workflow.auto_tuner = AutoTunerConfig(
        enabled=auto_tuner_enabled,
        on_slow_execution=on_slow_execution,
        on_high_memory=TriggerPolicy.WARN,
        latency_threshold_ms=500.0,
        max_evolution_attempts=3,
    )
    cfg.workflow.evolution = EvolutionWorkflowConfig(
        enabled=evolution_enabled,
        agents=["test_agent"] if evolution_enabled else [],
    )

    # Add a test agent
    from deliberate.config import AgentConfig

    cfg.agents["test_agent"] = AgentConfig(type="fake", behavior="echo")

    return Orchestrator(
        cfg,
        repo,
        budget_tracker=BudgetTracker(
            max_total_tokens=1_000,
            max_cost_usd=1.0,
            max_requests_per_agent=5,
            hard_timeout_seconds=60,
        ),
        worktree_mgr=WorktreeManager(repo),
    )


def _make_validation_result(
    passed: bool = True,
    needs_optimization: bool = False,
    performance_issue: PerformanceIssue = PerformanceIssue.NONE,
    regression_detected: bool = False,
) -> ValidationResult:
    """Create a ValidationResult for testing."""
    return ValidationResult(
        passed=passed,
        command="pytest",
        exit_code=0 if passed else 1,
        stdout="",
        stderr="",
        duration_seconds=1.0,
        tests_run=5,
        tests_passed=5 if passed else 4,
        tests_failed=0 if passed else 1,
        needs_optimization=needs_optimization,
        performance_issue=performance_issue,
        regression_detected=regression_detected,
    )


def _make_execution_result(
    validation_result: ValidationResult | None = None,
) -> ExecutionResult:
    """Create an ExecutionResult for testing."""
    return ExecutionResult(
        id="exec-1",
        agent="test_agent",
        worktree_path=None,
        diff="--- a/test.py\n+++ b/test.py\n@@ -1 +1 @@\n-old\n+new",
        summary="Execution completed",
        success=True,
        duration_seconds=10.0,
        token_usage=100,
        validation_result=validation_result,
    )


class TestShouldTriggerEvolution:
    """Tests for _should_trigger_evolution method."""

    def test_returns_false_when_auto_tuner_disabled(self, tmp_path: Path):
        """No trigger when auto-tuner is disabled."""
        orch = _make_orchestrator(tmp_path, auto_tuner_enabled=False)

        vr = _make_validation_result(
            passed=True,
            needs_optimization=True,
            performance_issue=PerformanceIssue.SLOW_EXECUTION,
        )
        results = [_make_execution_result(vr)]

        should_trigger, triggering_vr = orch._should_trigger_evolution(results, 0)

        assert should_trigger is False
        assert triggering_vr is None

    def test_returns_false_when_evolution_disabled(self, tmp_path: Path):
        """No trigger when evolution is disabled."""
        orch = _make_orchestrator(tmp_path, evolution_enabled=False)

        vr = _make_validation_result(
            passed=True,
            needs_optimization=True,
            performance_issue=PerformanceIssue.SLOW_EXECUTION,
        )
        results = [_make_execution_result(vr)]

        should_trigger, triggering_vr = orch._should_trigger_evolution(results, 0)

        assert should_trigger is False
        assert triggering_vr is None

    def test_returns_false_when_max_attempts_exceeded(self, tmp_path: Path):
        """No trigger when max evolution attempts exceeded."""
        orch = _make_orchestrator(tmp_path)

        vr = _make_validation_result(
            passed=True,
            needs_optimization=True,
            performance_issue=PerformanceIssue.SLOW_EXECUTION,
        )
        results = [_make_execution_result(vr)]

        # Max is 3, so 3 attempts means we've hit the limit
        should_trigger, triggering_vr = orch._should_trigger_evolution(results, 3)

        assert should_trigger is False
        assert triggering_vr is None

    def test_returns_false_when_tests_failed(self, tmp_path: Path):
        """No trigger when tests didn't pass."""
        orch = _make_orchestrator(tmp_path)

        vr = _make_validation_result(
            passed=False,
            needs_optimization=True,
            performance_issue=PerformanceIssue.SLOW_EXECUTION,
        )
        results = [_make_execution_result(vr)]

        should_trigger, triggering_vr = orch._should_trigger_evolution(results, 0)

        assert should_trigger is False
        assert triggering_vr is None

    def test_returns_false_when_regression_detected(self, tmp_path: Path):
        """No trigger when there's a regression (correctness_passed = False)."""
        orch = _make_orchestrator(tmp_path)

        vr = _make_validation_result(
            passed=True,
            regression_detected=True,
            needs_optimization=True,
            performance_issue=PerformanceIssue.SLOW_EXECUTION,
        )
        results = [_make_execution_result(vr)]

        should_trigger, triggering_vr = orch._should_trigger_evolution(results, 0)

        assert should_trigger is False
        assert triggering_vr is None

    def test_returns_false_when_no_optimization_needed(self, tmp_path: Path):
        """No trigger when optimization isn't needed."""
        orch = _make_orchestrator(tmp_path)

        vr = _make_validation_result(
            passed=True,
            needs_optimization=False,
            performance_issue=PerformanceIssue.NONE,
        )
        results = [_make_execution_result(vr)]

        should_trigger, triggering_vr = orch._should_trigger_evolution(results, 0)

        assert should_trigger is False
        assert triggering_vr is None

    def test_returns_false_when_policy_is_warn(self, tmp_path: Path):
        """No trigger when policy is WARN."""
        orch = _make_orchestrator(tmp_path, on_slow_execution=TriggerPolicy.WARN)

        vr = _make_validation_result(
            passed=True,
            needs_optimization=True,
            performance_issue=PerformanceIssue.SLOW_EXECUTION,
        )
        results = [_make_execution_result(vr)]

        should_trigger, triggering_vr = orch._should_trigger_evolution(results, 0)

        assert should_trigger is False
        assert triggering_vr is None

    def test_returns_false_when_policy_is_fail(self, tmp_path: Path):
        """No trigger when policy is FAIL."""
        orch = _make_orchestrator(tmp_path, on_slow_execution=TriggerPolicy.FAIL)

        vr = _make_validation_result(
            passed=True,
            needs_optimization=True,
            performance_issue=PerformanceIssue.SLOW_EXECUTION,
        )
        results = [_make_execution_result(vr)]

        should_trigger, triggering_vr = orch._should_trigger_evolution(results, 0)

        assert should_trigger is False
        assert triggering_vr is None

    def test_returns_true_for_slow_execution_with_evolve_policy(self, tmp_path: Path):
        """Triggers evolution for slow execution with EVOLVE policy."""
        orch = _make_orchestrator(tmp_path, on_slow_execution=TriggerPolicy.EVOLVE)

        vr = _make_validation_result(
            passed=True,
            needs_optimization=True,
            performance_issue=PerformanceIssue.SLOW_EXECUTION,
        )
        results = [_make_execution_result(vr)]

        should_trigger, triggering_vr = orch._should_trigger_evolution(results, 0)

        assert should_trigger is True
        assert triggering_vr is vr

    def test_returns_true_for_timeout_with_evolve_policy(self, tmp_path: Path):
        """Triggers evolution for timeout (treated as slow execution)."""
        orch = _make_orchestrator(tmp_path, on_slow_execution=TriggerPolicy.EVOLVE)

        vr = _make_validation_result(
            passed=True,
            needs_optimization=True,
            performance_issue=PerformanceIssue.TIMEOUT,
        )
        results = [_make_execution_result(vr)]

        should_trigger, triggering_vr = orch._should_trigger_evolution(results, 0)

        assert should_trigger is True
        assert triggering_vr is vr

    def test_returns_false_for_high_memory_when_policy_is_warn(self, tmp_path: Path):
        """No trigger for high memory when memory policy is WARN."""
        orch = _make_orchestrator(tmp_path, on_slow_execution=TriggerPolicy.EVOLVE)
        # on_high_memory defaults to WARN

        vr = _make_validation_result(
            passed=True,
            needs_optimization=True,
            performance_issue=PerformanceIssue.HIGH_MEMORY,
        )
        results = [_make_execution_result(vr)]

        should_trigger, triggering_vr = orch._should_trigger_evolution(results, 0)

        assert should_trigger is False
        assert triggering_vr is None

    def test_finds_first_optimization_candidate(self, tmp_path: Path):
        """Returns the first result that needs optimization."""
        orch = _make_orchestrator(tmp_path, on_slow_execution=TriggerPolicy.EVOLVE)

        vr1 = _make_validation_result(
            passed=True,
            needs_optimization=False,
            performance_issue=PerformanceIssue.NONE,
        )
        vr2 = _make_validation_result(
            passed=True,
            needs_optimization=True,
            performance_issue=PerformanceIssue.SLOW_EXECUTION,
        )
        results = [_make_execution_result(vr1), _make_execution_result(vr2)]

        should_trigger, triggering_vr = orch._should_trigger_evolution(results, 0)

        assert should_trigger is True
        assert triggering_vr is vr2


class TestBuildOptimizationTask:
    """Tests for _build_optimization_task method."""

    def test_includes_original_task(self, tmp_path: Path):
        """Task includes original task description."""
        orch = _make_orchestrator(tmp_path)
        vr = _make_validation_result(
            passed=True,
            needs_optimization=True,
            performance_issue=PerformanceIssue.SLOW_EXECUTION,
        )

        task = orch._build_optimization_task("Fix the bug", vr, "latency")

        assert "Fix the bug" in task
        assert "## Original Task" in task

    def test_includes_performance_issue(self, tmp_path: Path):
        """Task includes performance issue details."""
        orch = _make_orchestrator(tmp_path)
        vr = _make_validation_result(
            passed=True,
            needs_optimization=True,
            performance_issue=PerformanceIssue.SLOW_EXECUTION,
        )

        task = orch._build_optimization_task("Fix the bug", vr, "latency")

        assert "## Performance Issue" in task
        assert "slow_execution" in task

    def test_latency_target_guidance(self, tmp_path: Path):
        """Task includes latency-specific guidance."""
        orch = _make_orchestrator(tmp_path)
        vr = _make_validation_result(
            passed=True,
            needs_optimization=True,
            performance_issue=PerformanceIssue.SLOW_EXECUTION,
        )

        task = orch._build_optimization_task("Fix the bug", vr, "latency")

        assert "## Optimization Target: latency" in task
        assert "reducing execution time" in task
        assert "time complexity" in task

    def test_memory_target_guidance(self, tmp_path: Path):
        """Task includes memory-specific guidance."""
        orch = _make_orchestrator(tmp_path)
        vr = _make_validation_result(
            passed=True,
            needs_optimization=True,
            performance_issue=PerformanceIssue.HIGH_MEMORY,
        )

        task = orch._build_optimization_task("Fix the bug", vr, "memory")

        assert "## Optimization Target: memory" in task
        assert "reducing memory usage" in task
        assert "generators" in task

    def test_token_count_target_guidance(self, tmp_path: Path):
        """Task includes token count-specific guidance."""
        orch = _make_orchestrator(tmp_path)
        vr = _make_validation_result(
            passed=True,
            needs_optimization=True,
            performance_issue=PerformanceIssue.SLOW_EXECUTION,
        )

        task = orch._build_optimization_task("Fix the bug", vr, "token_count")

        assert "## Optimization Target: token_count" in task
        assert "Batching API calls" in task

    def test_includes_slowest_tests(self, tmp_path: Path):
        """Task includes slowest tests when available."""
        orch = _make_orchestrator(tmp_path)
        vr = _make_validation_result(
            passed=True,
            needs_optimization=True,
            performance_issue=PerformanceIssue.SLOW_EXECUTION,
        )
        vr.slowest_tests = [
            ("test_slow_one", 5.0),
            ("test_slow_two", 3.5),
        ]

        task = orch._build_optimization_task("Fix the bug", vr, "latency")

        assert "## Slowest Tests" in task
        assert "test_slow_one: 5.00s" in task
        assert "test_slow_two: 3.50s" in task

    def test_limits_slowest_tests_to_five(self, tmp_path: Path):
        """Only includes first 5 slowest tests."""
        orch = _make_orchestrator(tmp_path)
        vr = _make_validation_result(
            passed=True,
            needs_optimization=True,
            performance_issue=PerformanceIssue.SLOW_EXECUTION,
        )
        vr.slowest_tests = [(f"test_{i}", float(i)) for i in range(10)]

        task = orch._build_optimization_task("Fix the bug", vr, "latency")

        assert "test_0" in task
        assert "test_4" in task
        assert "test_5" not in task
