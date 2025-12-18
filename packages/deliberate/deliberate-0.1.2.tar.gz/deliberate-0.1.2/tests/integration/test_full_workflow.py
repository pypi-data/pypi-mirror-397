"""Integration tests for the full deliberate workflow."""

from unittest.mock import MagicMock, patch

import pytest

from deliberate.config import (
    AgentConfig,
    DeliberateConfig,
    ExecutionConfig,
    LimitsConfig,
    PlanningConfig,
    ReviewConfig,
    WorkflowConfig,
)
from deliberate.orchestrator import Orchestrator


@pytest.fixture(autouse=True)
def mock_tracker():
    """Mock tracker to avoid DuckDB lock issues."""
    with patch("deliberate.orchestrator.get_tracker") as mock:
        mock.return_value = MagicMock()
        yield mock


@pytest.fixture
def full_config():
    """Create a full config with multiple agents."""
    return DeliberateConfig(
        agents={
            "planner1": AgentConfig(
                type="fake",
                behavior="planner",
                capabilities=["planner"],
            ),
            "planner2": AgentConfig(
                type="fake",
                behavior="planner",
                capabilities=["planner"],
            ),
            "executor": AgentConfig(
                type="fake",
                behavior="planner",
                capabilities=["executor"],
            ),
            "reviewer1": AgentConfig(
                type="fake",
                behavior="critic",
                capabilities=["reviewer"],
            ),
            "reviewer2": AgentConfig(
                type="fake",
                behavior="critic",
                capabilities=["reviewer"],
            ),
        },
        workflow=WorkflowConfig(
            planning=PlanningConfig(
                enabled=True,
                agents=["planner1", "planner2"],
            ),
            execution=ExecutionConfig(
                enabled=True,
                agents=["executor"],
            ),
            review=ReviewConfig(
                enabled=True,
                agents=["reviewer1", "reviewer2"],
            ),
        ),
        limits=LimitsConfig(),
    )


class TestFullWorkflow:
    """Integration tests for the complete workflow."""

    @pytest.mark.asyncio
    async def test_planning_only(self, temp_git_repo, minimal_config):
        """Should run planning phase only."""
        minimal_config.workflow.execution.enabled = False
        minimal_config.workflow.review.enabled = False

        orchestrator = Orchestrator(minimal_config, temp_git_repo)
        result = await orchestrator.run("Add a hello world function")

        assert result.success
        assert result.selected_plan is not None
        assert "Plan" in result.selected_plan.content
        assert result.execution_results == []
        assert result.reviews == []

    @pytest.mark.asyncio
    async def test_planning_and_execution(self, temp_git_repo, minimal_config):
        """Should run planning and execution phases."""
        minimal_config.workflow.review.enabled = False

        orchestrator = Orchestrator(minimal_config, temp_git_repo)
        result = await orchestrator.run("Add a utility function")

        assert result.success
        assert result.selected_plan is not None
        assert len(result.execution_results) > 0
        assert result.execution_results[0].success
        assert result.reviews == []

    @pytest.mark.asyncio
    async def test_full_workflow_with_fakes(self, temp_git_repo, full_config):
        """Should run complete workflow with fake adapters."""
        orchestrator = Orchestrator(full_config, temp_git_repo)
        result = await orchestrator.run("Refactor the main module")

        assert result.success
        assert result.selected_plan is not None
        assert len(result.execution_results) > 0
        # Reviews may be empty if reviewer and executor are different
        # and executor didn't produce a diff

    @pytest.mark.asyncio
    async def test_execution_without_planning(self, temp_git_repo, minimal_config):
        """Should run execution without planning."""
        minimal_config.workflow.planning.enabled = False
        minimal_config.workflow.review.enabled = False

        orchestrator = Orchestrator(minimal_config, temp_git_repo)
        result = await orchestrator.run("Fix a bug")

        assert result.success
        assert result.selected_plan is None
        assert len(result.execution_results) > 0

    @pytest.mark.asyncio
    async def test_budget_tracking(self, temp_git_repo, minimal_config):
        """Should track budget across workflow."""
        orchestrator = Orchestrator(minimal_config, temp_git_repo)
        result = await orchestrator.run("Add documentation")

        assert result.total_token_usage > 0
        assert result.total_duration_seconds > 0

    @pytest.mark.asyncio
    async def test_worktree_cleanup(self, temp_git_repo, minimal_config):
        """Should cleanup worktrees after workflow."""
        orchestrator = Orchestrator(minimal_config, temp_git_repo)
        await orchestrator.run("Add a feature")

        # Worktrees should be cleaned up
        assert orchestrator.worktrees.active_count == 0


class TestWorkflowEdgeCases:
    """Tests for edge cases in the workflow."""

    @pytest.mark.asyncio
    async def test_empty_task(self, temp_git_repo, minimal_config):
        """Should handle empty task gracefully."""
        orchestrator = Orchestrator(minimal_config, temp_git_repo)
        result = await orchestrator.run("")

        # Should still complete (fake adapter doesn't care about empty task)
        assert result is not None

    @pytest.mark.asyncio
    async def test_no_agents_configured(self, temp_git_repo):
        """Should handle no agents gracefully."""
        config = DeliberateConfig(
            agents={},
            workflow=WorkflowConfig(
                planning=PlanningConfig(enabled=True, agents=[]),
                execution=ExecutionConfig(enabled=True, agents=[]),
                review=ReviewConfig(enabled=False, agents=[]),
            ),
        )

        orchestrator = Orchestrator(config, temp_git_repo)
        result = await orchestrator.run("Do something")

        assert result.success  # No errors, just no output
        assert result.selected_plan is None
        assert result.execution_results == []
