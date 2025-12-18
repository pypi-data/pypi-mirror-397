"""Git worktree management for isolated agent execution."""

import logging
import os
import shutil
import subprocess
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator


def get_actual_repo_root(path: Path) -> Path:
    """Get the actual git repo root, handling worktrees.

    When running inside a worktree, the .git is a file containing
    'gitdir: /path/to/main/.git/worktrees/name'. This function
    resolves back to the main repository root.

    Args:
        path: Path to start searching from.

    Returns:
        The resolved path to the main git repository root.
    """
    path = path.resolve()
    git_meta = path / ".git"

    if git_meta.is_file():
        # In a worktree - read the gitdir pointer
        try:
            content = git_meta.read_text().strip()
            if content.startswith("gitdir:"):
                gitdir = Path(content.split(":", 1)[1].strip())
                # Navigate from .git/worktrees/xxx to repo root
                # gitdir is like /repo/.git/worktrees/name
                if "worktrees" in gitdir.parts:
                    idx = gitdir.parts.index("worktrees")
                    # Parts before "worktrees" minus the ".git" at end
                    return Path(*gitdir.parts[: idx - 1]).resolve()
        except Exception:
            logging.debug("Failed to parse worktree gitdir", exc_info=True)
    elif git_meta.is_dir():
        # Normal repo root
        return path

    # Walk up to find .git
    for parent in path.parents:
        if (parent / ".git").exists():
            return get_actual_repo_root(parent)

    # Fallback to original path
    return path


@dataclass
class Worktree:
    """Represents a git worktree."""

    name: str
    path: Path
    ref: str
    created_at: float = field(default_factory=time.time)


class WorktreeManager:
    """Manages git worktrees for isolated agent execution.

    Each agent gets its own worktree to prevent conflicts when
    multiple agents are working on the same codebase.
    """

    def __init__(
        self,
        repo_root: Path,
        worktree_root: Path | None = None,
    ):
        """Initialize the worktree manager.

        Args:
            repo_root: Path to the main git repository.
            worktree_root: Path where worktrees will be created.
                          Defaults to <repo_root>/.deliberate/worktrees
        """
        self.repo_root = repo_root.resolve()
        configured_root = worktree_root
        env_root = os.environ.get("DELIBERATE_WORKTREE_ROOT")

        root_path = (
            Path(env_root).expanduser()
            if env_root
            else configured_root
            if configured_root
            else (repo_root / ".deliberate" / "worktrees")
        )

        self.worktree_root = root_path.resolve()
        self._active: dict[str, Worktree] = {}

        # Ensure worktree artifacts don't show up in git status
        self._ensure_git_ignore()

        # Auto-clean stale worktrees older than 24 hours
        self.cleanup_stale(max_age_seconds=24 * 3600)

    def scan_existing(self) -> list[Worktree]:
        """Scan and load existing worktrees from disk.

        This is useful when resuming a workflow in a new process where
        the in-memory _active dict is empty but worktrees exist on disk.

        Returns:
            List of Worktree objects found on disk.
        """
        if not self.worktree_root.exists():
            return []

        # Query git for all worktrees it knows about
        worktree_paths: dict[Path, str] = {}  # path -> branch/ref
        try:
            result = self._run_git(["git", "worktree", "list", "--porcelain"])
            if result.returncode == 0:
                current_path = None
                for line in result.stdout.splitlines():
                    if line.startswith("worktree "):
                        current_path = Path(line.split(" ", 1)[1]).resolve()
                    elif line.startswith("branch ") and current_path:
                        worktree_paths[current_path] = line.split(" ", 1)[1]
                    elif line.startswith("HEAD ") and current_path and current_path not in worktree_paths:
                        # Detached HEAD - use the SHA
                        worktree_paths[current_path] = line.split(" ", 1)[1][:8]
        except Exception:
            logging.debug("git worktree list failed during scan", exc_info=True)

        found = []
        for item in self.worktree_root.iterdir():
            if not item.is_dir():
                continue

            name = item.name
            path = item.resolve()

            # Skip if already tracked
            if name in self._active:
                found.append(self._active[name])
                continue

            # Get ref from git's worktree list or fall back to "unknown"
            ref = worktree_paths.get(path, "HEAD")

            worktree = Worktree(name=name, path=path, ref=ref)
            self._active[name] = worktree
            found.append(worktree)

        return found

    def _run_git(
        self,
        args: list[str],
        cwd: Path | None = None,
        check: bool = False,
    ) -> subprocess.CompletedProcess:
        """Run a git command with retry logic for lock contention.

        Args:
            args: Git command arguments (including 'git').
            cwd: Working directory. Defaults to repo_root.
            check: If True, raise RuntimeError on failure.

        Returns:
            CompletedProcess object.
        """
        cwd = cwd or self.repo_root
        max_retries = 10  # Increased retries for high contention
        delay = 0.1

        last_result = None

        for attempt in range(max_retries + 1):
            try:
                # Always capture output for checking lock messages
                result = subprocess.run(
                    args,
                    cwd=cwd,
                    capture_output=True,
                    text=True,
                )
                last_result = result

                if result.returncode == 0:
                    return result

                # Check for lock errors
                stderr = result.stderr.lower()
                is_lock_error = (
                    "lock" in stderr
                    or "file exists" in stderr
                    or "another git process" in stderr
                    or "unable to create" in stderr
                    or "index.lock" in stderr
                )

                if is_lock_error:
                    if attempt < max_retries:
                        logging.debug(
                            "Git lock contention on '%s' (attempt %d/%d), retrying in %.2fs...",
                            " ".join(args),
                            attempt + 1,
                            max_retries,
                            delay,
                        )
                        time.sleep(delay)
                        delay = min(delay * 2, 2.0)  # Cap delay at 2s
                        continue

                # If not a lock error, break immediately
                break

            except Exception:
                # OS errors
                if attempt < max_retries:
                    time.sleep(delay)
                    delay *= 2
                    continue
                raise

        if last_result is None:
            raise RuntimeError(f"Git command failed to execute: {' '.join(args)}")

        if check and last_result.returncode != 0:
            raise RuntimeError(f"Git command failed: {' '.join(args)}\n{last_result.stderr}")

        return last_result

    def cleanup_stale(self, max_age_seconds: float = 86400) -> int:
        """Clean up stale worktrees from previous runs.

        Args:
            max_age_seconds: Maximum age in seconds before a worktree is considered stale.

        Returns:
            Number of worktrees removed.
        """
        if not self.worktree_root.exists():
            return 0

        # First, let git prune its own metadata to avoid dangling refs
        try:
            self._run_git(["git", "worktree", "prune"])
        except Exception:
            logging.debug("git worktree prune failed during cleanup", exc_info=True)

        # Track worktrees Git still knows about to avoid removing active ones
        tracked_paths: set[Path] = set()
        try:
            listed = self._run_git(["git", "worktree", "list", "--porcelain"])
            if listed.returncode == 0:
                for line in listed.stdout.splitlines():
                    if line.startswith("worktree "):
                        _, path_str = line.split(" ", 1)
                        tracked_paths.add(Path(path_str).resolve())
        except Exception:
            logging.debug("git worktree list failed during cleanup", exc_info=True)

        count = 0
        now = time.time()

        for item in self.worktree_root.iterdir():
            if not item.is_dir():
                continue

            # Check if it's stale
            try:
                mtime = item.stat().st_mtime
                name = item.name

                # Skip worktrees git still considers active
                if item.resolve() in tracked_paths:
                    continue

                # Skip active worktrees (init runs before any create, but be defensive)
                if name in self._active:
                    continue

                if now - mtime > max_age_seconds:
                    self.remove(name, force=True)
                    count += 1
            except Exception:
                logging.warning("Failed cleaning stale worktree %s", item, exc_info=True)

        return count

    def _ensure_git_ignore(self) -> None:
        """Add .deliberate paths to git's local exclude file."""
        git_meta = self.repo_root / ".git"

        if git_meta.is_dir():
            git_dir = git_meta
        elif git_meta.is_file():
            try:
                content = git_meta.read_text().strip()
                if content.startswith("gitdir:"):
                    git_dir = (git_meta.parent / content.split(":", 1)[1].strip()).resolve()
                else:
                    return
            except Exception:
                return
        else:
            return

        exclude_path = git_dir / "info" / "exclude"
        exclude_path.parent.mkdir(parents=True, exist_ok=True)

        existing = exclude_path.read_text() if exclude_path.exists() else ""
        patterns = [".deliberate/", ".deliberate/worktrees/"]

        missing = [p for p in patterns if p not in existing.splitlines()]
        if not missing:
            return

        with exclude_path.open("a") as fh:
            if existing and not existing.endswith("\n"):
                fh.write("\n")
            fh.write("# Added by deliberate to hide worktree artifacts\n")
            for pattern in missing:
                fh.write(f"{pattern}\n")

    def create(self, name: str | None = None, ref: str = "HEAD") -> Worktree:
        """Create a new worktree.

        Args:
            name: Name for the worktree. Auto-generated if not provided.
            ref: Git ref to base the worktree on.

        Returns:
            Worktree object representing the created worktree.

        Raises:
            ValueError: If a worktree with the given name already exists.
            RuntimeError: If worktree creation fails.
        """
        name = name or f"jury-{uuid.uuid4().hex[:8]}"
        wt_path = self.worktree_root / name

        if wt_path.exists():
            raise ValueError(f"Worktree {name} already exists at {wt_path}")

        # Ensure worktree root exists
        self.worktree_root.mkdir(parents=True, exist_ok=True)

        # Create detached worktree
        self._run_git(["git", "worktree", "add", "--detach", str(wt_path), ref], check=True)

        try:
            (wt_path / ".owner_pid").write_text(str(os.getpid()))
        except Exception:
            logging.debug("Failed to record owner PID for worktree %s", wt_path, exc_info=True)

        worktree = Worktree(name=name, path=wt_path, ref=ref)
        self._active[name] = worktree
        return worktree

    def remove(self, name: str, force: bool = False) -> None:
        """Remove a worktree.

        Args:
            name: Name of the worktree to remove.
            force: If True, force removal even if there are uncommitted changes.
        """
        wt_path = self.worktree_root / name

        if not wt_path.exists():
            self._active.pop(name, None)
            return

        cmd = ["git", "worktree", "remove"]
        if force:
            cmd.append("--force")
        cmd.append(str(wt_path))

        result = self._run_git(cmd)

        # If removal failed and force is requested, try manual cleanup
        if result.returncode != 0 and force:
            shutil.rmtree(wt_path, ignore_errors=True)
            self._run_git(["git", "worktree", "prune"])

        self._active.pop(name, None)

    # Common paths to exclude from diffs (build artifacts, dependencies, etc.)
    # Use glob patterns that git pathspec understands (no magic chars in names)
    DIFF_EXCLUDE_PATTERNS = [
        "node_modules",
        ".venv",
        "**/[_][_]pycache[_][_]",  # Match __pycache__ using glob escaping
        ".pytest_cache",
        "target",  # Rust
        "dist",
        "build",
        "*.pyc",
        "*.pyo",
        "package-lock.json",
        "yarn.lock",
        "Cargo.lock",
        ".DS_Store",
    ]

    def get_diff(self, worktree: Worktree, exclude_patterns: list[str] | None = None) -> str:
        """Get the diff of changes in a worktree.

        Args:
            worktree: The worktree to get the diff for.
            exclude_patterns: Additional patterns to exclude from diff.

        Returns:
            The git diff as a string.
        """
        # Stage all changes including untracked files to capture them in diff
        self._run_git(["git", "add", "-A"], cwd=worktree.path)

        # Build git diff command with exclusions using pathspec
        # Use :(exclude)pattern syntax which is clearer
        diff_cmd = ["git", "diff", "--cached", "HEAD"]

        # Add exclusions if any
        all_excludes = list(self.DIFF_EXCLUDE_PATTERNS)
        if exclude_patterns:
            all_excludes.extend(exclude_patterns)

        if all_excludes:
            diff_cmd.append("--")
            diff_cmd.append(".")  # Include all files first
            for pattern in all_excludes:
                # Use :(exclude) pathspec format for exclusions
                diff_cmd.append(f":(exclude){pattern}")

        result = self._run_git(diff_cmd, cwd=worktree.path)
        return result.stdout

    def get_status(self, worktree: Worktree) -> str:
        """Get the status of a worktree.

        Args:
            worktree: The worktree to get status for.

        Returns:
            The git status output.
        """
        result = self._run_git(["git", "status", "--porcelain"], cwd=worktree.path)
        return result.stdout

    def commit_changes(
        self,
        worktree: Worktree,
        message: str,
        add_all: bool = True,
    ) -> str | None:
        """Commit changes in a worktree.

        Args:
            worktree: The worktree to commit in.
            message: Commit message.
            add_all: If True, add all changes before committing.

        Returns:
            The commit hash, or None if there were no changes.
        """
        if add_all:
            self._run_git(["git", "add", "-A"], cwd=worktree.path)

        # Check if there are changes to commit
        status = self.get_status(worktree)
        if not status.strip():
            return None

        result = self._run_git(
            ["git", "commit", "-m", message],
            cwd=worktree.path,
        )

        if result.returncode != 0:
            return None

        # Get the commit hash
        hash_result = self._run_git(
            ["git", "rev-parse", "HEAD"],
            cwd=worktree.path,
        )
        return hash_result.stdout.strip()

    @contextmanager
    def temporary(self, name: str | None = None, ref: str = "HEAD") -> Iterator[Worktree]:
        """Create a temporary worktree that is cleaned up automatically.

        Args:
            name: Name for the worktree. Auto-generated if not provided.
            ref: Git ref to base the worktree on.

        Yields:
            The created worktree.
        """
        worktree = self.create(name=name, ref=ref)
        try:
            yield worktree
        finally:
            self.remove(worktree.name, force=True)

    def cleanup_all(self) -> None:
        """Remove all active worktrees managed by this instance."""
        for name in list(self._active.keys()):
            self.remove(name, force=True)

        # Prune any stale worktree references
        self._run_git(["git", "worktree", "prune"])

    def list_worktrees(self) -> list[Worktree]:
        """List all active worktrees.

        Returns:
            List of active Worktree objects.
        """
        return list(self._active.values())

    def get_worktree(self, name: str) -> Worktree | None:
        """Get a worktree by name.

        Args:
            name: Name of the worktree.

        Returns:
            The worktree, or None if not found.
        """
        return self._active.get(name)

    def get_head_sha(self, worktree: Worktree) -> str:
        """Get the current HEAD SHA of the worktree.

        Args:
            worktree: The worktree to get HEAD SHA for.

        Returns:
            The full commit SHA.
        """
        result = self._run_git(["git", "rev-parse", "HEAD"], cwd=worktree.path, check=True)
        return result.stdout.strip()

    @property
    def active_count(self) -> int:
        """Get the number of active worktrees."""
        return len(self._active)

    def is_repo_dirty(self) -> bool:
        """Check if the main repository has uncommitted changes.

        Returns:
            True if there are modified or untracked files (excluding ignored).
        """
        result = self._run_git(
            ["git", "status", "--porcelain"],
            cwd=self.repo_root,
        )
        return bool(result.stdout.strip())
