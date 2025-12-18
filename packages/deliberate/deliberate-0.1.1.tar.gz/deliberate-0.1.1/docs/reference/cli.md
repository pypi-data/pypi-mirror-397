# CLI Reference

Complete reference for all `deliberate` commands and options.

## Global Options

```bash
deliberate --help              # Show available commands
deliberate --install-completion  # Install shell completion
deliberate --show-completion   # Show completion script
```

## Core Workflow Commands

### `run`

Run a complete workflow (plan → work → merge) on a new branch.

```bash
deliberate run "Add user authentication"
deliberate run @task.txt                    # Read task from file
deliberate run "Fix bug" --profile powerful # Use powerful models
deliberate run "Feature" --ci --artifacts ./out  # CI mode
```

| Option | Short | Description |
|--------|-------|-------------|
| `--config` | `-c` | Config file path |
| `--agents` | `-a` | Override agents (comma-separated) |
| `--profile` | `-p` | Profile: `cheap`, `balanced`, `powerful` |
| `--ci` | | CI mode (non-interactive, strict exit codes) |
| `--artifacts` | | Directory for run artifacts (default: `artifacts`) |
| `--skip-planning` | | Skip planning phase |
| `--skip-review` | | Skip review phase |
| `--dry-run` | | Run without making changes |
| `--json` | | Output as JSON |
| `--max-iterations` | | Override max refinement iterations |
| `--verbose` | `-v` | Verbose output |
| `--verbose-view` | | Dashboard view: `status`, `stdout`, `both` |
| `--interactive` | `-i` | Enable interactive review TUI |
| `--pager/--no-pager` | | Use pager for large diffs (default: enabled) |
| `--allow-dirty` | | Allow uncommitted changes |
| `--reuse-branch` | | Reuse existing branch, overwrite PLAN.md |
| `--evolve` | `-e` | Enable evolution phase (experimental) |
| `--evolve-iterations` | | Max evolution iterations (default: 10) |
| `--plan-only` | | Planning only, output JSON (for integrations) |
| `--from-plan` | | Load plan from JSON file |

**Tracing Options:**

| Option | Description |
|--------|-------------|
| `--trace` | Enable OpenTelemetry tracing |
| `--otlp-endpoint` | OTLP collector endpoint (e.g., `http://localhost:4317`) |
| `--otlp-protocol` | OTLP protocol: `grpc` (default) or `http` |
| `--trace-console` | Export traces to console/stdout |

### `plan`

Generate an execution plan and commit it to a new branch.

```bash
deliberate plan "Add user authentication"
deliberate plan @task.txt --branch deliberate/my-feature
```

| Option | Short | Description |
|--------|-------|-------------|
| `--config` | `-c` | Config file path |
| `--branch` | `-b` | Explicit branch name |
| `--profile` | `-p` | Profile: `cheap`, `balanced`, `powerful` |
| `--verbose` | `-v` | Verbose output |
| `--allow-dirty` | | Allow uncommitted changes |
| `--reuse-branch` | | Reuse existing branch |

### `work`

Execute the plan from the current deliberate branch.

```bash
deliberate work
deliberate work --branch deliberate/my-feature
deliberate work --skip-review
```

| Option | Short | Description |
|--------|-------|-------------|
| `--config` | `-c` | Config file path |
| `--branch` | `-b` | Deliberate branch to use |
| `--profile` | `-p` | Optimization profile |
| `--verbose` | `-v` | Verbose output |
| `--skip-review` | | Skip review phase |

### `merge`

Review results and merge winning implementation.

```bash
deliberate merge
deliberate merge --auto           # No prompts
deliberate merge --no-squash      # Preserve commits
deliberate merge --keep-branch    # Don't delete branch
```

| Option | Short | Description |
|--------|-------|-------------|
| `--config` | `-c` | Config file path |
| `--branch` | `-b` | Branch to merge |
| `--auto` | | Automatic merge without prompts |
| `--squash/--no-squash` | | Squash commits (default: squash) |
| `--delete-branch/--keep-branch` | | Delete branch after merge (default: delete) |
| `--profile` | `-p` | Profile for review phase |
| `--skip-review` | | Use first successful result |

### `status`

Show current workflow status.

```bash
deliberate status
deliberate status --json
```

| Option | Description |
|--------|-------------|
| `--json` | Output as JSON |

### `abort`

Abort the current workflow and return to parent branch.

```bash
deliberate abort
```

## Setup Commands

### `init`

Detect LLM tools and create configuration.

```bash
deliberate init                  # Create .deliberate.yaml
deliberate init --user           # Create in user config dir
deliberate init --quick          # Fast mode, skip auth checks
deliberate init --profile powerful  # Set default profile
```

| Option | Short | Description |
|--------|-------|-------------|
| `--force` | `-f` | Overwrite existing config |
| `--user` | `-u` | Create in user config directory |
| `--quick` | `-q` | Fast mode (skip auth and MCP detection) |
| `--skip-auth` | | Skip authentication verification |
| `--include-unauth` | | Include agents that failed auth |
| `--skip-mcp` | | Skip MCP server configuration |
| `--profile` | `-p` | Default profile (default: `balanced`) |
| `--verbose` | `-v` | Verbose output |

### `validate`

Validate a configuration file.

```bash
deliberate validate
deliberate validate --config ./my-config.yaml
```

| Option | Short | Description |
|--------|-------|-------------|
| `--config` | `-c` | Config file path |

## Analytics Commands

### `stats`

Show agent performance statistics.

```bash
deliberate stats                 # All stats
deliberate stats planners        # Planner stats only
deliberate stats executors       # Executor stats only
deliberate stats reviewers       # Reviewer stats only
deliberate stats -a claude       # Specific agent
deliberate stats --json          # JSON output
```

| Option | Short | Description |
|--------|-------|-------------|
| `--agent` | `-a` | Filter by agent name |
| `--json` | | Output as JSON |
| `--limit` | `-n` | Max agents per role (default: 10) |

### `clear-stats`

Clear all agent performance tracking data.

```bash
deliberate clear-stats
```

### `history`

Show recent workflow history.

```bash
deliberate history
deliberate history -n 20         # Last 20 workflows
deliberate history --json
```

| Option | Short | Description |
|--------|-------|-------------|
| `--limit` | `-n` | Number of workflows (default: 10) |
| `--json` | | Output as JSON |

## Automation Commands

### `maintain`

Run autonomous maintenance to fix flaky tests.

```bash
deliberate maintain --repo-owner myorg --repo-name myrepo
deliberate maintain --repo-owner myorg --repo-name myrepo \
  --test-command "pytest tests/unit" \
  --detect-runs 10 \
  --verify-runs 50
```

| Option | Description |
|--------|-------------|
| `--test-command` | Test command (default: `pytest`) |
| `--detect-runs` | Runs to detect flakes (default: 5) |
| `--verify-runs` | Runs to verify fix (default: 100) |
| `--repo-owner` | GitHub repository owner (required) |
| `--repo-name` | GitHub repository name (required) |

### `github-handle`

Handle GitHub events (triggered by GitHub Action bot).

```bash
deliberate github-handle
```

Used internally by the GitHub Action integration.

## Config File Locations

Deliberate searches for configuration in this order:

1. `./.deliberate.yaml` (project root)
2. `./deliberate.yaml` (project root)
3. `~/.deliberate/config.yaml` (user config)

Override with `--config` on any command.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Configuration error |
| 3 | Planning failed |
| 4 | Execution failed |
| 5 | Review failed / quality threshold not met |

In CI mode (`--ci`), exit codes are strict for pipeline integration.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | API key for Claude |
| `GEMINI_API_KEY` | API key for Gemini (also via `~/.gemini/settings.json`) |
| `OPENAI_API_KEY` | API key for OpenAI/Codex |
| `DELIBERATE_CONFIG` | Default config file path |
| `DELIBERATE_PROFILE` | Default profile |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP endpoint for tracing |
