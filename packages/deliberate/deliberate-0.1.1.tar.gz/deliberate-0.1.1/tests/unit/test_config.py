"""Tests for configuration loading."""

import tempfile

import pytest

from deliberate.config import AgentConfig, DeliberateConfig


class TestConfigLoading:
    """Tests for configuration loading."""

    def test_load_valid_config(self):
        """Should load a valid config file."""
        config_content = """
agents:
  test:
    type: fake
    behavior: echo
    capabilities: [planner]

workflow:
  planning:
    enabled: true
    agents: [test]
  execution:
    enabled: false
    agents: []
  review:
    enabled: false
    agents: []
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(config_content)
            f.flush()

            config = DeliberateConfig.load(f.name)

            assert "test" in config.agents
            assert config.agents["test"].type == "fake"
            assert config.workflow.planning.enabled is True
            assert config.workflow.execution.enabled is False

    def test_load_missing_file(self):
        """Should raise for missing file."""
        with pytest.raises(FileNotFoundError):
            DeliberateConfig.load("/nonexistent/path.yaml")

    def test_default_config(self):
        """Should create default config without file."""
        config = DeliberateConfig()

        assert config.agents == {}
        assert config.workflow.planning.enabled is True
        assert config.limits.budget.max_total_tokens == 500000

    def test_load_or_default_missing(self):
        """Should return default when file missing."""
        config = DeliberateConfig.load_or_default("/nonexistent/path.yaml")
        assert config is not None
        assert isinstance(config, DeliberateConfig)

    def test_get_agent(self):
        """Should get agent by name."""
        config = DeliberateConfig(
            agents={
                "test": AgentConfig(type="fake", behavior="echo"),
            }
        )

        agent = config.get_agent("test")
        assert agent.type == "fake"

    def test_get_agent_missing(self):
        """Should raise for missing agent."""
        config = DeliberateConfig()

        with pytest.raises(KeyError):
            config.get_agent("nonexistent")

    def test_get_planners(self):
        """Should filter agents by planner capability."""
        config = DeliberateConfig(
            agents={
                "planner1": AgentConfig(type="fake", capabilities=["planner", "executor"]),
                "reviewer1": AgentConfig(type="fake", capabilities=["reviewer"]),
            },
        )
        config.workflow.planning.agents = ["planner1", "reviewer1"]

        planners = config.get_planners()
        assert planners == ["planner1"]


class TestAgentConfig:
    """Tests for AgentConfig."""

    def test_default_values(self):
        """Should have sensible defaults."""
        agent = AgentConfig(type="fake")

        assert agent.command == []
        assert agent.capabilities == ["planner", "executor", "reviewer"]
        assert agent.config.max_tokens == 8000
        assert agent.cost.weight == 1.0

    def test_cli_agent(self):
        """Should accept CLI agent config."""
        agent = AgentConfig(
            type="cli",
            command=["claude", "--print", "-p"],
            capabilities=["planner"],
        )

        assert agent.type == "cli"
        assert agent.command == ["claude", "--print", "-p"]

    def test_mcp_agent(self):
        """Should accept MCP agent config."""
        agent = AgentConfig(
            type="mcp",
            command=["mcp-client"],
            mcp_endpoint="unix:///tmp/mcp.sock",
        )

        assert agent.type == "mcp"
        assert agent.mcp_endpoint == "unix:///tmp/mcp.sock"


class TestProfileApplication:
    """Tests for profile application and agent_overrides."""

    def test_apply_builtin_profile(self):
        """Should apply built-in profile workflow settings."""
        config = DeliberateConfig(
            agents={
                "claude": AgentConfig(type="cli", model="claude-sonnet-4-5"),
            },
        )

        result = config.apply_profile("powerful")

        # Workflow settings should be applied
        assert result.workflow.planning.debate.enabled is True
        assert result.workflow.planning.debate.rounds == 2
        assert result.workflow.refinement.max_iterations == 5

    def test_apply_profile_with_agent_overrides(self):
        """Should apply agent_overrides to change model."""
        config = DeliberateConfig(
            agents={
                "claude": AgentConfig(type="cli", model="claude-sonnet-4-5"),
                "gemini": AgentConfig(type="cli", model="gemini-2.0-flash"),
            },
        )

        result = config.apply_profile("powerful")

        # Model should be overridden to powerful variants
        assert result.agents["claude"].model == "claude-opus-4-5-20251101"
        assert result.agents["gemini"].model == "gemini-3.0-pro"

    def test_apply_profile_preserves_other_agent_fields(self):
        """Should preserve non-overridden agent fields."""
        config = DeliberateConfig(
            agents={
                "claude": AgentConfig(
                    type="cli",
                    command=["claude", "--custom-flag"],
                    model="claude-sonnet-4-5",
                    capabilities=["planner", "executor"],
                ),
            },
        )

        result = config.apply_profile("powerful")

        # Model should change but other fields preserved
        assert result.agents["claude"].model == "claude-opus-4-5-20251101"
        assert result.agents["claude"].command == ["claude", "--custom-flag"]
        assert result.agents["claude"].capabilities == ["planner", "executor"]

    def test_apply_profile_ignores_unknown_agents(self):
        """Should not fail when profile overrides unknown agents."""
        config = DeliberateConfig(
            agents={
                "custom": AgentConfig(type="fake", model="my-model"),
            },
        )

        # Should not raise even though powerful profile references claude/gemini/codex
        result = config.apply_profile("powerful")

        # Custom agent should be unchanged
        assert result.agents["custom"].model == "my-model"

    def test_cheap_profile_uses_fast_models(self):
        """Should use fast/cheap models in cheap profile."""
        config = DeliberateConfig(
            agents={
                "claude": AgentConfig(type="cli", model="claude-opus-4-5"),
                "gemini": AgentConfig(type="cli", model="gemini-3.0-pro"),
            },
        )

        result = config.apply_profile("cheap")

        # Should downgrade to cheaper models
        assert result.agents["claude"].model == "claude-sonnet-4-5-20250514"
        assert result.agents["gemini"].model == "gemini-2.0-flash-exp"
        # Workflow should disable expensive features
        assert result.workflow.planning.enabled is False
        assert result.workflow.refinement.enabled is False
