# CI Mode

Run deliberate in CI pipelines with `--ci` for non-interactive execution and structured output.

## Basic Usage

```bash
deliberate run "@task.txt" --ci
```

This:

- Runs non-interactively (no prompts)
- Writes artifacts to `./artifacts/`
- Sets exit code based on result
- Applies confidence gating

## Artifacts

CI mode writes two files:

```
artifacts/
├── deliberate-run.json     # Machine-readable results
└── deliberate-report.md    # Human-readable summary
```

Custom output directory:

```bash
deliberate run "@task.txt" --ci --artifacts ./output
```

### JSON Artifact

```json
{
  "run_id": "abc123",
  "task": "Add input validation",
  "profile": "balanced",
  "success": true,
  "confidence": 0.85,
  "selected_plan": { ... },
  "execution_result": { ... },
  "review_result": { ... },
  "timing": {
    "total_seconds": 120,
    "planning_seconds": 15,
    "execution_seconds": 80,
    "review_seconds": 25
  },
  "cost": {
    "total_tokens": 45000,
    "estimated_usd": 0.45
  }
}
```

### Markdown Report

```markdown
# Deliberate Run Report

**Task**: Add input validation
**Profile**: balanced
**Result**: Success (confidence: 85%)

## Plan
...

## Changes
...

## Review Summary
...
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success, confidence met threshold |
| 1 | Failure or low confidence |
| 2 | Budget exceeded |
| 3 | Timeout |

## GitHub Actions Example

```yaml
name: Deliberate Review

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install deliberate
        run: pip install deliberate

      - name: Run review
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          echo "Review the changes in this PR for correctness and security" > task.txt
          deliberate run "@task.txt" --profile balanced --ci

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: deliberate-report
          path: artifacts/
```

## Plan-Only Mode

For approval workflows, run planning separately:

```bash
# Step 1: Generate plan
deliberate run "@task.txt" --plan-only --artifacts ./plan

# Step 2: (Human approves plan)

# Step 3: Execute approved plan
deliberate run "@task.txt" --from-plan ./plan/deliberate-run.json --ci
```

## Budget Controls

Set limits to prevent runaway costs:

```yaml
limits:
  budget:
    max_total_tokens: 100000
    max_cost_usd: 5.0
  time:
    hard_timeout_minutes: 30
```

Or via CLI:

```bash
deliberate run "@task.txt" --ci --max-cost 5.0 --timeout 30
```

## Confidence Gating

CI mode fails if confidence is below threshold:

```yaml
ci:
  min_confidence: 0.7
  fail_on: [low_confidence, test_failure, budget_exceeded]
```

Confidence is calculated from review scores and agreement between reviewers.
