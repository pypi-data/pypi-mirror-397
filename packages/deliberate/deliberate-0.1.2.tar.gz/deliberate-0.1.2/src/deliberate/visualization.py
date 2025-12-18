"""Visualization utilities for orchestration and workflow."""

from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

from deliberate.config import DeliberateConfig


def render_orchestration_plan(
    config: DeliberateConfig,
    task: str,
    repo_root: Path,
    console: Console | None = None,
):
    """Render a visual representation of the orchestration plan.

    Args:
        config: Deliberate configuration
        task: Task description
        repo_root: Repository root path
        console: Rich console instance
    """
    console = console or Console()

    # Header
    console.print()
    console.print(
        Panel.fit(
            "[bold cyan]Orchestration Plan[/bold cyan]\n[dim]--dry-run mode[/dim]",
            border_style="cyan",
        )
    )

    # Task info
    console.print(f"\n[bold]Task:[/bold] {task[:200]}")
    if len(task) > 200:
        console.print(f"[dim]... ({len(task)} total characters)[/dim]")

    console.print(f"[bold]Repository:[/bold] {repo_root}")
    console.print()

    # Workflow tree
    _render_workflow_tree(config, console)

    # Agent details
    _render_agent_table(config, console)

    # Budget and limits
    _render_limits(config, console)

    # Worktree config
    if config.workflow.execution.worktree.enabled:
        _render_worktree_config(config, repo_root, console)


def _render_workflow_tree(config: DeliberateConfig, console: Console):
    """Render workflow as a tree structure."""
    tree = Tree("[bold]Workflow Phases[/bold]", guide_style="dim")

    # Planning phase
    planning = config.workflow.planning
    if planning.enabled:
        plan_node = tree.add(f"[cyan]1. Planning[/cyan] [dim]({len(planning.agents)} agent(s))[/dim]")
        for agent in planning.agents:
            agent_cfg = config.agents.get(agent)
            if agent_cfg:
                plan_node.add(f"→ {agent} [dim]({agent_cfg.type})[/dim]")

        if planning.debate.enabled:
            plan_node.add("[yellow]⚡ Debate enabled[/yellow]")

        plan_node.add(f"[dim]Selection: {planning.selection.method}[/dim]")
    else:
        tree.add("[dim]1. Planning (disabled)[/dim]")

    # Execution phase
    execution = config.workflow.execution
    if execution.enabled:
        exec_node = tree.add(f"[green]2. Execution[/green] [dim]({len(execution.agents)} agent(s))[/dim]")
        for agent in execution.agents:
            agent_cfg = config.agents.get(agent)
            if agent_cfg:
                exec_node.add(f"→ {agent} [dim]({agent_cfg.type})[/dim]")

        if execution.worktree.enabled:
            exec_node.add("[yellow]⚡ Worktrees enabled[/yellow]")
        if execution.parallelism.enabled:
            exec_node.add(f"[yellow]⚡ Parallel execution (max {execution.parallelism.max_parallel})[/yellow]")
    else:
        tree.add("[dim]2. Execution (disabled)[/dim]")

    # Review phase
    review = config.workflow.review
    if review.enabled:
        review_node = tree.add(f"[magenta]3. Review[/magenta] [dim]({len(review.agents)} agent(s))[/dim]")
        for agent in review.agents:
            agent_cfg = config.agents.get(agent)
            if agent_cfg:
                review_node.add(f"→ {agent} [dim]({agent_cfg.type})[/dim]")

        review_node.add(f"[dim]Aggregation: {review.aggregation.method}[/dim]")
        review_node.add(f"[dim]Criteria: {', '.join(review.scoring.criteria)}[/dim]")
    else:
        tree.add("[dim]3. Review (disabled)[/dim]")

    # Refinement phase
    refinement = config.workflow.refinement
    if refinement.enabled:
        ref_node = tree.add("[yellow]4. Refinement[/yellow] [dim](iterative improvement)[/dim]")
        ref_node.add(f"[dim]Max iterations: {refinement.max_iterations}[/dim]")
        ref_node.add(f"[dim]Improvement threshold: {refinement.min_improvement_threshold:.2f}[/dim]")
    else:
        tree.add("[dim]4. Refinement (disabled)[/dim]")

    console.print(tree)
    console.print()


def _render_agent_table(config: DeliberateConfig, console: Console):
    """Render agent configuration table."""
    table = Table(title="Agent Configuration", show_header=True, header_style="bold magenta")
    table.add_column("Agent", style="cyan")
    table.add_column("Type", style="dim")
    table.add_column("Capabilities")
    table.add_column("Cost Weight", justify="right")
    table.add_column("Max Tokens", justify="right")

    # Get all agents used in workflow
    all_agents = set()
    if config.workflow.planning.enabled:
        all_agents.update(config.workflow.planning.agents)
    if config.workflow.execution.enabled:
        all_agents.update(config.workflow.execution.agents)
    if config.workflow.review.enabled:
        all_agents.update(config.workflow.review.agents)

    for agent_name in sorted(all_agents):
        agent = config.agents.get(agent_name)
        if agent:
            capabilities = ", ".join(agent.capabilities) if agent.capabilities else "-"
            cost_weight = f"{agent.cost.weight:.1f}" if agent.cost and agent.cost.weight else "-"
            max_tokens = f"{agent.config.max_tokens:,}" if agent.config and agent.config.max_tokens else "-"

            table.add_row(
                agent_name,
                agent.type,
                capabilities,
                cost_weight,
                max_tokens,
            )

    console.print(table)
    console.print()


def _render_limits(config: DeliberateConfig, console: Console):
    """Render budget and time limits."""
    limits_table = Table(title="Limits & Budget", show_header=True, header_style="bold yellow")
    limits_table.add_column("Limit", style="cyan")
    limits_table.add_column("Value", justify="right")

    budget = config.limits.budget
    limits_table.add_row("Max Total Tokens", f"{budget.max_total_tokens:,}")
    limits_table.add_row("Max Cost (USD)", f"${budget.max_cost_usd:.2f}")
    limits_table.add_row("Max Requests/Agent", str(budget.max_requests_per_agent))

    time_limits = config.limits.time
    limits_table.add_row("Hard Timeout", f"{time_limits.hard_timeout_minutes} minutes")

    console.print(limits_table)
    console.print()


def _render_worktree_config(config: DeliberateConfig, repo_root: Path, console: Console):
    """Render worktree configuration."""
    worktree = config.workflow.execution.worktree

    console.print("[bold]Worktree Configuration:[/bold]")
    console.print(f"  Root: [cyan]{repo_root / worktree.root}[/cyan]")
    console.print(f"  Cleanup: {'✓ enabled' if worktree.cleanup else '✗ disabled'}")
    console.print()


def render_workflow_flowchart(
    config: DeliberateConfig,
    console: Console | None = None,
):
    """Render ASCII flowchart of the workflow.

    Args:
        config: Deliberate configuration
        console: Rich console instance
    """
    console = console or Console()

    planning = config.workflow.planning
    execution = config.workflow.execution
    review = config.workflow.review
    refinement = config.workflow.refinement

    console.print()
    console.print("[bold]Workflow Flowchart:[/bold]")
    console.print()

    # Build flowchart
    lines = []

    lines.append("    ┌─────────────┐")
    lines.append("    │    START    │")
    lines.append("    └──────┬──────┘")
    lines.append("           │")

    # Planning
    if planning.enabled:
        lines.append("           ▼")
        lines.append("    ┌──────────────────────┐")
        lines.append("    │  [cyan]PLANNING[/cyan]           │")
        lines.append(f"    │  {len(planning.agents)} agent(s)          │")
        if planning.debate.enabled:
            lines.append("    │  + debate            │")
        lines.append("    └──────────┬───────────┘")
        lines.append("               │")
    else:
        lines.append("           │ (planning skipped)")
        lines.append("           │")

    # Execution
    if execution.enabled:
        lines.append("           ▼")
        lines.append("    ┌──────────────────────┐")
        lines.append("    │  [green]EXECUTION[/green]          │")
        lines.append(f"    │  {len(execution.agents)} agent(s)          │")
        if execution.parallelism.enabled:
            lines.append("    │  + parallel          │")
        if execution.worktree.enabled:
            lines.append("    │  + worktrees         │")
        lines.append("    └──────────┬───────────┘")
        lines.append("               │")
    else:
        lines.append("           │ (execution skipped)")
        lines.append("           │")

    # Review
    if review.enabled:
        lines.append("           ▼")
        lines.append("    ┌──────────────────────┐")
        lines.append("    │  [magenta]REVIEW[/magenta]             │")
        lines.append(f"    │  {len(review.agents)} agent(s)          │")
        lines.append(f"    │  {review.aggregation.method:16s}│")
        lines.append("    └──────────┬───────────┘")
        lines.append("               │")
    else:
        lines.append("           │ (review skipped)")
        lines.append("           │")

    # Refinement
    if refinement.enabled:
        lines.append("           ▼")
        lines.append("    ┌──────────────────────┐")
        lines.append("    │  [yellow]REFINEMENT[/yellow]         │")
        lines.append(f"    │  max {refinement.max_iterations} iterations   │")
        lines.append("    └──────────┬───────────┘")
        lines.append("               │")
        lines.append("           ┌───┴────┐")
        lines.append("           │ improve│")
        lines.append("           │  loop  │")
        lines.append("           └───┬────┘")
        lines.append("               │")

    lines.append("           ▼")
    lines.append("    ┌──────────────┐")
    lines.append("    │   [bold green]COMPLETE[/bold green]   │")
    lines.append("    └──────────────┘")

    for line in lines:
        console.print(line)

    console.print()


def render_execution_summary(
    selected_agents: list[str],
    console: Console | None = None,
):
    """Render summary of what will be executed.

    Args:
        selected_agents: List of agent names that will execute
        console: Rich console instance
    """
    console = console or Console()

    console.print()
    console.print("[bold yellow]⚠ DRY RUN - No actual execution will occur[/bold yellow]")
    console.print()
    console.print(f"[bold]Agents that would execute:[/bold] {', '.join(selected_agents)}")
    console.print()
    console.print("[dim]To run for real, remove the --dry-run flag[/dim]")
    console.print()
