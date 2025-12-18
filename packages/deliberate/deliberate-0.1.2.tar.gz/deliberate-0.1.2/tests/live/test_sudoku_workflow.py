"""Live end-to-end test on a broken Sudoku solver using a scripted executor.

Runs planning → execution (with real code changes) → review to ensure the
workflow works with structured outputs and real file edits. Skipped unless
RUN_LIVE_SUDOKU=1 is set to avoid running by default.
"""

import subprocess
from pathlib import Path

import pytest

from deliberate.adapters.base import AdapterResponse, ModelAdapter
from deliberate.adapters.fake_adapter import FakeAdapter
from deliberate.budget.tracker import BudgetTracker
from deliberate.git.worktree import WorktreeManager
from deliberate.phases.execution import ExecutionPhase
from deliberate.phases.planning import PlanningPhase
from deliberate.phases.review import ReviewPhase


class ScriptedExecutorAdapter(ModelAdapter):
    """Deterministic executor that patches the Sudoku bug."""

    def __init__(self, name: str = "scripted-executor"):
        self.name = name

    async def call(
        self,
        prompt: str,
        *,
        system: str | None = None,
        max_tokens: int | None = None,
        temperature: float = 0.7,
        working_dir: str | None = None,
    ) -> AdapterResponse:  # pragma: no cover - unused in this test
        return AdapterResponse(content="noop", token_usage=1, duration_seconds=0.0)

    async def run_agentic(
        self,
        task: str,
        *,
        working_dir: str,
        timeout_seconds: int = 1200,
        on_question=None,
        **kwargs,
    ) -> AdapterResponse:
        solver_path = Path(working_dir) / "sudoku" / "solver.py"
        content = solver_path.read_text()
        patched = content.replace("range(1, 9)", "range(1, 10)")
        patched = patched.replace(
            "    if not empty:\n        return True",
            (
                "    if not empty:\n"
                "        for r in range(9):\n"
                "            for c in range(9):\n"
                "                val = board[r][c]\n"
                "                if val != 0:\n"
                "                    board[r][c] = 0\n"
                "                    if not is_valid(board, r, c, val):\n"
                "                        board[r][c] = val\n"
                "                        return False\n"
                "                    board[r][c] = val\n"
                "        return True"
            ),
        )
        solver_path.write_text(patched)

        summary = "Fixed Sudoku solver loop to try digits 1-9."
        return AdapterResponse(
            content=summary,
            token_usage=self.estimate_tokens(summary),
            duration_seconds=0.01,
            raw_response={"structured_output": {"summary": summary}},
        )


def _init_repo(repo_root: Path) -> None:
    """Initialize a git repo with a broken Sudoku solver and tests."""
    (repo_root / "sudoku").mkdir(parents=True, exist_ok=True)
    (repo_root / "sudoku" / "__init__.py").write_text("")
    (repo_root / "sudoku" / "solver.py").write_text(
        """\"\"\"Simple Sudoku solver with an off-by-one bug.\"\"\"

def is_valid(board, row, col, num):
    for i in range(9):
        if board[row][i] == num or board[i][col] == num:
            return False

    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(start_row, start_row + 3):
        for j in range(start_col, start_col + 3):
            if board[i][j] == num:
                return False
    return True


def find_empty(board):
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                return i, j
    return None


def solve(board):
    empty = find_empty(board)
    if not empty:
        return True
    row, col = empty

    # BUG: only tries digits 1-8
    for num in range(1, 9):
        if is_valid(board, row, col, num):
            board[row][col] = num
            if solve(board):
                return True
            board[row][col] = 0
    return False
"""
    )

    (repo_root / "tests").mkdir(exist_ok=True)
    (repo_root / "tests" / "conftest.py").write_text(
        "import sys\nfrom pathlib import Path\nsys.path.insert(0, str(Path(__file__).resolve().parents[1]))\n"
    )
    (repo_root / "tests" / "test_solver.py").write_text(
        """import copy
from sudoku import solver


def test_solve_easy_grid():
    puzzle = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ]
    expected_solution = [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9],
    ]

    board = copy.deepcopy(puzzle)
    solved = solver.solve(board)

    assert solved is True
    assert board == expected_solution


def test_detect_unsolvable():
    puzzle = [[1] * 9 for _ in range(9)]
    board = copy.deepcopy(puzzle)
    solved = solver.solve(board)
    assert solved is False
"""
    )

    (repo_root / "pyproject.toml").write_text(
        """[project]
name = "sudoku"
version = "0.1.0"
dependencies = ["pytest>=7"]

[tool.pytest.ini_options]
testpaths = ["tests"]
"""
    )

    subprocess.run(["git", "init", "-q"], cwd=repo_root, check=True)
    subprocess.run(["git", "add", "."], cwd=repo_root, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "initial broken sudoku"],
        cwd=repo_root,
        check=True,
        env={
            "GIT_AUTHOR_NAME": "test",
            "GIT_AUTHOR_EMAIL": "test@example.com",
            "GIT_COMMITTER_NAME": "test",
            "GIT_COMMITTER_EMAIL": "test@example.com",
        },
    )


@pytest.mark.asyncio
async def test_sudoku_workflow(tmp_path: Path):
    """End-to-end workflow fixes the Sudoku bug using structured tool outputs."""
    repo_root = tmp_path / "sudoku-demo"
    repo_root.mkdir()
    _init_repo(repo_root)

    adapters = {
        "planner_a": FakeAdapter(name="planner_a", behavior="planner"),
        "planner_b": FakeAdapter(name="planner_b", behavior="planner"),
        "judge": FakeAdapter(name="judge", behavior="judge"),
        "executor": ScriptedExecutorAdapter(name="executor"),
        "reviewer": FakeAdapter(name="reviewer", behavior="critic"),
    }

    budget = BudgetTracker(max_total_tokens=100_000, max_cost_usd=10.0)
    planning = PlanningPhase(
        agents=["planner_a", "planner_b"],
        adapters=adapters,
        budget=budget,
        selection_method="llm_judge",
        judge_agent="judge",
    )
    execution = ExecutionPhase(
        agents=["executor"],
        adapters=adapters,
        budget=budget,
        worktree_mgr=WorktreeManager(repo_root),
        use_worktrees=True,
        run_tests=True,
        tests_command="pytest",
        test_timeout_seconds=120,
    )
    review = ReviewPhase(
        agents=["reviewer"],
        adapters=adapters,
        budget=budget,
        criteria=["correctness", "code_quality", "completeness", "risk"],
    )

    selected_plan, _, _ = await planning.run("Fix the Sudoku solver to use digits 1-9.")
    assert selected_plan is not None

    results = await execution.run("Fix the Sudoku solver to use digits 1-9.", selected_plan)
    assert len(results) == 1
    result = results[0]
    assert result.success is True
    assert result.validation_result is not None
    assert result.validation_result.passed
    assert result.diff and "range(1, 10)" in result.diff

    solver_after = Path(result.worktree_path) / "sudoku" / "solver.py"
    assert "range(1, 10)" in solver_after.read_text()

    reviews, vote_result = await review.run("Fix the Sudoku solver to use digits 1-9.", results)
    assert vote_result is not None
    assert vote_result.winner_id == result.id
    assert reviews
