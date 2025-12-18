"""Unit tests for the planning phase."""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from deliberate.adapters.base import AdapterResponse, ModelAdapter
from deliberate.budget.tracker import BudgetTracker
from deliberate.phases.planning import IterativePlanningConfig, PlanningPhase
from deliberate.types import Plan


@pytest.fixture
def mock_budget():
    """Mock the budget tracker."""
    return MagicMock(spec=BudgetTracker)


@pytest.fixture
def mock_adapters():
    """Create mock adapters."""
    adapter1 = MagicMock(spec=ModelAdapter)
    adapter1.call = AsyncMock()
    adapter1.call.return_value = AdapterResponse(
        content="Plan content 1",
        token_usage=100,
        duration_seconds=1.0,
    )
    adapter1.estimate_cost.return_value = 0.01

    adapter2 = MagicMock(spec=ModelAdapter)
    adapter2.call = AsyncMock()
    adapter2.call.return_value = AdapterResponse(
        content="Plan content 2",
        token_usage=100,
        duration_seconds=1.0,
    )
    adapter2.estimate_cost.return_value = 0.01

    return {"agent1": adapter1, "agent2": adapter2}


class TestPlanningPhase:
    """Tests for PlanningPhase logic."""

    @pytest.mark.asyncio
    async def test_collect_plans_success(self, mock_budget, mock_adapters):
        """Should collect plans from all agents."""
        phase = PlanningPhase(
            agents=["agent1", "agent2"],
            adapters=mock_adapters,
            budget=mock_budget,
        )

        plans = await phase._collect_plans("Test task")

        assert len(plans) == 2
        assert plans[0].agent == "agent1"
        assert plans[1].agent == "agent2"
        assert plans[0].content == "Plan content 1"

        # Verify budget recording
        assert mock_budget.record_usage.call_count == 2
        mock_budget.record_usage.assert_any_call("agent1", 100, 0.01)

    @pytest.mark.asyncio
    async def test_collect_plans_partial_failure(self, mock_budget, mock_adapters):
        """Should continue if one agent fails."""
        # Make agent2 fail
        mock_adapters["agent2"].call.side_effect = RuntimeError("API Error")

        phase = PlanningPhase(
            agents=["agent1", "agent2"],
            adapters=mock_adapters,
            budget=mock_budget,
        )

        plans = await phase._collect_plans("Test task")

        assert len(plans) == 1
        assert plans[0].agent == "agent1"
        # Should verify exception was logged/printed (omitted for unit test simplicity)

    @pytest.mark.asyncio
    async def test_select_plan_first(self, mock_budget, mock_adapters):
        """Should select first plan by default."""
        phase = PlanningPhase(
            agents=["agent1", "agent2"],
            adapters=mock_adapters,
            budget=mock_budget,
            selection_method="first",
        )

        plans = [
            Plan(id="p1", agent="agent1", content="c1", token_usage=10),
            Plan(id="p2", agent="agent2", content="c2", token_usage=10),
        ]

        selected = await phase._select_plan("task", plans)
        assert selected == plans[0]

    @pytest.mark.asyncio
    async def test_judge_select_success(self, mock_budget, mock_adapters):
        """Should use judge to select plan."""
        # Setup judge adapter
        judge_adapter = AsyncMock()
        judge_adapter.call.return_value = AdapterResponse(
            content="Selecting now.",
            token_usage=50,
            duration_seconds=1.0,
            raw_response={
                "choices": [
                    {
                        "message": {
                            "tool_calls": [
                                {
                                    "function": {
                                        "name": "select_plan",
                                        "arguments": json.dumps({"plan_id": 2, "reasoning": "Covers more risks"}),
                                    }
                                }
                            ]
                        }
                    }
                ]
            },
        )
        mock_adapters["judge"] = judge_adapter

        phase = PlanningPhase(
            agents=["agent1", "agent2"],
            adapters=mock_adapters,
            budget=mock_budget,
            selection_method="llm_judge",
            judge_agent="judge",
        )

        plans = [
            Plan(id="p1", agent="agent1", content="c1", token_usage=10),
            Plan(id="p2", agent="agent2", content="c2", token_usage=10),
        ]

        selected = await phase._select_plan("task", plans)

        # Expect Plan 2 (index 1)
        assert selected == plans[1]

        # Verify judge was called with both plans
        call_args = judge_adapter.call.call_args[0][0]
        assert "Plan 1" in call_args
        assert "Plan 2" in call_args

    @pytest.mark.asyncio
    async def test_judge_select_text_match(self, mock_budget, mock_adapters):
        """Should still parse textual plan numbers when tools are not used."""
        judge_adapter = AsyncMock()
        judge_adapter.call.return_value = AdapterResponse(
            content="I have reviewed the plans. The best one is Plan 2 because...",
            token_usage=50,
            duration_seconds=1.0,
        )
        mock_adapters["judge"] = judge_adapter

        phase = PlanningPhase(
            agents=["agent1", "agent2"],
            adapters=mock_adapters,
            budget=mock_budget,
            selection_method="llm_judge",
            judge_agent="judge",
        )

        plans = [
            Plan(id="p1", agent="agent1", content="c1", token_usage=10),
            Plan(id="p2", agent="agent2", content="c2", token_usage=10),
        ]

        selected = await phase._select_plan("task", plans)
        assert selected == plans[1]

    @pytest.mark.asyncio
    async def test_judge_select_fallback(self, mock_budget, mock_adapters):
        """Should fallback to first plan if judge fails to pick."""
        judge_adapter = AsyncMock()
        judge_adapter.call.return_value = AdapterResponse(
            content="Both plans look interesting.",  # No "Plan N" pattern
            token_usage=50,
            duration_seconds=1.0,
        )
        mock_adapters["judge"] = judge_adapter

        phase = PlanningPhase(
            agents=["agent1", "agent2"],
            adapters=mock_adapters,
            budget=mock_budget,
            selection_method="llm_judge",
            judge_agent="judge",
        )

        plans = [
            Plan(id="p1", agent="agent1", content="c1", token_usage=10),
            Plan(id="p2", agent="agent2", content="c2", token_usage=10),
        ]

        selected = await phase._select_plan("task", plans)
        assert selected == plans[0]  # Fallback

    @pytest.mark.asyncio
    async def test_run_debate(self, mock_budget, mock_adapters):
        """Should run debate rounds."""
        phase = PlanningPhase(
            agents=["agent1", "agent2"],
            adapters=mock_adapters,
            budget=mock_budget,
            debate_enabled=True,
            debate_rounds=1,
        )

        plans = [
            Plan(id="p1", agent="agent1", content="c1", token_usage=10),
            Plan(id="p2", agent="agent2", content="c2", token_usage=10),
        ]

        messages = await phase._run_debate("task", plans)

        # 2 agents * 1 round = 2 messages
        assert len(messages) == 2
        assert messages[0].agent == "agent1"
        assert messages[0].reply_to == "agent2"  # agent1 critiques agent2 (circular)

        # Verify prompts contained other plan
        call_args_1 = mock_adapters["agent1"].call.call_args[0][0]
        assert "c2" in call_args_1  # agent1 sees plan 2 content


class TestIterativePlanningConfig:
    """Tests for IterativePlanningConfig."""

    def test_default_values(self):
        """Default configuration values are sensible."""
        config = IterativePlanningConfig()

        assert config.enabled is False
        assert config.max_iterations == 5
        assert config.success_threshold == 0.9
        assert config.critic_agent is None
        assert config.require_structure is True
        assert config.weights is None

    def test_custom_values(self):
        """Can set custom configuration values."""
        config = IterativePlanningConfig(
            enabled=True,
            max_iterations=10,
            success_threshold=0.8,
            critic_agent="critic-gpt",
            require_structure=False,
            weights={"feasibility": 0.4, "clarity": 0.6},
        )

        assert config.enabled is True
        assert config.max_iterations == 10
        assert config.success_threshold == 0.8
        assert config.critic_agent == "critic-gpt"
        assert config.require_structure is False
        assert config.weights == {"feasibility": 0.4, "clarity": 0.6}


class TestIterativePlanning:
    """Tests for iterative planning mode."""

    @pytest.mark.asyncio
    async def test_run_uses_iterative_mode_when_enabled(self, mock_budget, mock_adapters):
        """Should use iterative planning when enabled."""
        # Setup adapter to return a structured plan
        plan_response = """
<plan>
## Implementation Steps
1. Create the user model
2. Add authentication endpoints
3. Implement session management

## Risks and Concerns
- Security vulnerabilities in auth flow
- Session expiration handling

## Affected Files
- models/user.py
- routes/auth.py
</plan>
"""
        mock_adapters["agent1"].call.return_value = AdapterResponse(
            content=plan_response,
            token_usage=200,
            duration_seconds=2.0,
        )

        iterative_config = IterativePlanningConfig(
            enabled=True,
            max_iterations=1,  # Only one iteration for testing
            success_threshold=0.5,  # Low threshold for test
            require_structure=True,
        )

        phase = PlanningPhase(
            agents=["agent1"],
            adapters=mock_adapters,
            budget=mock_budget,
            iterative_config=iterative_config,
        )

        selected, all_plans, debate_messages = await phase.run("Build user auth")

        # Should return a plan
        assert selected is not None
        assert "iterative" in selected.id.lower() or selected.agent == "agent1"
        # Should have one plan
        assert len(all_plans) == 1
        # No debate messages in iterative mode
        assert len(debate_messages) == 0

    @pytest.mark.asyncio
    async def test_iterative_planning_returns_none_with_no_agents(self, mock_budget):
        """Should return None when no agents available."""
        iterative_config = IterativePlanningConfig(enabled=True)

        phase = PlanningPhase(
            agents=[],
            adapters={},
            budget=mock_budget,
            iterative_config=iterative_config,
        )

        selected, all_plans, debate_messages = await phase.run("Test task")

        assert selected is None
        assert all_plans == []
        assert debate_messages == []

    @pytest.mark.asyncio
    async def test_iterative_planning_returns_none_with_missing_adapter(self, mock_budget):
        """Should return None when adapter not found."""
        iterative_config = IterativePlanningConfig(enabled=True)

        phase = PlanningPhase(
            agents=["missing_agent"],
            adapters={},  # No adapters
            budget=mock_budget,
            iterative_config=iterative_config,
        )

        selected, all_plans, debate_messages = await phase.run("Test task")

        assert selected is None
        assert all_plans == []

    @pytest.mark.asyncio
    async def test_iterative_planning_uses_critic_when_configured(self, mock_budget, mock_adapters):
        """Should use critic agent when configured."""
        # Setup planner response
        plan_content = """
<plan>
## Implementation Steps
1. Step one
2. Step two

## Risks and Concerns
- Some risk

## Affected Files
- file.py
</plan>
"""
        mock_adapters["agent1"].call.return_value = AdapterResponse(
            content=plan_content,
            token_usage=150,
            duration_seconds=1.5,
        )

        # Setup critic adapter
        critic_adapter = MagicMock(spec=ModelAdapter)
        critic_adapter.call = AsyncMock()
        critic_adapter.call.return_value = AdapterResponse(
            content="""
{
    "feasibility": 0.9,
    "completeness": 0.85,
    "clarity": 0.88,
    "risk_awareness": 0.92,
    "overall_score": 0.89,
    "feedback": "Well structured plan",
    "suggestions": []
}
""",
            token_usage=100,
            duration_seconds=1.0,
        )
        mock_adapters["critic"] = critic_adapter

        iterative_config = IterativePlanningConfig(
            enabled=True,
            max_iterations=1,
            success_threshold=0.5,
            critic_agent="critic",
            require_structure=True,
        )

        phase = PlanningPhase(
            agents=["agent1"],
            adapters=mock_adapters,
            budget=mock_budget,
            iterative_config=iterative_config,
        )

        selected, all_plans, debate_messages = await phase.run("Build feature X")

        # Should get a plan
        assert selected is not None
        # Critic should have been called
        assert critic_adapter.call.called

    @pytest.mark.asyncio
    async def test_build_iterative_planning_prompt(self, mock_budget, mock_adapters):
        """Should build proper prompt for iterative planning."""
        phase = PlanningPhase(
            agents=["agent1"],
            adapters=mock_adapters,
            budget=mock_budget,
        )

        prompt = phase._build_iterative_planning_prompt("Create a REST API")

        # Should contain the task
        assert "Create a REST API" in prompt
        # Should contain requirements
        assert "Numbered steps" in prompt
        assert "Risk section" in prompt
        assert "Affected files" in prompt
        # Should have format instructions
        assert "<plan>" in prompt
        assert "</plan>" in prompt

    @pytest.mark.asyncio
    async def test_classic_mode_still_works(self, mock_budget, mock_adapters):
        """Classic mode should work when iterative not enabled."""
        phase = PlanningPhase(
            agents=["agent1", "agent2"],
            adapters=mock_adapters,
            budget=mock_budget,
            selection_method="first",
            # iterative_config defaults to disabled
        )

        selected, all_plans, debate_messages = await phase.run("Build something")

        # Should use classic mode
        assert selected is not None
        assert len(all_plans) == 2  # Both agents contribute
        assert selected.agent == "agent1"  # First plan selected

    @pytest.mark.asyncio
    async def test_iterative_planning_handles_exception(self, mock_budget, mock_adapters):
        """Should handle exceptions gracefully."""
        # Make the adapter throw an exception
        mock_adapters["agent1"].call.side_effect = RuntimeError("API Error")

        iterative_config = IterativePlanningConfig(
            enabled=True,
            max_iterations=1,
            success_threshold=0.5,
        )

        phase = PlanningPhase(
            agents=["agent1"],
            adapters=mock_adapters,
            budget=mock_budget,
            iterative_config=iterative_config,
        )

        selected, all_plans, debate_messages = await phase.run("Test task")

        # Exception is caught - returns empty plan or None depending on result
        # The key is that it doesn't crash
        if selected is not None:
            # When IterativeSolver returns a result even on failure,
            # the plan content should be empty
            assert selected.content == ""
        assert debate_messages == []
