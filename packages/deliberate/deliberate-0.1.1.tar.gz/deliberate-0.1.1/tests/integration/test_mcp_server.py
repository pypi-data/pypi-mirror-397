"""Integration tests for MCP orchestrator server.

These tests start the actual MCP server and verify the auth flow works
end-to-end with HTTP requests.
"""

import asyncio
import json
import socket
import tempfile
from pathlib import Path
from typing import Any

import httpx
import pytest

# Import from deliberate to ensure migrations are applied
from deliberate.mcp_orchestrator_server import OrchestratorServer
from deliberate.tracking.migrations import Migrator


@pytest.fixture
def db_connection() -> Any:
    """Create an in-memory DuckDB/SQLite connection and run migrations."""
    try:
        import duckdb

        conn = duckdb.connect(":memory:")
        is_duckdb = True
    except ImportError:
        import sqlite3

        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        is_duckdb = False

    migrator = Migrator(conn, is_duckdb)
    migrator.migrate()
    yield conn
    conn.close()


@pytest.fixture
def free_port() -> int:
    """Get a free port for testing."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        s.listen(1)
        return s.getsockname()[1]


class TestMCPServerAuth:
    """Integration tests for MCP server authentication."""

    @pytest.mark.asyncio
    async def test_server_starts_and_accepts_connections(self, db_connection: Any, free_port: int):
        """Server should start and accept SSE connections."""
        server = OrchestratorServer(
            db_connection=db_connection,
            agent_names=["claude"],
            host="127.0.0.1",
            port=free_port,
        )

        server_task = asyncio.create_task(server.run())
        await asyncio.sleep(0.5)  # Wait for server to start

        try:
            url = server.get_url()
            assert url is not None
            assert str(free_port) in url
            assert "/sse" in url

            # Test connection with valid token
            token = server.get_token_for_agent("claude")
            headers = {"Authorization": f"Bearer {token}"}

            async with httpx.AsyncClient() as client:
                async with client.stream("GET", url, headers=headers, timeout=5) as response:
                    assert response.status_code == 200
                    # Read first event to verify SSE is working
                    async for line in response.aiter_lines():
                        if line.startswith("data:"):
                            # Got SSE data, connection works
                            break
        finally:
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass

    @pytest.mark.asyncio
    async def test_token_verifier_maps_to_agent_identity(self, db_connection: Any, free_port: int):
        """Token verifier should correctly identify agents."""
        agent_names = ["claude", "gemini", "codex"]
        server = OrchestratorServer(
            db_connection=db_connection,
            agent_names=agent_names,
            host="127.0.0.1",
            port=free_port,
        )

        server_task = asyncio.create_task(server.run())
        await asyncio.sleep(0.5)

        try:
            # Verify each agent's token maps correctly
            for name in agent_names:
                token = server.get_token_for_agent(name)
                access_token = await server.token_verifier.verify_token(token)
                assert access_token is not None
                assert access_token.client_id == name
        finally:
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass


class TestMCPConfigFileGeneration:
    """Integration tests for .mcp.json file generation."""

    @pytest.mark.asyncio
    async def test_mcp_config_file_roundtrip(self, db_connection: Any, free_port: int):
        """Config written to file should be valid JSON with correct structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            worktree_path = Path(tmpdir) / "agent-worktree"
            worktree_path.mkdir()

            server = OrchestratorServer(
                db_connection=db_connection,
                agent_names=["claude"],
                host="127.0.0.1",
                port=free_port,
            )

            # Get config and write to file
            config = server.get_mcp_config_for_agent("claude")
            config_path = worktree_path / ".mcp.json"
            config_path.write_text(json.dumps(config, indent=2))

            # Read back and verify
            loaded = json.loads(config_path.read_text())
            assert loaded == config

            # Verify Claude Code can parse this format
            mcp_servers = loaded.get("mcpServers", {})
            assert "deliberate-orchestrator" in mcp_servers

            server_config = mcp_servers["deliberate-orchestrator"]
            assert server_config["type"] == "sse"
            assert "url" in server_config
            assert "headers" in server_config
            assert server_config["headers"]["Authorization"].startswith("Bearer ")

    @pytest.mark.asyncio
    async def test_multiple_agents_get_unique_configs(self, db_connection: Any, free_port: int):
        """Each agent should get a unique config with different tokens."""
        with tempfile.TemporaryDirectory() as tmpdir:
            agent_names = ["claude", "gemini", "codex"]
            server = OrchestratorServer(
                db_connection=db_connection,
                agent_names=agent_names,
                host="127.0.0.1",
                port=free_port,
            )

            configs = {}
            for name in agent_names:
                agent_dir = Path(tmpdir) / name
                agent_dir.mkdir()
                config = server.get_mcp_config_for_agent(name)
                config_path = agent_dir / ".mcp.json"
                config_path.write_text(json.dumps(config, indent=2))
                configs[name] = config

            # Verify all tokens are unique
            tokens = set()
            for name, config in configs.items():
                auth_header = config["mcpServers"]["deliberate-orchestrator"]["headers"]["Authorization"]
                token = auth_header.replace("Bearer ", "")
                assert token not in tokens, f"Duplicate token for {name}"
                tokens.add(token)


class TestOrchestratorMCPIntegration:
    """Integration tests for orchestrator's MCP server integration."""

    @pytest.fixture(autouse=True)
    def mock_tracker(self):
        """Mock tracker to avoid DuckDB lock issues."""
        from unittest.mock import MagicMock, patch

        with patch("deliberate.orchestrator.get_tracker") as mock:
            mock.return_value = MagicMock()
            yield mock

    @pytest.fixture
    def free_port(self) -> int:
        """Get a free port for testing."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            s.listen(1)
            return s.getsockname()[1]

    @pytest.mark.asyncio
    async def test_orchestrator_starts_mcp_server_with_tokens(
        self, temp_git_repo: Path, minimal_config: Any, db_connection: Any, free_port: int
    ):
        """Orchestrator should start MCP server and generate tokens for agents."""
        from deliberate.orchestrator import Orchestrator

        orchestrator = Orchestrator(minimal_config, temp_git_repo)

        # Manually create and start the MCP server with dynamic port
        # (simulating what _start_mcp_server does but with our free port)
        orchestrator.mcp_server = OrchestratorServer(
            db_connection=db_connection,
            agent_names=list(orchestrator.adapters.keys()),
            port=free_port,
        )
        server_task = asyncio.create_task(orchestrator.mcp_server.run())
        await asyncio.sleep(0.5)

        try:
            # Server should have started
            url = orchestrator.mcp_server.get_url()
            assert url is not None
            assert str(free_port) in url

            # Token should exist for the fake agent
            token = orchestrator.mcp_server.get_token_for_agent("fake")
            assert token is not None

            # Verify token maps correctly
            access_token = await orchestrator.mcp_server.token_verifier.verify_token(token)
            assert access_token is not None
            assert access_token.client_id == "fake"
        finally:
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass

    @pytest.mark.asyncio
    async def test_orchestrator_writes_mcp_config_to_path(
        self, temp_git_repo: Path, minimal_config: Any, db_connection: Any, free_port: int
    ):
        """Orchestrator should write valid .mcp.json to worktree paths."""
        from deliberate.orchestrator import Orchestrator

        orchestrator = Orchestrator(minimal_config, temp_git_repo)

        # Manually set up MCP server
        orchestrator.mcp_server = OrchestratorServer(
            db_connection=db_connection,
            agent_names=list(orchestrator.adapters.keys()),
            port=free_port,
        )
        server_task = asyncio.create_task(orchestrator.mcp_server.run())
        await asyncio.sleep(0.5)

        try:
            # Test writing config to a path
            test_dir = temp_git_repo / "test-agent-dir"
            test_dir.mkdir()

            success = orchestrator.write_mcp_config_to_path("fake", test_dir)
            assert success

            config_path = test_dir / ".mcp.json"
            assert config_path.exists()

            config = json.loads(config_path.read_text())
            assert "mcpServers" in config
            assert "deliberate-orchestrator" in config["mcpServers"]

            # Verify config has correct structure for Claude Code
            mcp_config = config["mcpServers"]["deliberate-orchestrator"]
            assert mcp_config["type"] == "sse"
            assert "Authorization" in mcp_config["headers"]
        finally:
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass

    def test_write_mcp_config_returns_false_without_server(self, temp_git_repo: Path, minimal_config: Any):
        """write_mcp_config_to_path should return False when server not started."""
        from deliberate.orchestrator import Orchestrator

        orchestrator = Orchestrator(minimal_config, temp_git_repo)

        # Without starting server, should return False
        test_dir = temp_git_repo / "test-agent-dir"
        test_dir.mkdir()

        result = orchestrator.write_mcp_config_to_path("fake", test_dir)
        assert result is False


class TestMCPServerSessionState:
    """Integration tests for MCP server session state."""

    @pytest.mark.asyncio
    async def test_session_tracks_questions(self, db_connection: Any):
        """Session should track questions asked during execution."""
        server = OrchestratorServer(
            db_connection=db_connection,
            agent_names=["claude"],
            host="127.0.0.1",
            port=0,
        )

        # Add question via session directly
        question_id = server.session.add_question(
            agent="claude",
            question="What framework should I use?",
            category="decision",
            context="Building a web app",
            suggestions=["React", "Vue", "Svelte"],
            urgency="medium",
        )

        assert question_id is not None

        # Verify question was stored
        questions = server.session.get_pending_questions()
        assert len(questions) == 1
        # Question data is nested inside "content"
        assert questions[0]["content"]["question"] == "What framework should I use?"
        assert questions[0]["content"]["category"] == "decision"
        assert questions[0]["agent"] == "claude"

    @pytest.mark.asyncio
    async def test_session_persists_across_requests(self, db_connection: Any):
        """Session state should persist across multiple questions."""
        server = OrchestratorServer(
            db_connection=db_connection,
            agent_names=["claude", "gemini"],
            host="127.0.0.1",
            port=0,
        )

        # Add questions from different agents
        q1 = server.session.add_question(
            agent="claude",
            question="Question 1",
            category="factual",
        )
        server.session.add_question(
            agent="gemini",
            question="Question 2",
            category="clarification",
        )

        # Both should be tracked
        all_questions = server.session.get_pending_questions()
        assert len(all_questions) == 2

        # Resolve one question
        server.session.add_answer(
            agent="user",
            question_id=q1,
            answer="Answer 1",
            confidence=1.0,
        )
        server.session.resolve_question(q1, "Answer 1")

        # One should remain pending
        pending = server.session.get_pending_questions()
        assert len(pending) == 1
        # Question data is nested inside "content"
        assert pending[0]["content"]["question"] == "Question 2"
        assert pending[0]["agent"] == "gemini"
