"""Tests for budget tracking."""

import pytest

from deliberate.budget.tracker import AgentUsage, BudgetExceededError, BudgetTracker


class TestBudgetTracker:
    """Tests for BudgetTracker."""

    def test_record_usage(self):
        """Should track token and request usage."""
        tracker = BudgetTracker(max_total_tokens=1000)
        tracker.record_usage("agent1", tokens=100, cost_usd=0.01)

        totals = tracker.get_totals()
        assert totals["tokens"] == 100
        assert totals["cost_usd"] == 0.01
        assert totals["requests_by_agent"]["agent1"] == 1

    def test_multiple_agents(self):
        """Should track usage per agent."""
        tracker = BudgetTracker(max_total_tokens=1000)
        tracker.record_usage("agent1", tokens=100)
        tracker.record_usage("agent2", tokens=200)
        tracker.record_usage("agent1", tokens=50)

        totals = tracker.get_totals()
        assert totals["tokens"] == 350
        assert totals["tokens_by_agent"]["agent1"] == 150
        assert totals["tokens_by_agent"]["agent2"] == 200

    def test_token_limit_exceeded(self):
        """Should raise when token limit exceeded."""
        tracker = BudgetTracker(max_total_tokens=100)
        tracker.record_usage("agent1", tokens=50)
        tracker.record_usage("agent1", tokens=40)

        with pytest.raises(BudgetExceededError, match="Token limit"):
            tracker.record_usage("agent1", tokens=20)

    def test_cost_limit_exceeded(self):
        """Should raise when cost limit exceeded."""
        tracker = BudgetTracker(max_cost_usd=1.0)
        tracker.record_usage("agent1", tokens=100, cost_usd=0.5)
        tracker.record_usage("agent1", tokens=100, cost_usd=0.4)

        with pytest.raises(BudgetExceededError, match="Cost limit"):
            tracker.record_usage("agent1", tokens=100, cost_usd=0.2)

    def test_request_limit_per_agent(self):
        """Should raise when request limit per agent exceeded."""
        tracker = BudgetTracker(max_requests_per_agent=2)
        tracker.record_usage("agent1", tokens=10)
        tracker.record_usage("agent1", tokens=10)

        with pytest.raises(BudgetExceededError, match="Request limit"):
            tracker.record_usage("agent1", tokens=10)

    def test_separate_agent_limits(self):
        """Each agent should have separate request limits."""
        tracker = BudgetTracker(max_requests_per_agent=2)
        tracker.record_usage("agent1", tokens=10)
        tracker.record_usage("agent1", tokens=10)
        # agent2 should still be able to make requests
        tracker.record_usage("agent2", tokens=10)
        tracker.record_usage("agent2", tokens=10)

    def test_can_afford_true(self):
        """Should return True when budget allows."""
        tracker = BudgetTracker(max_total_tokens=1000, max_requests_per_agent=10)
        tracker.record_usage("agent1", tokens=100)

        assert tracker.can_afford(500, "agent1")

    def test_can_afford_false_tokens(self):
        """Should return False when token budget insufficient."""
        tracker = BudgetTracker(max_total_tokens=100)
        tracker.record_usage("agent1", tokens=90)

        assert not tracker.can_afford(20, "agent1")

    def test_can_afford_false_requests(self):
        """Should return False when request limit reached."""
        tracker = BudgetTracker(max_requests_per_agent=2)
        tracker.record_usage("agent1", tokens=10)
        tracker.record_usage("agent1", tokens=10)

        assert not tracker.can_afford(10, "agent1")

    def test_get_remaining(self):
        """Should calculate remaining budget correctly."""
        tracker = BudgetTracker(
            max_total_tokens=1000,
            max_cost_usd=10.0,
            hard_timeout_seconds=3600,
        )
        tracker.record_usage("agent1", tokens=300, cost_usd=3.0)

        remaining = tracker.get_remaining()
        assert remaining["tokens"] == 700
        assert remaining["cost_usd"] == 7.0
        assert remaining["time_seconds"] > 3500  # Approximately

    def test_reset(self):
        """Should clear all usage on reset."""
        tracker = BudgetTracker()
        tracker.record_usage("agent1", tokens=100, cost_usd=1.0)
        tracker.reset()

        totals = tracker.get_totals()
        assert totals["tokens"] == 0
        assert totals["cost_usd"] == 0
        assert totals["requests_by_agent"] == {}

    def test_check_before_call(self):
        """Should pre-check if call is affordable."""
        tracker = BudgetTracker(max_total_tokens=100)
        tracker.record_usage("agent1", tokens=90)

        with pytest.raises(BudgetExceededError):
            tracker.check_before_call("agent1", estimated_tokens=20)


class TestAgentUsage:
    """Tests for AgentUsage dataclass."""

    def test_default_values(self):
        """Should have sensible defaults."""
        usage = AgentUsage()
        assert usage.tokens == 0
        assert usage.requests == 0
        assert usage.cost_usd == 0.0
