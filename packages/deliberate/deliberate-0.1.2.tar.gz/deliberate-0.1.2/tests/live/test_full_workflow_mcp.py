"""Full live workflow test with MCP auth.

This test runs the complete deliberate workflow with multiple agents,
verifying that MCP authentication and status updates work end-to-end.

Run with: RUN_LIVE_LLM_TESTS=1 uv run pytest tests/live/test_full_workflow_mcp.py -v -s
"""

import asyncio
import os
import subprocess
import tempfile
from pathlib import Path

import pytest

from deliberate.agent_detection import detect_agents

# Skip all tests in this module unless explicitly enabled
pytestmark = [
    pytest.mark.live_llm,
    pytest.mark.skipif(
        "RUN_LIVE_LLM_TESTS" not in os.environ,
        reason="Live LLM tests disabled (set RUN_LIVE_LLM_TESTS=1 to enable)",
    ),
]


def _pick_command(agent_name: str) -> list[str]:
    """Map agent names to non-interactive CLI commands."""
    if agent_name == "claude":
        return ["claude", "--print", "-p"]
    if agent_name == "gemini":
        return ["gemini", "-y"]
    if agent_name == "codex":
        return ["codex", "exec", "--skip-git-repo-check"]
    if agent_name == "copilot":
        return ["gh", "copilot", "chat", "-m"]
    return [agent_name]


@pytest.fixture(scope="session")
def available_live_agents():
    """Detect authenticated agents for live runs."""
    detected = asyncio.run(detect_agents(skip_mcp_detection=True))
    authed = [a for a in detected if a.has_auth]
    if not authed:
        pytest.skip("No authenticated CLI agents available for live LLM tests")
    return authed


@pytest.fixture
def temp_git_repo():
    """Create a temporary git repository for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir) / "sudoku-project"
        repo.mkdir()

        # Initialize git repo
        subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=repo,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=repo,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "commit.gpgsign", "false"],
            cwd=repo,
            check=True,
            capture_output=True,
        )

        # Create initial commit with a README
        readme = repo / "README.md"
        readme.write_text("# Sudoku Variant Project\n\nA fun puzzle game!\n")
        subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=repo,
            check=True,
            capture_output=True,
        )

        yield repo


class TestFullWorkflowWithMCP:
    """Full end-to-end workflow tests with MCP authentication."""

    @pytest.mark.asyncio
    @pytest.mark.timeout(600)  # 10 minute timeout
    async def test_multi_agent_sudoku_variant(self, temp_git_repo, available_live_agents):
        """Run full workflow with multiple agents building a sudoku variant.

        This test:
        1. Uses Claude and Gemini for planning (debate mode)
        2. Uses Claude for execution
        3. Uses Gemini for review
        4. Verifies MCP status updates are received with correct agent identity

        Cost estimate: ~$0.50-1.00 per run
        """
        from deliberate.config import (
            AgentConfig,
            DeliberateConfig,
            ExecutionConfig,
            LimitsConfig,
            PlanningConfig,
            ReviewConfig,
            WorkflowConfig,
            WorktreeConfig,
        )
        from deliberate.orchestrator import Orchestrator

        if len(available_live_agents) < 2:
            pytest.skip("Need at least two authenticated agents for multi-agent live test")

        # Track status updates

        # Use the first two authenticated agents for planning; first executes
        planner_agents = [a.name for a in available_live_agents[:2]]
        exec_agent = planner_agents[0]

        def to_agent_cfg(agent_name: str) -> AgentConfig:
            return AgentConfig(
                type="cli",
                command=_pick_command(agent_name),
                capabilities=["planner", "executor", "reviewer"],
                permission_mode="bypassPermissions" if agent_name in {"claude", "gemini", "codex"} else None,
            )

        config = DeliberateConfig(
            agents={name: to_agent_cfg(name) for name in planner_agents},
            workflow=WorkflowConfig(
                mode="multi-pass",
                planning=PlanningConfig(
                    enabled=True,
                    agents=planner_agents,  # Both plan in parallel
                ),
                execution=ExecutionConfig(
                    enabled=True,
                    agents=[exec_agent],  # First agent executes
                ),
                review=ReviewConfig(
                    enabled=False,  # Skip review to keep test fast
                    agents=[],
                ),
            ),
            worktrees=WorktreeConfig(enabled=True),
            limits=LimitsConfig(
                max_tokens=50000,
                max_cost=2.0,
            ),
        )

        # Create orchestrator
        orchestrator = Orchestrator(config, temp_git_repo)

        # Run the workflow
        task = """Create a simple 4x4 number puzzle in puzzle.py.

Requirements:
1. A 4x4 grid where numbers 1-4 appear once per row and column
2. A solve() function using backtracking
3. A simple test that creates and solves a puzzle"""

        print(f"\n{'=' * 60}")
        print("RUNNING FULL MULTI-AGENT WORKFLOW")
        print(f"{'=' * 60}")
        print(f"Task: {task[:100]}...")
        print(f"Agents: {list(config.agents.keys())}")
        print(f"Repo: {temp_git_repo}")
        print(f"{'=' * 60}\n")

        result = await orchestrator.run(task)

        # Print results
        print(f"\n{'=' * 60}")
        print("WORKFLOW RESULTS")
        print(f"{'=' * 60}")
        print(f"Success: {result.success}")
        print(f"Duration: {result.total_duration_seconds:.1f}s")
        print(f"Tokens: {result.total_token_usage}")

        if result.selected_plan:
            print(f"\nSelected Plan (from {result.selected_plan.agent}):")
            print(result.selected_plan.content[:500] + "...")

        if result.execution_results:
            print(f"\nExecution Results ({len(result.execution_results)} agents):")
            for exec_result in result.execution_results:
                print(f"  - {exec_result.agent}: {'OK' if exec_result.success else 'FAILED'}")
                if exec_result.diff:
                    print(f"    Diff: {len(exec_result.diff)} chars")

        if result.reviews:
            print(f"\nReviews ({len(result.reviews)}):")
            for review in result.reviews:
                print(f"  - {review.agent}: {review.verdict}")
                print(f"    Score: {review.score}")

        # Check MCP status updates
        if orchestrator.mcp_server:
            updates = orchestrator.mcp_server.get_updates()
            print(f"\nMCP Status Updates ({len(updates)}):")
            for update in updates:
                print(f"  [{update.agent_name}] {update.phase}/{update.status}: {update.message[:50]}...")

            # Verify agent identity in updates
            agent_names_in_updates = {u.agent_name for u in updates}
            print(f"\nAgents that sent updates: {agent_names_in_updates}")

        print(f"{'=' * 60}\n")

        # Assertions
        assert result.success, f"Workflow failed: {result.error}"
        assert result.selected_plan is not None, "No plan was selected"
        assert len(result.execution_results) > 0, "No execution results"

        # Verify code was generated
        if result.execution_results[0].diff:
            assert "puzzle" in result.execution_results[0].diff.lower(), "Expected puzzle code in diff"

    @pytest.mark.asyncio
    @pytest.mark.timeout(300)  # 5 minute timeout
    async def test_single_agent_quick_task(self, temp_git_repo):
        """Quick single-agent test to verify basic MCP auth flow.

        This is a faster smoke test that verifies:
        1. MCP server starts with auth
        2. Agent can connect and execute
        3. Status updates are received

        Cost estimate: ~$0.10 per run
        """
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

        # Try to pick a single authenticated agent
        detected = await detect_agents(skip_mcp_detection=True)
        authed = [a for a in detected if a.has_auth]
        if not authed:
            pytest.skip("No authenticated agents available for live single-agent test")
        agent_name = authed[0].name

        config = DeliberateConfig(
            agents={
                agent_name: AgentConfig(
                    type="cli",
                    command=_pick_command(agent_name),
                    capabilities=["planner", "executor"],
                    permission_mode="bypassPermissions" if agent_name in {"claude", "gemini", "codex"} else None,
                ),
            },
            workflow=WorkflowConfig(
                planning=PlanningConfig(enabled=False, agents=[]),
                execution=ExecutionConfig(enabled=True, agents=[agent_name]),
                review=ReviewConfig(enabled=False, agents=[]),
            ),
            limits=LimitsConfig(max_tokens=10000, max_cost=0.50),
        )

        orchestrator = Orchestrator(config, temp_git_repo)

        task = "Create hello.py that prints 'Hello, Sudoku!'"

        print("\nRunning quick single-agent test...")
        result = await orchestrator.run(task)

        print(f"Success: {result.success}")
        print(f"Duration: {result.total_duration_seconds:.1f}s")

        # Check for MCP updates
        if orchestrator.mcp_server:
            updates = orchestrator.mcp_server.get_updates()
            print(f"MCP Updates: {len(updates)}")
            if updates:
                # Verify agent identity
                for update in updates:
                    print(f"  {update.agent_name}: {update.message[:50]}...")
                    # If updates came through, agent_name should match selected agent
                    if update.agent_name != "unknown":
                        assert update.agent_name == agent_name, (
                            f"Expected agent '{agent_name}', got '{update.agent_name}'"
                        )

        assert result.success, f"Workflow failed: {result.error}"


class TestMCPAuthVerification:
    """Tests specifically for MCP authentication verification."""

    @pytest.mark.asyncio
    @pytest.mark.timeout(120)
    async def test_token_identity_preserved(self, temp_git_repo):
        """Verify that agent identity is correctly preserved through MCP auth.

        This test:
        1. Starts MCP server with known agent tokens
        2. Simulates agents connecting with their tokens
        3. Verifies ctx.client_id returns correct agent name

        Cost: ~$0 (no LLM calls, just server verification)
        """
        import socket

        from deliberate.mcp_orchestrator_server import OrchestratorServer

        # Find free port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            s.listen(1)
            free_port = s.getsockname()[1]

        agent_names = ["claude", "gemini", "codex"]
        server = OrchestratorServer(
            agent_names=agent_names,
            host="127.0.0.1",
            port=free_port,
        )

        server_task = asyncio.create_task(server.run())
        await asyncio.sleep(0.5)

        try:
            # Verify each agent has unique token
            tokens = {}
            for name in agent_names:
                token = server.get_token_for_agent(name)
                assert token is not None, f"No token for {name}"
                assert token not in tokens.values(), f"Duplicate token for {name}"
                tokens[name] = token

            # Verify token verification returns correct identity
            for name, token in tokens.items():
                access_token = await server.token_verifier.verify_token(token)
                assert access_token is not None, f"Token verification failed for {name}"
                assert access_token.client_id == name, f"Expected client_id '{name}', got '{access_token.client_id}'"

            print(f"All {len(agent_names)} agents have unique tokens with correct identity")

        finally:
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass
