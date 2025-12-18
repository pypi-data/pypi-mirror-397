# Deliberate

Multi-LLM ensemble orchestrator for code generation and review.

## What is Deliberate?

Deliberate orchestrates multiple LLM agents to collaboratively plan, execute, and review coding tasks. Instead of relying on a single model, it uses ensemble methods—independent generation, peer voting, and synthesis—to produce higher-quality outputs.

## Key Features

- **Multi-agent planning** — Multiple LLMs propose plans, debate, and vote on the best approach
- **Isolated execution** — Each agent works in its own git worktree
- **Dev Container support** — Run validation in isolated Docker containers for security
- **TDD inner loop** — Cheap test→fail→fix cycles before expensive LLM review
- **Peer review** — Multiple agents score and vote on results
- **Profiles** — Trade cost vs quality with `cheap`, `balanced`, `powerful`
- **CI integration** — Non-interactive mode with JSON/Markdown artifacts
- **Agent tracking** — Learn which agents perform best over time
- **Interactive review** — Inspect diffs, open the worktree in your editor, and pick the winner
- **Live dashboard** — Verbose mode surfaces per-phase progress and agent status updates

## How It Works

```
Task → Planning → Execution → Validation → Review → Refinement → Result
         ↓           ↓            ↓           ↓           ↓
      Multiple    Isolated     Lint &     Peer       Iterate
       agents     worktrees    tests      voting     on feedback
```

1. **Planning**: Multiple agents propose plans, optionally debate, winner selected
2. **Execution**: Agent(s) implement the plan in isolated git worktrees
3. **Validation**: Run linters and tests, fix failures before review
4. **Review**: Multiple agents score the result, votes aggregated
5. **Refinement**: If confidence is low, iterate with reviewer feedback

## Next Steps

- [Quickstart](quickstart.md) — Get running in 5 minutes
- [Workflow Phases](guides/workflow.md) — Understand each phase in detail
- [Configuring Agents](guides/agents.md) — Set up Claude, Gemini, Codex, etc.
- [Dev Container Support](guides/devcontainer.md) — Isolated test execution with Docker
