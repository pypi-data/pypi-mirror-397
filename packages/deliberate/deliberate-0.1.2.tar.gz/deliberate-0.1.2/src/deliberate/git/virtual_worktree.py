"""Virtual worktree manager for fast unit testing.

This module provides an in-memory implementation of WorktreeManager
that doesn't require real git operations, making tests fast and
portable across platforms.
"""

import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator


@dataclass
class VirtualFile:
    """Represents a file in the virtual filesystem."""

    content: str = ""
    staged: bool = False


@dataclass
class VirtualWorktree:
    """Represents a virtual git worktree."""

    name: str
    path: Path
    ref: str
    created_at: float = field(default_factory=time.time)
    # In-memory file storage for the worktree
    files: dict[str, VirtualFile] = field(default_factory=dict)
    # Track commit history
    commits: list[tuple[str, str]] = field(default_factory=list)  # (hash, message)

    def write_file(self, path: str, content: str) -> None:
        """Write content to a file in this worktree."""
        self.files[path] = VirtualFile(content=content, staged=False)

    def read_file(self, path: str) -> str:
        """Read content from a file in this worktree."""
        if path not in self.files:
            raise FileNotFoundError(f"File not found: {path}")
        return self.files[path].content

    def stage_file(self, path: str) -> None:
        """Stage a file for commit."""
        if path in self.files:
            self.files[path].staged = True

    def stage_all(self) -> None:
        """Stage all modified files."""
        for file in self.files.values():
            file.staged = True

    def has_changes(self) -> bool:
        """Check if there are any uncommitted changes."""
        return any(f.staged or not f.staged for f in self.files.values() if f.content)


class VirtualWorktreeManager:
    """In-memory worktree manager for testing.

    Simulates git worktree operations without requiring a real git repository.
    Useful for:
    - Fast unit tests that don't need real git
    - Testing race conditions in parallel agent execution
    - Testing on systems without git installed
    - CI environments with restricted filesystem access
    """

    def __init__(
        self,
        repo_root: Path | None = None,
        worktree_root: Path | None = None,
    ):
        """Initialize the virtual worktree manager.

        Args:
            repo_root: Simulated repository root path.
            worktree_root: Simulated worktree root path.
        """
        self.repo_root = repo_root or Path("/virtual/repo")
        self.worktree_root = worktree_root or self.repo_root / ".deliberate" / "worktrees"
        self._active: dict[str, VirtualWorktree] = {}
        # Track files in the main repo
        self._repo_files: dict[str, str] = {"README.md": "# Virtual Repository\n"}

    def cleanup_stale(self, max_age_seconds: float = 86400) -> int:
        """Simulate cleanup of stale worktrees.

        In the virtual implementation, this removes worktrees older than
        the specified age from the in-memory store.

        Args:
            max_age_seconds: Maximum age in seconds before a worktree is considered stale.

        Returns:
            Number of worktrees removed.
        """
        now = time.time()
        stale_names = [name for name, wt in self._active.items() if now - wt.created_at > max_age_seconds]
        for name in stale_names:
            del self._active[name]
        return len(stale_names)

    def create(self, name: str | None = None, ref: str = "HEAD") -> VirtualWorktree:
        """Create a new virtual worktree.

        Args:
            name: Name for the worktree. Auto-generated if not provided.
            ref: Git ref to simulate basing the worktree on.

        Returns:
            VirtualWorktree object representing the created worktree.

        Raises:
            ValueError: If a worktree with the given name already exists.
        """
        name = name or f"jury-{uuid.uuid4().hex[:8]}"
        wt_path = self.worktree_root / name

        if name in self._active:
            raise ValueError(f"Worktree {name} already exists at {wt_path}")

        # Copy repo files to the new worktree
        worktree = VirtualWorktree(name=name, path=wt_path, ref=ref)
        for file_path, content in self._repo_files.items():
            worktree.files[file_path] = VirtualFile(content=content, staged=False)

        self._active[name] = worktree
        return worktree

    def remove(self, name: str, force: bool = False) -> None:
        """Remove a virtual worktree.

        Args:
            name: Name of the worktree to remove.
            force: If True, force removal (ignored in virtual implementation).
        """
        self._active.pop(name, None)

    def get_diff(self, worktree: VirtualWorktree) -> str:
        """Get the diff of changes in a virtual worktree.

        Args:
            worktree: The worktree to get the diff for.

        Returns:
            Simulated git diff as a string.
        """
        # Stage all changes first (mimics real behavior)
        worktree.stage_all()

        lines = []
        for file_path, file_obj in worktree.files.items():
            original = self._repo_files.get(file_path, "")
            if file_obj.content != original:
                lines.append(f"diff --git a/{file_path} b/{file_path}")
                if not original:
                    lines.append("new file mode 100644")
                lines.append(f"+++ b/{file_path}")
                for line in file_obj.content.splitlines():
                    lines.append(f"+{line}")
        return "\n".join(lines)

    def get_status(self, worktree: VirtualWorktree) -> str:
        """Get the status of a virtual worktree.

        Args:
            worktree: The worktree to get status for.

        Returns:
            Simulated git status output.
        """
        lines = []
        for file_path, file_obj in worktree.files.items():
            original = self._repo_files.get(file_path, "")
            if file_obj.content != original:
                status = "M " if original else "??"
                lines.append(f"{status} {file_path}")
        return "\n".join(lines)

    def commit_changes(
        self,
        worktree: VirtualWorktree,
        message: str,
        add_all: bool = True,
    ) -> str | None:
        """Commit changes in a virtual worktree.

        Args:
            worktree: The worktree to commit in.
            message: Commit message.
            add_all: If True, stage all changes before committing.

        Returns:
            Simulated commit hash, or None if there were no changes.
        """
        if add_all:
            worktree.stage_all()

        # Check if there are staged changes
        has_staged = any(f.staged for f in worktree.files.values())
        if not has_staged:
            return None

        # Generate a fake commit hash
        commit_hash = uuid.uuid4().hex[:8]
        worktree.commits.append((commit_hash, message))

        # Mark all files as committed (unstage them)
        for file_obj in worktree.files.values():
            file_obj.staged = False

        return commit_hash

    @contextmanager
    def temporary(self, name: str | None = None, ref: str = "HEAD") -> Iterator[VirtualWorktree]:
        """Create a temporary virtual worktree that is cleaned up automatically.

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
        """Remove all active worktrees."""
        self._active.clear()

    def list_worktrees(self) -> list[VirtualWorktree]:
        """List all active virtual worktrees.

        Returns:
            List of active VirtualWorktree objects.
        """
        return list(self._active.values())

    @property
    def active_count(self) -> int:
        """Get the number of active worktrees."""
        return len(self._active)

    # Test helper methods

    def add_repo_file(self, path: str, content: str) -> None:
        """Add a file to the virtual repository.

        This is useful for setting up test fixtures.

        Args:
            path: File path relative to repo root.
            content: File content.
        """
        self._repo_files[path] = content

    def get_worktree(self, name: str) -> VirtualWorktree | None:
        """Get a worktree by name.

        Args:
            name: Name of the worktree.

        Returns:
            The worktree, or None if not found.
        """
        return self._active.get(name)

    def get_head_sha(self, worktree: VirtualWorktree) -> str:
        """Get the current HEAD SHA of the worktree.

        Args:
            worktree: The worktree to get HEAD SHA for.

        Returns:
            The full commit SHA.
        """
        if worktree.commits:
            return worktree.commits[-1][0]
        # Return a mock SHA if no commits yet
        return "0000000000000000000000000000000000000000"
