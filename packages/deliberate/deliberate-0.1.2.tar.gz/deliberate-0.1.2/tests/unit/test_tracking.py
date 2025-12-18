"""Tests for agent performance tracking."""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from deliberate.tracking import (
    AgentPerformanceTracker,
    ExecutionRecord,
    PlanningRecord,
    ReviewRecord,
    WorkflowRecord,
    get_tracker,
    record_jury_result,
    reset_tracker,
)
from deliberate.types import ExecutionResult, JuryResult, Plan, Review, Score, Verdict, VoteResult


@pytest.fixture
def temp_db():
    """Create a temporary database path for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_performance.duckdb"
        yield db_path
        # Cleanup happens automatically when tmpdir is deleted


@pytest.fixture
def tracker(temp_db):
    """Create a tracker with temporary database."""
    t = AgentPerformanceTracker(temp_db)
    yield t
    t.close()


@pytest.fixture(autouse=True)
def reset_global_tracker():
    """Reset global tracker before each test."""
    reset_tracker()
    yield
    reset_tracker()


class TestAgentPerformanceTracker:
    """Tests for AgentPerformanceTracker."""

    def test_init_creates_tables(self, tracker):
        """Test that initialization creates required tables."""
        # Should not raise any errors
        assert tracker.get_workflow_count() == 0

    def test_record_workflow(self, tracker):
        """Test recording a workflow."""
        record = WorkflowRecord(
            workflow_id="wf-test-123",
            task_hash="abc123",
            task_preview="Test task",
            success=True,
            total_duration_seconds=10.5,
            total_tokens=1000,
            total_cost_usd=0.05,
            selected_planner="claude",
            winning_executor="gemini",
            refinement_triggered=False,
            final_score=0.85,
            initial_score=0.85,
            timestamp=datetime.now(),
        )
        tracker.record_workflow(record)
        assert tracker.get_workflow_count() == 1

    def test_record_planning(self, tracker):
        """Test recording planning performance."""
        # First record a workflow
        workflow = WorkflowRecord(
            workflow_id="wf-plan-test",
            task_hash="xyz",
            task_preview="Planning test",
            success=True,
            total_duration_seconds=5.0,
            total_tokens=500,
            total_cost_usd=0.02,
            selected_planner="claude",
            winning_executor=None,
            refinement_triggered=False,
            final_score=0.9,
            initial_score=0.9,
            timestamp=datetime.now(),
        )
        tracker.record_workflow(workflow)

        # Record planning
        record = PlanningRecord(
            agent="claude",
            was_selected=True,
            led_to_success=True,
            final_score=0.9,
            token_usage=200,
            timestamp=datetime.now(),
        )
        tracker.record_planning("wf-plan-test", record)

        # Check stats
        stats = tracker.get_planner_stats("claude")
        assert len(stats) == 1
        assert stats[0].agent == "claude"
        assert stats[0].wins == 1
        assert stats[0].win_rate == 1.0

    def test_record_execution(self, tracker):
        """Test recording execution performance."""
        workflow = WorkflowRecord(
            workflow_id="wf-exec-test",
            task_hash="xyz",
            task_preview="Execution test",
            success=True,
            total_duration_seconds=15.0,
            total_tokens=2000,
            total_cost_usd=0.10,
            selected_planner=None,
            winning_executor="claude",
            refinement_triggered=False,
            final_score=0.85,
            initial_score=0.85,
            timestamp=datetime.now(),
        )
        tracker.record_workflow(workflow)

        # Record executions
        record1 = ExecutionRecord(
            agent="claude",
            was_winner=True,
            success=True,
            error_category=None,
            score=0.85,
            rank=1,
            total_candidates=2,
            token_usage=1000,
            duration_seconds=10.0,
            timestamp=datetime.now(),
        )
        record2 = ExecutionRecord(
            agent="gemini",
            was_winner=False,
            success=True,
            error_category=None,
            score=0.75,
            rank=2,
            total_candidates=2,
            token_usage=800,
            duration_seconds=8.0,
            timestamp=datetime.now(),
        )
        tracker.record_execution("wf-exec-test", record1)
        tracker.record_execution("wf-exec-test", record2)

        # Check stats
        stats = tracker.get_executor_stats()
        assert len(stats) == 2

        # Claude should be first (winner)
        claude_stats = next(s for s in stats if s.agent == "claude")
        assert claude_stats.wins == 1
        assert claude_stats.win_rate == 1.0

        gemini_stats = next(s for s in stats if s.agent == "gemini")
        assert gemini_stats.wins == 0
        assert gemini_stats.win_rate == 0.0

    def test_record_review(self, tracker):
        """Test recording review accuracy."""
        workflow = WorkflowRecord(
            workflow_id="wf-review-test",
            task_hash="xyz",
            task_preview="Review test",
            success=True,
            total_duration_seconds=20.0,
            total_tokens=3000,
            total_cost_usd=0.15,
            selected_planner=None,
            winning_executor="exec-1",
            refinement_triggered=False,
            final_score=0.80,
            initial_score=0.80,
            timestamp=datetime.now(),
        )
        tracker.record_workflow(workflow)

        # Record reviews
        record1 = ReviewRecord(
            agent="reviewer1",
            candidate_id="exec-1",
            score_given=0.9,
            review_comment="Good job",
            was_candidate_winner=True,
            final_winner_score=0.9,
            timestamp=datetime.now(),
        )
        record2 = ReviewRecord(
            agent="reviewer1",
            candidate_id="exec-2",
            score_given=0.7,
            review_comment="Okay job",
            was_candidate_winner=False,
            final_winner_score=0.9,
            timestamp=datetime.now(),
        )
        tracker.record_review("wf-review-test", record1)
        tracker.record_review("wf-review-test", record2)

        # Check stats
        stats = tracker.get_reviewer_stats("reviewer1")
        assert len(stats) == 1
        assert stats[0].agent == "reviewer1"
        # 50% accuracy (gave highest to winner 1 out of 2 times)
        assert stats[0].review_accuracy == 0.5

    def test_get_best_planners(self, tracker):
        """Test getting top planners."""
        # Record multiple planners
        for i, agent in enumerate(["claude", "gemini", "codex"]):
            workflow = WorkflowRecord(
                workflow_id=f"wf-{i}",
                task_hash="xyz",
                task_preview=f"Test {i}",
                success=True,
                total_duration_seconds=5.0,
                total_tokens=500,
                total_cost_usd=0.02,
                selected_planner=agent,
                winning_executor=None,
                refinement_triggered=False,
                final_score=0.8 + i * 0.05,
                initial_score=0.8 + i * 0.05,
                timestamp=datetime.now(),
            )
            tracker.record_workflow(workflow)

            record = PlanningRecord(
                agent=agent,
                was_selected=True,
                led_to_success=True,
                final_score=0.8 + i * 0.05,
                token_usage=200,
                timestamp=datetime.now(),
            )
            tracker.record_planning(f"wf-{i}", record)

        best = tracker.get_best_planners(2)
        assert len(best) == 2
        # All have 100% win rate since each was selected once

    def test_get_best_executors(self, tracker):
        """Test getting top executors."""
        # Similar to planners test
        workflow = WorkflowRecord(
            workflow_id="wf-best-exec",
            task_hash="xyz",
            task_preview="Best executor test",
            success=True,
            total_duration_seconds=10.0,
            total_tokens=1000,
            total_cost_usd=0.05,
            selected_planner=None,
            winning_executor="top-agent",
            refinement_triggered=False,
            final_score=0.95,
            initial_score=0.95,
            timestamp=datetime.now(),
        )
        tracker.record_workflow(workflow)

        record = ExecutionRecord(
            agent="top-agent",
            was_winner=True,
            success=True,
            error_category=None,
            score=0.95,
            rank=1,
            total_candidates=1,
            token_usage=500,
            duration_seconds=5.0,
            timestamp=datetime.now(),
        )
        tracker.record_execution("wf-best-exec", record)

        best = tracker.get_best_executors(1)
        assert len(best) == 1
        assert best[0].agent == "top-agent"

    def test_get_leaderboard(self, tracker):
        """Test getting complete leaderboard."""
        leaderboard = tracker.get_leaderboard()
        assert "planners" in leaderboard
        assert "executors" in leaderboard
        assert "reviewers" in leaderboard

    def test_get_recent_workflows(self, tracker):
        """Test getting recent workflows."""
        for i in range(5):
            workflow = WorkflowRecord(
                workflow_id=f"wf-recent-{i}",
                task_hash="xyz",
                task_preview=f"Recent {i}",
                success=True,
                total_duration_seconds=5.0,
                total_tokens=500,
                total_cost_usd=0.02,
                selected_planner="claude",
                winning_executor="gemini",
                refinement_triggered=False,
                final_score=0.8,
                initial_score=0.8,
                timestamp=datetime.now(),
            )
            tracker.record_workflow(workflow)

        recent = tracker.get_recent_workflows(3)
        assert len(recent) == 3

    def test_export_stats(self, tracker):
        """Test exporting all stats."""
        stats = tracker.export_stats()
        assert "total_workflows" in stats
        assert "planners" in stats
        assert "executors" in stats
        assert "reviewers" in stats
        assert stats["total_workflows"] == 0


class TestRecordJuryResult:
    """Tests for record_jury_result function."""

    def test_record_jury_result_basic(self, temp_db):
        """Test recording a JuryResult."""
        tracker = AgentPerformanceTracker(temp_db)

        result = JuryResult(
            task="Test task for jury",
            selected_plan=Plan(
                id="plan-1",
                agent="claude",
                content="My plan",
                token_usage=100,
            ),
            execution_results=[
                ExecutionResult(
                    id="exec-1",
                    agent="claude",
                    worktree_path=None,
                    diff="some diff",
                    summary="Summary",
                    success=True,
                    token_usage=500,
                    duration_seconds=10.0,
                ),
                ExecutionResult(
                    id="exec-2",
                    agent="gemini",
                    worktree_path=None,
                    diff="other diff",
                    summary="Other summary",
                    success=True,
                    token_usage=400,
                    duration_seconds=8.0,
                ),
            ],
            reviews=[
                Review(
                    reviewer="reviewer1",
                    candidate_id="exec-1",
                    scores=[Score("correctness", 0.9, 9.0)],
                    overall_score=0.9,
                    recommendation=Verdict.ACCEPT,
                    token_usage=50,
                ),
                Review(
                    reviewer="reviewer1",
                    candidate_id="exec-2",
                    scores=[Score("correctness", 0.8, 8.0)],
                    overall_score=0.8,
                    recommendation=Verdict.ACCEPT,
                    token_usage=50,
                ),
            ],
            vote_result=VoteResult(
                winner_id="exec-1",
                rankings=["exec-1", "exec-2"],
                scores={"exec-1": 0.9, "exec-2": 0.8},
                vote_breakdown={"reviewer1": {"exec-1": 0.9, "exec-2": 0.8}},
                confidence=0.7,
            ),
            final_diff="some diff",
            summary="Test summary",
            success=True,
            total_duration_seconds=25.0,
            total_token_usage=1100,
            total_cost_usd=0.05,
        )

        workflow_id = record_jury_result(result, tracker)
        assert workflow_id.startswith("wf-")

        # Verify data was recorded
        assert tracker.get_workflow_count() == 1

        planner_stats = tracker.get_planner_stats("claude")
        assert len(planner_stats) == 1
        assert planner_stats[0].wins == 1

        executor_stats = tracker.get_executor_stats()
        assert len(executor_stats) == 2

        tracker.close()

    def test_record_jury_result_no_vote(self, temp_db):
        """Test recording result without vote result."""
        tracker = AgentPerformanceTracker(temp_db)

        result = JuryResult(
            task="Simple task",
            selected_plan=None,
            execution_results=[
                ExecutionResult(
                    id="exec-1",
                    agent="claude",
                    worktree_path=None,
                    diff="diff",
                    summary="Summary",
                    success=True,
                    token_usage=500,
                    duration_seconds=10.0,
                ),
            ],
            reviews=[],
            vote_result=None,
            final_diff="diff",
            summary="Summary",
            success=True,
            total_duration_seconds=10.0,
            total_token_usage=500,
            total_cost_usd=0.02,
        )

        record_jury_result(result, tracker)
        assert tracker.get_workflow_count() == 1

        tracker.close()


class TestClearStats:
    """Tests for clearing tracking data."""

    def test_clear_all(self, temp_db):
        """Test clearing all tracking data."""
        tracker = AgentPerformanceTracker(temp_db)

        # Add some data
        for i in range(3):
            workflow = WorkflowRecord(
                workflow_id=f"wf-clear-{i}",
                task_hash="xyz",
                task_preview=f"Test {i}",
                success=True,
                total_duration_seconds=5.0,
                total_tokens=500,
                total_cost_usd=0.02,
                selected_planner="claude",
                winning_executor="gemini",
                refinement_triggered=False,
                final_score=0.8,
                initial_score=0.8,
                timestamp=datetime.now(),
            )
            tracker.record_workflow(workflow)

            record = PlanningRecord(
                agent="claude",
                was_selected=True,
                led_to_success=True,
                final_score=0.8,
                token_usage=200,
                timestamp=datetime.now(),
            )
            tracker.record_planning(f"wf-clear-{i}", record)

        assert tracker.get_workflow_count() == 3
        assert len(tracker.get_planner_stats()) > 0

        # Clear all
        deleted = tracker.clear_all()
        assert deleted == 3
        assert tracker.get_workflow_count() == 0
        assert len(tracker.get_planner_stats()) == 0

        tracker.close()

    def test_clear_empty_db(self, temp_db):
        """Test clearing empty database."""
        tracker = AgentPerformanceTracker(temp_db)
        deleted = tracker.clear_all()
        assert deleted == 0
        tracker.close()


class TestGlobalTracker:
    """Tests for global tracker singleton."""

    def test_get_tracker_returns_same_instance(self, temp_db):
        """Test that get_tracker returns singleton."""
        tracker1 = get_tracker(temp_db)
        tracker2 = get_tracker(temp_db)
        assert tracker1 is tracker2

    def test_reset_tracker(self, temp_db):
        """Test resetting the global tracker."""
        tracker1 = get_tracker(temp_db)
        reset_tracker()
        # After reset, should get new instance
        tracker2 = get_tracker(temp_db)
        assert tracker1 is not tracker2
