# Profiles

Profiles let you trade cost vs quality without editing your config file.

## Built-in Profiles

| Profile | Planning | Review | Refinement | Use Case |
|---------|----------|--------|------------|----------|
| `cheap` | Minimal | Disabled | Disabled | Quick iterations, low cost |
| `balanced` | Enabled | Enabled | 1 iteration | Default, good tradeoff |
| `powerful` | Full debate | All reviewers | 3 iterations | Critical code, thorough |

## Using Profiles

```bash
# Use a specific profile
deliberate run "task" --profile cheap
deliberate run "task" --profile powerful

# Default is 'balanced'
deliberate run "task"
```

## What Profiles Change

Profiles are overlays that modify your base config. For example:

**cheap:**
```yaml
workflow:
  planning:
    debate:
      enabled: false
  review:
    enabled: false
  refinement:
    enabled: false
```

**powerful:**
```yaml
workflow:
  planning:
    debate:
      enabled: true
      rounds: 2
  review:
    agents: all  # Use every available reviewer
  refinement:
    enabled: true
    max_iterations: 3
```

## Agent Model Overrides

Profiles automatically override which model each agent uses. The built-in profiles select different model tiers:

| Profile | Claude | Gemini | Codex |
|---------|--------|--------|-------|
| `cheap` | claude-sonnet-4-5-20250514 | gemini-2.0-flash-exp | gpt-5.1-codex-mini |
| `balanced` | claude-sonnet-4-5-20250514 | gemini-2.5-pro | gpt-5.1-codex-mini |
| `powerful` | claude-opus-4-5-20251101 | gemini-3.0-pro | gpt-5.2 |

This means when you run `--profile powerful`, your agents automatically use the most capable models, even if your base config specifies cheaper defaults.

### Custom Agent Overrides

You can define your own agent overrides in custom profiles:

```yaml
profiles:
  research:
    description: "Deep research mode using Opus"
    workflow:
      planning:
        debate: { enabled: true, rounds: 3 }
    agent_overrides:
      claude:
        model: claude-opus-4-5-20251101
        config:
          max_tokens: 32000
```

Agent overrides only apply to agents that exist in your config. If your config defines `claude` and `custom-agent`, but the profile only has overrides for `claude`, then `custom-agent` keeps its original settings.

## Custom Profiles

Define your own in `.deliberate.yaml`:

```yaml
profiles:
  quick-review:
    description: "Fast review, no refinement"
    workflow:
      planning:
        enabled: false
      review:
        enabled: true
        agents: [gemini]  # Just one reviewer
      refinement:
        enabled: false

  thorough:
    description: "Maximum scrutiny"
    workflow:
      planning:
        debate:
          enabled: true
          rounds: 3
      review:
        scoring:
          criteria: [correctness, security, performance, maintainability]
      refinement:
        enabled: true
        max_iterations: 5
    agent_overrides:
      gemini:
        model: "gemini-3.0-pro"
```

Use with:

```bash
deliberate run "task" --profile quick-review
deliberate run "task" --profile thorough
```

## Default Profile

Set a default in your config:

```yaml
default_profile: balanced

profiles:
  balanced:
    # ...
```

Override at runtime with `--profile`.

## CI Recommendations

For CI pipelines:

```bash
# Fast feedback on PRs
deliberate run "@task.txt" --profile cheap --ci

# Merge to main
deliberate run "@task.txt" --profile balanced --ci

# Release branches
deliberate run "@task.txt" --profile powerful --ci
```