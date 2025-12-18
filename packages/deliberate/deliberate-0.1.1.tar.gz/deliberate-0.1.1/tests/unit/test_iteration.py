"""Tests for the iteration module.

Tests the iterative solving meta-pattern:
- Solution history accumulation
- Soft score tracking (0.0-1.0 partial correctness)
- Feedback building for different domains
- Iterative context construction
- Self-auditing for early termination
"""

import pytest

from deliberate.iteration import (
    DiffFeedbackBuilder,
    FeedbackContext,
    IterationConfig,
    SolutionAttempt,
    SolutionHistory,
    TestFeedbackBuilder,
    build_iteration_prompt,
)


class TestSolutionAttempt:
    """Tests for SolutionAttempt dataclass."""

    def test_create_basic(self):
        attempt = SolutionAttempt(
            iteration=1,
            code="def foo(): pass",
            output="test output",
            success=False,
            soft_score=0.5,
            feedback="Some feedback",
        )
        assert attempt.iteration == 1
        assert attempt.code == "def foo(): pass"
        assert attempt.soft_score == 0.5
        assert not attempt.success

    def test_create_successful(self):
        attempt = SolutionAttempt(
            iteration=3,
            code="def bar(): return 42",
            output="42",
            success=True,
            soft_score=1.0,
            feedback="All tests passed",
        )
        assert attempt.success
        assert attempt.soft_score == 1.0


class TestSolutionHistory:
    """Tests for SolutionHistory class."""

    def test_empty_history(self):
        history = SolutionHistory()
        assert len(history) == 0
        assert history.get_best() is None
        assert history.get_successful() == []

    def test_add_attempt(self):
        history = SolutionHistory()
        attempt = SolutionAttempt(
            iteration=1,
            code="x",
            output="out",
            success=False,
            soft_score=0.3,
            feedback="fb",
        )
        history.add(attempt)
        assert len(history) == 1
        assert history.attempts[0] == attempt

    def test_get_best(self):
        history = SolutionHistory()
        history.add(SolutionAttempt(1, "a", "o", False, 0.3, "f"))
        history.add(SolutionAttempt(2, "b", "o", False, 0.8, "f"))
        history.add(SolutionAttempt(3, "c", "o", False, 0.5, "f"))

        best = history.get_best()
        assert best is not None
        assert best.soft_score == 0.8
        assert best.iteration == 2

    def test_get_successful(self):
        history = SolutionHistory()
        history.add(SolutionAttempt(1, "a", "o", False, 0.3, "f"))
        history.add(SolutionAttempt(2, "b", "o", True, 1.0, "f"))
        history.add(SolutionAttempt(3, "c", "o", False, 0.5, "f"))

        successful = history.get_successful()
        assert len(successful) == 1
        assert successful[0].iteration == 2

    def test_select_for_context_all(self):
        history = SolutionHistory()
        history.add(SolutionAttempt(1, "a", "o", False, 0.3, "f"))
        history.add(SolutionAttempt(2, "b", "o", False, 0.8, "f"))

        selected = history.select_for_context(
            max_solutions=5,
            selection_probability=1.0,  # Select all
            seed=42,
        )
        assert len(selected) == 2

    def test_select_for_context_max_limit(self):
        history = SolutionHistory()
        for i in range(10):
            history.add(SolutionAttempt(i, f"code{i}", "o", False, i / 10, "f"))

        selected = history.select_for_context(
            max_solutions=3,
            selection_probability=1.0,
            seed=42,
        )
        assert len(selected) == 3

    def test_select_for_context_improving_order(self):
        history = SolutionHistory()
        history.add(SolutionAttempt(1, "a", "o", False, 0.8, "f"))
        history.add(SolutionAttempt(2, "b", "o", False, 0.3, "f"))
        history.add(SolutionAttempt(3, "c", "o", False, 0.5, "f"))

        # Improving order: worst to best
        selected = history.select_for_context(improving_order=True, seed=42)
        scores = [s.soft_score for s in selected]
        assert scores == [0.3, 0.5, 0.8]

        # Reverse: best to worst
        selected = history.select_for_context(improving_order=False, seed=42)
        scores = [s.soft_score for s in selected]
        assert scores == [0.8, 0.5, 0.3]

    def test_format_for_prompt(self):
        history = SolutionHistory()
        history.add(SolutionAttempt(1, "code1", "out1", False, 0.3, "feedback1"))
        history.add(SolutionAttempt(2, "code2", "out2", False, 0.8, "feedback2"))

        selected = history.select_for_context(seed=42)
        formatted = history.format_for_prompt(selected)

        assert "<solution_1>" in formatted
        assert "<solution_2>" in formatted
        assert "code1" in formatted or "code2" in formatted
        assert "<solution_score>" in formatted

    def test_score_trajectory(self):
        history = SolutionHistory()
        history.add(SolutionAttempt(1, "a", "o", False, 0.3, "f"))
        history.add(SolutionAttempt(2, "b", "o", False, 0.5, "f"))
        history.add(SolutionAttempt(3, "c", "o", False, 0.7, "f"))

        trajectory = history.get_score_trajectory()
        assert trajectory == [0.3, 0.5, 0.7]

    def test_is_improving(self):
        history = SolutionHistory()
        history.add(SolutionAttempt(1, "a", "o", False, 0.3, "f"))
        history.add(SolutionAttempt(2, "b", "o", False, 0.5, "f"))
        history.add(SolutionAttempt(3, "c", "o", False, 0.7, "f"))

        assert history.is_improving(threshold=0.01)

    def test_is_not_improving(self):
        history = SolutionHistory()
        history.add(SolutionAttempt(1, "a", "o", False, 0.7, "f"))
        history.add(SolutionAttempt(2, "b", "o", False, 0.5, "f"))
        history.add(SolutionAttempt(3, "c", "o", False, 0.3, "f"))

        assert not history.is_improving(threshold=0.01)


class TestIterationConfig:
    """Tests for IterationConfig dataclass."""

    def test_defaults(self):
        config = IterationConfig()
        assert config.max_iterations == 10
        assert config.max_solutions_in_context == 5
        assert config.success_threshold == 1.0
        assert config.return_best_on_failure is True

    def test_custom_config(self):
        config = IterationConfig(
            max_iterations=5,
            max_solutions_in_context=3,
            success_threshold=0.9,
        )
        assert config.max_iterations == 5
        assert config.success_threshold == 0.9


class TestTestFeedbackBuilder:
    """Tests for TestFeedbackBuilder."""

    def test_passing_tests(self):
        builder = TestFeedbackBuilder()
        evaluation = {"passed": True, "failures": []}
        context = FeedbackContext(
            expected="all pass",
            actual="all pass",
            match=True,
            soft_score=1.0,
        )

        feedback = builder.build(evaluation, context)
        assert feedback.success
        assert feedback.score == 1.0
        assert "passed" in feedback.text.lower()

    def test_failing_tests(self):
        builder = TestFeedbackBuilder()
        evaluation = {
            "passed": False,
            "failures": [{"name": "test_foo", "message": "assertion failed"}],
            "stderr": "AssertionError: expected 1 got 2",
            "exit_code": 1,
            "total": 2,
            "passed_count": 1,
        }
        context = FeedbackContext(
            expected="all pass",
            actual="1/2 pass",
            match=False,
            soft_score=0.5,
        )

        feedback = builder.build(evaluation, context)
        assert not feedback.success
        assert feedback.score == 0.5
        assert len(feedback.issues) > 0
        assert "test_foo" in feedback.issues[0]


class TestDiffFeedbackBuilder:
    """Tests for DiffFeedbackBuilder.

    Tests array/grid comparison feedback for general use cases
    (not limited to any specific domain like ARC-AGI).
    """

    def test_matching_arrays(self):
        """Test feedback when expected and actual arrays match exactly."""
        builder = DiffFeedbackBuilder()
        expected = [1, 2, 3, 4]
        actual = [1, 2, 3, 4]
        context = FeedbackContext(
            expected=expected,
            actual=actual,
            match=True,
            soft_score=1.0,
        )

        feedback = builder.build({}, context)
        assert feedback.success
        assert feedback.score == 1.0

    def test_partially_matching_arrays(self):
        """Test feedback when arrays partially match."""
        builder = DiffFeedbackBuilder()
        expected = [1, 2, 3, 4]
        actual = [1, 0, 3, 4]  # One element different
        context = FeedbackContext(
            expected=expected,
            actual=actual,
            match=False,
            soft_score=0.75,
        )

        feedback = builder.build({}, context)
        assert not feedback.success
        assert feedback.score == 0.75
        assert len(feedback.issues) > 0

    def test_2d_array_comparison(self):
        """Test feedback for 2D array comparisons."""
        builder = DiffFeedbackBuilder()
        expected = [[1, 2], [3, 4]]
        actual = [[1, 0], [3, 4]]  # One cell different
        context = FeedbackContext(
            expected=expected,
            actual=actual,
            match=False,
            soft_score=0.75,
        )

        feedback = builder.build({}, context)
        assert not feedback.success
        assert feedback.score == 0.75
        assert "1 cells differ" in feedback.issues[0]

    def test_shape_mismatch(self):
        """Test feedback when array shapes don't match."""
        builder = DiffFeedbackBuilder()
        expected = [[1, 2], [3, 4]]
        actual = [[1, 2, 3], [4, 5, 6]]  # Different shape
        context = FeedbackContext(
            expected=expected,
            actual=actual,
            match=False,
            soft_score=0.0,
        )

        feedback = builder.build({}, context)
        assert not feedback.success
        assert feedback.score == 0.0
        assert "Shape mismatch" in feedback.issues[0]


class TestBuildIterationPrompt:
    """Tests for build_iteration_prompt function."""

    def test_no_history(self):
        prompt = build_iteration_prompt("Solve the puzzle", "")
        assert prompt == "Solve the puzzle"

    def test_with_history(self):
        history_context = "<solution_1>...</solution_1>"
        prompt = build_iteration_prompt("Solve the puzzle", history_context)
        assert "Solve the puzzle" in prompt
        assert "EXISTING PARTIAL/INCORRECT SOLUTIONS" in prompt
        assert "<solution_1>" in prompt


class TestSolutionHistoryPersistence:
    """Tests for SolutionHistory persistence with SolutionStore."""

    @pytest.fixture
    def tracker_and_store(self, tmp_path):
        """Create tracker and solution store for testing."""
        from deliberate.tracking.solution_store import SolutionStore
        from deliberate.tracking.tracker import AgentPerformanceTracker

        db_path = tmp_path / "test_db.duckdb"
        tracker = AgentPerformanceTracker(str(db_path))
        store = SolutionStore(tracker)
        return tracker, store

    def test_history_without_store(self):
        """History works without SolutionStore (backward compatibility)."""
        history = SolutionHistory()
        attempt = SolutionAttempt(
            iteration=1,
            code="def foo(): pass",
            output="test output",
            success=True,
            soft_score=1.0,
            feedback="All passed",
        )
        history.add(attempt)
        assert len(history) == 1

    def test_configure_persistence(self, tracker_and_store):
        """History can be configured with persistence settings."""
        tracker, store = tracker_and_store

        history = SolutionHistory()
        history.configure(
            solution_store=store,
            task_hash="test_task",
            workflow_id="wf_123",
            agent="claude",
        )

        assert history._solution_store is store
        assert history._task_hash == "test_task"
        assert history._workflow_id == "wf_123"
        assert history._agent == "claude"

    def test_persist_successful_attempt(self, tracker_and_store):
        """Successful attempts are persisted automatically."""
        tracker, store = tracker_and_store

        history = SolutionHistory()
        history.configure(
            solution_store=store,
            task_hash="test_persist",
            agent="claude",
        )

        # Add successful attempt (should persist)
        attempt = SolutionAttempt(
            iteration=1,
            code="def foo(): return 42",
            output="42",
            success=True,
            soft_score=1.0,
            feedback="All tests passed",
        )
        history.add(attempt, persist_if_successful=True)

        # Verify persisted
        count = store.count_by_task("test_persist")
        assert count == 1

    def test_no_persist_failed_attempt(self, tracker_and_store):
        """Failed attempts are not auto-persisted."""
        tracker, store = tracker_and_store

        history = SolutionHistory()
        history.configure(
            solution_store=store,
            task_hash="test_no_persist",
            agent="claude",
        )

        # Add failed attempt (should not persist)
        attempt = SolutionAttempt(
            iteration=1,
            code="def foo(): return None",
            output="None",
            success=False,
            soft_score=0.5,
            feedback="Some tests failed",
        )
        history.add(attempt, persist_if_successful=True)

        # Verify not persisted
        count = store.count_by_task("test_no_persist")
        assert count == 0

    def test_persist_best(self, tracker_and_store):
        """persist_best() saves the best attempt."""
        tracker, store = tracker_and_store

        history = SolutionHistory()
        history.configure(
            solution_store=store,
            task_hash="test_persist_best",
            agent="claude",
        )

        # Add multiple attempts without auto-persist
        history.add(
            SolutionAttempt(1, "a", "o", False, 0.3, "f"),
            persist_if_successful=False,
        )
        history.add(
            SolutionAttempt(2, "b", "o", False, 0.8, "f"),
            persist_if_successful=False,
        )
        history.add(
            SolutionAttempt(3, "c", "o", False, 0.5, "f"),
            persist_if_successful=False,
        )

        # Manually persist best
        result = history.persist_best()
        assert result is True

        # Verify persisted
        count = store.count_by_task("test_persist_best")
        assert count == 1

    def test_get_historical_context(self, tracker_and_store):
        """get_historical_context() retrieves past solutions."""
        tracker, store = tracker_and_store

        # Pre-populate store with historical solutions
        from deliberate.tracking.solution_store import SolutionRecord

        for i in range(3):
            record = SolutionRecord(
                id=f"hist_{i}",
                task_hash="test_historical",
                solution_type="iteration_attempt",
                agent="claude",
                success=True,
                overall_score=0.9 + i * 0.03,
                code_content=f"def foo{i}(): return {i}",
                feedback_summary="All passed",
                is_valid=True,
                generation=i + 1,
            )
            store.add(record, immediate=True)

        # Create history and get historical context
        history = SolutionHistory()
        history.configure(
            solution_store=store,
            task_hash="test_historical",
        )

        historical = history.get_historical_context(max_solutions=5, min_score=0.9)

        assert len(historical) == 3
        # Should be highest scores first
        assert historical[0].soft_score >= historical[1].soft_score
        # Should have historical marker
        assert historical[0].metadata.get("historical") is True

    def test_historical_context_empty_no_store(self):
        """get_historical_context() returns empty without store."""
        history = SolutionHistory()
        historical = history.get_historical_context()
        assert historical == []

    def test_attempt_to_record_conversion(self, tracker_and_store):
        """Verify attempt is correctly converted to record."""
        tracker, store = tracker_and_store

        history = SolutionHistory()
        history.configure(
            solution_store=store,
            task_hash="test_conversion",
            workflow_id="wf_456",
            agent="gpt-4",
        )

        attempt = SolutionAttempt(
            iteration=5,
            code="def bar(): return 'hello'",
            output="hello",
            success=True,
            soft_score=0.95,
            feedback="Almost perfect",
            error=None,
            token_usage=1000,
            duration_seconds=2.5,
        )
        history.add(attempt, persist_if_successful=True)

        # Retrieve and verify
        records = store.get_best_for_task("test_conversion")
        assert len(records) == 1
        record = records[0]

        assert record.task_hash == "test_conversion"
        assert record.workflow_id == "wf_456"
        assert record.solution_type == "iteration_attempt"
        assert record.agent == "gpt-4"
        assert record.code_content == "def bar(): return 'hello'"
        assert record.overall_score == 0.95
        assert record.generation == 5
        assert record.token_usage == 1000
        assert record.duration_seconds == 2.5
