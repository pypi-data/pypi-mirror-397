"""Type definitions for iterative solving.

Inspired by the meta-pattern from poetiq-arc-agi-solver:
- "The prompt is an interface, not the intelligence"
- Iterative problem-solving loop with structured feedback
- Self-auditing for early termination on success
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class TerminationReason(Enum):
    """Why the iterative solver terminated."""

    SUCCESS = "success"  # Solution passed all checks
    MAX_ITERATIONS = "max_iterations"  # Hit iteration limit
    BUDGET_EXHAUSTED = "budget_exhausted"  # Ran out of tokens/cost budget
    TIMEOUT = "timeout"  # Ran out of time
    MANUAL_STOP = "manual_stop"  # User or system requested stop


@dataclass
class SolutionAttempt:
    """A single solution attempt with its evaluation.

    Similar to poetiq's ARCAGISolution, capturing both the solution
    and its feedback for use in subsequent iterations.
    """

    iteration: int
    code: str | None  # The generated solution (could be code or other artifact)
    output: str  # Raw output from running the solution
    success: bool  # Did this attempt pass all checks?
    soft_score: float  # Partial correctness score 0.0-1.0
    feedback: str  # Structured feedback for the LLM
    error: str | None = None  # Error message if any
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    token_usage: int = 0
    duration_seconds: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class IterationConfig:
    """Configuration for the iterative solver.

    Mirrors the key parameters from poetiq's ExpertConfig.
    """

    # Core iteration settings
    max_iterations: int = 10  # Maximum solve attempts
    max_solutions_in_context: int = 5  # Max past solutions to include in prompt
    selection_probability: float = 1.0  # Probability of including each past solution

    # Self-auditing thresholds
    success_threshold: float = 1.0  # Score needed to consider "success"
    min_improvement_threshold: float = 0.05  # Min improvement to continue iterating
    return_best_on_failure: bool = True  # Return best attempt if no success

    # Context building
    improving_order: bool = True  # Show solutions worst-to-best (learning order)
    shuffle_examples: bool = False  # Randomize input examples
    include_all_feedback: bool = True  # Include all feedback vs just summary

    # Budget limits
    max_tokens: int | None = None
    max_cost_usd: float | None = None
    max_time_seconds: float | None = None

    # Seed for reproducibility
    seed: int = 0


@dataclass
class IterationResult:
    """Result of a complete iterative solving session.

    Captures all attempts and the final outcome.
    """

    success: bool
    termination_reason: TerminationReason
    iterations_completed: int
    best_attempt: SolutionAttempt | None
    all_attempts: list[SolutionAttempt]
    final_score: float
    total_tokens: int
    total_duration: float
    improvement_trajectory: list[float]  # Score at each iteration

    @property
    def summary(self) -> str:
        """Human-readable summary of the iteration result."""
        status = "SUCCESS" if self.success else "FAILED"
        reason = self.termination_reason.value
        return (
            f"Iterative Solving: {status} ({reason}) "
            f"after {self.iterations_completed} iteration(s), "
            f"final score: {self.final_score:.2f}"
        )


@dataclass
class FeedbackContext:
    """Context for building feedback from an evaluation.

    Generic structure that can be specialized for different domains
    (test failures, code review, ARC-AGI examples, etc.)
    """

    # What was expected
    expected: Any
    # What was produced
    actual: Any
    # Whether they match
    match: bool
    # Partial correctness score
    soft_score: float
    # Human-readable diff or comparison
    diff: str | None = None
    # Specific error messages
    errors: list[str] = field(default_factory=list)
    # Additional context
    metadata: dict[str, Any] = field(default_factory=dict)
