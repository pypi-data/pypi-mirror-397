# GitHub Bot Integration

Deliberate can be triggered directly from GitHub PR comments, allowing your team to run multi-LLM code reviews, optimizations, and implementations with human approval gates.

## Quick Start

1. Copy `.github/workflows/deliberate-bot.yml` to your repository
2. Add API keys as GitHub Secrets (`ANTHROPIC_API_KEY`, etc.)
3. Comment `/deliberate review` on any PR

## Commands

| Command | Description |
|---------|-------------|
| `/deliberate review` | Comprehensive code review |
| `/deliberate optimize` | Performance and readability improvements |
| `/deliberate test` | Generate tests for changes |
| `/deliberate fix` | Fix issues from review comments |
| `/deliberate docs` | Add documentation |
| `/deliberate implement "task"` | Custom implementation task |

### Options

- `--profile cheap|balanced|max_quality` - Select optimization profile

### Examples

```
/deliberate review
/deliberate optimize --profile max_quality
/deliberate implement "add caching to the API layer"
```

## How It Works

```
User: /deliberate review
         |
         v
    +---------+
    | Parse   |  Bot parses command
    | Command |  and validates user
    +---------+
         |
         v
    +---------+
    | Plan    |  deliberate --plan-only
    | Phase   |  generates approach
    +---------+
         |
         v
    +---------+
    | Post    |  Bot posts plan
    | Plan    |  as PR comment
    +---------+
         |
         v
    +---------+
    | Wait    |  User reacts with
    | Approval|  thumbs up/down
    +---------+
         |
    +----+----+
    |         |
   YES       NO
    |         |
    v         v
+---------+ +----------+
| Execute | | Post     |
| Task    | | Rejected |
+---------+ +----------+
    |
    v
+---------+
| Commit  |  Push changes
| Changes |  to PR branch
+---------+
    |
    v
+---------+
| Post    |  Summary comment
| Summary |  with results
+---------+
```

## Setup

### 1. Add Workflow File

Copy `.github/workflows/deliberate-bot.yml` to your repository. The workflow uses `uv run --with deliberate` to install and run deliberate from PyPI.

### 2. Configure Secrets

Add API keys for your LLM providers in repository settings (Settings > Secrets and variables > Actions):

| Secret | Required | Description |
|--------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes* | Claude API key |
| `GEMINI_API_KEY` | No | Google Gemini key |
| `OPENAI_API_KEY` | No | OpenAI API key |

*At least one LLM API key is required.

### 3. Repository Configuration (Optional)

Create `.deliberate.yaml` in your repository root to customize agent behavior and how changes are applied back to your repository. By default, changes are merged, but you can configure the `apply_strategy` to `squash` or `copy` (which will simply overwrite files).

```yaml
agents:
  claude:
    type: cli
    command: ['claude', '--print', '-p']
    capabilities: ['planner', 'executor', 'reviewer']

workflow:
  planning:
    enabled: true
    agents: [claude]
  execution:
    enabled: true
    agents: [claude]
    worktree:
      apply_strategy: merge # Options: merge, squash, copy
  review:
    enabled: true
    agents: [claude]
```

When `deliberate` runs in CI mode, the bot will push the changes from the winning worktree back to the PR branch according to the configured `apply_strategy`.
## Security

### Authorization

Only repository collaborators can trigger the bot. Non-collaborators who comment `/deliberate` will receive an error message.

### Approval Flow

- Plan execution requires explicit approval via reaction
- Only collaborators can approve/reject plans
- 10-minute timeout before auto-cancellation

### Cost Controls

Configure budget limits in `.deliberate.yaml`:

```yaml
limits:
  budget:
    max_total_tokens: 100000
    max_cost_usd: 5.0
```

## Troubleshooting

### Bot doesn't respond

1. Check that the workflow file exists at `.github/workflows/deliberate-bot.yml`
2. Verify the comment is on a PR (not an issue)
3. Check that the user is a repository collaborator
4. View workflow logs in the Actions tab

### Planning fails

1. Verify API keys are set in repository secrets
2. Check the planning output in workflow logs
3. Ensure the LLM CLI tools (claude, gemini) are available

### Execution fails

1. Check for permission issues in the worktree
2. Verify the plan was approved within timeout
3. Review execution logs for specific errors

### Changes not committed

The bot only commits if:
1. Execution was successful
2. There are actual code changes (not just artifacts)
3. The plan was approved (not rejected/timed out)

## CLI Flags for GitHub Integration

The GitHub bot uses these CLI flags that were added for this integration:

```bash
# Run planning only (for bot to post plan and wait for approval)
uv run deliberate run @task.txt --plan-only --artifacts ./plan

# Execute with pre-loaded plan (after approval)
uv run deliberate run @task.txt --from-plan ./plan/deliberate-run.json --ci
```

### `--plan-only`

Runs only the planning phase, skips execution and review. Outputs the plan as JSON. Useful for the approval workflow where you want to show the user the plan before executing.

### `--from-plan <path>`

Loads an existing plan from a JSON file (the artifact from a `--plan-only` run) and skips the planning phase. Proceeds directly to execution with the loaded plan.

## Advanced Usage

### Custom Actions

Add custom predefined actions by extending `src/deliberate/github/actions.py`:

```python
PREDEFINED_ACTIONS["security"] = PredefinedAction(
    name="security",
    description="Security audit of changes",
    task_template="""Perform a security audit of this PR.

    Check for:
    1. SQL injection vulnerabilities
    2. XSS vulnerabilities
    3. Authentication/authorization issues
    4. Sensitive data exposure
    """,
    default_profile="max_quality",
)
```

### Self-Hosted Runners

For long-running tasks or private models, use self-hosted runners:

```yaml
jobs:
  deliberate:
    runs-on: self-hosted
    timeout-minutes: 120  # Increase timeout
```

### Using a Specific Version

Pin to a specific version of deliberate:

```yaml
- name: Create task file
  run: |
    uv run --with 'deliberate==0.1.0' python3 << 'PYEOF'
    ...
```

### Multiple Approvers

Modify the approval step to require multiple approvers by editing the workflow.
