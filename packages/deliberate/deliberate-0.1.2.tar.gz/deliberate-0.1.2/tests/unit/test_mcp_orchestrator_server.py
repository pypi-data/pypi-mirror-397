"""Unit tests for MCP orchestrator server."""

import pytest

from deliberate.mcp_orchestrator_server import (
    AgentTokenVerifier,
    OrchestratorServer,
    StatusUpdate,
)


class TestAgentTokenVerifier:
    """Unit tests for AgentTokenVerifier."""

    def test_create_token_returns_unique_tokens(self):
        """Each agent should get a unique token."""
        verifier = AgentTokenVerifier()

        token1 = verifier.create_token("claude")
        token2 = verifier.create_token("gemini")
        token3 = verifier.create_token("codex")

        assert token1 != token2
        assert token2 != token3
        assert token1 != token3

    def test_create_token_maps_to_agent_name(self):
        """Token should map back to the correct agent name."""
        verifier = AgentTokenVerifier()

        token = verifier.create_token("claude")

        assert verifier.get_agent_name(token) == "claude"

    def test_get_agent_name_returns_none_for_invalid_token(self):
        """Unknown tokens should return None."""
        verifier = AgentTokenVerifier()
        verifier.create_token("claude")

        assert verifier.get_agent_name("invalid-token") is None

    @pytest.mark.asyncio
    async def test_verify_token_returns_access_token(self):
        """Valid token should return AccessToken with correct client_id."""
        verifier = AgentTokenVerifier()
        token = verifier.create_token("gemini")

        access_token = await verifier.verify_token(token)

        assert access_token is not None
        assert access_token.client_id == "gemini"
        assert access_token.token == token
        assert "update_status" in access_token.scopes
        assert "ask_question" in access_token.scopes

    @pytest.mark.asyncio
    async def test_verify_token_returns_none_for_invalid(self):
        """Invalid token should return None."""
        verifier = AgentTokenVerifier()

        result = await verifier.verify_token("not-a-valid-token")

        assert result is None


class TestOrchestratorServerTokenAuth:
    """Unit tests for OrchestratorServer token authentication."""

    def test_server_generates_tokens_for_agents(self):
        """Server should generate tokens for each agent name provided."""
        agent_names = ["claude", "gemini", "codex"]

        server = OrchestratorServer(agent_names=agent_names, port=0)

        for name in agent_names:
            token = server.get_token_for_agent(name)
            assert token is not None
            assert len(token) > 20  # Tokens should be substantial

    def test_server_without_auth_has_no_tokens(self):
        """Server without agent_names should not have tokens."""
        server = OrchestratorServer(agent_names=None, port=0)

        assert server.get_token_for_agent("claude") is None
        assert server.token_verifier is None

    def test_get_mcp_config_for_agent_structure(self):
        """MCP config should have correct structure for Claude Code."""
        server = OrchestratorServer(
            agent_names=["claude"],
            host="127.0.0.1",
            port=9999,
        )

        config = server.get_mcp_config_for_agent("claude")

        assert config is not None
        assert "mcpServers" in config
        assert "deliberate-orchestrator" in config["mcpServers"]

        mcp_config = config["mcpServers"]["deliberate-orchestrator"]
        assert mcp_config["type"] == "sse"
        assert "url" in mcp_config
        assert "headers" in mcp_config
        assert "Authorization" in mcp_config["headers"]
        assert mcp_config["headers"]["Authorization"].startswith("Bearer ")

    def test_get_mcp_config_includes_correct_url(self):
        """MCP config URL should point to SSE endpoint."""
        server = OrchestratorServer(
            agent_names=["claude"],
            host="127.0.0.1",
            port=9999,
        )

        config = server.get_mcp_config_for_agent("claude")
        url = config["mcpServers"]["deliberate-orchestrator"]["url"]

        assert "127.0.0.1" in url
        assert "9999" in url
        assert url.endswith("/sse")

    def test_get_mcp_config_returns_none_for_unknown_agent(self):
        """Should return None for agents not in the list."""
        server = OrchestratorServer(
            agent_names=["claude"],
            port=0,
        )

        assert server.get_mcp_config_for_agent("unknown") is None

    def test_get_mcp_config_returns_none_without_auth(self):
        """Should return None when auth is not enabled."""
        server = OrchestratorServer(agent_names=None, port=0)

        assert server.get_mcp_config_for_agent("claude") is None

    def test_each_agent_gets_unique_token_in_config(self):
        """Different agents should have different tokens in their configs."""
        server = OrchestratorServer(
            agent_names=["claude", "gemini"],
            port=0,
        )

        config1 = server.get_mcp_config_for_agent("claude")
        config2 = server.get_mcp_config_for_agent("gemini")

        token1 = config1["mcpServers"]["deliberate-orchestrator"]["headers"]["Authorization"]
        token2 = config2["mcpServers"]["deliberate-orchestrator"]["headers"]["Authorization"]

        assert token1 != token2


class TestOrchestratorServerStatusUpdates:
    """Unit tests for status update tracking."""

    def test_get_updates_returns_empty_initially(self):
        """Updates should be empty when server starts."""
        server = OrchestratorServer(port=0)

        updates = server.get_updates()

        assert updates == []

    def test_callback_is_called_on_status_update(self):
        """Callback should be invoked when status update is received."""
        received_updates = []

        def callback(update: StatusUpdate):
            received_updates.append(update)

        server = OrchestratorServer(
            callback=callback,
            port=0,
        )

        # Simulate adding an update directly
        from datetime import datetime

        update = StatusUpdate(
            agent_name="claude",
            phase="execution",
            status="started",
            message="Beginning work",
            timestamp=datetime.now(),
        )
        server.updates.append(update)
        if server.callback:
            server.callback(update)

        assert len(received_updates) == 1
        assert received_updates[0].agent_name == "claude"
        assert received_updates[0].message == "Beginning work"

    def test_get_updates_filters_by_agent(self):
        """Should filter updates by agent name."""
        from datetime import datetime

        server = OrchestratorServer(port=0)

        # Add updates from different agents
        for agent in ["claude", "gemini", "claude"]:
            server.updates.append(
                StatusUpdate(
                    agent_name=agent,
                    phase="execution",
                    status="progress",
                    message=f"Update from {agent}",
                    timestamp=datetime.now(),
                )
            )

        claude_updates = server.get_updates(agent_name="claude")
        gemini_updates = server.get_updates(agent_name="gemini")

        assert len(claude_updates) == 2
        assert len(gemini_updates) == 1
        assert all(u.agent_name == "claude" for u in claude_updates)


class TestOrchestratorServerPortSelection:
    """Unit tests for port selection."""

    def test_auto_port_selection(self):
        """Port 0 should trigger auto-selection."""
        server = OrchestratorServer(port=0)

        # Before run(), actual_port is None
        assert server.actual_port is None
        # find_free_port should return a valid port
        port = server._find_free_port()
        assert port > 0
        assert port < 65536

    def test_fixed_port_used(self):
        """Fixed port should be used when specified."""
        server = OrchestratorServer(port=9999)

        port = server._find_free_port()

        assert port == 9999
