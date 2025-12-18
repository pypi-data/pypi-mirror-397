# Architecture

How deliberate's components fit together.

## High-Level Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              deliberate CLI                                  │
│                                                                             │
│  deliberate run "task"    deliberate init    deliberate stats               │
├─────────────────────────────────────────────────────────────────────────────┤
│                              Orchestrator                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐│
│  │   Config    │  │   Budget    │  │  Worktree   │  │   Agent Tracker     ││
│  │   Loader    │  │   Tracker   │  │   Manager   │  │    (DuckDB)         ││
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────┘│
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                         Workflow Phases                              │  │
│  │  ┌──────────┐  ┌───────────┐  ┌──────────┐  ┌────────────────────┐  │  │
│  │  │ Planning │→ │ Execution │→ │  Review  │→ │    Refinement      │  │  │
│  │  └──────────┘  └───────────┘  └──────────┘  └────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                            Adapter Layer                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────────────────┐ │
│  │ CLIAdapter  │  │ MCPAdapter  │  │         FakeAdapter                 │ │
│  │ (subprocess)│  │ (JSON-RPC)  │  │         (testing)                   │ │
│  └──────┬──────┘  └──────┬──────┘  └─────────────────────────────────────┘ │
└─────────┴────────────────┴─────────────────────────────────────────────────┘
          │                │
          ▼                ▼
    ┌───────────┐    ┌───────────┐
    │  claude   │    │ MCP server│
    │  gemini   │    │           │
    │  codex    │    │           │
    └───────────┘    └───────────┘
```

## Key Components

### Orchestrator

The central coordinator. It:

- Loads configuration
- Builds adapters for each agent
- Runs workflow phases in sequence
- Tracks budget and timing
- Produces artifacts

### Adapters

Adapters abstract different ways to talk to LLMs:

- **CLIAdapter**: Spawns subprocess, passes task, reads stdout
- **MCPAdapter**: Connects via JSON-RPC, accesses tools/resources
- **FakeAdapter**: Returns canned responses for testing

All adapters implement the same interface, so phases don't care which type they're using.

### Worktree Manager

Creates isolated git worktrees for execution:

```
.deliberate/worktrees/
├── jury-a1b2c3d4/    # Agent 1's workspace
├── jury-e5f6g7h8/    # Agent 2's workspace
└── ...
```

Each agent gets a clean copy of the repo. Changes don't affect your working directory until you accept them.

Once an agent's changes are approved, they are applied back to the main repository using a configurable `apply_strategy` (`merge`, `squash`, or `copy`). The `merge` and `squash` strategies leverage Git to integrate changes, while `copy` directly overwrites files. If `merge` or `squash` fail (e.g., due to conflicts), the system will automatically fall back to the `copy` strategy to ensure the changes are applied.
### Budget Tracker

Enforces limits on:

- Total tokens across all agents
- Total cost in USD
- Requests per agent
- Wall-clock time

Raises `BudgetExceededError` if limits are hit.

### Agent Tracker

DuckDB database storing:

- Which agents are best at planning vs execution
- Win rates and average scores
- Performance trends over time

Query with `deliberate stats`.

## Phase Details

### Planning Phase

1. Each planner agent receives the task
2. Each returns a structured plan
3. If debate enabled, agents critique each other
4. Selection picks the winner (LLM judge, voting, or first)

### Execution Phase

1. Create worktree for the agent
2. Pass task + selected plan
3. Agent makes changes
4. Collect diff and summary
5. Run validation (lint, test, fix loop)

### Review Phase

1. Each reviewer receives the diff
2. Each scores on criteria (correctness, quality, etc.)
3. Votes aggregated (Borda, approval, weighted)
4. Winner selected with confidence score

### Refinement Phase

1. Extract feedback from low-scoring reviews
2. Re-execute with feedback context (same worktree)
3. Re-review
4. Keep best version, revert if regression

## Configuration Loading

Deliberate searches for config in order:

1. `--config` flag (explicit path)
2. `.deliberate.yaml` in current directory
3. `~/.config/deliberate/config.yaml` (user config)

Profiles are overlays that modify the base config.

## Artifacts

CI mode produces:

- `deliberate-run.json` — Machine-readable full result
- `deliberate-report.md` — Human-readable summary

Both contain: task, plan, execution result, review scores, timing, cost.
