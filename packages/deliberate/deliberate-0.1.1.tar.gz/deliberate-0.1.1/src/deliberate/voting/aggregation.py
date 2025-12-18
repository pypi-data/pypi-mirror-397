"""Voting aggregation algorithms for multi-LLM review."""


def aggregate_borda(
    candidates: list[str],
    vote_breakdown: dict[str, dict[str, float]],
) -> dict[str, float]:
    """Aggregate votes using Borda count.

    Borda count assigns points based on ranking position:
    - With N candidates, 1st place gets N-1 points, 2nd gets N-2, etc.
    - Final scores are normalized to 0-1.

    Args:
        candidates: List of candidate IDs.
        vote_breakdown: Mapping of reviewer -> {candidate -> score}.
                       Higher scores indicate better candidates.

    Returns:
        Mapping of candidate -> normalized aggregated score.
    """
    if not candidates:
        return {}

    n = len(candidates)
    scores = {c: 0.0 for c in candidates}

    for reviewer_scores in vote_breakdown.values():
        # Sort candidates by this reviewer's score (highest first)
        ranked = sorted(
            candidates,
            key=lambda c: reviewer_scores.get(c, 0),
            reverse=True,
        )

        # Assign Borda points
        for position, candidate in enumerate(ranked):
            points = n - 1 - position
            scores[candidate] += points

    # Normalize to 0-1
    num_voters = len(vote_breakdown)
    if num_voters > 0:
        max_possible = (n - 1) * num_voters
        if max_possible > 0:
            scores = {c: s / max_possible for c, s in scores.items()}

    return scores


def aggregate_approval(
    candidates: list[str],
    vote_breakdown: dict[str, dict[str, float]],
    threshold: float = 0.7,
) -> dict[str, float]:
    """Aggregate votes using approval voting.

    Each reviewer "approves" candidates with score >= threshold.
    Final score is the fraction of reviewers who approved.

    Args:
        candidates: List of candidate IDs.
        vote_breakdown: Mapping of reviewer -> {candidate -> score}.
        threshold: Minimum score to count as approval (normalized 0-1).

    Returns:
        Mapping of candidate -> approval ratio (0-1).
    """
    if not candidates:
        return {}

    scores = {c: 0.0 for c in candidates}
    num_voters = len(vote_breakdown)

    if num_voters == 0:
        return scores

    for reviewer_scores in vote_breakdown.values():
        for candidate in candidates:
            if reviewer_scores.get(candidate, 0) >= threshold:
                scores[candidate] += 1

    # Normalize to approval ratio
    scores = {c: s / num_voters for c, s in scores.items()}

    return scores


def aggregate_weighted_borda(
    candidates: list[str],
    vote_breakdown: dict[str, dict[str, float]],
    weights: dict[str, float] | None = None,
) -> dict[str, float]:
    """Aggregate votes using weighted Borda count.

    Like Borda count, but each reviewer's vote is weighted.
    Useful when some reviewers are more trusted than others.

    Args:
        candidates: List of candidate IDs.
        vote_breakdown: Mapping of reviewer -> {candidate -> score}.
        weights: Mapping of reviewer -> weight. Defaults to equal weights.

    Returns:
        Mapping of candidate -> normalized weighted score.
    """
    if not candidates:
        return {}

    n = len(candidates)
    scores = {c: 0.0 for c in candidates}

    if weights is None:
        weights = {r: 1.0 for r in vote_breakdown.keys()}

    total_weight = sum(weights.get(r, 1.0) for r in vote_breakdown.keys())

    if total_weight == 0:
        return scores

    for reviewer, reviewer_scores in vote_breakdown.items():
        reviewer_weight = weights.get(reviewer, 1.0)

        # Sort candidates by this reviewer's score (highest first)
        ranked = sorted(
            candidates,
            key=lambda c: reviewer_scores.get(c, 0),
            reverse=True,
        )

        # Assign weighted Borda points
        for position, candidate in enumerate(ranked):
            points = (n - 1 - position) * reviewer_weight
            scores[candidate] += points

    # Normalize to 0-1
    max_possible = (n - 1) * total_weight
    if max_possible > 0:
        scores = {c: s / max_possible for c, s in scores.items()}

    return scores


def calculate_confidence(scores: dict[str, float]) -> float:
    """Calculate confidence level of voting result.

    Measures how decisive the vote was based on the gap between
    first and second place.

    Args:
        scores: Mapping of candidate -> score.

    Returns:
        Confidence value between 0-1.
        Higher values indicate more decisive victories.
    """
    if len(scores) < 2:
        return 1.0

    sorted_scores = sorted(scores.values(), reverse=True)
    gap = sorted_scores[0] - sorted_scores[1]

    # Normalize gap (max possible gap is 1.0)
    return min(1.0, gap)


def get_rankings(scores: dict[str, float]) -> list[str]:
    """Get candidates ranked by score.

    Args:
        scores: Mapping of candidate -> score.

    Returns:
        List of candidate IDs ordered from best to worst.
    """
    return sorted(scores.keys(), key=lambda c: scores[c], reverse=True)
