"""Solution history management for iterative solving.

Accumulates past solution attempts with their feedback, enabling
the LLM to learn from its mistakes across iterations.

Now with optional DuckDB persistence via SolutionStore (Phase 1.4 of Blackboard).
"""

from __future__ import annotations

import logging
import random
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Sequence

from .types import SolutionAttempt

if TYPE_CHECKING:
    from deliberate.tracking.solution_store import SolutionRecord, SolutionStore

logger = logging.getLogger(__name__)


@dataclass
class SolutionHistory:
    """Manages history of solution attempts for iterative solving.

    Similar to poetiq's `solutions: list[ARCAGISolution]` accumulator,
    but with additional selection and formatting capabilities.

    Optionally backed by DuckDB persistence via SolutionStore:
    - Session attempts are stored in memory for fast access
    - Successful solutions are persisted for cross-session learning
    - Historical successful solutions can be retrieved as few-shot examples
    """

    attempts: list[SolutionAttempt] = field(default_factory=list)
    _seed: int = field(default=0)

    # Persistence configuration (set via configure())
    _solution_store: SolutionStore | None = field(default=None, repr=False)
    _task_hash: str | None = field(default=None)
    _workflow_id: str | None = field(default=None)
    _agent: str = field(default="unknown")

    def configure(
        self,
        solution_store: SolutionStore | None = None,
        task_hash: str | None = None,
        workflow_id: str | None = None,
        agent: str = "unknown",
    ) -> None:
        """Configure persistence for this history.

        Args:
            solution_store: Optional SolutionStore for DuckDB persistence.
            task_hash: Task hash for filtering solutions.
            workflow_id: Optional workflow ID for tracking.
            agent: Agent name for attribution.
        """
        self._solution_store = solution_store
        self._task_hash = task_hash
        self._workflow_id = workflow_id
        self._agent = agent

    def add(self, attempt: SolutionAttempt, persist_if_successful: bool = True) -> None:
        """Add a new solution attempt to history.

        Args:
            attempt: The solution attempt to add.
            persist_if_successful: If True and attempt is successful, persist to store.
        """
        self.attempts.append(attempt)

        # Persist successful attempts for future learning
        if persist_if_successful and attempt.success and self._solution_store:
            self._persist_attempt(attempt)

    def get_best(self) -> SolutionAttempt | None:
        """Get the attempt with the highest soft_score."""
        if not self.attempts:
            return None
        return max(self.attempts, key=lambda a: a.soft_score)

    def get_successful(self) -> list[SolutionAttempt]:
        """Get all attempts that were marked as successful."""
        return [a for a in self.attempts if a.success]

    def select_for_context(
        self,
        max_solutions: int = 5,
        selection_probability: float = 1.0,
        improving_order: bool = True,
        seed: int | None = None,
    ) -> list[SolutionAttempt]:
        """Select solutions to include in the next prompt's context.

        Implements poetiq's selection strategy:
        - Probabilistic selection from all solutions
        - Sort by score (worst-to-best for "improving order")
        - Limit to max_solutions

        Args:
            max_solutions: Maximum number of solutions to include.
            selection_probability: Probability of including each solution.
            improving_order: If True, show worst-to-best (learning order).
            seed: Random seed for reproducibility.

        Returns:
            List of selected SolutionAttempts in display order.
        """
        if not self.attempts:
            return []

        # Set seed if provided
        rng = random.Random(seed if seed is not None else self._seed)

        # Probabilistic selection
        selected = []
        for attempt in self.attempts:
            if rng.random() < selection_probability:
                selected.append(attempt)

        if not selected:
            return []

        # Sort by score
        selected.sort(key=lambda a: a.soft_score, reverse=not improving_order)

        # Limit to max_solutions
        return selected[:max_solutions]

    def format_for_prompt(
        self,
        selected: Sequence[SolutionAttempt],
        include_code: bool = True,
        include_full_feedback: bool = True,
    ) -> str:
        """Format selected solutions for inclusion in an LLM prompt.

        Generates XML-style structured output similar to poetiq's
        FEEDBACK_PROMPT format.

        Args:
            selected: The solutions to format.
            include_code: Whether to include the solution code.
            include_full_feedback: Whether to include full feedback or summary.

        Returns:
            Formatted string for prompt injection.
        """
        if not selected:
            return ""

        blocks = []
        for i, attempt in enumerate(selected, start=1):
            block = f"""<solution_{i}>
<solution_iteration>{attempt.iteration}</solution_iteration>
"""
            if include_code and attempt.code:
                block += f"""<solution_code>
```
{attempt.code}
```
</solution_code>
"""
            block += f"""<solution_evaluation>
{attempt.feedback if include_full_feedback else self._summarize_feedback(attempt)}
</solution_evaluation>
<solution_score>{attempt.soft_score:.2f}</solution_score>
<solution_success>{attempt.success}</solution_success>
</solution_{i}>"""
            blocks.append(block)

        return "\n\n".join(blocks)

    def _summarize_feedback(self, attempt: SolutionAttempt) -> str:
        """Create a brief summary of the feedback."""
        if attempt.success:
            return "All checks passed."
        elif attempt.error:
            return f"Error: {attempt.error[:200]}..."
        else:
            # Take first 200 chars of feedback
            return attempt.feedback[:200] + "..."

    def get_score_trajectory(self) -> list[float]:
        """Get the sequence of soft_scores across iterations."""
        return [a.soft_score for a in self.attempts]

    def get_best_score(self) -> float:
        """Get the highest score achieved so far."""
        if not self.attempts:
            return 0.0
        return max(a.soft_score for a in self.attempts)

    def is_improving(self, window: int = 3, threshold: float = 0.01) -> bool:
        """Check if scores are improving over recent iterations.

        Args:
            window: Number of recent iterations to consider.
            threshold: Minimum improvement to count as "improving".

        Returns:
            True if the trend is upward.
        """
        if len(self.attempts) < 2:
            return True  # Not enough data to determine

        recent = self.get_score_trajectory()[-window:]
        if len(recent) < 2:
            return True

        # Simple check: is the last score better than the first in window?
        return recent[-1] > recent[0] + threshold

    def clear(self) -> None:
        """Clear all history."""
        self.attempts.clear()

    def __len__(self) -> int:
        return len(self.attempts)

    def __iter__(self):
        return iter(self.attempts)

    # -------------------------------------------------------------------------
    # Persistence Methods (SolutionStore integration)
    # -------------------------------------------------------------------------

    def get_historical_context(
        self,
        max_solutions: int = 3,
        min_score: float = 0.9,
    ) -> list[SolutionAttempt]:
        """Retrieve historical successful solutions as few-shot examples.

        Queries the SolutionStore for past successful solutions on similar tasks
        that can be used as context for the current solving session.

        Args:
            max_solutions: Maximum number of historical solutions to retrieve.
            min_score: Minimum score threshold for historical solutions.

        Returns:
            List of historical SolutionAttempts for prompt context.
        """
        if not self._solution_store or not self._task_hash:
            return []

        try:
            records = self._solution_store.get_best_for_task(
                self._task_hash,
                limit=max_solutions,
                min_score=min_score,
                solution_type="iteration_attempt",
            )

            # Convert records to SolutionAttempts
            historical = []
            for record in records:
                attempt = self._record_to_attempt(record)
                historical.append(attempt)

            if historical:
                logger.info(f"Loaded {len(historical)} historical solutions for task")

            return historical

        except Exception as e:
            logger.warning(f"Failed to load historical context: {e}")
            return []

    def persist_best(self) -> bool:
        """Persist the best attempt from this session to the store.

        Call this at the end of a successful solving session to save
        the best solution for future reference.

        Returns:
            True if persistence was successful, False otherwise.
        """
        best = self.get_best()
        if not best or not self._solution_store or not self._task_hash:
            return False

        try:
            self._persist_attempt(best)
            return True
        except Exception as e:
            logger.warning(f"Failed to persist best attempt: {e}")
            return False

    def _persist_attempt(self, attempt: SolutionAttempt) -> None:
        """Persist a single attempt to the SolutionStore."""
        if not self._solution_store or not self._task_hash:
            return

        from deliberate.tracking.solution_store import SolutionRecord

        record = SolutionRecord(
            id=SolutionRecord.new_id(),
            task_hash=self._task_hash,
            workflow_id=self._workflow_id,
            solution_type="iteration_attempt",
            agent=self._agent,
            success=attempt.success,
            overall_score=attempt.soft_score,
            code_content=attempt.code,
            feedback_summary=self._summarize_feedback(attempt),
            error_message=attempt.error,
            generation=attempt.iteration,
            is_valid=attempt.success,
            is_champion=attempt.success and attempt.soft_score >= 1.0,
            token_usage=attempt.token_usage,
            duration_seconds=attempt.duration_seconds,
        )

        self._solution_store.add(record, immediate=True)
        logger.debug(f"Persisted attempt iteration={attempt.iteration} to store")

    def _record_to_attempt(self, record: SolutionRecord) -> SolutionAttempt:
        """Convert a SolutionRecord back to a SolutionAttempt."""
        return SolutionAttempt(
            iteration=record.generation,
            code=record.code_content,
            output="[Historical - output not stored]",
            success=record.success,
            soft_score=record.overall_score,
            feedback=record.feedback_summary or "",
            error=record.error_message,
            timestamp=record.created_at,
            token_usage=record.token_usage or 0,
            duration_seconds=record.duration_seconds or 0.0,
            metadata={"historical": True, "solution_id": record.id},
        )
