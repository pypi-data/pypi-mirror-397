"""Unit tests for MCP adapter."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from mcp import types

from deliberate.adapters.mcp_adapter import MCPAdapter


@pytest.fixture
def adapter() -> MCPAdapter:
    """Create an MCP adapter instance."""
    return MCPAdapter(
        name="test_mcp",
        command=["claude", "mcp", "serve"],
        timeout_seconds=30,
    )


def make_text_result(text: str = "ok") -> types.CreateMessageResult:
    """Helper to build a CreateMessageResult with text content."""
    return types.CreateMessageResult(
        role="assistant",
        content=types.TextContent(type="text", text=text),
        model="dummy",
    )


@pytest.mark.asyncio
async def test_call_builds_sampling_request(adapter: MCPAdapter):
    """Ensure call constructs typed sampling/createMessage requests."""
    mock_session = AsyncMock()
    mock_session.send_request.return_value = make_text_result("response")
    adapter._session = mock_session

    result = await adapter.call("hello world", system="sys prompt", max_tokens=123, temperature=0.2)

    request = mock_session.send_request.call_args[0][0]
    inner_request = request.root
    assert isinstance(inner_request, types.CreateMessageRequest)
    assert inner_request.params.maxTokens == 123
    assert inner_request.params.systemPrompt == "sys prompt"
    assert inner_request.params.temperature == 0.2
    assert inner_request.params.includeContext == "allServers"
    assert inner_request.params.messages[0].content.text == "hello world"

    assert result.content == "response"


@pytest.mark.asyncio
async def test_run_agentic_uses_pagination(adapter: MCPAdapter):
    """Agentic runs should fetch paginated tools/resources and include context."""
    mock_session = AsyncMock()
    mock_session.send_request.return_value = make_text_result("agentic")

    mock_session.list_tools = AsyncMock(
        side_effect=[
            types.ListToolsResult(
                tools=[types.Tool(name="git", inputSchema={})],
                nextCursor="cursor-1",
            ),
            types.ListToolsResult(
                tools=[types.Tool(name="bash", inputSchema={})],
                nextCursor=None,
            ),
        ]
    )
    mock_session.list_resources = AsyncMock(
        return_value=types.ListResourcesResult(
            resources=[types.Resource(name="readme", uri="file:///tmp/readme.md", description="readme")],
            nextCursor=None,
        )
    )

    adapter._session = mock_session
    adapter._server_cwd = "/tmp/project"

    response = await adapter.run_agentic("do work", working_dir="/tmp/project", timeout_seconds=10)

    # Pagination: second call uses the next cursor
    assert mock_session.list_tools.await_count == 2
    first_kwargs = mock_session.list_tools.await_args_list[0].kwargs
    second_kwargs = mock_session.list_tools.await_args_list[1].kwargs
    assert first_kwargs["params"] is None
    assert second_kwargs["params"].cursor == "cursor-1"

    request = mock_session.send_request.call_args[0][0].root
    assert "Working directory: /tmp/project" in request.params.messages[0].content.text
    assert request.params.includeContext == "allServers"

    assert response.content == "agentic"


@pytest.mark.asyncio
async def test_ensure_session_restarts_on_cwd_change(adapter: MCPAdapter):
    """Working directory changes should trigger a new MCP session."""
    adapter._session = MagicMock()
    adapter._server_cwd = "/tmp/old"

    adapter._shutdown_session = AsyncMock()
    adapter._start_session = AsyncMock(return_value="new-session")

    session = await adapter._ensure_session(working_dir="/tmp/new")

    adapter._shutdown_session.assert_awaited()
    adapter._start_session.assert_awaited_with(working_dir="/tmp/new")
    assert session == "new-session"


def test_mcp_adapter_estimate_tokens(adapter: MCPAdapter):
    """Test token estimation heuristic."""
    text = "a" * 400
    tokens = adapter.estimate_tokens(text)
    assert tokens == 100
