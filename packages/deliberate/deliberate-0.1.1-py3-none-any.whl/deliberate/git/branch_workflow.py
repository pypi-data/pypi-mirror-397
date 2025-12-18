"""Git branch-based workflow management for deliberate.

This module implements the git-native workflow where:
- Plans are committed as PLAN.md files on dedicated branches
- Workflow state is persisted in Git, not ephemeral RAM
- CLI commands mimic Git operations (plan, work, status, merge)
"""

import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Literal

PLAN_FILENAME = "PLAN.md"
BRANCH_PREFIX = "deliberate/"


@dataclass
class BranchWorkflow:
    """Represents a deliberate workflow on a Git branch.

    Attributes:
        branch_name: The full branch name (e.g., 'deliberate/add-users-endpoint')
        parent_branch: The branch this was created from (e.g., 'main')
        task: The original task description
        status: Current workflow status
        created_at: When the branch was created
    """

    branch_name: str
    parent_branch: str
    task: str
    status: Literal["planning", "working", "ready_to_merge", "merged"] = "planning"
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def short_name(self) -> str:
        """Get the branch name without the 'deliberate/' prefix."""
        if self.branch_name.startswith(BRANCH_PREFIX):
            return self.branch_name[len(BRANCH_PREFIX) :]
        return self.branch_name


def slugify(text: str, max_length: int = 50) -> str:
    """Convert text to a URL-safe slug suitable for branch names.

    Args:
        text: Text to slugify
        max_length: Maximum length of the resulting slug

    Returns:
        Slugified string
    """
    # Convert to lowercase
    slug = text.lower()

    # Replace spaces and underscores with hyphens
    slug = re.sub(r"[\s_]+", "-", slug)

    # Remove any non-alphanumeric characters (except hyphens)
    slug = re.sub(r"[^a-z0-9-]", "", slug)

    # Remove consecutive hyphens
    slug = re.sub(r"-+", "-", slug)

    # Remove leading/trailing hyphens
    slug = slug.strip("-")

    # Truncate to max length
    if len(slug) > max_length:
        slug = slug[:max_length].rstrip("-")

    return slug or "task"


class BranchWorkflowManager:
    """Manages Git branch-based workflows for deliberate.

    This class handles:
    - Creating deliberate branches with PLAN.md files
    - Reading/writing plan content from/to branches
    - Tracking workflow state via Git
    - Merging completed work back to parent branches
    """

    def __init__(self, repo_root: Path):
        """Initialize the branch workflow manager.

        Args:
            repo_root: Path to the Git repository root
        """
        self.repo_root = repo_root.resolve()

    def _run_git(
        self,
        args: list[str],
        cwd: Path | None = None,
        check: bool = True,
    ) -> subprocess.CompletedProcess:
        """Run a git command.

        Args:
            args: Git command arguments (including 'git')
            cwd: Working directory. Defaults to repo_root.
            check: If True, raise RuntimeError on failure.

        Returns:
            CompletedProcess object
        """
        cwd = cwd or self.repo_root
        result = subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            text=True,
        )

        if check and result.returncode != 0:
            raise RuntimeError(f"Git command failed: {' '.join(args)}\n{result.stderr}")

        return result

    def get_current_branch(self) -> str:
        """Get the current Git branch name.

        Returns:
            Current branch name
        """
        result = self._run_git(["git", "rev-parse", "--abbrev-ref", "HEAD"])
        return result.stdout.strip()

    def get_default_branch(self) -> str:
        """Get the default branch name (main/master).

        Returns:
            Default branch name
        """
        # Try to get the default branch from remote
        result = self._run_git(
            ["git", "symbolic-ref", "refs/remotes/origin/HEAD"],
            check=False,
        )
        if result.returncode == 0:
            # refs/remotes/origin/main -> main
            return result.stdout.strip().split("/")[-1]

        # Fallback: check if main or master exists
        for branch in ["main", "master"]:
            result = self._run_git(
                ["git", "show-ref", "--verify", f"refs/heads/{branch}"],
                check=False,
            )
            if result.returncode == 0:
                return branch

        # Ultimate fallback
        return "main"

    def is_deliberate_branch(self, branch_name: str | None = None) -> bool:
        """Check if the given or current branch is a deliberate branch.

        Args:
            branch_name: Branch to check. Uses current branch if None.

        Returns:
            True if this is a deliberate branch
        """
        branch = branch_name or self.get_current_branch()
        return branch.startswith(BRANCH_PREFIX)

    def create_plan_branch(
        self,
        task: str,
        branch_name: str | None = None,
        base_ref: str | None = None,
        allow_existing: bool = False,
        worktree_root: Path | None = None,
    ) -> tuple[BranchWorkflow, Path | None]:
        """Create a new deliberate branch for a task and optional worktree.

        Args:
            task: The task description
            branch_name: Optional explicit branch name. Auto-generated if not provided.
            base_ref: Git ref to base the branch on. Defaults to current HEAD.
            allow_existing: If True, reuse and check out an existing branch.
            worktree_root: If provided, also create a git worktree at this root/branch-name.

        Returns:
            (BranchWorkflow, worktree_path or None)

        Raises:
            ValueError: If a branch with the given name already exists and cannot be reused
        """
        # Get parent branch before creating new one
        parent_branch = self.get_current_branch()

        # Generate branch name if not provided
        auto_generated = branch_name is None
        if not branch_name:
            slug = slugify(task)
            branch_name = f"{BRANCH_PREFIX}{slug}"

        # Ensure branch name has prefix
        if not branch_name.startswith(BRANCH_PREFIX):
            branch_name = f"{BRANCH_PREFIX}{branch_name}"

        def branch_exists(name: str) -> bool:
            result = self._run_git(
                ["git", "show-ref", "--verify", f"refs/heads/{name}"],
                check=False,
            )
            return result.returncode == 0

        if branch_exists(branch_name):
            if allow_existing:
                if worktree_root:
                    worktree_root.mkdir(parents=True, exist_ok=True)
                    safe_dirname = branch_name.replace("/", "__")
                    worktree_path = worktree_root / safe_dirname
                    if not worktree_path.exists():
                        self._run_git(["git", "worktree", "add", str(worktree_path), branch_name])
                    return BranchWorkflow(
                        branch_name=branch_name,
                        parent_branch=parent_branch,
                        task=task,
                        status="planning",
                    ), worktree_path
                else:
                    self._run_git(["git", "checkout", branch_name])
                    return BranchWorkflow(
                        branch_name=branch_name,
                        parent_branch=parent_branch,
                        task=task,
                        status="planning",
                    ), None
            if auto_generated:
                # Find a unique suffix
                idx = 2
                candidate = f"{branch_name}-{idx}"
                while branch_exists(candidate):
                    idx += 1
                    candidate = f"{branch_name}-{idx}"
                branch_name = candidate
            else:
                raise ValueError(f"Branch '{branch_name}' already exists")

        # Create and checkout the new branch
        base = base_ref or "HEAD"
        self._run_git(["git", "branch", branch_name, base])

        worktree_path = None
        if worktree_root:
            worktree_root.mkdir(parents=True, exist_ok=True)
            worktree_path = self.ensure_worktree(branch_name, worktree_root)
            # Ensure worktree root is ignored in main repo status
            exclude_file = self.repo_root / ".git" / "info" / "exclude"
            line = f"{worktree_root.relative_to(self.repo_root)}/\n"
            if not exclude_file.exists():
                exclude_file.parent.mkdir(parents=True, exist_ok=True)
                exclude_file.write_text(line)
            else:
                content = exclude_file.read_text()
                if line not in content:
                    exclude_file.write_text(content + line)

        return BranchWorkflow(
            branch_name=branch_name,
            parent_branch=parent_branch,
            task=task,
            status="planning",
        ), worktree_path

    def ensure_worktree(self, branch_name: str, worktree_root: Path) -> Path:
        """Ensure a worktree exists for a deliberate branch."""
        worktree_root.mkdir(parents=True, exist_ok=True)
        safe_dirname = branch_name.replace("/", "__")
        worktree_path = worktree_root / safe_dirname

        # Check if worktree already exists
        if not worktree_path.exists():
            self._run_git(["git", "worktree", "add", str(worktree_path), branch_name])

        return worktree_path

    def write_plan(self, plan_content: str, agent: str | None = None, worktree_path: Path | None = None) -> Path:
        """Write the plan content to PLAN.md and commit.

        Args:
            plan_content: The plan markdown content
            agent: Name of the agent that created the plan
            worktree_path: Optional worktree path where the branch is checked out

        Returns:
            Path to the created PLAN.md file
        """
        target_root = worktree_path or self.repo_root
        plan_path = target_root / PLAN_FILENAME

        # Build plan file with metadata header
        header = f"""# Implementation Plan

**Generated by:** {agent or "deliberate"}
**Created:** {datetime.now().isoformat()}

---

"""
        full_content = header + plan_content

        plan_path.write_text(full_content)

        # Stage and commit
        self._run_git(["git", "add", str(plan_path)], cwd=target_root)

        branch_result = self._run_git(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=target_root,
        )
        branch = branch_result.stdout.strip() or self.get_current_branch()
        short_name = branch[len(BRANCH_PREFIX) :] if branch.startswith(BRANCH_PREFIX) else branch

        self._run_git(
            [
                "git",
                "commit",
                "-m",
                f"docs: create execution plan for {short_name}",
            ],
            cwd=target_root,
        )

        return plan_path

    def read_plan(self) -> str | None:
        """Read the plan content from PLAN.md on current branch.

        Returns:
            Plan content, or None if PLAN.md doesn't exist
        """
        plan_path = self.repo_root / PLAN_FILENAME
        if not plan_path.exists():
            return None
        return plan_path.read_text()

    def has_plan(self) -> bool:
        """Check if the current branch has a PLAN.md file.

        Returns:
            True if PLAN.md exists
        """
        return (self.repo_root / PLAN_FILENAME).exists()

    def update_plan(self, plan_content: str, message: str | None = None) -> None:
        """Update the plan content and commit the changes.

        Args:
            plan_content: Updated plan markdown content
            message: Optional commit message. Auto-generated if not provided.
        """
        plan_path = self.repo_root / PLAN_FILENAME
        plan_path.write_text(plan_content)

        self._run_git(["git", "add", str(plan_path)])

        commit_msg = message or "docs: update execution plan"
        self._run_git(["git", "commit", "-m", commit_msg])

    def get_parent_branch(self) -> str | None:
        """Try to determine the parent branch of current deliberate branch.

        This uses git merge-base to find the common ancestor with likely parents.

        Returns:
            Parent branch name, or None if cannot be determined
        """
        current = self.get_current_branch()
        if not self.is_deliberate_branch(current):
            return None

        # Try common parent candidates
        default = self.get_default_branch()
        candidates = [default]
        if default != "main":
            candidates.append("main")
        if default != "master":
            candidates.append("master")

        for candidate in candidates:
            result = self._run_git(
                ["git", "show-ref", "--verify", f"refs/heads/{candidate}"],
                check=False,
            )
            if result.returncode == 0:
                return candidate

        return default

    def merge_to_parent(
        self,
        parent_branch: str | None = None,
        squash: bool = True,
        delete_branch: bool = True,
        source_branch: str | None = None,
    ) -> None:
        """Merge a deliberate branch back to parent.

        Args:
            parent_branch: Target branch to merge into. Auto-detected if None.
            squash: If True, squash all commits into one.
            delete_branch: If True, delete the deliberate branch after merge.
            source_branch: The deliberate branch to merge. If None, uses current branch.

        Raises:
            RuntimeError: If source_branch is not a deliberate branch or merge fails
        """
        current = source_branch or self.get_current_branch()
        if not self.is_deliberate_branch(current):
            raise RuntimeError(f"Not a deliberate branch: {current}")

        target = parent_branch or self.get_parent_branch() or self.get_default_branch()

        # Checkout parent branch
        self._run_git(["git", "checkout", target])

        # Dry-run merge to detect conflicts early
        dry_run = self._run_git(
            ["git", "merge", "--no-commit", "--no-ff", current],
            check=False,
        )
        if dry_run.returncode != 0:
            # Abort the dry-run merge to clean the index
            self._run_git(["git", "merge", "--abort"], check=False)
            raise RuntimeError(
                f"Merge would result in conflicts. Resolve on branch '{current}' or re-run after fixing."
            )
        # Abort the clean dry-run to reset state before the real merge
        self._run_git(["git", "merge", "--abort"], check=False)

        # Merge for real
        if squash:
            self._run_git(["git", "merge", "--squash", current])
            # Squash merge requires manual commit
            short_name = current[len(BRANCH_PREFIX) :]
            self._run_git(
                [
                    "git",
                    "commit",
                    "-m",
                    f"feat: {short_name}\n\nMerged from deliberate workflow branch.",
                ]
            )
        else:
            self._run_git(["git", "merge", "--no-edit", current])

        # Delete the deliberate branch
        if delete_branch:
            self._run_git(["git", "branch", "-D", current])

    def list_deliberate_branches(self) -> list[str]:
        """List all deliberate branches in the repository.

        Returns:
            List of branch names starting with 'deliberate/'
        """
        result = self._run_git(["git", "branch", "--list", f"{BRANCH_PREFIX}*"])
        branches = []
        for line in result.stdout.splitlines():
            # Remove leading markers (* for current, + for linked worktree) and whitespace
            branch = line.strip().lstrip("*+ ").strip()
            if branch:
                branches.append(branch)
        return branches

    def cleanup_plan(self) -> None:
        """Remove PLAN.md from working directory without deleting from Git history."""
        plan_path = self.repo_root / PLAN_FILENAME
        if plan_path.exists():
            plan_path.unlink()

    def abort(self) -> str:
        """Abort the current deliberate workflow.

        Returns to the parent branch without merging any changes.

        Returns:
            The branch that was switched to
        """
        current = self.get_current_branch()
        parent = self.get_parent_branch() or self.get_default_branch()

        if self.is_deliberate_branch(current):
            self._run_git(["git", "checkout", parent])
            # Optionally delete the branch
            self._run_git(["git", "branch", "-D", current], check=False)

        return parent
