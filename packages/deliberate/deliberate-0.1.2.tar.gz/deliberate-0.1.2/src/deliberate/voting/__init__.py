"""Voting and aggregation logic for deliberate."""

from deliberate.voting.aggregation import (
    aggregate_approval,
    aggregate_borda,
    aggregate_weighted_borda,
)

__all__ = ["aggregate_borda", "aggregate_approval", "aggregate_weighted_borda"]
