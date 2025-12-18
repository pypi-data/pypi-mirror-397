import subprocess
from pathlib import Path

from deliberate.budget.tracker import BudgetTracker
from deliberate.config import DeliberateConfig
from deliberate.git.worktree import WorktreeManager
from deliberate.orchestrator import Orchestrator


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo, check=True)
    (repo / "README.md").write_text("# Test\n")
    subprocess.run(["git", "add", "README.md"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo, check=True)
    return repo


def test_orchestrator_allows_injected_budget_and_worktree(tmp_path):
    repo = _init_repo(tmp_path)

    cfg = DeliberateConfig()
    cfg.tracking.enabled = False
    injected_budget = BudgetTracker(
        max_total_tokens=1_000, max_cost_usd=1.0, max_requests_per_agent=5, hard_timeout_seconds=60
    )
    injected_worktrees = WorktreeManager(repo)

    orch = Orchestrator(
        cfg,
        repo,
        budget_tracker=injected_budget,
        worktree_mgr=injected_worktrees,
    )

    assert orch.budget is injected_budget
    assert orch.worktrees is injected_worktrees
