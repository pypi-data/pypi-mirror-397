"""Maintenance Workflow."""

import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

from rich.console import Console

from deliberate.config import DeliberateConfig
from deliberate.github.client import GitHubClient
from deliberate.orchestrator import Orchestrator
from deliberate.validation.failure_interpreter import FailureInterpreter
from deliberate.validation.types import RunArtifacts

console = Console()


class MaintenanceWorkflow:
    """Automated maintenance workflow for flaky tests."""

    def __init__(self, test_command: str, github_token: str, repo_owner: str, repo_name: str):
        self.test_command = test_command
        self.gh_client = GitHubClient(github_token, repo_owner, repo_name)

    def run_git(self, args: list[str]) -> None:
        """Run a git command."""
        console.print(f"[dim]git {' '.join(args)}[/dim]")
        subprocess.run(["git"] + args, check=True)

    def detect_flakes(self, runs: int) -> list[str]:
        """Run the test suite multiple times to identify flakes using reusable interpreters."""
        console.print(f"[bold]Detecting flaky tests ({runs} runs)...[/bold]")

        failed_tests = set()
        interpreter = FailureInterpreter()

        for i in range(runs):
            console.print(f"Run {i + 1}/{runs}...")

            # Create a temp file for JUnit XML per run
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".xml",
                prefix="junit_report_",
                delete=False,
            ) as tmp:
                junit_xml_path = Path(tmp.name)

            try:
                # Modify the test command to output JUnit XML
                test_command_with_xml = f"{self.test_command} --junitxml={junit_xml_path}"

                result = subprocess.run(
                    test_command_with_xml,
                    shell=True,
                    capture_output=True,
                    text=True,
                )

                junit_xml = junit_xml_path.read_text() if junit_xml_path.exists() else None

                artifacts = RunArtifacts(
                    command=self.test_command,
                    cwd=Path.cwd(),
                    exit_code=result.returncode or 0,
                    duration_seconds=0.0,
                    stdout=result.stdout or "",
                    stderr=result.stderr or "",
                    junit_xml=junit_xml,
                )

                interpretation = interpreter.interpret(artifacts)
                if interpretation.failed_tests:
                    failed_tests.update(interpretation.failed_tests)
                elif result.returncode != 0:
                    console.print(f"[yellow]Run {i + 1} failed but no failures extracted.[/yellow]")
            finally:
                # Clean up the temporary XML file
                junit_xml_path.unlink(missing_ok=True)

        if not failed_tests:
            console.print("[green]No flakes detected.[/green]")
            return []

        console.print(f"[red]Flakes detected:[/red] {', '.join(failed_tests)}")
        return list(failed_tests)

    def verify_fix(self, test_command: str, runs: int) -> bool:
        """Verify the fix by running the tests multiple times."""
        console.print(f"[bold]Verifying fix ({runs} runs)...[/bold]")

        for i in range(runs):
            console.print(f"Verify Run {i + 1}/{runs}...")
            result = subprocess.run(
                test_command,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            if result.returncode != 0:
                console.print(f"[red]Verification failed on run {i + 1}[/red]")
                return False

        console.print("[green]Verification successful![/green]")
        return True

    async def run(self, detect_runs: int = 5, verify_runs: int = 100):
        """Run the full maintenance cycle."""

        # 1. Detect
        flaky_tests = self.detect_flakes(detect_runs)
        if not flaky_tests:
            return

        # 2. Setup Branch
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        branch_name = f"fix/flaky-tests-{timestamp}"

        # Ensure we are on main and up to date
        self.run_git(["checkout", "main"])
        self.run_git(["pull", "origin", "main"])
        self.run_git(["checkout", "-b", branch_name])

        # 3. Create Task & Plan
        task = (
            f"The following tests are flaky (failed intermittently during {detect_runs} runs):\n"
            f"{', '.join(flaky_tests)}\n\n"
            "Analyze the test code and production code to identify the cause of the flakiness "
            "(e.g., race conditions, non-deterministic order, shared state, timeout issues).\n"
            "Fix the tests to be stable."
        )

        cfg = DeliberateConfig.load_or_default(None)
        # Apply profile for high quality
        cfg = cfg.apply_profile("max_quality")
        cfg.ci.enabled = True
        cfg.limits.safety.require_human_approval = False

        orchestrator = Orchestrator(cfg, Path.cwd(), console=console)

        console.print("[bold]Generating plan and executing fix...[/bold]")
        result = await orchestrator.run(task)

        if not result.success:
            console.print("[red]Fix execution failed.[/red]")
            return

        # 4. Verify
        if not self.verify_fix(self.test_command, verify_runs):
            console.print("[red]Fix verification failed. Aborting PR.[/red]")
            return

        # 5. Push & PR
        self.run_git(["add", "-A"])
        # Cleanup
        self.run_git(["reset", "--", "artifacts/", "plan-artifacts/", "*.txt"])

        if subprocess.run(["git", "diff", "--cached", "--quiet"], check=False).returncode == 0:
            console.print("[yellow]No changes to commit.[/yellow]")
            return

        self.run_git(["commit", "-m", f"Fix flaky tests: {', '.join(flaky_tests)}"])
        self.run_git(["push", "origin", branch_name])

        flake_list = "\n".join([f"- `{t}`" for t in flaky_tests])

        pr_body = (
            f"## Automated Flaky Test Fix\n\n"
            f"**Detected Flakes:**\n"
            f"{flake_list}\n\n"
            f"**Verification:**\n"
            f"Passed {verify_runs} consecutive runs.\n\n"
            f"**Summary:**\n{result.summary or 'No summary provided.'}"
        )

        pr_number = self.gh_client.create_pull_request(
            title=f"Fix flaky tests: {', '.join(flaky_tests)}",
            body=pr_body,
            head=branch_name,
        )

        console.print(f"[green]PR created: #{pr_number}[/green]")
