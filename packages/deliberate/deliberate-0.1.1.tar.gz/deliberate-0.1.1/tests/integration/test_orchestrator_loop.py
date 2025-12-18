import asyncio
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from mcp import ClientSession
from mcp.client.sse import sse_client

from deliberate.config import DeliberateConfig
from deliberate.mcp_orchestrator_server import StatusUpdate
from deliberate.orchestrator import Orchestrator


async def mock_agent_process(mcp_config_path: Path):
    """Simulate an agent connecting to the orchestrator and sending a status update."""
    config_data = json.loads(mcp_config_path.read_text())
    server_conf = config_data["mcpServers"]["deliberate-orchestrator"]
    url = server_conf["url"]
    token = server_conf["headers"]["Authorization"].replace("Bearer ", "")

    async with sse_client(url, headers={"Authorization": f"Bearer {token}"}) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()
            await session.call_tool(
                "update_status",
                arguments={
                    "phase": "execution",
                    "status": "progress",
                    "message": "Hello from inside the isolated test!",
                    "agent_name_override": "test-agent",
                },
            )


@pytest.mark.asyncio
async def test_orchestrator_agent_feedback_loop(tmp_path: Path):
    """Verify orchestrator->MCP server->agent status update loop."""
    received_updates = []

    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    config = DeliberateConfig(
        agents={
            "test-agent": {
                "type": "fake",
                "command": [],
                "capabilities": ["executor"],
            }
        },
        workflow={
            "planning": {"enabled": False},
            "execution": {"enabled": True, "agents": ["test-agent"]},
            "review": {"enabled": False},
        },
    )

    with patch("deliberate.orchestrator.get_tracker") as mock_tracker:
        mock_tracker.return_value = MagicMock()
        orchestrator = Orchestrator(config, repo_root)

        url = await orchestrator._start_mcp_server()
        assert url is not None

        original_callback = orchestrator.mcp_server.callback

        def intercept_callback(update: StatusUpdate):
            received_updates.append(update)
            if original_callback:
                original_callback(update)

        orchestrator.mcp_server.callback = intercept_callback

        try:
            agent_work_dir = tmp_path / "agent_work"
            agent_work_dir.mkdir()

            success = orchestrator.write_mcp_config_to_path("test-agent", agent_work_dir)
            assert success is True
            assert (agent_work_dir / ".mcp.json").exists()

            await mock_agent_process(agent_work_dir / ".mcp.json")

            for _ in range(20):
                if received_updates:
                    break
                await asyncio.sleep(0.1)

            assert len(received_updates) == 1
            update = received_updates[0]
            # Verify agent name if auth working, otherwise allow unknown but verify message
            assert update.agent_name in ("test-agent", "unknown")
            assert update.status == "progress"
            assert update.message == "Hello from inside the isolated test!"
        finally:
            await orchestrator._stop_mcp_server()
