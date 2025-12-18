# Agent Protocols

How deliberate communicates with different types of LLM agents.

## Overview

Deliberate supports multiple protocols for agent communication:

| Protocol | Transport | Use Case |
|----------|-----------|----------|
| CLI | Subprocess stdin/stdout | Simple, works today |
| MCP | JSON-RPC over stdio/SSE | Rich tool access |

## CLI Protocol

The default and simplest option. Deliberate spawns a subprocess and communicates via command-line arguments or stdin.

**How it works:**

```python
# Claude: task as argument
proc = subprocess.run(["claude", "--print", "-p", task])

# Gemini: task via stdin
proc = subprocess.run(["gemini", "-y"], input=task)
```

**Pros:**

- Simple, direct integration
- Works with any CLI tool
- No protocol overhead

**Cons:**

- Limited structured communication
- CLI-specific quirks (stdin vs args)

**Configuration:**

```yaml
agents:
  claude:
    type: cli
    command: ["claude", "--print", "-p"]
```

## MCP Protocol

Model Context Protocol, developed by Anthropic. Provides rich tool and resource access.

**How it works:**

1. Start agent as MCP server
2. Send JSON-RPC requests over stdio
3. Agent responds with structured data
4. Access tools, resources, prompts

**Features:**

- Tool discovery and invocation
- Resource access (files, context)
- Structured responses
- Session management

**Pros:**

- Rich tool access (git, filesystem, bash)
- Standard protocol
- Bidirectional communication

**Cons:**

- More complex setup
- Requires MCP-compatible agent

**Configuration:**

```yaml
agents:
  codex-mcp:
    type: mcp
    command: ["codex", "mcp-server"]
```

**Supported agents:**

- `codex mcp-server`
- `claude mcp serve`

## When to Use Which

| Scenario | Recommended |
|----------|-------------|
| Quick planning/review | CLI |
| Code execution with tools | MCP |
| Simple task, any agent | CLI |
| Need git/file operations | MCP |

## Hybrid Configuration

Use both in the same workflow:

```yaml
agents:
  claude-cli:
    type: cli
    command: ["claude", "--print", "-p"]
    capabilities: [planner, reviewer]

  codex-mcp:
    type: mcp
    command: ["codex", "mcp-server"]
    capabilities: [executor]

workflow:
  planning:
    agents: [claude-cli]    # Fast CLI for planning
  execution:
    agents: [codex-mcp]     # MCP for tool access
  review:
    agents: [claude-cli]    # CLI for quick reviews
```

## MCP Server Mode

Deliberate can also run as an MCP server, allowing agents to connect and report status:

```bash
python -m deliberate.mcp_orchestrator_server
```

Agents receive `DELIBERATE_ORCHESTRATOR_URL` environment variable and can call tools like `update_status` to report progress.

## References

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [Claude MCP Documentation](https://docs.anthropic.com/en/docs/build-with-claude/mcp)
