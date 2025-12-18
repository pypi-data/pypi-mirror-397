"""Tests for voting aggregation logic."""

import pytest

from deliberate.voting.aggregation import (
    aggregate_approval,
    aggregate_borda,
    aggregate_weighted_borda,
    calculate_confidence,
    get_rankings,
)


class TestBordaCount:
    """Tests for Borda count aggregation."""

    def test_single_voter(self):
        """Single voter should produce clear ranking."""
        scores = aggregate_borda(
            ["A", "B", "C"],
            {"r1": {"A": 0.9, "B": 0.5, "C": 0.3}},
        )

        assert scores["A"] > scores["B"] > scores["C"]
        assert scores["A"] == 1.0  # Top choice gets max score

    def test_unanimous_voting(self):
        """All voters agree should give clear winner."""
        scores = aggregate_borda(
            ["A", "B"],
            {
                "r1": {"A": 0.9, "B": 0.1},
                "r2": {"A": 0.8, "B": 0.2},
                "r3": {"A": 0.7, "B": 0.3},
            },
        )

        assert scores["A"] == 1.0
        assert scores["B"] == 0.0

    def test_tie(self):
        """Equal votes should produce tie."""
        scores = aggregate_borda(
            ["A", "B"],
            {
                "r1": {"A": 0.9, "B": 0.1},
                "r2": {"A": 0.1, "B": 0.9},
            },
        )

        assert scores["A"] == scores["B"]
        assert scores["A"] == 0.5

    def test_empty_candidates(self):
        """Empty candidates should return empty dict."""
        scores = aggregate_borda([], {"r1": {}})
        assert scores == {}

    def test_empty_voters(self):
        """Empty voters should return zero scores."""
        scores = aggregate_borda(["A", "B"], {})
        assert scores == {"A": 0.0, "B": 0.0}

    def test_three_way_race(self):
        """Three candidates with varied preferences."""
        scores = aggregate_borda(
            ["A", "B", "C"],
            {
                "r1": {"A": 0.9, "B": 0.5, "C": 0.1},
                "r2": {"A": 0.1, "B": 0.9, "C": 0.5},
            },
        )

        # B should win (2nd + 1st = 3 points)
        # A should be 2nd (1st + 3rd = 2 points)
        # C should be 3rd (3rd + 2nd = 1 point)
        assert scores["B"] > scores["A"] > scores["C"]


class TestApprovalVoting:
    """Tests for approval voting aggregation."""

    def test_above_threshold(self):
        """Candidate above threshold should get approval."""
        scores = aggregate_approval(
            ["A", "B"],
            {"r1": {"A": 0.8, "B": 0.6}},
            threshold=0.7,
        )

        assert scores["A"] == 1.0  # Approved
        assert scores["B"] == 0.0  # Not approved

    def test_unanimous_approval(self):
        """All approve one candidate."""
        scores = aggregate_approval(
            ["A", "B"],
            {
                "r1": {"A": 0.9, "B": 0.5},
                "r2": {"A": 0.8, "B": 0.6},
            },
            threshold=0.7,
        )

        assert scores["A"] == 1.0
        assert scores["B"] == 0.0

    def test_partial_approval(self):
        """Some approve, some don't."""
        scores = aggregate_approval(
            ["A"],
            {
                "r1": {"A": 0.8},  # Approves
                "r2": {"A": 0.6},  # Does not approve
            },
            threshold=0.7,
        )

        assert scores["A"] == 0.5  # 1 out of 2 approved

    def test_custom_threshold(self):
        """Custom threshold should work."""
        scores = aggregate_approval(
            ["A", "B"],
            {"r1": {"A": 0.5, "B": 0.4}},
            threshold=0.45,
        )

        assert scores["A"] == 1.0  # 0.5 >= 0.45
        assert scores["B"] == 0.0  # 0.4 < 0.45


class TestWeightedBorda:
    """Tests for weighted Borda count."""

    def test_equal_weights(self):
        """Equal weights should match regular Borda."""
        candidates = ["A", "B"]
        votes = {
            "r1": {"A": 0.9, "B": 0.1},
            "r2": {"A": 0.1, "B": 0.9},
        }

        regular = aggregate_borda(candidates, votes)
        weighted = aggregate_weighted_borda(candidates, votes, {"r1": 1.0, "r2": 1.0})

        assert regular == weighted

    def test_unequal_weights(self):
        """Higher weight should have more influence."""
        scores = aggregate_weighted_borda(
            ["A", "B"],
            {
                "r1": {"A": 0.9, "B": 0.1},  # Prefers A
                "r2": {"A": 0.1, "B": 0.9},  # Prefers B
            },
            {"r1": 2.0, "r2": 1.0},  # r1 has double weight
        )

        # r1's preference for A should win
        assert scores["A"] > scores["B"]


class TestConfidence:
    """Tests for confidence calculation."""

    def test_clear_winner(self):
        """Clear winner should have high confidence."""
        confidence = calculate_confidence({"A": 1.0, "B": 0.0})
        assert confidence == 1.0

    def test_close_race(self):
        """Close race should have low confidence."""
        confidence = calculate_confidence({"A": 0.51, "B": 0.49})
        assert confidence == pytest.approx(0.02)

    def test_tie(self):
        """Tie should have zero confidence."""
        confidence = calculate_confidence({"A": 0.5, "B": 0.5})
        assert confidence == 0.0

    def test_single_candidate(self):
        """Single candidate should have full confidence."""
        confidence = calculate_confidence({"A": 0.8})
        assert confidence == 1.0


class TestRankings:
    """Tests for ranking generation."""

    def test_basic_ranking(self):
        """Rankings should be in descending score order."""
        rankings = get_rankings({"A": 0.5, "B": 0.8, "C": 0.3})
        assert rankings == ["B", "A", "C"]

    def test_empty_scores(self):
        """Empty scores should return empty list."""
        rankings = get_rankings({})
        assert rankings == []
