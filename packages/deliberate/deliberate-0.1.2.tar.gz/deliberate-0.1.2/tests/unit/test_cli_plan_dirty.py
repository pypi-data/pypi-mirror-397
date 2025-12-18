import subprocess
from pathlib import Path

from typer.testing import CliRunner

from deliberate.cli import PLAN_FILENAME, app

runner = CliRunner()


def _init_repo_with_config(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo, check=True)
    (repo / "README.md").write_text("# Test\n")
    subprocess.run(["git", "add", "README.md"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo, check=True)

    # Minimal config with fake planner
    (repo / ".deliberate.yaml").write_text(
        """
agents:
  fake:
    type: fake
    behavior: echo
    capabilities: [planner]
workflow:
  planning:
    enabled: true
    agents: [fake]
  execution:
    enabled: false
  review:
    enabled: false
tracking:
  enabled: false
"""
    )
    subprocess.run(["git", "add", ".deliberate.yaml"], cwd=repo, check=True)
    subprocess.run(
        ["git", "commit", "-m", "add deliberate config"],
        cwd=repo,
        check=True,
        stdout=subprocess.PIPE,
    )
    return repo


def test_plan_blocks_on_dirty_without_flag(tmp_path, monkeypatch):
    repo = _init_repo_with_config(tmp_path)
    (repo / "dirty.txt").write_text("dirty")
    monkeypatch.chdir(repo)

    result = runner.invoke(app, ["plan", "test task"], env={"PYTHONPATH": str(Path.cwd())})

    assert result.exit_code != 0
    assert "uncommitted changes" in result.output
    # Branch should not exist
    branches = subprocess.run(["git", "branch", "--list", "deliberate/*"], cwd=repo, capture_output=True, text=True)
    assert branches.stdout.strip() == ""


def test_plan_allows_dirty_with_flag(tmp_path, monkeypatch):
    repo = _init_repo_with_config(tmp_path)
    (repo / "dirty.txt").write_text("dirty")
    monkeypatch.chdir(repo)

    result = runner.invoke(
        app,
        ["plan", "test task", "--allow-dirty"],
        env={"PYTHONPATH": str(Path.cwd())},
    )

    # Should complete planning and create deliberate branch with PLAN.md
    assert result.exit_code == 0
    branches = subprocess.run(["git", "branch", "--list", "deliberate/*"], cwd=repo, capture_output=True, text=True)
    assert "deliberate/test-task" in branches.stdout
    wt_plan = repo / ".deliberate" / "worktrees" / "deliberate__test-task" / PLAN_FILENAME
    assert wt_plan.exists()


def test_plan_reuses_existing_branch(tmp_path, monkeypatch):
    repo = _init_repo_with_config(tmp_path)
    monkeypatch.chdir(repo)

    # First run to create branch
    first = runner.invoke(
        app,
        ["plan", "test task"],
        env={"PYTHONPATH": str(Path.cwd())},
    )
    assert first.exit_code == 0

    # Modify plan to detect overwrite
    wt_plan = repo / ".deliberate" / "worktrees" / "deliberate__test-task" / PLAN_FILENAME
    wt_plan.write_text("old plan")

    second = runner.invoke(
        app,
        ["plan", "test task", "--reuse-branch"],
        env={"PYTHONPATH": str(Path.cwd())},
    )
    assert second.exit_code == 0
    branches = subprocess.run(["git", "branch", "--list", "deliberate/*"], cwd=repo, capture_output=True, text=True)
    assert "deliberate/test-task" in branches.stdout
    # PLAN.md should be overwritten by planner; at least not the placeholder
    assert wt_plan.read_text() != "old plan"


def test_plan_auto_suffix_when_branch_exists(tmp_path, monkeypatch):
    repo = _init_repo_with_config(tmp_path)
    monkeypatch.chdir(repo)

    first = runner.invoke(app, ["plan", "test task"], env={"PYTHONPATH": str(Path.cwd())})
    assert first.exit_code == 0

    second = runner.invoke(app, ["plan", "test task"], env={"PYTHONPATH": str(Path.cwd())})
    assert second.exit_code == 0

    branches = subprocess.run(["git", "branch", "--list", "deliberate/*"], cwd=repo, capture_output=True, text=True)
    out = branches.stdout
    assert "deliberate/test-task" in out
    assert "deliberate/test-task-2" in out
    wt1 = repo / ".deliberate" / "worktrees" / "deliberate__test-task" / PLAN_FILENAME
    wt2 = repo / ".deliberate" / "worktrees" / "deliberate__test-task-2" / PLAN_FILENAME
    assert wt1.exists()
    assert wt2.exists()
