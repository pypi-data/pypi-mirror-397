"GitHub Bot Handler."

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

from rich.console import Console

from deliberate.config import DeliberateConfig
from deliberate.github.bot import (
    format_failure_comment,
    format_plan_comment,
    format_rejected_comment,
    format_success_comment,
    format_timeout_comment,
    parse_command,
)
from deliberate.github.client import GitHubClient
from deliberate.orchestrator import Orchestrator

console = Console()


class GitHubHandler:
    """Handles GitHub events for the Deliberate bot."""

    def __init__(self, event_path: str, token: str):
        self.event_path = Path(event_path)
        self.token = token

        # Load event data
        if not self.event_path.exists():
            raise FileNotFoundError(f"Event path not found: {event_path}")
        self.event = json.loads(self.event_path.read_text())

        # Extract event details
        try:
            self.repo_owner = self.event["repository"]["owner"]["login"]
            self.repo_name = self.event["repository"]["name"]

            # Initialize Client
            self.gh_client = GitHubClient(token, self.repo_owner, self.repo_name)

            # Handle issue_comment event
            if "issue" in self.event:
                self.issue_number = self.event["issue"]["number"]
                self.is_pr = "pull_request" in self.event["issue"]
            elif "pull_request" in self.event:
                self.issue_number = self.event["pull_request"]["number"]
                self.is_pr = True
            else:
                self.issue_number = None
                self.is_pr = False

            if "comment" in self.event:
                self.comment_id = self.event["comment"]["id"]
                self.sender = self.event["comment"]["user"]["login"]
                self.comment_body = self.event["comment"]["body"]
            else:
                self.comment_id = None
                self.sender = self.event.get("sender", {}).get("login", "unknown")
                self.comment_body = ""

        except KeyError as e:
            console.print(f"[red]Error parsing event data:[/red] {e}")
            # Don't crash immediately, as we might not need all fields depending on logic
            self.is_pr = False

    def run_git(self, args: list[str]) -> None:
        """Run a git command."""
        console.print(f"[dim]git {' '.join(args)}[/dim]")
        subprocess.run(["git"] + args, check=True)

    def is_collaborator(self, username: str) -> bool:
        """Check if a user is a collaborator on the repo."""
        return self.gh_client.is_collaborator(username)

    def create_comment(self, body: str) -> int:
        """Post a comment to the issue/PR."""
        if not self.issue_number:
            console.print("[red]Cannot create comment: No issue number[/red]")
            return 0
        return self.gh_client.create_comment(self.issue_number, body)

    def checkout_pr(self):
        """Fetch and checkout the PR branch."""
        if not self.issue_number:
            raise ValueError("No issue number")

        # Fetch PR head to a local branch
        branch_name = f"pr-{self.issue_number}"
        self.run_git(["fetch", "origin", f"pull/{self.issue_number}/head:{branch_name}"])
        self.run_git(["checkout", f"{branch_name}"])

        # Configure git user
        self.run_git(["config", "user.name", "Deliberate Bot"])
        self.run_git(["config", "user.email", "deliberate-bot@users.noreply.github.com"])

    def wait_for_approval(self, plan_comment_id: int, timeout_minutes: int = 10) -> tuple[bool, Optional[str]]:
        """Wait for +1 reaction on the plan comment."""
        poll_interval = 10
        max_polls = (timeout_minutes * 60) // poll_interval

        console.print(f"Waiting for approval on comment {plan_comment_id}...")

        for i in range(max_polls):
            try:
                reactions = self.gh_client.get_reactions(plan_comment_id)

                for reaction in reactions:
                    user = reaction["user"]["login"]
                    content = reaction["content"]

                    # Only accept reactions from collaborators
                    if not self.is_collaborator(user):
                        continue

                    if content == "+1":
                        return True, user
                    if content == "-1":
                        return False, user

            except Exception:
                pass  # Client logs error

            time.sleep(poll_interval)

        return False, None  # Timeout

    async def handle(self):
        """Main handler loop."""
        # 0. Basic checks
        if not self.is_pr:
            console.print("Not a PR event, skipping.")
            return

        if not self.comment_body.strip().startswith("/deliberate"):
            console.print("Not a deliberate command, skipping.")
            return

        # 1. Check user permission
        console.print(f"Checking permission for @{self.sender}...")
        if not self.is_collaborator(self.sender):
            self.create_comment(f"@{self.sender} You must be a repository collaborator to use the Deliberate bot.")
            return

        # 2. Parse command
        parsed = parse_command(self.comment_body)
        if not parsed.valid:
            if parsed.error:
                self.create_comment(parsed.error)
            return

        console.print(f"Command parsed: {parsed.action} (profile: {parsed.profile})")

        # 3. Checkout PR
        try:
            self.checkout_pr()
        except Exception as e:
            error_msg = f"Failed to checkout PR branch: {e}"
            console.print(f"[red]{error_msg}[/red]")
            self.create_comment(error_msg)
            sys.exit(1)

        # 4. Run Planning
        try:
            cfg = DeliberateConfig.load_or_default(None)
            if parsed.profile:
                cfg = cfg.apply_profile(parsed.profile)

            # Disable execution/review for planning phase
            plan_cfg = cfg.model_copy(deep=True)
            plan_cfg.workflow.execution.enabled = False
            plan_cfg.workflow.review.enabled = False
            plan_cfg.workflow.refinement.enabled = False

            # Use CI settings for non-interactive mode
            plan_cfg.ci.enabled = True

            console.print("Running planning phase...")
            orchestrator = Orchestrator(plan_cfg, Path.cwd(), console=console)

            task_content = parsed.task

            result = await orchestrator.run(task_content)

            if not result.selected_plan:
                error = result.error or "Planning failed to produce a plan."
                self.create_comment(f"Planning failed: {error}")
                sys.exit(1)

            # Post plan
            if not result.selected_plan:
                self.create_comment("Planning completed but no plan was selected.")
                sys.exit(1)

            selected_plan = result.selected_plan
            assert selected_plan is not None  # Narrow type after sys.exit guard
            plan_comment_id = self.create_comment(
                format_plan_comment(
                    parsed.action,
                    parsed.profile,
                    selected_plan.content,
                    self.sender,
                )
            )

        except Exception as e:
            console.print(f"[red]Planning error:[/red] {e}")
            self.create_comment(f"An internal error occurred during planning: {e}")
            sys.exit(1)

        # 5. Wait for approval
        approved, approver = self.wait_for_approval(plan_comment_id)

        if not approved:
            if approver:  # Rejected
                self.create_comment(format_rejected_comment(parsed.action, approver))
                console.print(f"Plan rejected by @{approver}")
            else:  # Timeout
                self.create_comment(format_timeout_comment(parsed.action, 10))
                console.print("Plan approval timed out")
            return

        # 6. Execute
        console.print(f"Plan approved by @{approver}. Executing...")
        try:
            exec_cfg = cfg.model_copy(deep=True)
            # Use CI settings
            exec_cfg.ci.enabled = True
            exec_cfg.limits.safety.require_human_approval = False
            exec_cfg.limits.safety.dry_run = False

            # We already have a plan, so we use it
            # Orchestrator handles loading the plan if passed
            orchestrator = Orchestrator(exec_cfg, Path.cwd(), console=console)

            result = await orchestrator.run(task_content, preloaded_plan=result.selected_plan)

            if not result.success:
                error = result.error or "Execution failed."
                self.create_comment(format_failure_comment(parsed.action, error))
                sys.exit(1)

            # 7. Commit changes
            self.run_git(["add", "-A"])
            # Reset artifacts and temporary files
            self.run_git(["reset", "--", "artifacts/", "plan-artifacts/", "task.txt", "*.txt"])

            # Check for changes
            status = subprocess.run(["git", "diff", "--cached", "--quiet"], check=False)
            if status.returncode == 0:  # No changes
                msg = f"## Deliberate Complete\n\nNo code changes were made.\n\n**Approved by:** @{approver}"
                self.create_comment(msg)
                return

            commit_msg = (
                f"Apply deliberate {parsed.action}\n\n"
                f"Requested by: @{self.sender}\n"
                f"Approved by: @{approver}\n"
                f"Profile: {parsed.profile}"
            )

            self.run_git(["commit", "-m", commit_msg])

            # Push changes
            branch_name = f"pr-{self.issue_number}"
            # push to the PR ref
            self.run_git(["push", "origin", f"{branch_name}:refs/pull/{self.issue_number}/head"])

            # 8. Post success
            self.create_comment(
                format_success_comment(
                    parsed.action,
                    result.summary or "No summary available",
                    result.total_duration_seconds,
                    result.total_token_usage,
                    result.total_cost_usd,
                    approver or "unknown",
                )
            )

        except Exception as e:
            console.print(f"[red]Execution error:[/red] {e}")
            self.create_comment(f"An internal error occurred during execution: {e}")
            sys.exit(1)
