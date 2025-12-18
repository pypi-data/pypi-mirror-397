"""Tests for the VirtualWorktreeManager.

Verifies that the virtual implementation matches the behavior
of the real WorktreeManager for use in unit tests.
"""

import pytest

from deliberate.git.virtual_worktree import VirtualWorktreeManager


class TestVirtualWorktreeCreate:
    """Tests for worktree creation."""

    def test_create_worktree(self) -> None:
        """Creates a virtual worktree."""
        mgr = VirtualWorktreeManager()
        worktree = mgr.create("test-wt")

        assert worktree.name == "test-wt"
        assert worktree.path == mgr.worktree_root / "test-wt"
        assert mgr.active_count == 1

    def test_create_auto_name(self) -> None:
        """Auto-generates name if not provided."""
        mgr = VirtualWorktreeManager()
        worktree = mgr.create()

        assert worktree.name.startswith("jury-")
        assert len(worktree.name) == 13  # "jury-" + 8 hex chars

    def test_create_duplicate_fails(self) -> None:
        """Fails when creating duplicate worktree."""
        mgr = VirtualWorktreeManager()
        mgr.create("test-wt")

        with pytest.raises(ValueError, match="already exists"):
            mgr.create("test-wt")

    def test_create_copies_repo_files(self) -> None:
        """New worktree gets copies of repo files."""
        mgr = VirtualWorktreeManager()
        mgr.add_repo_file("src/main.py", "print('hello')")

        worktree = mgr.create("test-wt")

        assert "README.md" in worktree.files
        assert "src/main.py" in worktree.files
        assert worktree.read_file("src/main.py") == "print('hello')"


class TestVirtualWorktreeRemove:
    """Tests for worktree removal."""

    def test_remove_worktree(self) -> None:
        """Removes a virtual worktree."""
        mgr = VirtualWorktreeManager()
        mgr.create("test-wt")

        mgr.remove("test-wt")

        assert mgr.active_count == 0
        assert mgr.get_worktree("test-wt") is None

    def test_remove_nonexistent(self) -> None:
        """Handles removing nonexistent worktree gracefully."""
        mgr = VirtualWorktreeManager()
        mgr.remove("nonexistent")  # Should not raise


class TestVirtualWorktreeDiff:
    """Tests for diff generation."""

    def test_get_diff_new_file(self) -> None:
        """Diff shows new files."""
        mgr = VirtualWorktreeManager()
        worktree = mgr.create("test-wt")

        worktree.write_file("new_file.txt", "Hello\n")
        diff = mgr.get_diff(worktree)

        assert "new_file.txt" in diff
        assert "+Hello" in diff

    def test_get_diff_modified_file(self) -> None:
        """Diff shows modified files."""
        mgr = VirtualWorktreeManager()
        mgr.add_repo_file("existing.txt", "Original content")
        worktree = mgr.create("test-wt")

        worktree.write_file("existing.txt", "Modified content")
        diff = mgr.get_diff(worktree)

        assert "existing.txt" in diff
        assert "+Modified content" in diff

    def test_get_diff_no_changes(self) -> None:
        """Empty diff when no changes."""
        mgr = VirtualWorktreeManager()
        worktree = mgr.create("test-wt")

        diff = mgr.get_diff(worktree)
        assert diff == ""


class TestVirtualWorktreeStatus:
    """Tests for status reporting."""

    def test_get_status_new_file(self) -> None:
        """Status shows new untracked files."""
        mgr = VirtualWorktreeManager()
        worktree = mgr.create("test-wt")

        worktree.write_file("new_file.txt", "Hello")
        status = mgr.get_status(worktree)

        assert "new_file.txt" in status
        assert "??" in status

    def test_get_status_modified_file(self) -> None:
        """Status shows modified files."""
        mgr = VirtualWorktreeManager()
        mgr.add_repo_file("existing.txt", "Original")
        worktree = mgr.create("test-wt")

        worktree.write_file("existing.txt", "Modified")
        status = mgr.get_status(worktree)

        assert "existing.txt" in status
        assert "M " in status

    def test_get_status_no_changes(self) -> None:
        """Empty status when no changes."""
        mgr = VirtualWorktreeManager()
        worktree = mgr.create("test-wt")

        status = mgr.get_status(worktree)
        assert status == ""


class TestVirtualWorktreeCommit:
    """Tests for commit functionality."""

    def test_commit_changes(self) -> None:
        """Commits staged changes."""
        mgr = VirtualWorktreeManager()
        worktree = mgr.create("test-wt")

        worktree.write_file("new_file.txt", "Hello")
        commit_hash = mgr.commit_changes(worktree, "Add new file")

        assert commit_hash is not None
        assert len(commit_hash) == 8  # Hex hash
        assert len(worktree.commits) == 1
        assert worktree.commits[0][1] == "Add new file"

    def test_commit_no_changes(self) -> None:
        """Returns None when nothing to commit."""
        mgr = VirtualWorktreeManager()
        worktree = mgr.create("test-wt")

        # Clear the default files to simulate no changes
        worktree.files.clear()

        commit_hash = mgr.commit_changes(worktree, "Empty commit")
        assert commit_hash is None


class TestVirtualWorktreeTemporary:
    """Tests for temporary context manager."""

    def test_temporary_cleanup(self) -> None:
        """Cleans up worktree after context."""
        mgr = VirtualWorktreeManager()

        with mgr.temporary("test-wt") as worktree:
            assert worktree.name == "test-wt"
            assert mgr.active_count == 1

        assert mgr.active_count == 0

    def test_temporary_cleanup_on_exception(self) -> None:
        """Cleans up even when exception occurs."""
        mgr = VirtualWorktreeManager()

        with pytest.raises(RuntimeError):
            with mgr.temporary("test-wt"):
                raise RuntimeError("Test error")

        assert mgr.active_count == 0


class TestVirtualWorktreeList:
    """Tests for listing worktrees."""

    def test_list_worktrees(self) -> None:
        """Lists all active worktrees."""
        mgr = VirtualWorktreeManager()
        mgr.create("wt1")
        mgr.create("wt2")

        worktrees = mgr.list_worktrees()
        names = [wt.name for wt in worktrees]

        assert "wt1" in names
        assert "wt2" in names
        assert len(worktrees) == 2

    def test_active_count(self) -> None:
        """Tracks active worktree count."""
        mgr = VirtualWorktreeManager()

        assert mgr.active_count == 0

        mgr.create("wt1")
        assert mgr.active_count == 1

        mgr.create("wt2")
        assert mgr.active_count == 2

        mgr.remove("wt1")
        assert mgr.active_count == 1


class TestVirtualWorktreeCleanup:
    """Tests for cleanup functionality."""

    def test_cleanup_all(self) -> None:
        """Removes all worktrees."""
        mgr = VirtualWorktreeManager()
        mgr.create("wt1")
        mgr.create("wt2")

        mgr.cleanup_all()

        assert mgr.active_count == 0

    def test_cleanup_stale(self) -> None:
        """Removes worktrees older than specified age."""
        import time

        mgr = VirtualWorktreeManager()
        wt = mgr.create("old-wt")
        # Manually set creation time to 2 days ago
        wt.created_at = time.time() - (48 * 3600)

        removed = mgr.cleanup_stale(max_age_seconds=24 * 3600)

        assert removed == 1
        assert mgr.active_count == 0


class TestVirtualWorktreeParallelism:
    """Tests for parallel execution scenarios."""

    def test_multiple_worktrees_isolated(self) -> None:
        """Changes in one worktree don't affect others."""
        mgr = VirtualWorktreeManager()
        wt1 = mgr.create("wt1")
        wt2 = mgr.create("wt2")

        wt1.write_file("file1.txt", "Content 1")
        wt2.write_file("file2.txt", "Content 2")

        assert "file1.txt" in wt1.files
        assert "file1.txt" not in wt2.files
        assert "file2.txt" in wt2.files
        assert "file2.txt" not in wt1.files

    def test_concurrent_create_unique_names(self) -> None:
        """Auto-generated names are unique."""
        mgr = VirtualWorktreeManager()

        # Create many worktrees with auto names
        worktrees = [mgr.create() for _ in range(100)]
        names = [wt.name for wt in worktrees]

        # All names should be unique
        assert len(set(names)) == 100


class TestVirtualWorktreeFile:
    """Tests for file operations in worktrees."""

    def test_write_and_read_file(self) -> None:
        """Can write and read files."""
        mgr = VirtualWorktreeManager()
        worktree = mgr.create("test-wt")

        worktree.write_file("src/module.py", "def hello(): pass")
        content = worktree.read_file("src/module.py")

        assert content == "def hello(): pass"

    def test_read_nonexistent_file(self) -> None:
        """Raises error when reading nonexistent file."""
        mgr = VirtualWorktreeManager()
        worktree = mgr.create("test-wt")

        with pytest.raises(FileNotFoundError):
            worktree.read_file("nonexistent.txt")

    def test_stage_file(self) -> None:
        """Can stage individual files."""
        mgr = VirtualWorktreeManager()
        worktree = mgr.create("test-wt")

        worktree.write_file("file1.txt", "Content 1")
        worktree.write_file("file2.txt", "Content 2")
        worktree.stage_file("file1.txt")

        assert worktree.files["file1.txt"].staged is True
        assert worktree.files["file2.txt"].staged is False

    def test_stage_all(self) -> None:
        """Can stage all files at once."""
        mgr = VirtualWorktreeManager()
        worktree = mgr.create("test-wt")

        worktree.write_file("file1.txt", "Content 1")
        worktree.write_file("file2.txt", "Content 2")
        worktree.stage_all()

        assert worktree.files["file1.txt"].staged is True
        assert worktree.files["file2.txt"].staged is True
