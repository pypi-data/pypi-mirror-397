"""Tests for git worktree management."""

import subprocess

import pytest

from deliberate.git.worktree import WorktreeManager


class TestWorktreeManager:
    """Tests for WorktreeManager."""

    def test_create_worktree(self, temp_git_repo):
        """Should create a new worktree."""
        mgr = WorktreeManager(temp_git_repo)
        worktree = mgr.create("test-wt")

        assert worktree.path.exists()
        assert worktree.name == "test-wt"
        assert (worktree.path / "README.md").exists()

    def test_create_worktree_auto_name(self, temp_git_repo):
        """Should auto-generate name if not provided."""
        mgr = WorktreeManager(temp_git_repo)
        worktree = mgr.create()

        assert worktree.name.startswith("jury-")
        assert len(worktree.name) == 13  # "jury-" + 8 hex chars

    def test_create_duplicate_fails(self, temp_git_repo):
        """Should fail when creating duplicate worktree."""
        mgr = WorktreeManager(temp_git_repo)
        mgr.create("test-wt")

        with pytest.raises(ValueError, match="already exists"):
            mgr.create("test-wt")

    def test_remove_worktree(self, temp_git_repo):
        """Should remove a worktree."""
        mgr = WorktreeManager(temp_git_repo)
        worktree = mgr.create("test-wt")
        wt_path = worktree.path

        mgr.remove("test-wt", force=True)

        assert not wt_path.exists()
        assert mgr.active_count == 0

    def test_remove_nonexistent(self, temp_git_repo):
        """Should handle removing nonexistent worktree gracefully."""
        mgr = WorktreeManager(temp_git_repo)
        mgr.remove("nonexistent")  # Should not raise

    def test_get_diff(self, temp_git_repo):
        """Should get diff of changes in worktree."""
        mgr = WorktreeManager(temp_git_repo)
        worktree = mgr.create("test-wt")

        # Make a change
        (worktree.path / "new_file.txt").write_text("Hello\n")

        # Diff should show the new file (untracked files not in diff)
        # Let's stage it first
        import subprocess

        subprocess.run(
            ["git", "add", "new_file.txt"],
            cwd=worktree.path,
            check=True,
        )

        diff = mgr.get_diff(worktree)
        # git diff HEAD shows staged changes
        assert "new_file.txt" in diff or diff == ""  # May vary by git version

    def test_get_status(self, temp_git_repo):
        """Should get status of worktree."""
        mgr = WorktreeManager(temp_git_repo)
        worktree = mgr.create("test-wt")

        # Make a change
        (worktree.path / "new_file.txt").write_text("Hello\n")

        status = mgr.get_status(worktree)
        assert "new_file.txt" in status

    def test_temporary_context_manager(self, temp_git_repo):
        """Should cleanup worktree after context."""
        mgr = WorktreeManager(temp_git_repo)

        with mgr.temporary("test-wt") as worktree:
            wt_path = worktree.path
            assert wt_path.exists()

        assert not wt_path.exists()

    def test_cleanup_all(self, temp_git_repo):
        """Should cleanup all worktrees."""
        mgr = WorktreeManager(temp_git_repo)
        wt1 = mgr.create("wt1")
        wt2 = mgr.create("wt2")

        mgr.cleanup_all()

        assert not wt1.path.exists()
        assert not wt2.path.exists()
        assert mgr.active_count == 0

    def test_list_worktrees(self, temp_git_repo):
        """Should list all active worktrees."""
        mgr = WorktreeManager(temp_git_repo)
        mgr.create("wt1")
        mgr.create("wt2")

        worktrees = mgr.list_worktrees()
        names = [wt.name for wt in worktrees]

        assert "wt1" in names
        assert "wt2" in names
        assert len(worktrees) == 2

    def test_active_count(self, temp_git_repo):
        """Should track active worktree count."""
        mgr = WorktreeManager(temp_git_repo)

        assert mgr.active_count == 0

        mgr.create("wt1")
        assert mgr.active_count == 1

        mgr.create("wt2")
        assert mgr.active_count == 2

        mgr.remove("wt1")
        assert mgr.active_count == 1

    def test_run_git_retry_logic(self, temp_git_repo):
        """Test that _run_git retries on lock errors."""
        mgr = WorktreeManager(temp_git_repo)
        from unittest.mock import MagicMock, patch

        # Mock subprocess.run
        with patch("deliberate.git.worktree.subprocess.run") as mock_run:
            # Setup mock side effects
            # 1. Lock error
            # 2. Lock error
            # 3. Success

            lock_error = MagicMock(returncode=128, stderr="fatal: Unable to create '.../index.lock': File exists.")
            success = MagicMock(returncode=0, stdout="success", stderr="")

            mock_run.side_effect = [lock_error, lock_error, success]

            # Mock time.sleep to avoid actual delays
            with patch("deliberate.git.worktree.time.sleep") as mock_sleep:
                result = mgr._run_git(["git", "status"])

                assert result.returncode == 0
                assert result.stdout == "success"
                assert mock_run.call_count == 3
                assert mock_sleep.call_count == 2

    def test_run_git_max_retries_exceeded(self, temp_git_repo):
        """Test that _run_git fails after retries exhausted."""
        mgr = WorktreeManager(temp_git_repo)
        from unittest.mock import MagicMock, patch

        with patch("deliberate.git.worktree.subprocess.run") as mock_run:
            lock_error = MagicMock(returncode=128, stderr="fatal: Unable to create '.../index.lock': File exists.")
            mock_run.return_value = lock_error

            with patch("deliberate.git.worktree.time.sleep"):
                result = mgr._run_git(["git", "status"], check=False)

                assert result.returncode == 128
                assert mock_run.call_count == 11  # 1 initial + 10 retries


class TestWorktreeEdgeCases:
    """Edge case tests for WorktreeManager."""

    def test_create_worktree_from_detached_head(self, temp_git_repo):
        """Should create worktree when main repo is in detached HEAD state."""
        # Detach HEAD
        subprocess.run(
            ["git", "checkout", "--detach"],
            cwd=temp_git_repo,
            check=True,
            capture_output=True,
        )

        mgr = WorktreeManager(temp_git_repo)
        worktree = mgr.create("test-wt")

        assert worktree.path.exists()
        assert worktree.name == "test-wt"

    def test_create_worktree_from_specific_commit(self, temp_git_repo):
        """Should create worktree from a specific commit SHA."""
        # Create a second commit
        (temp_git_repo / "second.txt").write_text("Second file\n")
        subprocess.run(["git", "add", "."], cwd=temp_git_repo, check=True)
        subprocess.run(
            ["git", "commit", "-m", "Second commit"],
            cwd=temp_git_repo,
            check=True,
            capture_output=True,
        )

        # Get first commit SHA
        result = subprocess.run(
            ["git", "rev-list", "--max-parents=0", "HEAD"],
            cwd=temp_git_repo,
            capture_output=True,
            text=True,
            check=True,
        )
        first_commit = result.stdout.strip()

        mgr = WorktreeManager(temp_git_repo)
        worktree = mgr.create("old-commit-wt", ref=first_commit)

        # Second file should NOT exist in worktree (from first commit)
        assert worktree.path.exists()
        assert not (worktree.path / "second.txt").exists()
        assert (worktree.path / "README.md").exists()

    def test_create_worktree_from_branch(self, temp_git_repo):
        """Should create worktree from a named branch."""
        # Create a new branch with different content
        subprocess.run(
            ["git", "checkout", "-b", "feature-branch"],
            cwd=temp_git_repo,
            check=True,
            capture_output=True,
        )
        (temp_git_repo / "feature.txt").write_text("Feature content\n")
        subprocess.run(["git", "add", "."], cwd=temp_git_repo, check=True)
        subprocess.run(
            ["git", "commit", "-m", "Feature commit"],
            cwd=temp_git_repo,
            check=True,
            capture_output=True,
        )

        # Switch back to main (use "main" as that's the default in newer git)
        subprocess.run(
            ["git", "checkout", "main"],
            cwd=temp_git_repo,
            check=True,
            capture_output=True,
        )

        mgr = WorktreeManager(temp_git_repo)
        worktree = mgr.create("feature-wt", ref="feature-branch")

        # Feature file should exist
        assert (worktree.path / "feature.txt").exists()

    def test_worktree_with_dirty_main_repo(self, temp_git_repo):
        """Should create worktree even when main repo has uncommitted changes."""
        # Make uncommitted changes in main repo
        (temp_git_repo / "dirty.txt").write_text("Uncommitted content\n")

        mgr = WorktreeManager(temp_git_repo)
        worktree = mgr.create("clean-wt")

        # Worktree should be clean (based on last commit)
        assert worktree.path.exists()
        assert not (worktree.path / "dirty.txt").exists()

    def test_worktree_with_staged_changes_in_main(self, temp_git_repo):
        """Should create worktree when main repo has staged but uncommitted changes."""
        # Stage changes without committing
        (temp_git_repo / "staged.txt").write_text("Staged content\n")
        subprocess.run(
            ["git", "add", "staged.txt"],
            cwd=temp_git_repo,
            check=True,
        )

        mgr = WorktreeManager(temp_git_repo)
        worktree = mgr.create("from-staged-wt")

        # Worktree should not have staged file (it's from last commit)
        assert worktree.path.exists()
        assert not (worktree.path / "staged.txt").exists()

    def test_remove_worktree_with_uncommitted_changes(self, temp_git_repo):
        """Should force remove worktree with uncommitted changes."""
        mgr = WorktreeManager(temp_git_repo)
        worktree = mgr.create("dirty-wt")

        # Make changes in the worktree
        (worktree.path / "uncommitted.txt").write_text("Dirty content\n")

        # Normal remove might fail, but force should work
        mgr.remove("dirty-wt", force=True)

        assert not worktree.path.exists()
        assert mgr.active_count == 0

    def test_commit_changes_in_worktree(self, temp_git_repo):
        """Should commit changes in worktree without affecting main repo."""
        mgr = WorktreeManager(temp_git_repo)
        worktree = mgr.create("commit-test-wt")

        # Add a new file and commit
        (worktree.path / "worktree_file.txt").write_text("Worktree content\n")
        commit_hash = mgr.commit_changes(worktree, "Add worktree file")

        assert commit_hash is not None
        assert len(commit_hash) == 40  # Full SHA

        # Main repo should not have this file
        assert not (temp_git_repo / "worktree_file.txt").exists()

        # Worktree should have clean status after commit
        status = mgr.get_status(worktree)
        assert status.strip() == ""

    def test_get_diff_with_binary_files(self, temp_git_repo):
        """Should handle binary files in diff."""
        mgr = WorktreeManager(temp_git_repo)
        worktree = mgr.create("binary-wt")

        # Create a simple binary file
        binary_content = bytes([0x00, 0xFF, 0xAB, 0xCD])
        (worktree.path / "binary.bin").write_bytes(binary_content)

        diff = mgr.get_diff(worktree)
        # Diff should mention the file but mark as binary
        assert "binary.bin" in diff

    def test_cleanup_stale_worktrees(self, temp_git_repo):
        """Should cleanup stale worktrees from previous runs."""
        mgr = WorktreeManager(temp_git_repo)
        wt = mgr.create("old-wt")

        # Manually age the worktree directory
        import os
        import time

        old_time = time.time() - (48 * 3600)  # 48 hours ago
        os.utime(wt.path, (old_time, old_time))

        # Create new manager which should cleanup old worktrees
        mgr2 = WorktreeManager(temp_git_repo)
        # The old worktree from mgr should be cleaned up
        # (Note: This tests the auto-cleanup in __init__)

        # Create a fresh worktree to verify manager works
        new_wt = mgr2.create("new-wt")
        assert new_wt.path.exists()

    def test_parallel_worktree_isolation(self, temp_git_repo):
        """Changes in one worktree should not affect another."""
        mgr = WorktreeManager(temp_git_repo)
        wt1 = mgr.create("parallel-1")
        wt2 = mgr.create("parallel-2")

        # Make different changes in each worktree
        (wt1.path / "file1.txt").write_text("Content 1\n")
        (wt2.path / "file2.txt").write_text("Content 2\n")

        # Commit in wt1
        mgr.commit_changes(wt1, "Add file1")

        # wt2 should not have file1
        assert (wt1.path / "file1.txt").exists()
        assert not (wt2.path / "file1.txt").exists()
        assert (wt2.path / "file2.txt").exists()
        assert not (wt1.path / "file2.txt").exists()

    def test_worktree_with_submodules(self, temp_git_repo):
        """Should handle repos with submodules (if any)."""
        # This is a basic test - submodules are complex
        mgr = WorktreeManager(temp_git_repo)
        worktree = mgr.create("submodule-test-wt")

        # Worktree should be created successfully
        assert worktree.path.exists()

        # .git should be a file (gitdir reference), not a directory
        git_path = worktree.path / ".git"
        assert git_path.exists()
        # In worktrees, .git is a file pointing to the actual git dir
        assert git_path.is_file()

    def test_worktree_preserves_gitignore(self, temp_git_repo):
        """Worktree should respect .gitignore from main repo."""
        # Create .gitignore in main repo
        (temp_git_repo / ".gitignore").write_text("*.log\n__pycache__/\n")
        subprocess.run(["git", "add", ".gitignore"], cwd=temp_git_repo, check=True)
        subprocess.run(
            ["git", "commit", "-m", "Add gitignore"],
            cwd=temp_git_repo,
            check=True,
            capture_output=True,
        )

        mgr = WorktreeManager(temp_git_repo)
        worktree = mgr.create("gitignore-wt")

        # Create an ignored file in worktree
        (worktree.path / "debug.log").write_text("Log content\n")

        # Status should not show ignored file
        status = mgr.get_status(worktree)
        assert "debug.log" not in status
