# MCP Orchestrator Server

## Overview

The MCP Orchestrator Server is a unified MCP (Model Context Protocol) server that exposes orchestrator functions to agents. It uses SSE (Server-Sent Events) transport to support multiple concurrent agent connections.

## Architecture

```
┌─────────────────┐         ┌──────────────────────┐         ┌────────────┐
│   Agent 1       │────────▶│  MCP Orchestrator    │────────▶│ Orchestrator│
│ (CLI/MCP Agent) │  SSE    │  Server (Starlette)  │ Callback│             │
└─────────────────┘         │                      │         └────────────┘
                            │  - update_status     │
┌─────────────────┐         │  - (future tools)    │
│   Agent 2       │────────▶│                      │
│ (CLI/MCP Agent) │  SSE    └──────────────────────┘
└─────────────────┘
```

## Features

### Current Tools

- **`update_status`**: Allows agents to report their status and progress to the orchestrator
  - `agent_name`: Name of the agent reporting
  - `phase`: Current workflow phase (planning, execution, review, refinement)
  - `status`: Status type (started, progress, completed, error)
  - `message`: Human-readable status message
  - `metadata`: Optional metadata (e.g., progress %, tokens used)

### Future Tools (Planned)

- **`query_context`**: Ask orchestrator for context information
- **`request_clarification`**: Request human clarification on ambiguous points
- **`get_budget_status`**: Check remaining token/cost budget

## Implementation Details

### Transport

The server uses SSE (Server-Sent Events) transport over HTTP, which provides:
- Multiple concurrent client connections
- Bidirectional communication over HTTP
- Standard HTTP infrastructure (proxies, load balancers, etc.)

### Server Stack

- **FastMCP**: High-level MCP server framework that handles all transport/routing
- **Uvicorn**: High-performance ASGI server
- **MCP SDK**: Model Context Protocol implementation

The implementation leverages FastMCP's `@mcp.tool()` decorator for simple tool registration, avoiding manual ASGI/HTTP setup.

### Port Allocation

The server automatically selects an available port on startup (using port 0, which triggers auto-selection). The actual port is stored in `OrchestratorServer.actual_port` and the full URL is available via `get_url()`.

## Usage for Agents

### Environment Variable

Agents receive the server URL via the `DELIBERATE_ORCHESTRATOR_URL` environment variable:

```bash
DELIBERATE_ORCHESTRATOR_URL=http://127.0.0.1:PORT/messages
```

### Connecting

Agents can connect to the MCP server using standard MCP client libraries:

```python
from mcp.client.sse import sse_client

async with sse_client(os.environ["DELIBERATE_ORCHESTRATOR_URL"]) as (read, write):
    # Use MCP client to call tools
    await client.call_tool("update_status", {
        "agent_name": "my_agent",
        "phase": "execution",
        "status": "progress",
        "message": "Processing file 3 of 10"
    })
```

## Lifecycle

1. **Startup**: Orchestrator starts MCP server as async task before workflow begins
2. **Runtime**: Agents connect and call tools as needed
3. **Callbacks**: Server invokes registered callbacks for tool calls (e.g., status updates)
4. **Shutdown**: Orchestrator cancels server task after workflow completes

## File Location

- Implementation: `src/deliberate/mcp_orchestrator_server.py`
- Integration: `src/deliberate/orchestrator.py` (see `_start_orchestrator_server()` and `_stop_orchestrator_server()`)

## Testing

Run the server standalone for testing:

```bash
uv run python -m deliberate.mcp_orchestrator_server
```

This starts the server with a debug callback that prints updates to stdout.

## Verified Functionality

The MCP server has been tested and verified to:
- ✅ Start successfully and auto-allocate ports
- ✅ Generate correct SSE endpoint URLs
- ✅ Accept MCP client connections
- ✅ List tools via MCP protocol
- ✅ Handle tool invocations (update_status)
- ✅ Support multiple concurrent client connections
- ✅ Invoke callbacks correctly
- ✅ Shut down cleanly

All tests pass with 3 concurrent clients each sending multiple status updates.
