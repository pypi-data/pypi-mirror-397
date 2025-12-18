"""Tests for dynamic review criteria generation."""

from pathlib import Path

import pytest

from deliberate.adapters.fake_adapter import FakeAdapter
from deliberate.budget.tracker import BudgetTracker
from deliberate.phases.review import ReviewPhase
from deliberate.review.criteria import generate_review_criteria


@pytest.mark.asyncio
async def test_generate_review_criteria_with_tool_call(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("Optimize SQL queries for performance.")
    (repo / "db.sql").write_text("SELECT * FROM users;")

    adapter = FakeAdapter(name="criteria_agent", behavior="criteria")

    result = await generate_review_criteria(
        "Optimize SQL queries",
        repo,
        adapter,
        max_criteria=4,
    )

    assert result is not None
    names, descriptions, tokens = result
    assert "Query Performance" in names
    assert descriptions.get("Query Performance")
    assert tokens > 0


def test_review_phase_update_criteria():
    phase = ReviewPhase(
        agents=["r1"],
        adapters={"r1": FakeAdapter(name="r1", behavior="critic")},
        budget=BudgetTracker(),
        criteria=["correctness"],
    )

    phase.update_criteria(
        ["Query Performance", "Index Usage"],
        {"Query Performance": "Focus on SQL execution speed"},
    )

    assert phase.criteria == ["Query Performance", "Index Usage"]
    assert phase._describe_criterion("Query Performance") == "Focus on SQL execution speed"
    assert "Evaluate" in phase._describe_criterion("Index Usage")
