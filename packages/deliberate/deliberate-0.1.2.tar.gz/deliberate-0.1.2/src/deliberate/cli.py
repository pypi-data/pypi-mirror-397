"""CLI for deliberate."""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

from deliberate.agent_detection import (
    _generate_fallback_config,
    configure_mcp_servers_interactive,
    detect_agents,
    generate_config,
)
from deliberate.artifacts import write_markdown_report, write_run_artifact
from deliberate.config import DeliberateConfig
from deliberate.git.branch_workflow import PLAN_FILENAME, BranchWorkflowManager
from deliberate.git.worktree import Worktree, WorktreeManager, get_actual_repo_root
from deliberate.github.handler import GitHubHandler
from deliberate.orchestrator import Orchestrator
from deliberate.review_tui import show_diff_with_pager
from deliberate.tracing import init_tracing, shutdown_tracing
from deliberate.tracking import get_tracker
from deliberate.types import ExecutionResult, JuryResult
from deliberate.verbose_logger import init_verbose_logger
from deliberate.visualization import (
    render_execution_summary,
    render_orchestration_plan,
    render_workflow_flowchart,
)

app = typer.Typer(
    name="deliberate",
    help=(
        "Multi-LLM ensemble orchestrator for code generation and review.\n\n"
        "Default flow: `run` is a macro that creates a deliberate/<slug> branch, "
        "commits PLAN.md, executes, applies the winner onto that branch, and attempts "
        "to merge back to the parent with conflict pre-checks.\n\n"
        "Quick examples:\n"
        '  deliberate run "Add feature X"   # plan → work → merge on deliberate/<slug>\n'
        "  deliberate status                 # show branch/plan/worktrees\n"
        "  deliberate merge --auto           # finish from a deliberate branch\n"
    ),
)
console = Console()


def _load_config(config_path: Optional[Path] = None) -> Optional[DeliberateConfig]:
    """Load configuration, returning None if not found."""
    try:
        return DeliberateConfig.load_or_default(config_path)
    except FileNotFoundError:
        return None


def _load_task_content(task: str) -> str:
    """Load task content from file if prefixed with @, otherwise return as-is.

    Args:
        task: Task string or @path to load from file (path is relative to CWD)

    Returns:
        Task content as string (trailing whitespace trimmed)

    Raises:
        typer.Exit: If file doesn't exist or can't be read
    """
    if task.startswith("@"):
        # Load from file
        task_file = Path(task[1:])
        if not task_file.exists():
            console.print(f"[red]Error:[/red] Task file not found: {task_file}")
            raise typer.Exit(1)
        try:
            return task_file.read_text().strip()
        except Exception as e:
            console.print(f"[red]Error:[/red] Failed to read task file: {e}")
            raise typer.Exit(1)
    return task


@app.command()
def run(
    task: str = typer.Argument(
        ...,
        help="Task text, or @path to read task from a file relative to the current directory",
    ),
    config: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help=(
            "Config file path; if omitted searches ./.deliberate.yaml, ./deliberate.yaml, "
            "then ~/.deliberate/config.yaml"
        ),
    ),
    agents: Optional[str] = typer.Option(
        None,
        "--agents",
        "-a",
        help=("Comma-separated agents to use (overrides planning/execution/review agents, e.g., 'claude,fake')"),
    ),
    skip_planning: bool = typer.Option(
        False,
        "--skip-planning",
        help="Skip the planning phase",
    ),
    skip_review: bool = typer.Option(
        False,
        "--skip-review",
        help="Skip the review phase",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Run without making actual changes",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output results as JSON",
    ),
    profile: Optional[str] = typer.Option(
        None,
        "--profile",
        "-p",
        help="Profile: cheap, balanced (default), powerful",
    ),
    ci: bool = typer.Option(
        False,
        "--ci",
        help="CI mode: non-interactive, strict exit codes, and artifact output",
    ),
    artifact_dir: Path = typer.Option(
        Path("artifacts"),
        "--artifacts",
        help="Directory to write run artifacts",
    ),
    max_iterations: Optional[int] = typer.Option(
        None,
        "--max-iterations",
        help="Override max refinement iterations",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show verbose output",
    ),
    verbose_view: str = typer.Option(
        "both",
        "--verbose-view",
        help="Verbose dashboard view: status, stdout, or both (default)",
        case_sensitive=False,
    ),
    interactive: bool = typer.Option(
        False,
        "--interactive",
        "-i",
        help="Enable interactive review TUI to override jury votes before committing",
    ),
    pager: bool = typer.Option(
        True,
        "--pager/--no-pager",
        help="Use pager (bat/less) for large diffs (default: enabled)",
    ),
    enable_tracing: bool = typer.Option(
        False,
        "--trace",
        help="Enable OpenTelemetry tracing (also on when any OTLP/trace flag is set)",
    ),
    otlp_endpoint: Optional[str] = typer.Option(
        None,
        "--otlp-endpoint",
        help="OTLP collector endpoint (e.g., http://localhost:4317); enables tracing if set",
    ),
    trace_console: bool = typer.Option(
        False,
        "--trace-console",
        help="Export traces to console/stdout (for debugging; enables tracing)",
    ),
    otlp_protocol: Optional[str] = typer.Option(
        None,
        "--otlp-protocol",
        help=(
            "OTLP protocol to use: 'grpc' (default) or 'http'/'http/protobuf'. "
            "If not specified, tries gRPC first, falls back to HTTP."
        ),
    ),
    plan_only: bool = typer.Option(
        False,
        "--plan-only",
        help="Run planning phase only and output plan as JSON (for GitHub Bot integration)",
    ),
    from_plan: Optional[Path] = typer.Option(
        None,
        "--from-plan",
        help="Skip planning and load plan from a JSON file (for GitHub Bot integration)",
    ),
    allow_dirty: bool = typer.Option(
        False,
        "--allow-dirty",
        help="Allow running with uncommitted changes in the repository",
    ),
    reuse_branch: bool = typer.Option(
        False,
        "--reuse-branch",
        help="If branch already exists, check it out and overwrite PLAN.md",
    ),
    evolve: bool = typer.Option(
        False,
        "--evolve",
        "-e",
        help="Enable evolution phase for iterative improvement (AlphaEvolve-inspired)",
    ),
    evolve_iterations: Optional[int] = typer.Option(
        None,
        "--evolve-iterations",
        help="Max evolution iterations (default: 10)",
    ),
):
    """Run a task (macro: plan → work → merge on a deliberate/<slug> branch)."""
    # Check for dirty repository early
    # Use a temporary manager just for the check
    mgr = WorktreeManager(Path.cwd())
    if mgr.is_repo_dirty() and not allow_dirty:
        console.print("[red]Error:[/red] Repository has uncommitted changes.")
        console.print("Deliberate requires a clean working directory to ensure safety.")
        console.print("Please commit or stash your changes, or use [bold]--allow-dirty[/bold] to override.")
        raise typer.Exit(1)

    # Load task content from file if needed
    task_content = _load_task_content(task)

    # Initialize tracing if requested
    # Enable console export automatically when verbose mode is enabled
    should_trace = enable_tracing or otlp_endpoint or trace_console or verbose
    console_export_enabled = trace_console or verbose

    if should_trace:
        try:
            init_tracing(
                service_name="deliberate",
                otlp_endpoint=otlp_endpoint,
                otlp_protocol=otlp_protocol,
                console_export=console_export_enabled,
            )
            if verbose and not trace_console:
                console.print("[dim]OpenTelemetry tracing enabled (console export)[/dim]\n")
        except ImportError:
            if not verbose:
                # Only show warning if explicitly requested (not just verbose mode)
                console.print(
                    "[yellow]Warning:[/yellow] Tracing requested but opentelemetry not installed. "
                    "Install with: pip install deliberate[tracing]"
                )

    try:
        cfg = DeliberateConfig.load_or_default(config)
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    # Apply profile (default or specified)
    effective_profile = profile or cfg.default_profile
    if effective_profile:
        try:
            cfg = cfg.apply_profile(effective_profile)
        except ValueError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    # Override config with CLI options
    if agents:
        agent_list = [a.strip() for a in agents.split(",")]
        cfg.workflow.planning.agents = agent_list
        cfg.workflow.execution.agents = agent_list
        cfg.workflow.review.agents = agent_list

    if skip_planning:
        cfg.workflow.planning.enabled = False

    if skip_review:
        cfg.workflow.review.enabled = False

    if max_iterations is not None:
        cfg.workflow.refinement.max_iterations = max_iterations

    # Enable evolution phase if requested
    if evolve:
        cfg.workflow.evolution.enabled = True
        # Use all configured agents for evolution if none specified
        if not cfg.workflow.evolution.agents:
            all_agents = list(cfg.agents.keys())
            cfg.workflow.evolution.agents = all_agents

    if evolve_iterations is not None:
        cfg.workflow.evolution.max_iterations = evolve_iterations

    # Handle --plan-only: only run planning, skip everything else
    if plan_only:
        cfg.workflow.execution.enabled = False
        cfg.workflow.review.enabled = False
        cfg.workflow.refinement.enabled = False
        json_output = True  # Force JSON output for plan-only mode

    # Handle --from-plan: load existing plan, skip planning phase
    loaded_plan = None
    if from_plan:
        if not from_plan.exists():
            console.print(f"[red]Error:[/red] Plan file not found: {from_plan}")
            raise typer.Exit(1)
        try:
            plan_data = json.loads(from_plan.read_text())
            # Extract plan from the run artifact format
            if "data" in plan_data and "selected_plan" in plan_data["data"]:
                raw_plan = plan_data["data"]["selected_plan"]
            elif "selected_plan" in plan_data:
                raw_plan = plan_data["selected_plan"]
            else:
                console.print("[red]Error:[/red] Could not find 'selected_plan' in plan file")
                raise typer.Exit(1)

            # Ensure plan is in the dict format expected by orchestrator
            if isinstance(raw_plan, str):
                loaded_plan = {"content": raw_plan, "agent": "preloaded", "id": "plan-preloaded"}
            else:
                loaded_plan = raw_plan
            cfg.workflow.planning.enabled = False  # Skip planning since we have a plan
        except json.JSONDecodeError as e:
            console.print(f"[red]Error:[/red] Invalid JSON in plan file: {e}")
            raise typer.Exit(1)

    # CI mode overrides
    if ci:
        cfg.ci.enabled = True
        cfg.limits.safety.require_human_approval = False
        cfg.limits.safety.dry_run = False
        interactive = False

    if dry_run:
        cfg.limits.safety.dry_run = True
        # Show orchestration plan and exit
        render_orchestration_plan(cfg, task_content, Path.cwd(), console)
        render_workflow_flowchart(cfg, console)

        # Show which agents would execute
        all_agents = set()
        if cfg.workflow.planning.enabled:
            all_agents.update(cfg.workflow.planning.agents)
        if cfg.workflow.execution.enabled:
            all_agents.update(cfg.workflow.execution.agents)
        if cfg.workflow.review.enabled:
            all_agents.update(cfg.workflow.review.agents)

        render_execution_summary(sorted(all_agents), console)
        return

    verbose_view_normalized = verbose_view.lower()
    if verbose_view_normalized not in {"status", "stdout", "both"}:
        console.print("[red]Error:[/red] --verbose-view must be one of: status, stdout, both")
        raise typer.Exit(1)

    # Initialize verbose logger if requested
    if verbose:
        init_verbose_logger(
            console=console,
            enabled=True,
            show_stdout=verbose_view_normalized in {"stdout", "both"},
        )

    # Run the orchestrator (macro: plan -> work -> merge)
    orchestrator: Orchestrator | None = None
    keep_worktrees = not ci  # keep around for potential apply step outside CI
    branch_mgr: BranchWorkflowManager | None = None
    branch_workflow = None
    plan_result = None

    use_branch_flow = not plan_only and not from_plan

    try:
        if use_branch_flow:
            branch_mgr = BranchWorkflowManager(Path.cwd())
            try:
                branch_workflow, _worktree_path = branch_mgr.create_plan_branch(task_content)
                console.print(f"[green]Created deliberate branch:[/green] {branch_workflow.branch_name}")
            except ValueError as e:
                console.print(f"[red]Error creating branch:[/red] {e}")
                raise typer.Exit(1)

            # Plan-only run
            plan_cfg = cfg.model_copy(deep=True)
            plan_cfg.workflow.execution.enabled = False
            plan_cfg.workflow.review.enabled = False
            plan_cfg.workflow.refinement.enabled = False

            plan_orchestrator = Orchestrator(
                plan_cfg,
                Path.cwd(),
                interactive_review=interactive,
                console=console,
            )
            plan_result = asyncio.run(plan_orchestrator.run(task_content, keep_worktrees=False))

            if not plan_result.selected_plan:
                console.print("[red]Error:[/red] No plan was generated.")
                branch_mgr.abort()
                raise typer.Exit(1)

            branch_mgr.write_plan(plan_result.selected_plan.content, agent=plan_result.selected_plan.agent)
            console.print(f"[dim]Plan committed to {PLAN_FILENAME}[/dim]")

            # Prepare main cfg with planning skipped, using committed plan
            exec_cfg = cfg.model_copy(deep=True)
            exec_cfg.workflow.planning.enabled = False
            preloaded_plan = {
                "id": plan_result.selected_plan.id,
                "agent": plan_result.selected_plan.agent,
                "content": plan_result.selected_plan.content,
            }

            orchestrator = Orchestrator(
                exec_cfg,
                Path.cwd(),
                interactive_review=interactive,
                console=console,
                execution_base_ref=branch_workflow.branch_name if branch_workflow else None,
            )
            result = asyncio.run(
                orchestrator.run(
                    task_content,
                    preloaded_plan=preloaded_plan,
                    keep_worktrees=True,
                )
            )
            result.profile = effective_profile
        else:
            orchestrator = Orchestrator(
                cfg,
                Path.cwd(),
                interactive_review=interactive,
                console=console,
                execution_base_ref=branch_workflow.branch_name if branch_workflow else None,
            )
            result = asyncio.run(
                orchestrator.run(task_content, preloaded_plan=loaded_plan, keep_worktrees=keep_worktrees)
            )
            result.profile = effective_profile
    finally:
        # Shutdown tracing to flush spans
        if should_trace:
            try:
                shutdown_tracing()
            except ImportError:
                pass

    # Emit artifacts
    artifact_dir.mkdir(parents=True, exist_ok=True)
    write_run_artifact(result, artifact_dir, profile_name=effective_profile, config=cfg)
    if ci:
        write_markdown_report(result, artifact_dir, profile_name=effective_profile, config=cfg)

    # Output results
    if json_output:
        _output_json(result)
    else:
        _output_rich(result, verbose, use_pager=pager)

    # Optional apply step (merge winning worktree back to repo)
    if orchestrator and keep_worktrees and result.success and result.vote_result and result.vote_result.winner_id:
        winner = next(
            (er for er in result.execution_results if er.id == result.vote_result.winner_id),
            None,
        )

        if use_branch_flow and branch_mgr and branch_workflow and winner:
            parent_branch = branch_workflow.parent_branch or branch_mgr.get_parent_branch()
            try:
                target_branch = branch_workflow.branch_name
                applied_branch = orchestrator.apply_changes(
                    winner,
                    target_branch=target_branch,
                    base_ref=parent_branch,
                )
                console.print(f"[bold green]✓ Applied to {applied_branch}.[/bold green]")
                # Auto-merge back to parent
                try:
                    branch_mgr.merge_to_parent(
                        parent_branch=parent_branch,
                        squash=cfg.workflow.execution.worktree.apply_strategy == "squash",
                        delete_branch=True,
                    )
                    console.print(f"[bold green]✓ Merged into {parent_branch}.[/bold green]")
                except RuntimeError as merge_err:
                    console.print(f"[bold red]Merge blocked by conflicts:[/bold red] {merge_err}")
                    console.print(f"[yellow]Resolve conflicts on {applied_branch} and rerun.[/yellow]")
                    keep_worktrees = False
            except Exception as e:
                console.print(f"[bold red]Failed to apply changes: {e}[/bold red]")
                if winner and winner.worktree_path:
                    console.print(f"Worktree preserved at: {winner.worktree_path}")
                keep_worktrees = False
        else:
            should_apply = False
            if interactive and winner:
                should_apply = typer.confirm(f"\nApply changes from {winner.agent} ({winner.id}) to current workspace?")
            elif cfg.ci.mode == "auto_apply":
                should_apply = True
            elif winner:
                strategy = cfg.workflow.execution.worktree.apply_strategy
                should_apply = typer.confirm(f"Apply changes using '{strategy}' strategy?")

            if should_apply and winner and winner.worktree_path:
                try:
                    branch_name = orchestrator.apply_changes(winner)
                    strategy = cfg.workflow.execution.worktree.apply_strategy
                    console.print(f"[bold green]✓ Applied to {branch_name} ({strategy}).[/bold green]")
                    console.print("[dim]Switch to base branch and merge.[/dim]")
                except Exception as e:  # pragma: no cover - interactive safeguard
                    console.print(f"[bold red]Failed to apply changes: {e}[/bold red]")
                    console.print(f"Worktree preserved at: {winner.worktree_path}")
                    keep_worktrees = False
            elif not should_apply and winner and winner.worktree_path:
                console.print("[yellow]Skipped applying changes.[/yellow]")
            else:
                console.print("[yellow]Winning worktree not available; cannot apply changes.[/yellow]")

    # Cleanup worktrees if we deferred cleanup
    if orchestrator and keep_worktrees:
        orchestrator.cleanup_worktrees()

    # Exit with appropriate code
    if ci:
        if not result.success:
            raise typer.Exit(1)
        if result.vote_result and result.vote_result.confidence < 0.6:
            console.print("[red]CI Failure: Result confidence too low[/red]")
            raise typer.Exit(1)
    else:
        if not result.success:
            raise typer.Exit(1)


@app.command()
def github_handle(
    event_path: Path = typer.Option(
        ...,
        "--event-path",
        help="Path to the GitHub event JSON file",
    ),
):
    """Handle a GitHub event (triggered by the GitHub Action bot)."""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        console.print("[red]Error:[/red] GITHUB_TOKEN environment variable is not set.")
        raise typer.Exit(1)

    try:
        handler = GitHubHandler(str(event_path), token)
        asyncio.run(handler.handle())
    except Exception as e:
        console.print(f"[red]Error handling GitHub event:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def maintain(
    test_command: str = typer.Option(
        "pytest",
        "--test-command",
        help="Command to run tests (e.g., 'pytest tests/unit')",
    ),
    detect_runs: int = typer.Option(
        5,
        "--detect-runs",
        help="Number of times to run tests to detect flakes",
    ),
    verify_runs: int = typer.Option(
        100,
        "--verify-runs",
        help="Number of times to run tests to verify the fix",
    ),
    repo_owner: str = typer.Option(
        ...,
        "--repo-owner",
        help="GitHub repository owner",
    ),
    repo_name: str = typer.Option(
        ...,
        "--repo-name",
        help="GitHub repository name",
    ),
):
    """Run autonomous maintenance to fix flaky tests."""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        console.print("[red]Error:[/red] GITHUB_TOKEN environment variable is not set.")
        raise typer.Exit(1)

    from deliberate.maintenance import MaintenanceWorkflow

    workflow = MaintenanceWorkflow(test_command, token, repo_owner, repo_name)
    asyncio.run(workflow.run(detect_runs=detect_runs, verify_runs=verify_runs))


@app.command()
def init(
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing config file",
    ),
    user_config: bool = typer.Option(
        False,
        "--user",
        "-u",
        help="Create config in user config directory instead of current directory",
    ),
    quick: bool = typer.Option(
        False,
        "--quick",
        "-q",
        help="Fast mode: skip auth verification and MCP detection (just find binaries)",
    ),
    skip_auth: bool = typer.Option(
        False,
        "--skip-auth",
        help="Skip authentication verification (faster but may create non-working config)",
    ),
    include_unauthenticated: bool = typer.Option(
        False,
        "--include-unauth",
        help="Include agents that failed authentication check",
    ),
    skip_mcp: bool = typer.Option(
        False,
        "--skip-mcp",
        help="Skip MCP server configuration (non-interactive)",
    ),
    profile: str = typer.Option(
        "balanced",
        "--profile",
        "-p",
        help="Default profile to use (cheap, balanced, powerful)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show verbose output",
    ),
):
    """Detect installed LLM tools and create a working configuration.

    This command will:
    1. Scan for installed LLM CLI tools (claude, gemini, aider, etc.)
    2. Verify authentication status (costs ~$0.0001 per agent) - skip with --quick
    3. Detect configured MCP servers - skip with --quick
    4. Generate a working .deliberate.yaml config

    By default creates .deliberate.yaml in the current directory.
    Use --user to create config.yaml in the OS-specific user config directory.
    Use --quick for fast setup (just finds binaries, skips auth and MCP detection).

    Available profiles: cheap, balanced, powerful
    """
    # Quick mode implies skip_auth and skip_mcp
    if quick:
        skip_auth = True
        skip_mcp = True
        include_unauthenticated = True
    # Determine config path
    if user_config:
        config_dir = DeliberateConfig.get_user_config_dir()
        config_dir.mkdir(parents=True, exist_ok=True)
        config_path = config_dir / "config.yaml"
    else:
        config_path = Path(".deliberate.yaml")

    # Check if config exists
    if config_path.exists() and not force:
        if not typer.confirm(f"{config_path} already exists. Overwrite?"):
            raise typer.Abort()

    console.print("[bold]Detecting LLM tools...[/bold]\n")

    # Detect agents with live progress updates
    progress_lines = []

    def progress_callback(message: str):
        """Callback to display progress during detection."""
        progress_lines.append(message)

    async def run_detection_with_live(live_display):
        """Run detection with live progress updates."""

        def update_callback(msg: str):
            progress_callback(msg)
            # Show last 10 lines
            live_display.update(Text("\n".join(progress_lines[-10:])))

        return await detect_agents(
            skip_auth_check=skip_auth,
            skip_mcp_detection=skip_mcp,
            verbose=verbose,
            progress_callback=update_callback,
        )

    with Live(Text("Starting scan..."), console=console, refresh_per_second=4) as live:
        agents = asyncio.run(run_detection_with_live(live))

    console.print()  # Add spacing after progress

    if not agents:
        console.print("[yellow]No LLM CLI tools found in PATH.[/yellow]")
        console.print("\nSupported tools:")
        console.print("  - claude (https://claude.ai/download)")
        console.print("  - gemini")
        console.print("  - aider (pip install aider-chat)")
        console.print("\nCreating fallback config with fake agent...")

        # Generate fallback config
        config_content = _generate_fallback_config()
        config_path.write_text(config_content)
        console.print(f"\n[green]Created {config_path}[/green]")
        return

    # Display detection results
    table = Table(title="Detected Agents")
    table.add_column("Agent", style="cyan")
    table.add_column("Version", style="dim")
    table.add_column("Auth", justify="center")
    table.add_column("MCP Servers", justify="right")
    table.add_column("Capabilities")

    for agent in agents:
        auth_status = "✓" if agent.has_auth else "✗"
        auth_style = "green" if agent.has_auth else "red"

        if not agent.authenticated and agent.auth_error and verbose:
            auth_display = f"[{auth_style}]{auth_status}[/] [dim]{agent.auth_error[:30]}[/dim]"
        else:
            auth_display = f"[{auth_style}]{auth_status}[/]"

        mcp_count = str(len(agent.mcp_servers)) if agent.mcp_servers else "-"

        table.add_row(
            agent.name,
            agent.version or "?",
            auth_display,
            mcp_count,
            ", ".join(agent.capabilities),
        )

    console.print(table)
    console.print()

    # Filter agents based on authentication
    if include_unauthenticated:
        config_agents = agents
    else:
        config_agents = [a for a in agents if a.has_auth]

    if not config_agents:
        console.print("[yellow]No authenticated agents found.[/yellow]")
        console.print("Config will use 'fake' agent for testing only.")
        console.print("\nTo authenticate agents:")
        console.print("  claude: Run 'claude' and complete login")
        console.print("  gemini: Set GEMINI_API_KEY environment variable")
        console.print("  aider:  Run 'aider' and follow authentication prompts")

        # Generate fallback config
        config_content = _generate_fallback_config()
        config_path.write_text(config_content)
        console.print(f"\n[green]Created {config_path}[/green]")
        return

    # Configure MCP servers interactively
    mcp_config = None
    has_mcp_servers = any(agent.mcp_servers for agent in config_agents)

    if has_mcp_servers and not skip_mcp:
        console.print("\n[bold]MCP Server Configuration[/bold]")
        console.print("MCP servers provide additional capabilities to agents.")
        console.print("You can enable different servers for each phase (planning, execution, review).\n")

        if typer.confirm("Configure MCP servers?", default=True):
            mcp_config = configure_mcp_servers_interactive(config_agents)

    # Generate and write config
    config_content = generate_config(config_agents, mcp_config, default_profile=profile)
    config_path.write_text(config_content)

    console.print(f"\n[green]Created {config_path}[/green]")

    # Show summary
    console.print(f"\n[bold]Configured agents:[/bold] {', '.join(a.name for a in config_agents)}")

    if mcp_config:
        total_servers = sum(len(servers) for agent_cfg in mcp_config.values() for servers in agent_cfg.values())
        if total_servers > 0:
            console.print(f"[bold]MCP servers configured:[/bold] {total_servers}")

    console.print("\n[bold]Next steps:[/bold]")
    console.print("  deliberate run 'your task here'")


@app.command()
def validate(
    config: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to configuration file",
    ),
):
    """Validate a configuration file."""
    try:
        cfg = DeliberateConfig.load_or_default(config)
        console.print("[green]Configuration valid[/green]")

        # Show summary
        table = Table(title="Configuration Summary")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Agents", ", ".join(cfg.agents.keys()))
        table.add_row("Planning agents", ", ".join(cfg.workflow.planning.agents))
        table.add_row("Execution agents", ", ".join(cfg.workflow.execution.agents))
        table.add_row("Review agents", ", ".join(cfg.workflow.review.agents))
        table.add_row("Max tokens", f"{cfg.limits.budget.max_total_tokens:,}")
        table.add_row("Max cost", f"${cfg.limits.budget.max_cost_usd:.2f}")

        console.print(table)

    except FileNotFoundError as e:
        console.print("[red]Error:[/red] Configuration file not found")
        console.print(f"  {e}")
        raise typer.Exit(1)

    except Exception as e:
        console.print("[red]Error:[/red] Invalid configuration")
        console.print(f"  {e}")
        raise typer.Exit(1)


def _output_json(result: JuryResult):
    """Output result as JSON."""
    output = {
        "task": result.task,
        "success": result.success,
        "error": result.error,
        "summary": result.summary,
        "final_diff": result.final_diff,
        "total_duration_seconds": result.total_duration_seconds,
        "total_token_usage": result.total_token_usage,
        "total_cost_usd": result.total_cost_usd,
        "selected_plan": {
            "id": result.selected_plan.id,
            "agent": result.selected_plan.agent,
            "content": result.selected_plan.content,
        }
        if result.selected_plan
        else None,
        "execution_results": [
            {
                "id": e.id,
                "agent": e.agent,
                "success": e.success,
                "error": e.error,
                "has_diff": bool(e.diff),
            }
            for e in result.execution_results
        ],
        "vote_result": {
            "winner_id": result.vote_result.winner_id,
            "rankings": result.vote_result.rankings,
            "scores": result.vote_result.scores,
            "confidence": result.vote_result.confidence,
        }
        if result.vote_result
        else None,
    }
    print(json.dumps(output, indent=2, default=str))


@app.command()
def stats(
    role: Optional[str] = typer.Argument(
        None,
        help="Filter by role: 'planners', 'executors', 'reviewers', or omit for all",
    ),
    agent: Optional[str] = typer.Option(
        None,
        "--agent",
        "-a",
        help="Filter stats for a specific agent",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output stats as JSON",
    ),
    limit: int = typer.Option(
        10,
        "--limit",
        "-n",
        help="Maximum number of agents to show per role",
    ),
):
    """Show agent performance statistics.

    View which agents are best at planning, execution, and reviewing
    based on historical workflow data.

    Examples:
        deliberate stats              # Show all stats
        deliberate stats planners     # Show only planner stats
        deliberate stats executors    # Show only executor stats
        deliberate stats -a claude    # Show stats for 'claude' agent
        deliberate stats --json       # Output as JSON
    """
    tracker = get_tracker()
    workflow_count = tracker.get_workflow_count()

    if workflow_count == 0:
        console.print("[yellow]No workflow data recorded yet.[/yellow]")
        console.print("Run some workflows first to collect agent performance data.")
        return

    if json_output:
        output = tracker.export_stats()
        print(json.dumps(output, indent=2, default=str))
        return

    console.print(Panel(f"Agent Performance Stats ({workflow_count} workflows)", expand=False))

    # Determine which roles to show
    roles_to_show = []
    if role is None:
        roles_to_show = ["planners", "executors", "reviewers"]
    elif role.lower() in ["planner", "planners", "planning"]:
        roles_to_show = ["planners"]
    elif role.lower() in ["executor", "executors", "execution"]:
        roles_to_show = ["executors"]
    elif role.lower() in ["reviewer", "reviewers", "review"]:
        roles_to_show = ["reviewers"]
    else:
        console.print(f"[red]Unknown role: {role}[/red]")
        console.print("Valid roles: planners, executors, reviewers")
        raise typer.Exit(1)

    # Show planners
    if "planners" in roles_to_show:
        planner_stats = tracker.get_planner_stats(agent)[:limit]
        if planner_stats:
            table = Table(title="Best Planners")
            table.add_column("Agent", style="cyan")
            table.add_column("Runs", justify="right")
            table.add_column("Wins", justify="right")
            table.add_column("Win Rate", justify="right")
            table.add_column("Success Rate", justify="right")
            table.add_column("Avg Score", justify="right")
            table.add_column("Trend", justify="center")

            for s in planner_stats:
                trend = ""
                if s.recent_win_rate is not None:
                    diff = s.recent_win_rate - s.win_rate
                    if diff > 0.05:
                        trend = "[green]↑[/green]"
                    elif diff < -0.05:
                        trend = "[red]↓[/red]"
                    else:
                        trend = "→"

                table.add_row(
                    s.agent,
                    str(s.total_runs),
                    str(s.wins),
                    f"{s.win_rate:.1%}",
                    f"{s.success_rate:.1%}" if s.wins > 0 else "-",
                    f"{s.avg_score:.2f}" if s.avg_score else "-",
                    trend,
                )
            console.print(table)
        else:
            console.print("[dim]No planner data available[/dim]")
        console.print()

    # Show executors
    if "executors" in roles_to_show:
        executor_stats = tracker.get_executor_stats(agent)[:limit]
        if executor_stats:
            table = Table(title="Best Executors")
            table.add_column("Agent", style="cyan")
            table.add_column("Runs", justify="right")
            table.add_column("Wins", justify="right")
            table.add_column("Win Rate", justify="right")
            table.add_column("Success Rate", justify="right")
            table.add_column("Avg Score", justify="right")
            table.add_column("Avg Duration", justify="right")
            table.add_column("Trend", justify="center")

            for s in executor_stats:
                trend = ""
                if s.recent_win_rate is not None:
                    diff = s.recent_win_rate - s.win_rate
                    if diff > 0.05:
                        trend = "[green]↑[/green]"
                    elif diff < -0.05:
                        trend = "[red]↓[/red]"
                    else:
                        trend = "→"

                duration = f"{s.avg_duration_seconds:.1f}s" if s.avg_duration_seconds else "-"

                table.add_row(
                    s.agent,
                    str(s.total_runs),
                    str(s.wins),
                    f"{s.win_rate:.1%}",
                    f"{s.success_rate:.1%}",
                    f"{s.avg_score:.2f}" if s.avg_score else "-",
                    duration,
                    trend,
                )
            console.print(table)
        else:
            console.print("[dim]No executor data available[/dim]")
        console.print()

    # Show reviewers
    if "reviewers" in roles_to_show:
        reviewer_stats = tracker.get_reviewer_stats(agent)[:limit]
        if reviewer_stats:
            table = Table(title="Reviewer Accuracy")
            table.add_column("Agent", style="cyan")
            table.add_column("Workflows", justify="right")
            table.add_column("Reviews", justify="right")
            table.add_column("Accuracy", justify="right")
            table.add_column("Avg Score Given", justify="right")

            for s in reviewer_stats:
                accuracy = f"{s.review_accuracy:.1%}" if s.review_accuracy else "-"
                table.add_row(
                    s.agent,
                    str(s.total_runs),
                    str(s.wins),  # wins = total_reviews for reviewers
                    accuracy,
                    f"{s.avg_score:.2f}" if s.avg_score else "-",
                )
            console.print(table)
        else:
            console.print("[dim]No reviewer data available[/dim]")


@app.command("clear-stats")
def clear_stats(
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Skip confirmation prompt",
    ),
):
    """Clear all agent performance tracking data.

    This permanently deletes all recorded workflow history and agent statistics.
    """
    tracker = get_tracker()
    count = tracker.get_workflow_count()

    if count == 0:
        console.print("[yellow]No tracking data to clear.[/yellow]")
        return

    if not force:
        if not typer.confirm(f"This will permanently delete {count} workflow records and all agent stats. Continue?"):
            raise typer.Abort()

    deleted = tracker.clear_all()
    console.print(f"[green]Cleared {deleted} workflow records and all agent statistics.[/green]")


@app.command()
def history(
    limit: int = typer.Option(
        10,
        "--limit",
        "-n",
        help="Number of recent workflows to show",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output as JSON",
    ),
):
    """Show recent workflow history.

    Lists recent workflow runs with their outcomes, selected planners,
    and winning executors.
    """
    tracker = get_tracker()
    workflows = tracker.get_recent_workflows(limit)

    if not workflows:
        console.print("[yellow]No workflow history available.[/yellow]")
        return

    if json_output:
        output = [
            {
                "workflow_id": w.workflow_id,
                "task_preview": w.task_preview,
                "success": w.success,
                "selected_planner": w.selected_planner,
                "winning_executor": w.winning_executor,
                "final_score": w.final_score,
                "duration_seconds": w.total_duration_seconds,
                "tokens": w.total_tokens,
                "cost_usd": w.total_cost_usd,
                "timestamp": w.timestamp.isoformat(),
            }
            for w in workflows
        ]
        print(json.dumps(output, indent=2))
        return

    table = Table(title="Recent Workflows")
    table.add_column("ID", style="dim")
    table.add_column("Task", max_width=40)
    table.add_column("Status", justify="center")
    table.add_column("Planner", style="cyan")
    table.add_column("Winner", style="green")
    table.add_column("Score", justify="right")
    table.add_column("Cost", justify="right")
    table.add_column("Time")

    for w in workflows:
        status = "[green]OK[/green]" if w.success else "[red]FAIL[/red]"
        score = f"{w.final_score:.2f}" if w.final_score else "-"
        cost = f"${w.total_cost_usd:.4f}" if w.total_cost_usd else "-"
        time_str = w.timestamp.strftime("%m-%d %H:%M")

        table.add_row(
            w.workflow_id[:8],
            w.task_preview[:40] + "..." if len(w.task_preview) > 40 else w.task_preview,
            status,
            w.selected_planner or "-",
            w.winning_executor or "-",
            score,
            cost,
            time_str,
        )

    console.print(table)


def _output_rich(result: JuryResult, verbose: bool, use_pager: bool = True):
    """Output result with rich formatting."""
    # Status panel
    status = "[green]SUCCESS[/green]" if result.success else "[red]FAILED[/red]"
    console.print(Panel(f"Jury Result: {status}", expand=False))

    if result.error:
        console.print(f"\n[red]Error:[/red] {result.error}")

    # Summary
    if result.summary:
        console.print("\n[bold]Summary:[/bold]")
        console.print(result.summary)

    # Plan info
    if result.selected_plan and verbose:
        console.print("\n[bold]Selected Plan[/bold] (by {0}):".format(result.selected_plan.agent))
        console.print(result.selected_plan.content[:1000])

    # Planning agents and debate
    if result.selected_plan and result.all_plans:
        console.print("\n[bold]Planning Agents:[/bold]")
        for plan in result.all_plans:
            marker = "(selected)" if plan.id == result.selected_plan.id else ""
            console.print(f"  - {plan.agent} {marker}")
        if result.debate_messages:
            console.print("\n[bold]Debate Participants:[/bold]")
            debated_agents = {m.agent for m in result.debate_messages}
            console.print("  " + ", ".join(sorted(debated_agents)))

    # Execution results
    if result.execution_results:
        console.print("\n[bold]Execution Results:[/bold]")
        for er in result.execution_results:
            status_icon = "[green]+" if er.success else "[red]x"
            console.print(f"  {status_icon} {er.agent}: {er.id}[/]")
            if er.error:
                console.print(f"    Error: {er.error}")

    # Vote results
    if result.vote_result and verbose:
        console.print("\n[bold]Vote Results:[/bold]")
        console.print(f"  Winner: {result.vote_result.winner_id}")
        console.print(f"  Confidence: {result.vote_result.confidence:.2f}")

        console.print("\n  Scores:")
        for cid, score in sorted(result.vote_result.scores.items(), key=lambda x: -x[1]):
            bar = "+" * int(score * 20)
            console.print(f"    {cid}: {bar} {score:.2f}")

    # Final diff
    if result.final_diff:
        console.print("\n[bold]Changes:[/bold]")

        if use_pager:
            show_diff_with_pager(result.final_diff, console)
        else:
            # No pager - show truncated inline
            syntax = Syntax(
                result.final_diff[:3000],
                "diff",
                theme="monokai",
                line_numbers=True,
            )
            console.print(syntax)

            if len(result.final_diff) > 3000:
                console.print(f"\n[dim](diff truncated, {len(result.final_diff)} chars total)[/dim]")

    # Stats
    console.print(
        f"\n[dim]Duration: {result.total_duration_seconds:.1f}s | "
        f"Tokens: {result.total_token_usage:,} | "
        f"Cost: ${result.total_cost_usd:.4f}[/dim]"
    )


# =============================================================================
# Git-Native Workflow Commands (plan, work, status, merge)
# =============================================================================


@app.command()
def plan(
    task: str = typer.Argument(
        ...,
        help="Task description or @path to read from file",
    ),
    config: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Config file path",
    ),
    branch: Optional[str] = typer.Option(
        None,
        "--branch",
        "-b",
        help="Explicit branch name (auto-generated from task if not provided)",
    ),
    profile: Optional[str] = typer.Option(
        None,
        "--profile",
        "-p",
        help="Profile: cheap, balanced (default), powerful",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show verbose output",
    ),
    allow_dirty: bool = typer.Option(
        False,
        "--allow-dirty",
        help="Allow running with uncommitted changes in the repository",
    ),
    reuse_branch: bool = typer.Option(
        False,
        "--reuse-branch",
        help="If branch already exists, check it out and overwrite PLAN.md",
    ),
):
    """Generate an execution plan and commit it to a new branch.

    Creates a branch named 'deliberate/<task-slug>' containing PLAN.md.
    The plan is versioned in Git, allowing manual edits before execution.

    Example:
        deliberate plan "Add user authentication"
        # Edit PLAN.md if needed
        deliberate work
    """
    task_content = _load_task_content(task)

    # Check for dirty repo
    mgr = WorktreeManager(Path.cwd())
    if mgr.is_repo_dirty() and not (allow_dirty or reuse_branch):
        console.print("[red]Error:[/red] Repository has uncommitted changes.")
        console.print("Please commit or stash your changes before planning, or pass --allow-dirty.")
        console.print("`--reuse-branch` will proceed even if the branch is dirty.")
        raise typer.Exit(1)

    # Load config
    try:
        cfg = DeliberateConfig.load_or_default(config)
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    # Apply profile
    if profile:
        try:
            cfg = cfg.apply_profile(profile)
        except ValueError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    # Disable everything except planning
    cfg.workflow.execution.enabled = False
    cfg.workflow.review.enabled = False
    cfg.workflow.refinement.enabled = False

    # Initialize branch workflow manager
    # Use actual repo root to avoid nested worktrees when running from a worktree
    actual_repo_root = get_actual_repo_root(Path.cwd())
    branch_mgr = BranchWorkflowManager(actual_repo_root)
    worktree_root = actual_repo_root / ".deliberate" / "worktrees"

    console.print(f"[bold]Planning:[/bold] {task_content[:80]}...")

    # Initialize verbose logger - always enabled for plan to show basic progress
    init_verbose_logger(console=console, enabled=True, show_stdout=verbose)
    # Suppress noisy INFO logs from MCP server
    logging.getLogger("deliberate.mcp_orchestrator_server").setLevel(logging.WARNING)
    logging.getLogger("mcp.server").setLevel(logging.WARNING)
    logging.getLogger("uvicorn").setLevel(logging.WARNING)

    try:
        # Create the deliberate branch
        workflow, wt_path = branch_mgr.create_plan_branch(
            task_content,
            branch_name=branch,
            allow_existing=reuse_branch,
            worktree_root=worktree_root,
        )
        if reuse_branch and branch == workflow.branch_name:
            console.print(f"[yellow]Reusing existing branch:[/yellow] {workflow.branch_name}")
        else:
            console.print(f"[green]Created branch:[/green] {workflow.branch_name}")

        # Run planning phase in isolated worktree if available
        planning_cwd = wt_path if wt_path else Path.cwd()
        orchestrator = Orchestrator(cfg, planning_cwd, console=console)
        result = asyncio.run(orchestrator.run(task_content))

        if result.selected_plan:
            # Write plan to PLAN.md and commit in worktree (if available)
            plan_path = branch_mgr.write_plan(
                result.selected_plan.content,
                agent=result.selected_plan.agent,
                worktree_path=wt_path,
            )
            console.print(f"[green]Plan written to:[/green] {plan_path} (by {result.selected_plan.agent})")
            console.print()
            console.print("[bold]Next steps:[/bold]")
            br = workflow.branch_name
            if wt_path:
                console.print(f"  1. Review: [cyan]git show {br}:{PLAN_FILENAME}[/cyan]")
                console.print(f"     (worktree at {wt_path})")
                console.print(f"  2. Edit:   [cyan]$EDITOR {wt_path / PLAN_FILENAME}[/cyan]")
            else:
                console.print(f"  1. Review: [cyan]git show {br}:{PLAN_FILENAME}[/cyan]")
                console.print(f"  2. Edit:   [cyan]$EDITOR {PLAN_FILENAME}[/cyan]")
            console.print(f"  3. Execute:[cyan]deliberate work --branch {br}[/cyan]")
        else:
            console.print("[red]Error:[/red] No plan was generated.")
            # Abort and return to original branch
            parent = branch_mgr.abort()
            console.print(f"[yellow]Returned to branch:[/yellow] {parent}")
            raise typer.Exit(1)

    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error during planning:[/red] {e}")
        # Try to abort
        try:
            branch_mgr.abort()
        except Exception:
            pass
        raise typer.Exit(1)


@app.command()
def work(
    config: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Config file path",
    ),
    branch: Optional[str] = typer.Option(
        None,
        "--branch",
        "-b",
        help="Deliberate branch to use (auto-detects if omitted)",
    ),
    profile: Optional[str] = typer.Option(
        None,
        "--profile",
        "-p",
        help="Optimization profile",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show verbose output",
    ),
    skip_review: bool = typer.Option(
        False,
        "--skip-review",
        help="Skip the review phase after execution",
    ),
):
    """Execute the plan from the current deliberate branch using committed PLAN.md.

    Reads PLAN.md from the current deliberate branch and runs execution agents.
    Must be run on a 'deliberate/*' branch created by 'deliberate plan'.

    Example:
        deliberate work
        deliberate status  # Check progress
    """
    branch_mgr = BranchWorkflowManager(Path.cwd())

    # Determine target deliberate branch
    current_branch = branch_mgr.get_current_branch()
    target_branch = None
    deliberate_branches = branch_mgr.list_deliberate_branches()

    if branch:
        target_branch = branch if branch.startswith("deliberate/") else f"deliberate/{branch}"
    elif branch_mgr.is_deliberate_branch(current_branch):
        target_branch = current_branch
    elif len(deliberate_branches) == 1:
        target_branch = deliberate_branches[0]

    if not target_branch or target_branch not in deliberate_branches:
        console.print("[red]Error:[/red] No deliberate branch selected.")
        console.print(f"Current branch: {current_branch}")
        if deliberate_branches:
            console.print("\nAvailable deliberate branches:")
            for b in deliberate_branches:
                console.print(f"  - {b}")
            console.print("\nSpecify one with [cyan]--branch <name>[/cyan]")
        else:
            console.print("\nTo start a new workflow, run:")
            console.print("  [cyan]deliberate plan 'your task'[/cyan]")
        raise typer.Exit(1)

    # Ensure plan exists on target branch (we check worktree)
    # Use actual repo root to avoid nested worktrees when running from a worktree
    actual_repo_root = get_actual_repo_root(Path.cwd())
    worktree_root = actual_repo_root / ".deliberate" / "worktrees"
    wt_path = branch_mgr.ensure_worktree(target_branch, worktree_root)

    plan_path = wt_path / PLAN_FILENAME
    if not plan_path.exists():
        console.print(f"[red]Error:[/red] No {PLAN_FILENAME} found on current branch.")
        console.print("Run 'deliberate plan <task>' first to create a plan.")
        raise typer.Exit(1)

    plan_content = plan_path.read_text()

    # Load config
    try:
        cfg = DeliberateConfig.load_or_default(config)
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    # Apply profile
    if profile:
        try:
            cfg = cfg.apply_profile(profile)
        except ValueError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    # Skip planning (we already have a plan)
    cfg.workflow.planning.enabled = False

    if skip_review:
        cfg.workflow.review.enabled = False

    console.print(f"[bold]Working on deliberate branch:[/bold] {target_branch}")
    console.print(f"[dim]Plan loaded from {wt_path / PLAN_FILENAME}[/dim]")

    # Initialize verbose logger if requested
    if verbose:
        init_verbose_logger(console=console, enabled=True, show_stdout=True)
        # Suppress noisy INFO logs from MCP server when using dashboard
        logging.getLogger("deliberate.mcp_orchestrator_server").setLevel(logging.WARNING)
        logging.getLogger("mcp.server").setLevel(logging.WARNING)
        logging.getLogger("uvicorn").setLevel(logging.WARNING)

    # Build preloaded plan dict from PLAN.md content
    preloaded_plan = {
        "id": "plan-from-branch",
        "agent": "branch",
        "content": plan_content,
    }

    # Run execution
    orchestrator = Orchestrator(
        cfg,
        actual_repo_root,  # Use actual repo root to avoid nested worktrees
        console=console,
        execution_base_ref=target_branch,  # create execution worktrees from deliberate branch
    )
    result = asyncio.run(
        orchestrator.run(
            plan_content,  # Use plan as task for execution context
            preloaded_plan=preloaded_plan,
            keep_worktrees=True,  # Keep for later merge
        )
    )

    if result.success:
        console.print()
        console.print("[green]Execution complete![/green]")
        console.print("\n[bold]Next steps:[/bold]")
        console.print("  1. Check status:  [cyan]deliberate status[/cyan]")
        console.print("  2. Review & merge: [cyan]deliberate merge[/cyan]")
    else:
        console.print()
        fallback_error = None
        if result.execution_results:
            failed = [er for er in result.execution_results if not er.success]
            if failed:
                first = failed[0]
                fallback_error = first.error or first.error_category or "Agent failed"
                fallback_error = f"{first.agent}: {fallback_error}"

        console.print(f"[red]Execution failed:[/red] {result.error or fallback_error or 'Unknown error'}")

        if result.execution_results:
            table = Table(title="Execution Results", show_header=True, header_style="bold magenta")
            table.add_column("Agent")
            table.add_column("Status")
            table.add_column("Error")
            table.add_column("Worktree")

            for er in result.execution_results:
                status = "[green]success[/green]" if er.success else "[red]failed[/red]"
                table.add_row(
                    er.agent,
                    status,
                    er.error or er.error_category or "",
                    str(er.worktree_path) if er.worktree_path else "",
                )
            console.print(table)

        raise typer.Exit(1)


@app.command("status")
def workflow_status(
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output as JSON",
    ),
):
    """Show the status of the current deliberate workflow.

    Displays information about the current branch, plan, and any
    execution results from worktrees.

    Example:
        deliberate status
    """
    branch_mgr = BranchWorkflowManager(Path.cwd())
    current_branch = branch_mgr.get_current_branch()

    if json_output:
        output = {
            "branch": current_branch,
            "is_deliberate_branch": branch_mgr.is_deliberate_branch(current_branch),
            "has_plan": branch_mgr.has_plan(),
            "parent_branch": branch_mgr.get_parent_branch(),
        }
        print(json.dumps(output, indent=2))
        return

    # Build status display
    is_deliberate = branch_mgr.is_deliberate_branch(current_branch)

    table = Table(title="Deliberate Workflow Status")
    table.add_column("Property", style="cyan")
    table.add_column("Value")

    table.add_row("Current Branch", current_branch)
    table.add_row(
        "Workflow Active",
        "[green]Yes[/green]" if is_deliberate else "[dim]No[/dim]",
    )

    if is_deliberate:
        has_plan = branch_mgr.has_plan()
        table.add_row(
            "Plan",
            f"[green]{PLAN_FILENAME}[/green]" if has_plan else "[red]Missing[/red]",
        )
        table.add_row("Parent Branch", branch_mgr.get_parent_branch() or "Unknown")

        # Check for worktrees
        worktree_mgr = WorktreeManager(Path.cwd())
        worktrees = worktree_mgr.list_worktrees()
        if worktrees:
            table.add_row("Worktrees", str(len(worktrees)))
            for wt in worktrees:
                status = worktree_mgr.get_status(wt)
                status_indicator = "[green]Modified[/green]" if status.strip() else "[dim]Clean[/dim]"
                table.add_row(f"  └─ {wt.name}", status_indicator)

    console.print(table)

    if not is_deliberate:
        console.print()
        console.print("[dim]Not on a deliberate branch. Start with:[/dim]")
        console.print("  [cyan]deliberate plan 'your task'[/cyan]")

    # List other deliberate branches
    other_branches = branch_mgr.list_deliberate_branches()
    other_branches = [b for b in other_branches if b != current_branch]
    if other_branches:
        console.print()
        console.print("[bold]Other deliberate branches:[/bold]")
        for b in other_branches[:5]:
            console.print(f"  - {b}")
        if len(other_branches) > 5:
            console.print(f"  [dim]... and {len(other_branches) - 5} more[/dim]")


@app.command("merge")
def workflow_merge(
    config: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Config file path",
    ),
    branch: Optional[str] = typer.Option(
        None,
        "--branch",
        "-b",
        help="Deliberate branch to merge (auto-detects if omitted)",
    ),
    auto: bool = typer.Option(
        False,
        "--auto",
        help="Automatically select winner and merge without prompts",
    ),
    squash: bool = typer.Option(
        True,
        "--squash/--no-squash",
        help="Squash commits when merging (default: squash)",
    ),
    delete_branch: bool = typer.Option(
        True,
        "--delete-branch/--keep-branch",
        help="Delete deliberate branch after merge (default: delete)",
    ),
    profile: Optional[str] = typer.Option(
        None,
        "--profile",
        "-p",
        help="Optimization profile for review phase",
    ),
    skip_review: bool = typer.Option(
        False,
        "--skip-review",
        help="Skip review phase and use first successful result",
    ),
):
    """Review execution results, dry-run for conflicts, then merge winning changes.

    Runs the review phase on worktree results, then merges the winning
    implementation back to the parent branch.

    Example:
        deliberate merge
        deliberate merge --branch deliberate/my-feature
        deliberate merge --auto  # No prompts
    """
    branch_mgr = BranchWorkflowManager(Path.cwd())
    current_branch = branch_mgr.get_current_branch()
    deliberate_branches = branch_mgr.list_deliberate_branches()
    parent_branch = branch_mgr.get_parent_branch() or "main"

    # Check for worktrees FIRST - worktree mode takes priority
    worktree_mgr = WorktreeManager(Path.cwd())
    worktree_mgr.scan_existing()  # Load worktrees from previous runs
    worktrees = worktree_mgr.list_worktrees()

    # Filter worktrees by associated deliberate branch
    def get_worktree_branch(wt_path: Path) -> str | None:
        """Determine which deliberate branch a worktree belongs to."""
        try:
            # Get the worktree's HEAD commit
            result = branch_mgr._run_git(["git", "rev-parse", "HEAD"], cwd=wt_path, check=False)
            if result.returncode != 0:
                return None
            head_sha = result.stdout.strip()

            # Find which deliberate branches contain this commit
            result = branch_mgr._run_git(
                ["git", "branch", "--contains", head_sha, "--list", "deliberate/*"], check=False
            )
            if result.returncode != 0:
                return None

            # Parse branches (format: "+ branch" or "  branch")
            for line in result.stdout.splitlines():
                branch = line.strip().lstrip("+* ")
                if branch.startswith("deliberate/"):
                    return branch
            return None
        except Exception:
            return None

    # Determine target branch for filtering (if specified or auto-detected)
    filter_branch = None
    if branch:
        filter_branch = branch if branch.startswith("deliberate/") else f"deliberate/{branch}"
    elif len(deliberate_branches) == 1:
        filter_branch = deliberate_branches[0]

    # Filter to worktrees with actual changes AND matching branch
    worktrees_with_changes = []
    for wt in worktrees:
        diff = worktree_mgr.get_diff(wt)
        if not diff or not diff.strip():
            continue

        wt_branch = get_worktree_branch(wt.path)

        # If filtering by branch, skip non-matching worktrees
        if filter_branch and wt_branch != filter_branch:
            continue

        worktrees_with_changes.append((wt, len(diff.splitlines()), wt_branch))

    if worktrees_with_changes:
        # WORKTREE MODE - we have worktrees with changes to merge
        if filter_branch:
            console.print(f"[bold]Merging worktrees from {filter_branch} → {parent_branch}[/bold]")
        else:
            console.print(f"[bold]Merging worktree changes → {parent_branch}[/bold]")

        # Convert worktrees to ExecutionResults for review
        candidates: list[ExecutionResult] = []
        worktree_map: dict[str, Worktree] = {}  # Map result ID to worktree
        branch_map: dict[str, str | None] = {}  # Map result ID to branch
        for i, (wt, lines, wt_branch) in enumerate(worktrees_with_changes):
            diff = worktree_mgr.get_diff(wt)
            result_id = f"wt-{i}"
            candidates.append(
                ExecutionResult(
                    id=result_id,
                    agent=wt.name,  # Use worktree name as agent
                    worktree_path=wt.path,
                    diff=diff,
                    summary=f"{lines} lines changed",
                    success=True,
                )
            )
            worktree_map[result_id] = wt
            branch_map[result_id] = wt_branch

        winner: ExecutionResult | None = None
        winner_wt: Worktree | None = None

        # Run review if multiple candidates and not skipping
        if len(candidates) > 1 and not skip_review:
            console.print(f"\n[dim]Running review phase on {len(candidates)} candidate(s)...[/dim]")

            # Load config for review
            cfg = _load_config(config)
            if not cfg:
                console.print("[yellow]No config found, skipping review.[/yellow]")
                skip_review = True
            else:
                try:
                    # Create orchestrator just for review
                    orchestrator = Orchestrator(cfg, Path.cwd(), console=console)

                    # Get task from PLAN.md if available
                    plan_path = Path.cwd() / PLAN_FILENAME
                    task = plan_path.read_text() if plan_path.exists() else "Review worktree changes"

                    # Run review phase
                    reviews, vote_result = asyncio.run(orchestrator.review.run(task, candidates))

                    if vote_result and vote_result.winner_id:
                        winner = next((c for c in candidates if c.id == vote_result.winner_id), None)
                        if winner:
                            winner_wt = worktree_map[winner.id]
                            console.print("\n[green]Review complete![/green]")
                            console.print(f"  Winner: {winner.agent}")
                            console.print(f"  Confidence: {vote_result.confidence:.0%}")

                            # Show rankings
                            if len(vote_result.rankings) > 1:
                                console.print("\n[dim]Rankings:[/dim]")
                                for rank, rid in enumerate(vote_result.rankings, 1):
                                    c = next((x for x in candidates if x.id == rid), None)
                                    if c:
                                        score = vote_result.scores.get(rid, 0)
                                        marker = "[green]→[/green]" if rid == winner.id else " "
                                        console.print(f"  {marker} {rank}. {c.agent} (score: {score:.2f})")
                    else:
                        console.print("[yellow]No clear winner, using heuristic.[/yellow]")

                except Exception as e:
                    console.print(f"[yellow]Review failed: {e}[/yellow]")
                    console.print("[dim]Falling back to selecting by most changes.[/dim]")

        # Fallback: select worktree with most changes
        if not winner_wt:
            winner_wt, winner_lines, winner_branch = max(worktrees_with_changes, key=lambda x: x[1])
            winner = next((c for c in candidates if worktree_map.get(c.id) == winner_wt), None)

        # At this point winner_wt is guaranteed to be set
        assert winner_wt is not None, "No worktree selected"

        if len(worktrees_with_changes) > 1:
            console.print("\n[dim]Candidates (by lines changed):[/dim]")
            for wt, lines, wt_branch in sorted(worktrees_with_changes, key=lambda x: -x[1]):
                marker = "[green]→[/green]" if wt.name == winner_wt.name else " "
                branch_info = f" [{wt_branch}]" if wt_branch and not filter_branch else ""
                console.print(f"  {marker} {wt.name}: {lines} lines{branch_info}")

        console.print(f"\n[bold]Will merge:[/bold] {winner_wt.name}")

        # Show diff preview
        diff = worktree_mgr.get_diff(winner_wt)
        if diff:
            diff_lines = diff.splitlines()
            console.print(f"[dim]({len(diff_lines)} lines of changes)[/dim]")

        # If not auto mode, confirm
        if not auto:
            if not typer.confirm("\nProceed with merge?"):
                console.print("[yellow]Merge cancelled.[/yellow]")
                raise typer.Exit(0)

        try:
            # Commit any uncommitted changes in the winner worktree
            worktree_mgr.commit_changes(winner_wt, "Deliberate: Final agent changes")

            # Get the commit SHA
            head_sha = worktree_mgr.get_head_sha(winner_wt)

            # Checkout parent branch
            branch_mgr._run_git(["git", "checkout", parent_branch])

            # Merge
            if squash:
                branch_mgr._run_git(["git", "merge", "--squash", head_sha])
                # Use worktree name for commit message
                short_name = winner_wt.name.replace("deliberate__", "").replace("exec-", "task-")
                branch_mgr._run_git(
                    [
                        "git",
                        "commit",
                        "-m",
                        f"feat: {short_name}\n\nMerged from deliberate workflow worktree.",
                    ]
                )
            else:
                branch_mgr._run_git(["git", "merge", "--no-edit", head_sha])

            console.print(f"[green]Merged to {parent_branch}![/green]")

            # Cleanup worktrees
            worktree_mgr.cleanup_all()

            # Optionally delete deliberate branches
            if delete_branch and deliberate_branches:
                for b in deliberate_branches:
                    branch_mgr._run_git(["git", "branch", "-D", b], check=False)
                console.print(f"[dim]Deleted {len(deliberate_branches)} deliberate branch(es)[/dim]")

            # Remove PLAN.md from working directory
            branch_mgr.cleanup_plan()

        except Exception as e:
            console.print(f"[red]Merge failed:[/red] {e}")
            console.print(f"\nWorktree preserved at: {winner_wt.path}")
            console.print("Resolve conflicts manually and retry.")
            raise typer.Exit(1)

        return

    # NO WORKTREES - fall back to branch mode
    # Determine target deliberate branch
    target_branch = None
    if branch:
        target_branch = branch if branch.startswith("deliberate/") else f"deliberate/{branch}"
    elif branch_mgr.is_deliberate_branch(current_branch):
        target_branch = current_branch
    elif len(deliberate_branches) == 1:
        target_branch = deliberate_branches[0]
        console.print(f"[dim]Auto-selecting branch: {target_branch}[/dim]")

    # Verify we have a valid deliberate branch
    if not target_branch or target_branch not in deliberate_branches:
        console.print("[red]Error:[/red] No worktrees or deliberate branch to merge.")
        console.print(f"Current branch: {current_branch}")
        if deliberate_branches:
            console.print("\nAvailable deliberate branches:")
            for b in deliberate_branches:
                console.print(f"  - {b}")
            console.print("\nSpecify one with [cyan]--branch <name>[/cyan]")
        else:
            console.print("\nNo deliberate branches found. Run:")
            console.print("  [cyan]deliberate plan 'your task'[/cyan]")
        raise typer.Exit(1)

    console.print(f"[bold]Merging:[/bold] {target_branch} → {parent_branch}")

    # Branch mode - no worktrees with changes, try to merge branch directly
    on_target_branch = current_branch == target_branch

    if on_target_branch:
        # Check working directory for uncommitted changes
        result = branch_mgr._run_git(["git", "status", "--porcelain"], check=False)
        has_changes = bool(result.stdout.strip() if result.returncode == 0 else "")

        if not has_changes:
            console.print("[yellow]No changes found to merge.[/yellow]")
            console.print("Run 'deliberate work' first to execute the plan.")
            raise typer.Exit(1)

        console.print("\n[bold]Mode:[/bold] Direct working directory (no worktrees)")
        diff_result = branch_mgr._run_git(["git", "diff", "--stat"], check=False)
        if diff_result.stdout.strip():
            console.print(f"[dim]{diff_result.stdout.strip()}[/dim]")

        confirm_msg = "\nCommit working directory changes and merge?"
    else:
        # Check if target branch has commits ahead of parent
        diff_result = branch_mgr._run_git(
            ["git", "diff", "--stat", f"{parent_branch}...{target_branch}"],
            check=False,
        )
        has_changes = bool(diff_result.stdout.strip())

        if not has_changes:
            console.print(f"[yellow]No changes found between {parent_branch} and {target_branch}.[/yellow]")
            raise typer.Exit(1)

        console.print(f"\n[bold]Mode:[/bold] Merging branch {target_branch}")
        console.print(f"[dim]{diff_result.stdout.strip()}[/dim]")

        confirm_msg = f"\nMerge {target_branch} into {parent_branch}?"

    # Confirm merge
    if not auto:
        if not typer.confirm(confirm_msg):
            console.print("[yellow]Merge cancelled.[/yellow]")
            raise typer.Exit(0)

    try:
        # Only commit working directory changes if we're on the target branch
        if on_target_branch:
            branch_mgr._run_git(["git", "add", "-A"])
            short_name = target_branch.replace("deliberate/", "")
            branch_mgr._run_git(
                [
                    "git",
                    "commit",
                    "-m",
                    f"feat({short_name}): implementation complete",
                ],
                check=False,
            )  # May fail if nothing to commit

        # Merge to parent using BranchWorkflowManager
        branch_mgr.merge_to_parent(
            parent_branch=parent_branch,
            squash=squash,
            delete_branch=delete_branch,
            source_branch=target_branch,
        )
        console.print(f"[green]Merged to {parent_branch}![/green]")

        if delete_branch:
            console.print(f"[dim]Deleted branch: {target_branch}[/dim]")

    except Exception as e:
        console.print(f"[red]Merge failed:[/red] {e}")
        console.print("Resolve conflicts manually and retry.")
        raise typer.Exit(1)


@app.command()
def abort():
    """Abort the current deliberate workflow.

    Returns to the parent branch and optionally deletes the workflow branch.
    Any uncommitted work in worktrees will be lost.

    Example:
        deliberate abort
    """
    branch_mgr = BranchWorkflowManager(Path.cwd())
    current_branch = branch_mgr.get_current_branch()

    if not branch_mgr.is_deliberate_branch(current_branch):
        console.print("[yellow]Not on a deliberate branch, nothing to abort.[/yellow]")
        return

    if not typer.confirm(f"Abort workflow on {current_branch}? This will discard any work."):
        raise typer.Abort()

    # Cleanup worktrees first
    try:
        worktree_mgr = WorktreeManager(Path.cwd())
        worktree_mgr.cleanup_all()
    except Exception as e:
        console.print(f"[yellow]Warning:[/yellow] Failed to cleanup worktrees: {e}")

    # Abort and return to parent
    parent = branch_mgr.abort()
    console.print(f"[green]Returned to:[/green] {parent}")
    console.print(f"[dim]Deleted branch: {current_branch}[/dim]")


if __name__ == "__main__":
    app()
