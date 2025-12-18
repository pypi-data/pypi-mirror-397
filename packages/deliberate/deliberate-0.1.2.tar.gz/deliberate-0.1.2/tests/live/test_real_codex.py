"""Live test using the real Codex CLI."""

import shutil
from unittest.mock import MagicMock, patch

import pytest

from deliberate.config import DeliberateConfig
from deliberate.mcp_orchestrator_server import StatusUpdate
from deliberate.orchestrator import Orchestrator

# Skip if codex is not installed
CODEX_PATH = shutil.which("codex")


@pytest.mark.skipif(not CODEX_PATH, reason="codex CLI not installed")
@pytest.mark.asyncio
async def test_real_codex_mcp_update(tmp_path):
    """Verify real codex CLI can connect to orchestrator MCP and update status."""

    # Pre-flight: ensure codex supports --json output; otherwise skip to avoid false negatives.
    import subprocess

    help_out = subprocess.run([CODEX_PATH, "--help"], capture_output=True, text=True)
    if "--json" not in help_out.stdout and "--json" not in help_out.stderr:
        pytest.skip("codex CLI present but does not support --json output required for MCP test")

    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    # Initialize git repo for worktrees
    subprocess.run(["git", "init"], cwd=repo_root, check=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=repo_root, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_root, check=True)
    (repo_root / "README.md").write_text("# Test Repo")
    subprocess.run(["git", "add", "."], cwd=repo_root, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_root, check=True)

    config = DeliberateConfig(
        agents={
            "codex-agent": {
                "type": "cli",
                "command": ["codex"],
            }
        },
        workflow={
            "planning": {"enabled": False},
            "execution": {"enabled": True, "agents": ["codex-agent"]},
            "review": {"enabled": False},
        },
        limits={
            "budget": {
                "max_cost_usd": 0.5,  # Allow some budget for real execution
                "max_total_tokens": 100000,
            }
        },
    )

    # Mock tracker to avoid DB locking issues during test
    with patch("deliberate.orchestrator.get_tracker") as mock_tracker:
        mock_tracker.return_value = MagicMock()

        orchestrator = Orchestrator(config, repo_root)

        # Capture updates
        received_updates = []

        # Start MCP server
        await orchestrator._start_mcp_server()

        # Intercept callback
        original_callback = orchestrator.mcp_server.callback

        def intercept_callback(update: StatusUpdate):
            print(f"Received update: {update}")
            received_updates.append(update)
            if original_callback:
                original_callback(update)

        orchestrator.mcp_server.callback = intercept_callback

        try:
            # Run the agent
            # We ask it to specifically use the tool.
            task = "Please call the 'update_status' tool with the message 'Hello from real codex'. Do nothing else."

            result = await orchestrator.run(task)

            # Check results
            print("Run result:", result)

            # Verify we received the update
            # It might be in result.status_updates or in our captured list

            found = False
            for update in received_updates:
                if "Hello from real codex" in update.message:
                    found = True
                    break

            if not found:
                # Check execution result for errors
                for res in result.execution_results:
                    print(f"Agent {res.agent} output:\n{res.summary}")
                    if res.error:
                        print(f"Agent error: {res.error}")

            assert found, "Did not receive expected status update from Codex"

        finally:
            await orchestrator._stop_mcp_server()
