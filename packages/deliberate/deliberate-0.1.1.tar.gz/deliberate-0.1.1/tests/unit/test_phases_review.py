"""Unit tests for the review phase."""

import json
from unittest.mock import MagicMock

import pytest

from deliberate.budget.tracker import BudgetTracker
from deliberate.phases.review import ReviewPhase
from deliberate.types import Verdict


@pytest.fixture
def mock_budget():
    """Mock the budget tracker."""
    return MagicMock(spec=BudgetTracker)


@pytest.fixture
def review_phase(mock_budget):
    """Create a ReviewPhase with simple criteria."""
    return ReviewPhase(
        agents=["reviewer"],
        adapters={},
        budget=mock_budget,
        criteria=["correctness", "code_quality"],
    )


def test_parse_review_tool_call(review_phase):
    """Should parse structured tool calls for submit_review."""
    raw_response = {
        "choices": [
            {
                "message": {
                    "tool_calls": [
                        {
                            "function": {
                                "name": "submit_review",
                                "arguments": json.dumps(
                                    {
                                        "scores": {
                                            "correctness": 9,
                                            "code_quality": 7,
                                        },
                                        "verdict": "reject",
                                        "reasoning": "Major bug in flow",
                                    }
                                ),
                            }
                        }
                    ]
                }
            }
        ]
    }

    review = review_phase._parse_review(
        "reviewer",
        "candidate-1",
        response="",
        tokens=42,
        raw_response=raw_response,
    )

    assert review.recommendation == Verdict.REJECT
    assert review.comments == "Major bug in flow"
    assert review.scores[0].raw_value == 9
    assert review.scores[1].raw_value == 7
    assert review.overall_score == pytest.approx((0.9 + 0.7) / 2)


def test_parse_review_neutral_on_failure(review_phase):
    """Should return neutral scores when parsing fails."""
    review = review_phase._parse_review(
        "reviewer",
        "candidate-1",
        response="not json at all",
        tokens=10,
        raw_response=None,
    )

    assert review.recommendation == Verdict.ACCEPT
    assert review.overall_score == 0.5
    assert all(score.value == 0.5 for score in review.scores)
