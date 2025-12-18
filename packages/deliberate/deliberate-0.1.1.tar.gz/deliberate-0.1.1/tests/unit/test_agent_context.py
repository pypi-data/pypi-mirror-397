"""Tests for AgentExecutionContext config schema."""

import json

import pytest

from deliberate.agent_context import (
    AgentExecutionContext,
    AgentIdentity,
    ExecutionSettings,
    MCPOrchestratorConfig,
    MCPServerConfig,
    MCPSettings,
    TaskContext,
    TelemetrySettings,
)


class TestAgentIdentity:
    def test_create_basic(self):
        identity = AgentIdentity(
            name="claude",
            parser="claude",
            role="executor",
        )
        assert identity.name == "claude"
        assert identity.parser == "claude"
        assert identity.role == "executor"
        assert identity.capabilities == ["executor"]

    def test_create_with_capabilities(self):
        identity = AgentIdentity(
            name="gemini",
            parser="gemini",
            role="planner",
            capabilities=["planner", "executor"],
        )
        assert identity.capabilities == ["planner", "executor"]


class TestTaskContext:
    def test_create_basic(self):
        task = TaskContext(
            id="exec-abc123",
            description="Add fibonacci function",
        )
        assert task.id == "exec-abc123"
        assert task.description == "Add fibonacci function"
        assert task.plan_id is None
        assert task.plan_content is None

    def test_create_with_plan(self):
        task = TaskContext(
            id="exec-abc123",
            description="Add fibonacci function",
            plan_id="plan-xyz",
            plan_content="## Plan\n1. Create fib.py",
        )
        assert task.plan_id == "plan-xyz"
        assert task.plan_content == "## Plan\n1. Create fib.py"


class TestMCPSettings:
    def test_empty_config(self):
        mcp = MCPSettings()
        assert mcp.orchestrator is None
        assert mcp.servers == []

    def test_with_orchestrator(self):
        mcp = MCPSettings(
            orchestrator=MCPOrchestratorConfig(
                url="http://localhost:8765/sse",
                token="test-token-123",
            )
        )
        assert mcp.orchestrator.url == "http://localhost:8765/sse"
        assert mcp.orchestrator.token == "test-token-123"

    def test_with_servers(self):
        mcp = MCPSettings(
            servers=[
                MCPServerConfig(
                    name="filesystem",
                    type="stdio",
                    command="npx",
                    args=["-y", "@anthropic/mcp-filesystem"],
                ),
                MCPServerConfig(
                    name="remote",
                    type="sse",
                    url="http://localhost:9000/sse",
                ),
            ]
        )
        assert len(mcp.servers) == 2
        assert mcp.servers[0].name == "filesystem"
        assert mcp.servers[0].type == "stdio"
        assert mcp.servers[1].type == "sse"


class TestAgentExecutionContext:
    @pytest.fixture
    def minimal_context(self):
        return AgentExecutionContext(
            agent=AgentIdentity(
                name="claude",
                parser="claude",
                role="executor",
            ),
            task=TaskContext(
                id="exec-123",
                description="Test task",
            ),
            execution=ExecutionSettings(
                working_dir="/tmp/worktree",
            ),
        )

    @pytest.fixture
    def full_context(self):
        return AgentExecutionContext(
            agent=AgentIdentity(
                name="claude",
                parser="claude",
                role="executor",
                capabilities=["planner", "executor"],
            ),
            task=TaskContext(
                id="exec-abc123",
                description="Add fibonacci function",
                plan_id="plan-xyz",
                plan_content="## Plan\n1. Create fib.py",
            ),
            mcp=MCPSettings(
                orchestrator=MCPOrchestratorConfig(
                    url="http://localhost:8765/sse",
                    token="bearer-token-abc123",
                ),
                servers=[
                    MCPServerConfig(
                        name="filesystem",
                        type="stdio",
                        command="npx",
                        args=["-y", "@anthropic/mcp-filesystem"],
                    ),
                ],
            ),
            execution=ExecutionSettings(
                working_dir="/path/to/worktree",
                timeout_seconds=1200,
                permission_mode="bypassPermissions",
                max_tokens=16000,
            ),
            telemetry=TelemetrySettings(
                endpoint="http://otel-collector:4318",
                exporter="otlp-http",
                environment="development",
            ),
        )

    def test_serialize_minimal(self, minimal_context):
        json_str = minimal_context.model_dump_json()
        data = json.loads(json_str)

        assert data["version"] == "1"
        assert data["agent"]["name"] == "claude"
        assert data["task"]["id"] == "exec-123"
        assert data["execution"]["working_dir"] == "/tmp/worktree"

    def test_serialize_full(self, full_context):
        json_str = full_context.model_dump_json(indent=2)
        data = json.loads(json_str)

        assert data["mcp"]["orchestrator"]["url"] == "http://localhost:8765/sse"
        assert len(data["mcp"]["servers"]) == 1
        assert data["telemetry"]["exporter"] == "otlp-http"

    def test_deserialize(self, full_context):
        json_str = full_context.model_dump_json()
        loaded = AgentExecutionContext.model_validate_json(json_str)

        assert loaded.agent.name == full_context.agent.name
        assert loaded.task.plan_content == full_context.task.plan_content
        assert loaded.mcp.orchestrator.token == full_context.mcp.orchestrator.token

    def test_write_and_load_from_worktree(self, minimal_context, tmp_path):
        # Write config to worktree
        config_path = minimal_context.write_to_worktree(tmp_path)

        # Verify path
        assert config_path == tmp_path / ".deliberate" / "config.json"
        assert config_path.exists()

        # Verify content
        data = json.loads(config_path.read_text())
        assert data["agent"]["name"] == "claude"

        # Load from worktree
        loaded = AgentExecutionContext.load_from_worktree(tmp_path)
        assert loaded.agent.name == minimal_context.agent.name
        assert loaded.task.id == minimal_context.task.id

    def test_config_exists(self, minimal_context, tmp_path):
        # Initially doesn't exist
        assert not AgentExecutionContext.config_exists(tmp_path)

        # Write and check again
        minimal_context.write_to_worktree(tmp_path)
        assert AgentExecutionContext.config_exists(tmp_path)

    def test_load_nonexistent_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            AgentExecutionContext.load_from_worktree(tmp_path)

    def test_roundtrip_preserves_data(self, full_context, tmp_path):
        """Verify all data survives write/read cycle."""
        full_context.write_to_worktree(tmp_path)
        loaded = AgentExecutionContext.load_from_worktree(tmp_path)

        # Compare all fields
        assert loaded.version == full_context.version
        assert loaded.agent.model_dump() == full_context.agent.model_dump()
        assert loaded.task.model_dump() == full_context.task.model_dump()
        assert loaded.mcp.model_dump() == full_context.mcp.model_dump()
        assert loaded.execution.model_dump() == full_context.execution.model_dump()
        assert loaded.telemetry.model_dump() == full_context.telemetry.model_dump()
