# Quickstart

Get deliberate running in 5 minutes.

## Install

```bash
uv add deliberate
# or
pip install deliberate
```

## Initialize

Run `init` to auto-detect available LLM CLI tools and create a config:

```bash
deliberate init
```

This creates `.deliberate.yaml` with agents found on your system (claude, gemini, codex, etc.).

## Set API Keys

Export your API keys:

```bash
export ANTHROPIC_API_KEY=sk-...
export GEMINI_API_KEY=...
export OPENAI_API_KEY=sk-...
```

Gemini can also read keys from `~/.gemini/settings.json`.

## Run a Task (git-native macro: plan → work → merge)

```bash
# Inline task
deliberate run "Add a function to calculate fibonacci numbers"

# From file
echo "Add input validation to the login form" > task.txt
deliberate run "@task.txt"

# Later, you can resume/inspect:
#   deliberate status   # show branch + plan
#   deliberate work     # rerun execution with committed plan
#   deliberate merge    # review/merge results back to parent branch
```

### Common Options

```bash
# Skip planning (use first agent's plan)
deliberate run "task" --skip-planning

# Skip review (just execute)
deliberate run "task" --skip-review

# Choose a profile
deliberate run "task" --profile cheap
deliberate run "task" --profile powerful

# Configure how changes are applied from the worktree (merge or squash) onto a deliberate/* branch
deliberate run "task" --config "workflow.execution.worktree.apply_strategy=squash"

# CI mode (non-interactive, writes artifacts)
deliberate run "task" --ci --artifacts ./output

# Show live dashboard with agent stdout (default)
deliberate run "task" -v
# Hide stdout panel if you want status-only
deliberate run "task" -v --verbose-view status
```

After a successful local run, results are applied onto a dedicated `deliberate/<slug>` branch (not your working tree). Use `deliberate merge` or native Git tooling to integrate, or open the worktree/branch in your editor before merging.

## Separate Plan/Work Flow

For more control, run planning and execution separately:

```bash
# Generate plan on a new branch
deliberate plan "Add user authentication"
# Creates deliberate/add-user-authentication branch with PLAN.md

# Review and edit PLAN.md if needed
code PLAN.md  # or vim, etc.
git add PLAN.md && git commit -m "Refined plan"

# Execute the plan
deliberate work

# Review results and merge
deliberate merge
```

This flow is useful when you want to:
- Review AI-generated plans before execution
- Edit the plan manually
- Run execution multiple times with different agents

## Interactive Review Mode

Use `--interactive` (or `-i`) to review agent results in a TUI before committing:

```bash
deliberate run "Add feature" --interactive
```

This launches a terminal UI where you can:
- View diffs from each agent's worktree
- Override the jury's vote
- Select which implementation to merge

## Verify It Works

Run with fake agents (no API keys needed):

```bash
deliberate run "test task" --config - <<EOF
agents:
  fake:
    type: fake
    behavior: echo
    capabilities: [planner, executor, reviewer]
workflow:
  planning: { enabled: false }
  execution: { enabled: true, agents: [fake] }
  review: { enabled: false }
EOF
```

## Next Steps

- [Workflow Phases](guides/workflow.md) — Understand what happens at each step
- [Configuring Agents](guides/agents.md) — Add more agents, tune settings
- [Profiles](guides/profiles.md) — Balance cost vs quality
- [CLI Reference](reference/cli.md) — All commands and options
