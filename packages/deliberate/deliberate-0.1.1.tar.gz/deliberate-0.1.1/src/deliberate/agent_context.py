"""Agent execution context schema for worktree configuration.

This module defines the canonical configuration file written to each worktree
at `.deliberate/config.json`. It contains all context an agent needs for
execution, centralizing configuration that was previously scattered across
adapter instances, environment variables, and callback chains.

Usage:
    # Write config during execution setup
    context = AgentExecutionContext(
        agent=AgentIdentity(name="claude", parser="claude", role="executor"),
        task=TaskContext(id="exec-123", description="Add fibonacci function"),
        execution=ExecutionSettings(working_dir="/path/to/worktree"),
    )
    config_path = context.write_to_worktree(worktree_path)

    # Read config in CLIAdapter
    context = AgentExecutionContext.load_from_worktree(worktree_path)
"""

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class AgentIdentity(BaseModel):
    """Identity and capabilities of the executing agent."""

    name: str
    """Agent name as defined in config (e.g., 'claude', 'gemini')."""

    parser: str
    """Parser type for output parsing (e.g., 'claude', 'gemini', 'codex', 'opencode')."""

    role: Literal["planner", "executor", "reviewer"]
    """Current role the agent is fulfilling."""

    capabilities: list[str] = Field(default_factory=lambda: ["executor"])
    """Agent's declared capabilities."""


class TaskContext(BaseModel):
    """Context about the task being executed."""

    id: str
    """Unique identifier for this execution (e.g., 'exec-a1b2c3d4')."""

    description: str
    """The task description or prompt."""

    plan_id: str | None = None
    """ID of the selected plan, if executing from a plan."""

    plan_content: str | None = None
    """Full content of the selected plan."""


class MCPOrchestratorConfig(BaseModel):
    """Configuration for connecting back to the orchestrator's MCP server."""

    url: str
    """SSE endpoint URL (e.g., 'http://localhost:8765/sse')."""

    token: str
    """Bearer token for authentication."""


class MCPServerConfig(BaseModel):
    """Configuration for an additional MCP server."""

    name: str
    """Server name for identification."""

    type: Literal["stdio", "sse"]
    """Connection type."""

    command: str | None = None
    """Command to execute (for stdio type)."""

    args: list[str] = Field(default_factory=list)
    """Command arguments (for stdio type)."""

    url: str | None = None
    """Server URL (for sse type)."""

    env: dict[str, str] = Field(default_factory=dict)
    """Environment variables for the server process."""


class MCPSettings(BaseModel):
    """MCP server configuration for the agent."""

    orchestrator: MCPOrchestratorConfig | None = None
    """Orchestrator MCP server config (for reporting results back)."""

    servers: list[MCPServerConfig] = Field(default_factory=list)
    """Additional MCP servers available to the agent."""


class ExecutionSettings(BaseModel):
    """Execution environment configuration."""

    working_dir: str
    """Absolute path to the worktree directory."""

    timeout_seconds: int = 1200
    """Maximum execution time in seconds."""

    permission_mode: str = "bypassPermissions"
    """CLI permission mode (default, dontAsk, bypassPermissions, acceptEdits, plan)."""

    max_tokens: int = 8000
    """Maximum tokens for agent response."""


class TelemetrySettings(BaseModel):
    """Telemetry configuration for the agent."""

    endpoint: str | None = None
    """OTLP endpoint URL."""

    exporter: str | None = None
    """Exporter type: none, otlp-http, otlp-grpc."""

    environment: str | None = None
    """Environment name for telemetry tags."""


class AgentExecutionContext(BaseModel):
    """Complete execution context for an agent in a worktree.

    This is the canonical configuration file written to `.deliberate/config.json`
    in each worktree. It contains all the information an agent needs to execute
    a task, replacing the 5-layer parameter passing chain.
    """

    version: str = "1"
    """Schema version for forward compatibility."""

    agent: AgentIdentity
    """Identity and capabilities of the executing agent."""

    task: TaskContext
    """Context about the task being executed."""

    mcp: MCPSettings = Field(default_factory=MCPSettings)
    """MCP server configuration."""

    execution: ExecutionSettings
    """Execution environment settings."""

    telemetry: TelemetrySettings = Field(default_factory=TelemetrySettings)
    """Telemetry configuration."""

    def write_to_worktree(self, worktree_path: Path) -> Path:
        """Write config to .deliberate/config.json in worktree.

        Args:
            worktree_path: Path to the worktree root directory.

        Returns:
            Path to the written config file.
        """
        config_dir = worktree_path / ".deliberate"
        config_dir.mkdir(parents=True, exist_ok=True)
        config_path = config_dir / "config.json"
        config_path.write_text(self.model_dump_json(indent=2))
        return config_path

    @classmethod
    def load_from_worktree(cls, worktree_path: Path) -> "AgentExecutionContext":
        """Load config from .deliberate/config.json in worktree.

        Args:
            worktree_path: Path to the worktree root directory.

        Returns:
            Loaded AgentExecutionContext instance.

        Raises:
            FileNotFoundError: If config file doesn't exist.
            ValidationError: If config file is invalid.
        """
        config_path = worktree_path / ".deliberate" / "config.json"
        return cls.model_validate_json(config_path.read_text())

    @classmethod
    def config_exists(cls, worktree_path: Path) -> bool:
        """Check if config file exists in worktree.

        Args:
            worktree_path: Path to the worktree root directory.

        Returns:
            True if config file exists.
        """
        config_path = worktree_path / ".deliberate" / "config.json"
        return config_path.exists()
