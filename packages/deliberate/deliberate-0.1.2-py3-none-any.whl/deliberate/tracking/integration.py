"""Integration helpers for recording workflow results.

Provides functions to record JuryResult data into the performance tracker.
"""

import uuid
from datetime import datetime

from deliberate.tracking.tracker import (
    AgentPerformanceTracker,
    ExecutionRecord,
    NoOpTracker,
    PlanningRecord,
    ReviewRecord,
    WorkflowRecord,
    get_tracker,
)
from deliberate.types import JuryResult
from deliberate.utils.hash_utils import hash_task


def record_jury_result(
    result: JuryResult,
    tracker: AgentPerformanceTracker | NoOpTracker | None = None,
    workflow_id: str | None = None,
) -> str:
    """Record a JuryResult into the performance tracker.

    Args:
        result: The JuryResult from an orchestrator run.
        tracker: Optional tracker instance. If None, uses global tracker.
        workflow_id: Optional workflow ID. If None, generates one.

    Returns:
        The workflow_id used for recording.
    """
    if tracker is None:
        tracker = get_tracker()

    if tracker is None:
        return workflow_id or f"wf-{uuid.uuid4().hex[:12]}"

    if workflow_id is None:
        workflow_id = f"wf-{uuid.uuid4().hex[:12]}"

    now = datetime.now()

    # Determine final score from vote result
    final_score = None
    if result.vote_result and result.vote_result.winner_id:
        final_score = result.vote_result.scores.get(result.vote_result.winner_id)

    # Calculate initial score and refinement cost
    initial_score = final_score
    refinement_token_usage = 0

    if result.refinement_triggered and final_score is not None:
        initial_score = final_score - result.final_improvement
        refinement_token_usage = sum(it.tokens_used for it in result.refinement_iterations)

    # Record the workflow
    workflow_record = WorkflowRecord(
        workflow_id=workflow_id,
        task_hash=hash_task(result.task),
        task_preview=result.task[:200],
        success=result.success,
        total_duration_seconds=result.total_duration_seconds,
        total_tokens=result.total_token_usage,
        total_cost_usd=result.total_cost_usd,
        selected_planner=result.selected_plan.agent if result.selected_plan else None,
        winning_executor=_get_winning_executor(result),
        refinement_triggered=result.refinement_triggered,
        final_score=final_score,
        initial_score=initial_score,
        refinement_token_usage=refinement_token_usage,
        timestamp=now,
    )
    tracker.record_workflow(workflow_record)

    # Record planning performance
    _record_planning_phase(tracker, workflow_id, result, now)

    # Record execution performance
    _record_execution_phase(tracker, workflow_id, result, now)

    # Record review accuracy
    _record_review_phase(tracker, workflow_id, result, now)

    return workflow_id


def _get_winning_executor(result: JuryResult) -> str | None:
    """Get the agent name of the winning executor."""
    if not result.vote_result or not result.execution_results:
        return None

    winner_id = result.vote_result.winner_id
    for er in result.execution_results:
        if er.id == winner_id:
            return er.agent
    return None


def _record_planning_phase(
    tracker: AgentPerformanceTracker | NoOpTracker,
    workflow_id: str,
    result: JuryResult,
    timestamp: datetime,
) -> None:
    """Record planning phase performance.

    Since we only have the selected plan in JuryResult, we record
    just that agent's performance. For tracking non-selected planners,
    we'd need to extend JuryResult to include all proposed plans.
    """
    if not result.selected_plan:
        return

    # Get final score for the selected plan
    final_score = None
    if result.vote_result:
        final_score = result.vote_result.scores.get(result.vote_result.winner_id)

    record = PlanningRecord(
        agent=result.selected_plan.agent,
        was_selected=True,
        led_to_success=result.success,
        final_score=final_score,
        token_usage=result.selected_plan.token_usage,
        timestamp=timestamp,
    )
    tracker.record_planning(workflow_id, record)


def _record_execution_phase(
    tracker: AgentPerformanceTracker | NoOpTracker,
    workflow_id: str,
    result: JuryResult,
    timestamp: datetime,
) -> None:
    """Record execution phase performance for all agents."""
    if not result.execution_results:
        return

    # Get rankings from vote result
    rankings = {}
    if result.vote_result:
        for rank, exec_id in enumerate(result.vote_result.rankings, 1):
            rankings[exec_id] = rank

    total_candidates = len(result.execution_results)
    winner_id = result.vote_result.winner_id if result.vote_result else None

    for er in result.execution_results:
        # Get score for this execution
        score = None
        if result.vote_result and er.id in result.vote_result.scores:
            score = result.vote_result.scores[er.id]

        record = ExecutionRecord(
            agent=er.agent,
            was_winner=(er.id == winner_id),
            success=er.success,
            error_category=er.error_category,
            score=score,
            rank=rankings.get(er.id),
            total_candidates=total_candidates,
            token_usage=er.token_usage,
            duration_seconds=er.duration_seconds,
            timestamp=timestamp,
        )
        tracker.record_execution(workflow_id, record)


def _record_review_phase(
    tracker: AgentPerformanceTracker | NoOpTracker,
    workflow_id: str,
    result: JuryResult,
    timestamp: datetime,
) -> None:
    """Record review accuracy for all reviewers."""
    if not result.reviews or not result.vote_result:
        return

    winner_id = result.vote_result.winner_id

    for review in result.reviews:
        # Find what score this reviewer gave to the actual winner
        winner_score = None
        if result.vote_result.vote_breakdown:
            reviewer_scores = result.vote_result.vote_breakdown.get(review.reviewer, {})
            winner_score = reviewer_scores.get(winner_id)

        record = ReviewRecord(
            agent=review.reviewer,
            candidate_id=review.candidate_id,
            score_given=review.overall_score,
            review_comment=review.comments,
            was_candidate_winner=(review.candidate_id == winner_id),
            final_winner_score=winner_score,
            timestamp=timestamp,
        )
        tracker.record_review(workflow_id, record)
