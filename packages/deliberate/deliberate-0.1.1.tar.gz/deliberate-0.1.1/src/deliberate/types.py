"""Core type definitions for deliberate."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from deliberate.validation.types import ValidationResult


class Phase(Enum):
    """Workflow phases."""

    PLANNING = "planning"
    EXECUTION = "execution"
    REVIEW = "review"


class Capability(Enum):
    """Agent capabilities."""

    PLANNER = "planner"
    EXECUTOR = "executor"
    REVIEWER = "reviewer"


class Verdict(Enum):
    """Allowed review recommendations/verdicts."""

    ACCEPT = "accept"
    REJECT = "reject"
    REVISE = "revise"


@dataclass
class Plan:
    """A plan produced by a planning agent."""

    id: str
    agent: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    token_usage: int = 0


@dataclass
class DebateMessage:
    """A message in a debate round."""

    agent: str
    content: str
    round: int
    reply_to: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ExecutionResult:
    """Result of an execution phase for a single agent."""

    id: str
    agent: str
    worktree_path: Path | None
    diff: str | None
    summary: str
    success: bool
    error: str | None = None
    error_category: str | None = None
    questions_asked: list[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    token_usage: int = 0
    # Use the richer ValidationResult from validation subsystem
    validation_result: "ValidationResult | None" = None
    stdout: str | None = None

    @property
    def tests_passed(self) -> bool:
        """Check if validation passed (or was not run)."""
        if self.validation_result is None:
            return True  # No validation = vacuous pass
        return self.validation_result.passed

    @property
    def has_regression(self) -> bool:
        """Check if this execution broke existing tests."""
        if self.validation_result is None:
            return False
        return self.validation_result.regression_detected


@dataclass
class Score:
    """A score for a single criterion."""

    criterion: str
    value: float  # normalized 0-1
    raw_value: float  # original scale (e.g., 1-10)
    reasoning: str | None = None


@dataclass
class Review:
    """A review of an execution result by a reviewer."""

    reviewer: str
    candidate_id: str
    scores: list[Score]
    overall_score: float  # aggregated 0-1
    recommendation: Verdict  # accept | reject | revise
    comments: str | None = None
    token_usage: int = 0


@dataclass
class RefinementFeedback:
    """Structured feedback for refinement iteration."""

    candidate_id: str
    iteration: int
    reviews: list["Review"]
    avg_score: float
    confidence: float
    issues: list[str]  # Extracted from review comments
    suggestions: list[str]  # Extracted recommendations

    def to_prompt(self) -> str:
        """Format feedback as refinement prompt."""
        return f"""
# Previous Attempt Review
Your previous implementation received the following feedback:

## Issues Identified
{chr(10).join(f"- {issue}" for issue in self.issues)}

## Reviewer Suggestions
{chr(10).join(f"- {suggestion}" for suggestion in self.suggestions)}

## Current Score
Average Score: {self.avg_score:.2f}/1.00
Reviewer Confidence: {self.confidence:.2f}
"""


@dataclass
class VoteResult:
    """Aggregated voting result across all reviewers."""

    winner_id: str
    rankings: list[str]  # ordered best to worst
    scores: dict[str, float]  # candidate_id -> aggregated score
    vote_breakdown: dict[str, dict[str, float]]  # reviewer -> candidate -> score
    confidence: float  # 0-1, how decisive the vote was


@dataclass
class RefinementIteration:
    """Results from one refinement iteration."""

    iteration_num: int
    feedback: RefinementFeedback
    execution_result: "ExecutionResult"
    reviews: list[Review]
    vote_result: VoteResult
    improvement_delta: float  # Score change from previous iteration
    tokens_used: int


@dataclass
class JuryResult:
    """Final result of a jury run."""

    task: str
    selected_plan: Plan | None
    execution_results: list[ExecutionResult]
    reviews: list[Review]
    vote_result: VoteResult | None
    final_diff: str | None
    summary: str
    success: bool
    # Fields with defaults must come after non-default fields
    all_plans: list[Plan] = field(default_factory=list)  # All planning proposals
    error: str | None = None
    total_duration_seconds: float = 0.0
    total_token_usage: int = 0
    total_cost_usd: float = 0.0
    refinement_iterations: list[RefinementIteration] = field(default_factory=list)
    refinement_triggered: bool = False
    final_improvement: float = 0.0  # Total score improvement from refinement
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    profile: str | None = None
    status_updates: list[dict] = field(default_factory=list)  # Status updates from agents
    debate_messages: list[DebateMessage] = field(default_factory=list)  # Messages exchanged during planning debate


# Re-export ValidationResult from validation subsystem for backwards compatibility
# Import at module level to avoid circular imports
def __getattr__(name: str):
    if name == "ValidationResult":
        from deliberate.validation.types import ValidationResult

        return ValidationResult
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
