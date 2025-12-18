"""Enhanced verbose logging for deliberate orchestration."""

from __future__ import annotations

import time
from collections import deque
from contextlib import contextmanager
from typing import Any

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.tree import Tree


class VerboseLogger:
    """Rich console logger for verbose orchestration output."""

    def __init__(self, console: Console | None = None, enabled: bool = False, show_stdout: bool = False):
        """Initialize verbose logger.

        Args:
            console: Rich console instance
            enabled: Whether verbose logging is enabled
            show_stdout: Whether to show agent stdout tail in the dashboard
        """
        self.console = console or Console()
        self.enabled = enabled
        self.show_stdout = show_stdout
        self._phase_times: dict[str, float] = {}
        self._agent_metrics: dict[str, dict[str, Any]] = {}
        self._current_phase: str | None = None
        self._workflow_start: float = 0

        # Live dashboard state
        self._live: Live | None = None
        self._logs: deque[str] = deque(maxlen=200)
        self._agent_states: dict[str, dict[str, Any]] = {}
        self._phase_states: dict[str, str] = {}
        self._phase_order = ["Planning", "Execution", "Review", "Refinement"]
        self._stdout_tail: dict[str, deque[str]] = {}
        self._stdout_partial: dict[str, str] = {}

    def _start_live(self):
        if not self.enabled or self._live:
            return
        self._live = Live(self._render_live(), console=self.console, refresh_per_second=4)
        self._live.start()

    def _stop_live(self):
        if self._live:
            self._live.stop()
            self._live = None

    def _refresh_live(self):
        if self._live:
            self._live.update(self._render_live(), refresh=True)

    def _append_log(self, message: str, level: str = "info"):
        if not self.enabled:
            return
        if not message:
            return
        prefix = {
            "warning": "[yellow]⚠[/yellow] ",
            "error": "[red]✗[/red] ",
            "success": "[green]✓[/green] ",
        }.get(level, "")
        self._logs.append(f"{prefix}{message}")
        self._refresh_live()

    def _set_phase_state(self, phase: str, state: str):
        self._phase_states[phase] = state
        self._refresh_live()

    def register_phases(self, phases: dict[str, bool]):
        """Pre-register phases so the live dashboard can show skipped phases."""
        if not self.enabled:
            return
        for phase in self._phase_order:
            self._phase_states[phase] = "pending" if phases.get(phase, True) else "skipped"
        self._refresh_live()

    def start_workflow(self, task: str):
        """Log the start of a workflow.

        Args:
            task: Task description
        """
        if not self.enabled:
            return

        self._workflow_start = time.time()
        self._start_live()
        self._append_log(f"Task: {task[:200]}")
        if len(task) > 200:
            self._append_log(f"... ({len(task)} total characters)")
        self.console.print()
        self.console.print(
            Panel.fit(
                "[bold cyan]Starting Workflow[/bold cyan]",
                border_style="cyan",
            )
        )
        self.console.print(f"\n[bold]Task:[/bold] {task[:200]}")
        if len(task) > 200:
            self.console.print(f"[dim]... ({len(task)} total characters)[/dim]")
        self.console.print()

    @contextmanager
    def phase(self, phase_name: str, agents: list[str] | None = None):
        """Context manager for tracking phase execution.

        Args:
            phase_name: Name of the phase (Planning, Execution, Review, etc.)
            agents: Optional list of agents participating in this phase

        Yields:
            None
        """
        if not self.enabled:
            yield
            return

        self._current_phase = phase_name
        self._set_phase_state(phase_name, "running")
        agent_str = f" ({', '.join(agents)})" if agents else ""

        self.console.print(f"[bold cyan]→ {phase_name}{agent_str}[/bold cyan]")
        self._append_log(f"{phase_name} started{agent_str}")

        phase_start = time.time()
        try:
            yield
            self._set_phase_state(phase_name, "completed")
        except Exception:
            self._set_phase_state(phase_name, "error")
            raise
        finally:
            duration = time.time() - phase_start
            self._phase_times[phase_name] = duration
            self.console.print(f"[dim]  ✓ {phase_name} completed in {duration:.2f}s[/dim]\n")
            self._append_log(f"{phase_name} completed in {duration:.2f}s")
            self._current_phase = None
            self._refresh_live()

    def log_agent_call(
        self,
        agent_name: str,
        operation: str,
        duration_seconds: float | None = None,
        tokens: int | None = None,
        cost_usd: float | None = None,
        success: bool = True,
        error: str | None = None,
    ):
        """Log an agent call with metrics.

        Args:
            agent_name: Name of the agent
            operation: Type of operation (plan, execute, review)
            duration_seconds: Call duration in seconds
            tokens: Token usage
            cost_usd: Cost in USD
            success: Whether the call succeeded
            error: Error message if failed
        """
        if not self.enabled:
            return

        # Track metrics
        if agent_name not in self._agent_metrics:
            self._agent_metrics[agent_name] = {
                "calls": 0,
                "total_duration": 0.0,
                "total_tokens": 0,
                "total_cost": 0.0,
                "errors": 0,
            }

        metrics = self._agent_metrics[agent_name]
        metrics["calls"] += 1

        if duration_seconds:
            metrics["total_duration"] += duration_seconds
        if tokens:
            metrics["total_tokens"] += tokens
        if cost_usd:
            metrics["total_cost"] += cost_usd
        if not success:
            metrics["errors"] += 1

        # Log the call
        status = "[green]✓[/green]" if success else "[red]✗[/red]"
        indent = "    " if self._current_phase else "  "

        parts = [f"{status} {agent_name}"]
        if operation:
            parts.append(f"[dim]{operation}[/dim]")
        if duration_seconds:
            parts.append(f"[dim]{duration_seconds:.2f}s[/dim]")
        if tokens:
            parts.append(f"[dim]{tokens:,} tokens[/dim]")
        if cost_usd:
            parts.append(f"[dim]${cost_usd:.4f}[/dim]")

        log_line = f"{indent}{' · '.join(parts)}"

        if error:
            self.console.print(log_line)
            self.console.print(f"{indent}  [red]Error: {error}[/red]")
        else:
            self.console.print(log_line)
        self._append_log(f"{agent_name} {operation} {'OK' if success else 'failed'}")

    def log_event(self, message: str, level: str = "info"):
        """Log a general event.

        Args:
            message: Message to log
            level: Log level (info, warning, error, success)
        """
        if not self.enabled:
            return

        indent = "    " if self._current_phase else "  "

        if level == "warning":
            self.console.print(f"{indent}[yellow]⚠ {message}[/yellow]")
        elif level == "error":
            self.console.print(f"{indent}[red]✗ {message}[/red]")
        elif level == "success":
            self.console.print(f"{indent}[green]✓ {message}[/green]")
        else:
            self.console.print(f"{indent}[dim]{message}[/dim]")
        self._append_log(message, level)

    def update_agent_status(self, agent: str, status: str, last_action: str | None = None):
        """Update the live dashboard's agent status table."""
        if not self.enabled:
            return
        state = self._agent_states.setdefault(
            agent,
            {"status": "pending", "last_action": "queued", "updated": time.time()},
        )
        state["status"] = status
        if last_action:
            state["last_action"] = last_action
        state["updated"] = time.time()
        self._append_log(f"{agent}: {status}" + (f" – {last_action}" if last_action else ""))
        self._refresh_live()

    def stream_output(self, agent: str, data: bytes, stream: str = "stdout"):
        """Capture streaming output (stdout/stderr) for live display."""
        if not self.enabled or not self.show_stdout:
            return

        decoded = data.decode("utf-8", errors="replace")
        partial = self._stdout_partial.get(agent, "")
        text = partial + decoded
        lines = text.splitlines(keepends=True)

        # If last line is not terminated, keep it as partial
        if lines and not lines[-1].endswith(("\n", "\r")):
            self._stdout_partial[agent] = lines[-1]
            complete = lines[:-1]
        else:
            self._stdout_partial[agent] = ""
            complete = lines

        tail = self._stdout_tail.setdefault(agent, deque(maxlen=50))
        for ln in complete:
            tail.append(ln.rstrip("\n"))

        self._refresh_live()

    def show_phase_summary(self):
        """Show summary of phase timings."""
        if not self.enabled or not self._phase_times:
            return

        self.console.print("\n[bold]Phase Timings:[/bold]")
        tree = Tree("", guide_style="dim")

        total_time = sum(self._phase_times.values())

        for phase, duration in self._phase_times.items():
            percentage = (duration / total_time * 100) if total_time > 0 else 0
            tree.add(f"{phase}: [cyan]{duration:.2f}s[/cyan] [dim]({percentage:.1f}%)[/dim]")

        self.console.print(tree)
        self.console.print()

    def show_agent_metrics(self):
        """Show detailed agent metrics."""
        if not self.enabled or not self._agent_metrics:
            return

        self.console.print("[bold]Agent Metrics:[/bold]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Agent", style="cyan")
        table.add_column("Calls", justify="right")
        table.add_column("Total Time", justify="right")
        table.add_column("Tokens", justify="right")
        table.add_column("Cost", justify="right")
        table.add_column("Errors", justify="right")

        for agent_name, metrics in sorted(self._agent_metrics.items()):
            table.add_row(
                agent_name,
                str(metrics["calls"]),
                f"{metrics['total_duration']:.2f}s",
                f"{metrics['total_tokens']:,}" if metrics["total_tokens"] > 0 else "-",
                f"${metrics['total_cost']:.4f}" if metrics["total_cost"] > 0 else "-",
                str(metrics["errors"]) if metrics["errors"] > 0 else "-",
            )

        self.console.print(table)
        self.console.print()

    def show_final_summary(
        self,
        success: bool,
        total_duration: float,
        total_tokens: int,
        total_cost: float,
    ):
        """Show final workflow summary.

        Args:
            success: Whether workflow succeeded
            total_duration: Total duration in seconds
            total_tokens: Total token usage
            total_cost: Total cost in USD
        """
        if not self.enabled:
            return

        self._stop_live()
        self.console.print()
        status = "[green]SUCCESS[/green]" if success else "[red]FAILED[/red]"
        self.console.print(Panel.fit(f"[bold]Workflow Complete: {status}[/bold]"))

        # Show phase breakdown
        self.show_phase_summary()

        # Show agent metrics
        self.show_agent_metrics()

        # Show totals
        self.console.print("[bold]Total Usage:[/bold]")
        self.console.print(f"  Duration: [cyan]{total_duration:.2f}s[/cyan]")
        self.console.print(f"  Tokens: [cyan]{total_tokens:,}[/cyan]")
        self.console.print(f"  Cost: [cyan]${total_cost:.4f}[/cyan]")
        self.console.print()

    def stop_live(self):
        """Stop the live dashboard (safe to call multiple times)."""
        self._stop_live()

    # Rendering helpers -------------------------------------------------
    def _status_badge(self, state: str) -> str:
        return {
            "pending": "[dim]•[/dim]",
            "running": "[yellow]↻[/yellow]",
            "completed": "[green]✓[/green]",
            "skipped": "[dim]–[/dim]",
            "error": "[red]✗[/red]",
        }.get(state, "[dim]?[/dim]")

    def _render_phase_progress(self) -> Panel:
        table = Table.grid(expand=True)
        for _ in self._phase_order:
            table.add_column(justify="center")

        cells = []
        for phase in self._phase_order:
            state = self._phase_states.get(phase, "pending")
            badge = self._status_badge(state)
            cells.append(f"{badge} {phase}")
        table.add_row(*cells)
        return Panel(table, title="Workflow", border_style="cyan")

    def _render_agent_table(self) -> Panel:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Agent", style="cyan", no_wrap=True)
        table.add_column("Status", style="white", no_wrap=True)
        table.add_column("Last Action", style="white")

        if not self._agent_states:
            table.add_row("[dim]No agents yet[/dim]", "", "")
        else:
            for agent, state in sorted(self._agent_states.items()):
                table.add_row(
                    agent,
                    self._status_badge(state.get("status", "pending")),
                    state.get("last_action", ""),
                )

        return Panel(table, title="Agents", border_style="magenta")

    def _render_logs(self) -> Panel:
        text = Text()
        if not self._logs:
            text.append("[dim]Waiting for events...[/dim]")
        else:
            for line in list(self._logs)[-12:]:
                try:
                    text.append_text(Text.from_markup(line))
                except Exception:
                    text.append(line)
                text.append("\n")
        return Panel(text, title="Logs", border_style="blue")

    def _render_stdout(self, max_lines: int = 20) -> Panel:
        text = Text()
        if not self._stdout_tail:
            text.append("[dim]Waiting for agent output...[/dim]")
        else:
            for agent, lines in sorted(self._stdout_tail.items()):
                if not lines:
                    continue
                text.append(f"{agent}:\n", style="cyan")
                data = list(lines)
                if len(data) > max_lines:
                    text.append(f"[dim]  … ({len(data) - max_lines} earlier lines truncated)[/dim]\n")
                    data = data[-max_lines:]
                for ln in data:
                    text.append(f"  {ln.rstrip()}\n")
        return Panel(text, title="Agent stdout", border_style="green")

    def _render_live(self) -> Layout:
        layout = Layout(name="root")
        if self.show_stdout:
            layout.split(
                Layout(name="top", size=5),
                Layout(name="middle", size=9),
                Layout(name="bottom", ratio=2),
            )
            layout["bottom"].split(
                Layout(name="logs"),
                Layout(name="stdout"),
            )
            layout["top"].update(self._render_phase_progress())
            layout["middle"].update(self._render_agent_table())
            layout["bottom"]["logs"].update(self._render_logs())
            layout["bottom"]["stdout"].update(self._render_stdout())
        else:
            layout.split(
                Layout(name="top", size=5),
                Layout(name="middle", size=9),
                Layout(name="bottom"),
            )
            layout["top"].update(self._render_phase_progress())
            layout["middle"].update(self._render_agent_table())
            layout["bottom"].update(self._render_logs())
        return layout


# Global logger instance
_verbose_logger: VerboseLogger | None = None


def get_verbose_logger() -> VerboseLogger:
    """Get the global verbose logger instance.

    Returns:
        The global VerboseLogger instance
    """
    global _verbose_logger
    if _verbose_logger is None:
        _verbose_logger = VerboseLogger(enabled=False)
    return _verbose_logger


def init_verbose_logger(console: Console | None = None, enabled: bool = False, show_stdout: bool = False):
    """Initialize the global verbose logger.

    Args:
        console: Rich console instance
        enabled: Whether verbose logging is enabled
        show_stdout: Whether to show agent stdout tail in the dashboard
    """
    global _verbose_logger
    _verbose_logger = VerboseLogger(console=console, enabled=enabled, show_stdout=show_stdout)
