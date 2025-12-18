# Configuring Agents

Deliberate supports three agent types: CLI, MCP, and Fake.

## Agent Types

| Type | Description | Use Case |
|------|-------------|----------|
| `cli` | Shell command that accepts prompts | Claude, Gemini, Codex CLIs |
| `mcp` | MCP-compatible server | Rich tool access |
| `fake` | Test double | Development, CI |

## CLI Agents

Most common. Spawns a subprocess and communicates via stdin/stdout.

```yaml
agents:
  claude:
    type: cli
    command: ["claude", "--print", "-p"]
    capabilities: [planner, executor, reviewer]
    config:
      max_tokens: 16000
      timeout_seconds: 1200
    model: "claude-opus-4-5-20251101"  # Optional: specific model ID

  gemini:
    type: cli
    command: ["gemini", "-y", "--output-format", "json"]
    capabilities: [planner, reviewer]
    model: "gemini-3.0-pro"  # Optional: specific model ID
```

### Capabilities

- `planner` — Can propose plans
- `executor` — Can implement code
- `reviewer` — Can review and score

Assign based on what the agent is good at.

### Model Configuration

The `model` field is optional but recommended. It helps tracking which specific model version was used for a task, and is required for API-based agents to know which endpoint to call. For CLI agents, it serves as documentation or can be passed to the tool if supported.

## MCP Agents

For agents that expose an MCP server (e.g., `codex mcp-server`).

```yaml
agents:
  codex-mcp:
    type: mcp
    command: ["codex", "mcp-server"]
    capabilities: [executor, reviewer]
    config:
      timeout_seconds: 600
    model: "gpt-5.2"
```

MCP provides richer tool access (git, filesystem, bash) compared to simple CLI.

## Fake Agents

For testing without API calls.

```yaml
agents:
  fake-planner:
    type: fake
    behavior: planner    # Returns a structured plan
    capabilities: [planner]

  fake-executor:
    type: fake
    behavior: echo       # Echoes the task
    capabilities: [executor]

  fake-critic:
    type: fake
    behavior: critic     # Returns review scores
    capabilities: [reviewer]
```

**Behaviors:**

- `echo` — Returns the input task
- `planner` — Returns a structured plan
- `critic` — Returns review scores
- `flaky` — Randomly fails (for testing retries)

## Auto-Detection

Run `deliberate init` to auto-detect available CLI tools:

```bash
deliberate init
```

This checks for `claude`, `gemini`, `codex`, `opencode`, etc. and creates a config with what's found.

## CLI-Specific Integration

Each CLI tool has slightly different integration requirements:

| CLI | Task Input | MCP Config | Notes |
|-----|-----------|-----------|-------|
| `claude` | `--print -p TASK` | `--mcp-config JSON` | Inline JSON flag |
| `gemini` | `-y` + stdin | `.gemini/settings.json` | File-based config |
| `codex` | `exec TASK` | Not yet supported | Discovery only |
| `opencode` | `run --format json TASK` | Not yet supported | JSON lines output |

**MCP Server Injection:**

- **Claude**: Pass MCP servers inline via `--mcp-config '{"mcpServers": {...}}'`
- **Gemini**: Writes `.gemini/settings.json` to the working directory with `mcpServers` config. You can also set your `GEMINI_API_KEY` in this file.
- **Codex**: Use `type: mcp` with `codex mcp-server` for full MCP support

## Environment Variables and Keys

API keys can be set via:

1. System environment: `export ANTHROPIC_API_KEY=...`
2. `.env` file in project root
3. **Gemini Specific**: `~/.gemini/settings.json` for API keys and global settings.

```yaml
agents:
  claude:
    type: cli
    command: ["claude", "--print", "-p"]
    env:
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}  # From environment
```

For Gemini:
Deliberate will automatically update the local `.gemini/settings.json` to inject the MCP server configuration required for tools to work.

## Assigning Agents to Phases

```yaml
workflow:
  planning:
    agents: [claude, gemini]   # Both propose plans
  execution:
    agents: [claude]           # Only Claude executes
  review:
    agents: [gemini, codex]    # Both review
```

## Timeouts and Limits

```yaml
agents:
  claude:
    type: cli
    command: ["claude", "--print", "-p"]
    config:
      max_tokens: 16000
      timeout_seconds: 1200    # 20 minutes

limits:
  budget:
    max_total_tokens: 500000
    max_cost_usd: 10.0
  time:
    hard_timeout_minutes: 45
```