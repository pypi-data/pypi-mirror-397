"""Interactive TUI for reviewing execution results and overriding jury votes."""

import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Callable, Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.syntax import Syntax
from rich.table import Table

from deliberate.types import ExecutionResult, VoteResult


class ReviewTUI:
    """Interactive terminal UI for reviewing execution results."""

    def __init__(self, console: Optional[Console] = None):
        """Initialize the review TUI.

        Args:
            console: Rich console instance (creates new one if not provided)
        """
        self.console = console or Console()
        self._editor_launcher: Callable[[list[str]], subprocess.Popen] = subprocess.Popen

    def review_and_select_winner(
        self,
        execution_results: list[ExecutionResult],
        vote_result: VoteResult | None,
        task: str,
    ) -> str:
        """Interactive review to select the winning execution.

        Args:
            execution_results: List of execution results from different agents
            vote_result: Jury vote result (can be None if voting failed)
            task: The task that was executed

        Returns:
            The ID of the selected winning execution
        """
        self.console.clear()
        self.console.print(Panel.fit("[bold cyan]Interactive Review[/bold cyan]", border_style="cyan"))
        self.console.print(f"\n[bold]Task:[/bold] {task[:100]}...")
        self.console.print()

        # Show execution results summary
        self._show_execution_summary(execution_results, vote_result)

        # Show jury recommendation
        if vote_result and vote_result.winner_id:
            self.console.print(
                f"\n[bold green]Jury Recommendation:[/bold green] {vote_result.winner_id} "
                f"(confidence: {vote_result.confidence:.2f})"
            )
        else:
            self.console.print("\n[yellow]⚠ No jury vote available[/yellow]")

        # Interactive selection
        while True:
            self.console.print("\n[bold]Options:[/bold]")
            self.console.print("  [cyan]1-{}[/cyan] View execution details".format(len(execution_results)))
            self.console.print("  [cyan]a[/cyan] Accept jury recommendation")
            self.console.print("  [cyan]s[/cyan] Select different winner manually")
            self.console.print("  [cyan]o[/cyan] Open an execution worktree in your editor")
            self.console.print("  [cyan]q[/cyan] Quit without selecting")

            choice = Prompt.ask("Your choice", default="a" if vote_result else "s")

            if choice == "q":
                raise KeyboardInterrupt("Review cancelled by user")

            elif choice == "a":
                if vote_result and vote_result.winner_id:
                    if Confirm.ask(f"Accept {vote_result.winner_id} as winner?", default=True):
                        return vote_result.winner_id
                else:
                    self.console.print("[red]No jury recommendation available[/red]")

            elif choice == "s":
                winner = self._manual_selection(execution_results)
                if winner:
                    return winner

            elif choice == "o":
                selected = self._prompt_for_execution(execution_results, action="open")
                if selected:
                    self._open_worktree(selected)

            elif choice.isdigit() and 1 <= int(choice) <= len(execution_results):
                idx = int(choice) - 1
                self._show_execution_details(execution_results[idx])

            else:
                self.console.print("[red]Invalid choice[/red]")

    def _show_execution_summary(
        self,
        execution_results: list[ExecutionResult],
        vote_result: VoteResult | None,
    ):
        """Show summary table of all execution results."""
        table = Table(title="Execution Results", show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=3)
        table.add_column("Agent", style="cyan")
        table.add_column("Status", justify="center")
        table.add_column("Score", justify="right")
        table.add_column("Has Changes", justify="center")

        for idx, result in enumerate(execution_results, 1):
            status = "[green]✓[/green]" if result.success else "[red]✗[/red]"
            score = (
                f"{vote_result.scores.get(result.id, 0):.2f}"
                if vote_result and result.id in vote_result.scores
                else "-"
            )
            has_changes = "[green]✓[/green]" if result.diff else "[dim]-[/dim]"

            table.add_row(
                str(idx),
                result.agent,
                status,
                score,
                has_changes,
            )

        self.console.print(table)

    def _show_execution_details(self, result: ExecutionResult):
        """Show detailed view of a single execution result with tab-like toggles."""
        view = "diff"
        while True:
            self.console.clear()
            self.console.print(
                Panel.fit(
                    f"[bold cyan]Execution Details: {result.agent}[/bold cyan]",
                    subtitle="[dim][d]iff  [f]iles  [s]tdout  [b]ack[/dim]",
                    border_style="cyan",
                )
            )

            status = "[green]SUCCESS[/green]" if result.success else "[red]FAILED[/red]"
            self.console.print(f"\n[bold]Status:[/bold] {status}")
            self.console.print(f"[bold]ID:[/bold] {result.id}")

            if result.error:
                self.console.print(f"\n[bold red]Error:[/bold red] {result.error}")

            if view == "diff":
                current_view = "Diff"
            elif view == "files":
                current_view = "Files"
            else:
                current_view = "Stdout"

            self.console.print(f"\n[bold]View:[/bold] {current_view}")

            if view == "diff":
                if result.diff:
                    self.console.print("\n[bold]Changes:[/bold]")
                    self._show_diff_with_pager(result.diff)
                else:
                    self.console.print("\n[yellow]No changes made[/yellow]")
            elif view == "files":
                if result.diff:
                    self._show_files_view(result.diff)
                else:
                    self.console.print("\n[yellow]No changes made[/yellow]")
            elif view == "stdout":
                if result.stdout:
                    self.console.print("\n[bold]Agent stdout/stderr:[/bold]")
                    self._show_stdout_with_pager(result.stdout)
                else:
                    self.console.print("\n[yellow]No stdout captured for this run[/yellow]")

            if result.duration_seconds:
                self.console.print(f"\n[dim]Duration: {result.duration_seconds:.2f}s[/dim]")

            choice = Prompt.ask(
                "\nSwitch view or back?",
                choices=["d", "f", "s", "b"],
                default="b",
            )
            if choice == "b":
                break
            if choice == "d":
                view = "diff"
            elif choice == "f":
                view = "files"
            else:
                view = "stdout"

    def _prompt_for_execution(
        self,
        execution_results: list[ExecutionResult],
        action: str = "open",
    ) -> ExecutionResult | None:
        """Prompt the user to choose an execution result for a follow-up action."""
        self.console.print(f"\n[bold]Select a run to {action}:[/bold]")

        for idx, result in enumerate(execution_results, 1):
            status = "✓" if result.success else "✗"
            path_display = f" ({result.worktree_path})" if result.worktree_path else ""
            self.console.print(f"  [{idx}] {status} {result.agent}{path_display}")

        while True:
            choice = Prompt.ask("Select number (or 'c' to cancel)", default="1")
            if choice.lower() == "c":
                return None
            if choice.isdigit() and 1 <= int(choice) <= len(execution_results):
                return execution_results[int(choice) - 1]
            self.console.print("[red]Invalid choice[/red]")

    def _open_worktree(self, result: ExecutionResult) -> None:
        """Open the execution's worktree in the user's editor or IDE."""
        if not result.worktree_path:
            self.console.print("[red]This result does not have a worktree to open.[/red]")
            return

        path = Path(result.worktree_path)
        if not path.exists():
            self.console.print(f"[red]Worktree path not found:[/red] {path}")
            return

        command = resolve_editor_command(path)
        if not command:
            self.console.print(
                "[yellow]No GUI/editor command found.[/yellow] "
                "Set $VISUAL or $EDITOR, or install VS Code (`code`) to enable quick open."
            )
            self.console.print(f"You can still inspect the worktree manually: cd {path}")
            return

        try:
            self._editor_launcher(command)
        except Exception as exc:  # pragma: no cover - defensive
            self.console.print(f"[red]Failed to launch editor:[/red] {exc}")
            self.console.print(f"You can open it manually with: {' '.join(command)}")
            return

        self.console.print(
            f"[green]Opened {path} in your editor.[/green] "
            "You can run tests or start the app directly inside that isolated worktree before merging."
        )

    def _show_diff_with_pager(self, diff: str, threshold: int = 50):
        """Show diff, using pager for large diffs.

        Args:
            diff: The diff content to display
            threshold: Line threshold for using pager (default: 50 lines)
        """
        lines = diff.split("\n")

        if len(lines) <= threshold:
            # Small diff - show inline
            syntax = Syntax(diff, "diff", theme="monokai", line_numbers=True)
            self.console.print(syntax)
        else:
            # Large diff - offer to use pager
            self.console.print(f"[dim]Diff has {len(lines)} lines[/dim]")

            if Confirm.ask("Open in pager?", default=True):
                self._show_in_pager(diff, syntax="diff")
            else:
                # Show first 50 lines
                truncated = "\n".join(lines[:50])
                syntax = Syntax(truncated, "diff", theme="monokai", line_numbers=True)
                self.console.print(syntax)
                self.console.print(f"\n[dim]... ({len(lines) - 50} more lines)[/dim]")

    def _split_diff_by_file(self, diff: str) -> dict[str, str]:
        """Split a unified diff into per-file sections."""
        files: dict[str, list[str]] = {}
        current_file: str | None = None
        current_lines: list[str] = []

        for line in diff.splitlines():
            if line.startswith("diff --git "):
                if current_file and current_lines:
                    files[current_file] = current_lines

                parts = line.split()
                if len(parts) >= 4 and parts[3].startswith("b/"):
                    current_file = parts[3][2:]
                else:
                    current_file = line.replace("diff --git ", "")
                current_lines = [line]
                continue

            if current_file is None:
                current_file = "changes"
            current_lines.append(line)

        if current_file and current_lines:
            files[current_file] = current_lines

        return {name: "\n".join(lines) for name, lines in files.items()}

    def _show_files_view(self, diff: str) -> None:
        """Browse changed files and open individual patches."""
        files = self._split_diff_by_file(diff)

        if not files:
            self.console.print("\n[yellow]No file-level changes detected.[/yellow]")
            return

        file_items = list(files.items())

        while True:
            self.console.print("\n[bold]Changed files:[/bold]")
            for idx, (name, _) in enumerate(file_items, 1):
                self.console.print(f"  [{idx}] {name}")

            choice = Prompt.ask("View file diff (number) or 'b' to go back", default="b")
            if choice.lower() == "b":
                break

            if choice.isdigit() and 1 <= int(choice) <= len(file_items):
                _, content = file_items[int(choice) - 1]
                self._show_diff_with_pager(content, threshold=120)
            else:
                self.console.print("[red]Invalid choice[/red]")

    def _show_in_pager(self, content: str, syntax: str = "diff"):
        """Show content in external pager (bat or less).

        Args:
            content: Content to display
            syntax: Syntax highlighting type
        """
        import shutil
        import subprocess
        import tempfile

        # Try bat first (better syntax highlighting)
        if shutil.which("bat"):
            with tempfile.NamedTemporaryFile(mode="w", suffix=".diff", delete=False) as f:
                f.write(content)
                temp_path = f.name

            try:
                subprocess.run(
                    ["bat", "--style=numbers,grid", f"--language={syntax}", temp_path],
                    check=False,
                )
            finally:
                Path(temp_path).unlink(missing_ok=True)

        # Fallback to less
        elif shutil.which("less"):
            subprocess.run(["less", "-R"], input=content.encode(), check=False)

        # Last resort: rich pager
        else:
            from rich.console import Console

            pager_console = Console()
            with pager_console.pager():
                syntax_obj = Syntax(content, syntax, theme="monokai", line_numbers=True)
                pager_console.print(syntax_obj)

    def _show_stdout_with_pager(self, content: str, threshold: int = 80):
        """Show stdout log with optional pager for long outputs."""
        lines = content.splitlines()
        if len(lines) <= threshold:
            self.console.print("\n".join(lines))
            return

        self.console.print(f"[dim]Log has {len(lines)} lines[/dim]")
        if Confirm.ask("Open log in pager?", default=True):
            self._show_in_pager(content, syntax="text")
        else:
            truncated = "\n".join(lines[:threshold])
            self.console.print(truncated)
            self.console.print(f"\n[dim]... ({len(lines) - threshold} more lines)[/dim]")

    def _manual_selection(self, execution_results: list[ExecutionResult]) -> str | None:
        """Manually select a winner from execution results.

        Args:
            execution_results: List of execution results

        Returns:
            The ID of the selected execution, or None if cancelled
        """
        self.console.print("\n[bold]Select Winner:[/bold]")

        # Show numbered list
        for idx, result in enumerate(execution_results, 1):
            status = "✓" if result.success else "✗"
            has_diff = "📝" if result.diff else "  "
            self.console.print(f"  [{idx}] {status} {has_diff} {result.agent} ({result.id[:8]})")

        while True:
            choice = Prompt.ask("Select number (or 'c' to cancel)", default="1")

            if choice.lower() == "c":
                return None

            if choice.isdigit() and 1 <= int(choice) <= len(execution_results):
                idx = int(choice) - 1
                selected = execution_results[idx]

                if Confirm.ask(f"Select {selected.agent} ({selected.id[:8]}) as winner?"):
                    return selected.id
            else:
                self.console.print("[red]Invalid choice[/red]")


def show_diff_with_pager(diff: str, console: Optional[Console] = None):
    """Utility function to show a diff with automatic pager selection.

    Args:
        diff: The diff content to display
        console: Rich console instance (creates new one if not provided)
    """
    console = console or Console()
    tui = ReviewTUI(console)
    tui._show_diff_with_pager(diff)


def resolve_editor_command(path: Path) -> list[str] | None:
    """Resolve the best available editor command for a path."""
    editor = os.environ.get("VISUAL") or os.environ.get("EDITOR")
    if editor:
        return shlex.split(editor) + [str(path)]

    if shutil.which("code"):
        return ["code", str(path)]

    if sys.platform == "darwin" and shutil.which("open"):
        return ["open", str(path)]

    if shutil.which("xdg-open"):
        return ["xdg-open", str(path)]

    return None
