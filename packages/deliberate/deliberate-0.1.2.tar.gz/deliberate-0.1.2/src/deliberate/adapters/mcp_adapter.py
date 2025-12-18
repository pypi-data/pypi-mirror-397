"""MCP (Model Context Protocol) adapter for LLM agents.

Uses the official `mcp` client to manage protocol negotiation, transport,
and future protocol updates.
"""

import asyncio
import logging
import time
from contextlib import AsyncExitStack
from datetime import timedelta
from typing import Any, Callable

from mcp import (
    ClientSession,
    Implementation,
    StdioServerParameters,
    stdio_client,
    types,
)
from mcp.shared.exceptions import McpError
from mcp.shared.version import SUPPORTED_PROTOCOL_VERSIONS

from deliberate import __version__ as deliberate_version
from deliberate.adapters.base import AdapterResponse, ModelAdapter, ResourceInfo, ToolInfo

logger = logging.getLogger(__name__)


class MCPAdapter(ModelAdapter):
    """Adapter for MCP-based LLM agents using the official MCP client."""

    def __init__(
        self,
        name: str,
        command: list[str],
        env: dict[str, str] | None = None,
        timeout_seconds: int = 1200,
    ):
        """Initialize MCP adapter.

        Args:
            name: Agent name for logging/tracking.
            command: Command to start MCP server (e.g. ["claude", "mcp", "serve"]).
            env: Optional environment variables for the server process.
            timeout_seconds: Default timeout for operations.
        """
        if not command:
            raise ValueError("MCPAdapter requires a command to start the MCP server")

        self.name = name
        self.command = command
        self.env = env or {}
        self.timeout_seconds = timeout_seconds

        self._stack: AsyncExitStack | None = None
        self._session: ClientSession | None = None
        self._server_cwd: str | None = None
        self._protocol_version: str | None = None

    def _build_server_params(self, working_dir: str | None = None) -> StdioServerParameters:
        """Convert adapter configuration into stdio server parameters."""
        return StdioServerParameters(
            command=self.command[0],
            args=self.command[1:],
            env=self.env or None,
            cwd=working_dir,
        )

    async def _start_session(self, *, working_dir: str | None = None) -> ClientSession:
        """Start the MCP stdio transport and initialize the protocol session."""
        self._stack = AsyncExitStack()
        self._server_cwd = working_dir

        params = self._build_server_params(working_dir)
        try:
            read_stream, write_stream = await self._stack.enter_async_context(stdio_client(params))
            session = ClientSession(
                read_stream=read_stream,
                write_stream=write_stream,
                read_timeout_seconds=timedelta(seconds=self.timeout_seconds),
                client_info=Implementation(name="deliberate", version=deliberate_version),
            )

            init_result = await session.initialize()
            self._protocol_version = str(init_result.protocolVersion)
            self._session = session

            logger.info(
                "Connected to MCP server (protocol %s, supported: %s)",
                init_result.protocolVersion,
                ", ".join(SUPPORTED_PROTOCOL_VERSIONS),
            )
            return session
        except Exception:
            await self._shutdown_session()
            raise

    async def _shutdown_session(self) -> None:
        """Close the session and underlying transport."""
        if self._stack is not None:
            try:
                await self._stack.aclose()
            finally:
                self._stack = None
                self._session = None
                self._server_cwd = None
                self._protocol_version = None

    async def _ensure_session(self, *, working_dir: str | None = None) -> ClientSession:
        """Ensure we have an initialized session, restarting if cwd changes."""
        if self._session and (working_dir is None or working_dir == self._server_cwd):
            return self._session

        if self._session and working_dir != self._server_cwd:
            logger.info(
                "Restarting MCP session to use working directory %s (was %s)",
                working_dir,
                self._server_cwd,
            )
            await self._shutdown_session()

        return await self._start_session(working_dir=working_dir)

    async def _list_all_tools(self, session: ClientSession) -> list[types.Tool]:
        """Fetch the full tool list, handling pagination for forward compatibility."""
        tools: list[types.Tool] = []
        cursor: str | None = None

        while True:
            params = types.PaginatedRequestParams(cursor=cursor) if cursor else None
            result = await session.list_tools(params=params)
            tools.extend(result.tools)
            cursor = result.nextCursor
            if not cursor:
                break

        return tools

    async def _list_all_resources(self, session: ClientSession) -> list[types.Resource]:
        """Fetch the full resource list, handling pagination for forward compatibility."""
        resources: list[types.Resource] = []
        cursor: str | None = None

        while True:
            params = types.PaginatedRequestParams(cursor=cursor) if cursor else None
            result = await session.list_resources(params=params)
            resources.extend(result.resources)
            cursor = result.nextCursor
            if not cursor:
                break

        return resources

    async def list_tools(self, *, working_dir: str | None = None) -> list[ToolInfo]:
        """List available MCP tools.

        Exposes all tools provided by the MCP server in a normalized format.

        Args:
            working_dir: Optional working directory for the MCP server.

        Returns:
            List of ToolInfo with tool names, descriptions, and schemas.
        """
        session = await self._ensure_session(working_dir=working_dir)
        mcp_tools = await self._list_all_tools(session)

        return [
            ToolInfo(
                name=tool.name,
                description=tool.description,
                source="mcp",
                parameters=tool.inputSchema,  # inputSchema is required per MCP spec
                metadata={
                    "protocol_version": self._protocol_version,
                },
            )
            for tool in mcp_tools
        ]

    async def list_resources(self, *, working_dir: str | None = None) -> list[ResourceInfo]:
        """List available MCP resources.

        Exposes all resources (files, URIs) provided by the MCP server.

        Args:
            working_dir: Optional working directory for the MCP server.

        Returns:
            List of ResourceInfo with URIs and metadata.
        """
        session = await self._ensure_session(working_dir=working_dir)
        mcp_resources = await self._list_all_resources(session)

        return [
            ResourceInfo(
                uri=str(resource.uri),
                name=resource.name,
                description=getattr(resource, "description", None),
                mime_type=getattr(resource, "mimeType", None),
                metadata={
                    "protocol_version": self._protocol_version,
                },
            )
            for resource in mcp_resources
        ]

    @staticmethod
    def _build_sampling_message(text: str) -> types.SamplingMessage:
        """Create a user sampling message with typed content."""
        return types.SamplingMessage(
            role="user",
            content=types.TextContent(type="text", text=text),
        )

    def _build_create_message_request(
        self,
        messages: list[types.SamplingMessage],
        *,
        max_tokens: int,
        temperature: float,
        system_prompt: str | None,
        include_context: bool,
    ) -> types.ServerRequest:
        """Construct a sampling/createMessage request for the MCP server.

        Note: sampling/createMessage is modeled as a server request in MCP. We
        return `Any` here and rely on the client to accept the JSON-RPC payload.
        """
        params = types.CreateMessageRequestParams(
            messages=messages,
            maxTokens=max_tokens,
            temperature=temperature,
            systemPrompt=system_prompt,
            includeContext="allServers" if include_context else None,
        )

        return types.ServerRequest(root=types.CreateMessageRequest(params=params))

    @staticmethod
    def _extract_text_content(content: Any) -> str:
        """Normalize different MCP content types to text."""
        if isinstance(content, types.TextContent):
            return content.text
        if hasattr(content, "text"):
            return str(content.text)
        if hasattr(content, "data"):
            return str(content.data)
        return str(content)

    async def _send_sampling_request(
        self,
        session: ClientSession,
        request: Any,
        *,
        timeout_seconds: int | None = None,
    ) -> types.CreateMessageResult:
        """Send a sampling request and handle MCP errors with context."""
        request_timeout = timedelta(seconds=timeout_seconds) if timeout_seconds else None
        try:
            return await session.send_request(
                request,
                types.CreateMessageResult,
                request_read_timeout_seconds=request_timeout,
            )
        except McpError as exc:
            raise RuntimeError(f"MCP sampling error ({exc.error.code}): {exc.error.message}") from exc

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
        """Make a single completion call via MCP sampling/createMessage."""
        session = await self._ensure_session(working_dir=working_dir)
        start_time = time.time()

        request = self._build_create_message_request(
            [self._build_sampling_message(prompt)],
            max_tokens=max_tokens or 4000,
            temperature=temperature,
            system_prompt=system,
            include_context=True,
        )

        result = await self._send_sampling_request(session, request)

        duration = time.time() - start_time
        content = self._extract_text_content(result.content)
        token_usage = self.estimate_tokens(content + prompt)

        return AdapterResponse(
            content=content,
            token_usage=token_usage,
            duration_seconds=duration,
            raw_response=result.model_dump(mode="json", by_alias=True),
            stdout=content,
        )

    async def run_agentic(
        self,
        task: str,
        *,
        working_dir: str,
        timeout_seconds: int = 1200,
        on_question: Callable[[str], str] | None = None,
        schema_name: str | None = None,
        extra_mcp_servers: list | None = None,
    ) -> AdapterResponse:
        """Run an agentic task via MCP using the typed client."""
        session = await self._ensure_session(working_dir=working_dir)
        start_time = time.time()

        try:
            tools = await self._list_all_tools(session)
        except Exception as exc:  # pragma: no cover - defensive against unsupported servers
            logger.warning("Failed to list MCP tools: %s", exc)
            tools = []

        try:
            resources = await self._list_all_resources(session)
        except Exception as exc:  # pragma: no cover
            logger.warning("Failed to list MCP resources: %s", exc)
            resources = []

        tool_names = ", ".join(t.name for t in tools) if tools else "None"
        resource_names = ", ".join(str(r.uri) for r in resources) if resources else "None"

        task_message = (
            f"Task: {task}\n\n"
            f"Working directory: {working_dir}\n\n"
            "Use the available MCP tools and resources to complete the task.\n"
            f"Tools: {tool_names}\n"
            f"Resources: {resource_names}\n"
            "Summarize the actions taken and the results."
        )

        request = self._build_create_message_request(
            [self._build_sampling_message(task_message)],
            max_tokens=8000,
            temperature=0.0,  # Deterministic for task execution
            system_prompt=None,
            include_context=True,
        )

        result = await self._send_sampling_request(session, request, timeout_seconds=timeout_seconds)

        duration = time.time() - start_time
        content = self._extract_text_content(result.content)
        token_usage = self.estimate_tokens(task + content)

        return AdapterResponse(
            content=content,
            token_usage=token_usage,
            duration_seconds=duration,
            raw_response=result.model_dump(mode="json", by_alias=True),
            stdout=content,
        )

    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._shutdown_session()

    def __del__(self):
        """Best-effort cleanup when adapter is destroyed."""
        if self._stack is not None:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self._shutdown_session())
            except Exception:
                pass
