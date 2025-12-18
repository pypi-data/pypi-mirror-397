# Workflow Phases

Deliberate runs tasks through up to five phases. Each can be enabled/disabled independently.

## 1. Planning

Multiple agents propose plans for the task. They can optionally debate their approaches before a winner is selected.

```yaml
workflow:
  planning:
    enabled: true
    agents: [claude, gemini]
    debate:
      enabled: true
      rounds: 1
    selection:
      method: llm_judge  # or borda, first
      judge: claude
```

**Selection methods:**

- `llm_judge` — Another LLM picks the best plan
- `borda` — Agents vote, points by ranking
- `first` — Just use the first plan (skip voting)

## 2. Execution

The selected plan is executed by one or more agents in isolated git worktrees. Each agent produces a diff and summary.

```yaml
workflow:
  execution:
    enabled: true
    agents: [claude]
    worktree:
      enabled: true
      root: .deliberate/worktrees
      cleanup: true
```

Worktrees prevent agents from interfering with each other or your working directory.

## 3. Validation (TDD Inner Loop)

Before expensive LLM review, deliberate runs a cheap validation loop:

1. **Lint** — Catch syntax errors immediately
2. **Test** — Run the project's test suite
3. **Fix** — If tests fail, feed errors back to the agent
4. **Retry** — Repeat until tests pass or max iterations reached

This prevents wasting review cycles on obviously broken code.

```yaml
workflow:
  execution:
    validation:
      lint_command: "ruff check ."
      test_command: "pytest"
      max_fix_iterations: 3
```

### Dev Container Isolation

For extra security, validation can run inside a Docker container:

```yaml
workflow:
  execution:
    validation:
      devcontainer:
        enabled: true
        auto_detect: true  # Finds .devcontainer/devcontainer.json
```

This prevents agent-generated code from affecting the host system.
See [Dev Container Support](devcontainer.md) for details.

## 4. Review

Multiple agents review the execution results, scoring on criteria like correctness, code quality, and completeness.

```yaml
workflow:
  review:
    enabled: true
    agents: [claude, gemini]
    scoring:
      criteria: [correctness, code_quality, completeness, risk]
    aggregation:
      method: borda  # or approval, weighted_borda
```

**Aggregation methods:**

- `borda` — Points based on ranking position
- `approval` — Count scores above threshold
- `weighted_borda` — Borda with reviewer weights

## 5. Refinement

If review confidence is low, refinement iterates with feedback:

1. Extract issues from reviews
2. Re-execute with feedback context
3. Re-review the updated code
4. Revert if score drops

```yaml
workflow:
  refinement:
    enabled: true
    min_confidence: 0.3
    min_winner_score: 0.6
    max_iterations: 2
    revert_on_regression: true
```

## Skipping Phases

Use CLI flags to skip phases:

```bash
deliberate run "task" --skip-planning   # Use first agent's plan
deliberate run "task" --skip-review     # No peer review
```

Or disable in config:

```yaml
workflow:
  planning:
    enabled: false
```

## Git-Native Workflow

Deliberate exposes the workflow phases as atomic, git-native commands. This allows for manual intervention, state persistence, and a more controlled development process.

### `deliberate plan <task>`

Analyzes the repo, creates a feature branch (`deliberate/<task-slug>`), and commits a `PLAN.md` file.

```bash
deliberate plan "Add OAuth support"
# Branch created: deliberate/add-oauth-support
# Plan written to: PLAN.md
```

You can edit `PLAN.md` manually to correct or refine the plan before execution.

### `deliberate work`

Executes the plan found in the current branch's `PLAN.md`. It spins up agents in isolated worktrees to implement the changes.

```bash
# Must be on a deliberate branch
deliberate work
```

### `deliberate status`

Shows the current state of execution, including active agents, costs, and test results.

```bash
deliberate status
```

### `deliberate merge`

Triggers the Review phase (if not already done), displays a comparison of results, and allows you to interactive select the best solution to merge back into the parent branch.

```bash
deliberate merge
# > Reviewing candidates...
# > Winner: Gemini
# > Merge Gemini's changes to 'main'? [y/N]
```