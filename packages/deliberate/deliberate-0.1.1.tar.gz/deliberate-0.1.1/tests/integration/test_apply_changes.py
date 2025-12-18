from unittest.mock import MagicMock, patch

import pytest

from deliberate.orchestrator import Orchestrator
from deliberate.types import ExecutionResult


class TestApplyChanges:
    @pytest.fixture(autouse=True)
    def mock_tracker(self):
        """Mock tracker to avoid DuckDB lock issues."""
        with patch("deliberate.orchestrator.get_tracker") as mock:
            mock.return_value = MagicMock()
            yield mock

    @pytest.mark.asyncio
    async def test_apply_changes_merge_strategy(self, temp_git_repo, minimal_config):
        """Test applying changes via git merge."""
        # 1. Setup config
        minimal_config.workflow.execution.worktree.apply_strategy = "merge"
        minimal_config.tracking.enabled = False
        orchestrator = Orchestrator(minimal_config, temp_git_repo)

        # 2. Create a worktree manually via the manager
        wt = orchestrator.worktrees.create("test-wt")

        # 3. Make changes in worktree
        (wt.path / "new_file.txt").write_text("content")

        # 4. Create ExecutionResult
        result = ExecutionResult(id="1", agent="agent", worktree_path=wt.path, diff="", summary="", success=True)

        # 5. Apply changes
        branch = orchestrator.apply_changes(result)

        # 6. Verify changes in repo root
        assert (temp_git_repo / "new_file.txt").exists()
        assert (temp_git_repo / "new_file.txt").read_text() == "content"

        # 7. Verify git log has the commit on the new branch
        assert branch.startswith("deliberate/")
        log = orchestrator.worktrees._run_git(["git", "log", "--oneline", "-5"], cwd=temp_git_repo).stdout
        assert "Deliberate: Auto-commit of agent changes" in log or "Merge" in log

    @pytest.mark.asyncio
    async def test_apply_changes_squash_strategy(self, temp_git_repo, minimal_config):
        """Test applying changes via git squash."""
        minimal_config.workflow.execution.worktree.apply_strategy = "squash"
        minimal_config.tracking.enabled = False
        orchestrator = Orchestrator(minimal_config, temp_git_repo)

        wt = orchestrator.worktrees.create("test-wt-squash")
        (wt.path / "squash_file.txt").write_text("content")

        result = ExecutionResult(id="3", agent="agent", worktree_path=wt.path, diff="", summary="", success=True)

        branch = orchestrator.apply_changes(result)

        # Verify file exists
        assert (temp_git_repo / "squash_file.txt").exists()

        # Verify changes committed on branch
        assert branch.startswith("deliberate/")
        status = orchestrator.worktrees._run_git(["git", "status", "--porcelain"], cwd=temp_git_repo).stdout
        non_worktree_status = [line for line in status.splitlines() if ".deliberate/worktrees" not in line]
        assert not non_worktree_status
        log = orchestrator.worktrees._run_git(["git", "log", "--oneline", "-3"], cwd=temp_git_repo).stdout
        assert "Deliberate: Apply changes (squash)" in log

    @pytest.mark.asyncio
    async def test_apply_changes_copy_strategy(self, temp_git_repo, minimal_config):
        """Test applying changes via copy strategy raises error."""
        minimal_config.workflow.execution.worktree.apply_strategy = "copy"
        minimal_config.tracking.enabled = False
        orchestrator = Orchestrator(minimal_config, temp_git_repo)

        wt = orchestrator.worktrees.create("test-wt-copy")
        (wt.path / "copy_file.txt").write_text("content")

        result = ExecutionResult(id="2", agent="agent", worktree_path=wt.path, diff="", summary="", success=True)

        with pytest.raises(RuntimeError, match="deprecated and unsafe"):
            orchestrator.apply_changes(result)

    @pytest.mark.asyncio
    async def test_apply_changes_merge_conflict(self, temp_git_repo, minimal_config):
        """Test applying changes with merge conflict raises descriptive error."""
        minimal_config.workflow.execution.worktree.apply_strategy = "merge"
        minimal_config.tracking.enabled = False
        orchestrator = Orchestrator(minimal_config, temp_git_repo)

        # 0. Create base state
        (temp_git_repo / "conflict.txt").write_text("base content")
        orchestrator.worktrees._run_git(["git", "add", "conflict.txt"], cwd=temp_git_repo)
        orchestrator.worktrees._run_git(["git", "commit", "-m", "base commit"], cwd=temp_git_repo)

        # 1. Create worktree from current HEAD
        wt = orchestrator.worktrees.create("test-conflict")

        # 2. Modify file in main repo AND commit
        (temp_git_repo / "conflict.txt").write_text("main content")
        orchestrator.worktrees._run_git(["git", "add", "conflict.txt"], cwd=temp_git_repo)
        orchestrator.worktrees._run_git(["git", "commit", "-m", "main changes"], cwd=temp_git_repo)

        # 3. Modify same file in worktree (will be auto-committed by apply_changes)
        (wt.path / "conflict.txt").write_text("worktree content")

        result = ExecutionResult(id="4", agent="agent", worktree_path=wt.path, diff="", summary="", success=True)

        with pytest.raises(RuntimeError, match="Branch left at"):
            orchestrator.apply_changes(result)
