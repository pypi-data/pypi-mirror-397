"""Base adapter interface for LLM backends."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from deliberate.adapters.cli_adapter import MCPServerConfig


@dataclass
class ToolInfo:
    """Information about an available tool.

    Provides a consistent representation of tools across different adapter types
    (MCP, CLI, etc.) so consumers can discover what capabilities are available.
    """

    name: str
    description: str | None = None
    source: str = "unknown"  # e.g., "mcp", "cli", "builtin"
    parameters: dict | None = None  # JSON schema for tool parameters
    metadata: dict = field(default_factory=dict)  # Additional adapter-specific info


@dataclass
class ResourceInfo:
    """Information about an available resource.

    Resources are data sources (files, URIs, etc.) that can be read by the adapter.
    """

    uri: str
    name: str | None = None
    description: str | None = None
    mime_type: str | None = None
    metadata: dict = field(default_factory=dict)


@dataclass
class AdapterResponse:
    """Response from a model adapter call."""

    content: str
    token_usage: int
    duration_seconds: float
    raw_response: dict | None = None
    stdout: str | None = None


class ModelAdapter(ABC):
    """Abstract base class for model adapters."""

    name: str

    @abstractmethod
    async def call(
        self,
        prompt: str,
        *,
        system: str | None = None,
        max_tokens: int | None = None,
        temperature: float = 0.7,
        working_dir: str | None = None,
        schema_name: str | None = None,
    ) -> AdapterResponse:
        """Make a single completion call.

        Args:
            prompt: The user prompt to send.
            system: Optional system prompt.
            max_tokens: Maximum tokens in response.
            temperature: Sampling temperature.
            schema_name: Optional JSON schema name for structured output.
            working_dir: Optional working directory for context.

        Returns:
            AdapterResponse with the model's response.
        """
        ...

    @abstractmethod
    async def run_agentic(
        self,
        task: str,
        *,
        working_dir: str,
        timeout_seconds: int = 1200,
        on_question: Callable[[str], str] | None = None,
        schema_name: str | None = "execution",
        extra_mcp_servers: "list[MCPServerConfig] | None" = None,
    ) -> AdapterResponse:
        """Run an agentic task that may take many minutes and may ask questions.

        Args:
            task: The task description to execute.
            working_dir: Working directory for the agent.
            timeout_seconds: Maximum time for execution.
            on_question: Optional callback for handling questions.
            extra_mcp_servers: Additional MCP servers to inject.

        Returns:
            AdapterResponse with execution results.
        """
        ...

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for a text string.

        Uses a rough heuristic of ~4 characters per token.

        Args:
            text: The text to estimate tokens for.

        Returns:
            Estimated token count.
        """
        return len(text) // 4

    def estimate_cost(self, tokens: int) -> float:
        """Estimate cost in USD for a number of tokens.

        Uses a rough default of $0.20 per 1000 tokens.

        Args:
            tokens: Number of tokens.

        Returns:
            Estimated cost in USD.
        """
        return tokens / 5000

    async def list_tools(self, *, working_dir: str | None = None) -> list[ToolInfo]:
        """List available tools for this adapter.

        Exposes the tools that the wrapped LLM/agent can use. This allows
        consumers to discover capabilities without running a task.

        Args:
            working_dir: Optional working directory context.

        Returns:
            List of ToolInfo describing available tools.
        """
        return []

    async def list_resources(self, *, working_dir: str | None = None) -> list[ResourceInfo]:
        """List available resources for this adapter.

        Exposes data sources (files, URIs) that can be accessed.

        Args:
            working_dir: Optional working directory context.

        Returns:
            List of ResourceInfo describing available resources.
        """
        return []
