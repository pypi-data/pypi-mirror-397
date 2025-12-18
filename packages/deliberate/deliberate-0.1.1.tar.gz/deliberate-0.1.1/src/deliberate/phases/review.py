"""Review phase for deliberate."""

import asyncio
from dataclasses import dataclass
from typing import Any

from deliberate.adapters.base import ModelAdapter
from deliberate.budget.tracker import BudgetTracker
from deliberate.prompts.review import CRITERIA_DESCRIPTIONS, REVIEW_PROMPT
from deliberate.types import ExecutionResult, Review, Score, Verdict, VoteResult
from deliberate.utils.structured_output import extract_tool_call
from deliberate.voting.aggregation import (
    aggregate_approval,
    aggregate_borda,
    aggregate_weighted_borda,
    calculate_confidence,
    get_rankings,
)


@dataclass
class ReviewPhase:
    """Orchestrates the review phase of the jury workflow.

    Multiple agents review execution results and vote on
    the best candidate using configured aggregation.
    """

    agents: list[str]
    adapters: dict[str, ModelAdapter]
    budget: BudgetTracker
    criteria: list[str]
    criteria_descriptions: dict[str, str] | None = None
    scale: str = "1-10"
    aggregation_method: str = "borda"  # borda | approval | weighted_borda
    approval_threshold: float = 0.7
    reject_is_veto: bool = False
    # Validation gating
    validation_required_for_winner: bool = True  # Winner must pass validation
    validation_penalty: float = 0.5  # Score penalty for failing validation (0-1)

    def update_criteria(self, criteria: list[str], descriptions: dict[str, str] | None = None):
        """Replace review criteria with dynamically generated ones."""
        if criteria:
            self.criteria = criteria
        if descriptions is not None:
            self.criteria_descriptions = descriptions

    async def run(
        self,
        task: str,
        candidates: list[ExecutionResult],
    ) -> tuple[list[Review], VoteResult | None]:
        """Run the review phase.

        Args:
            task: The original task description.
            candidates: List of execution results to review.

        Returns:
            Tuple of (reviews, vote_result).
        """
        # Filter to successful candidates (allow missing diffs/summaries)
        valid = [c for c in candidates if c.success]

        if not valid:
            return [], None

        reviews = await self._collect_reviews(task, valid)

        if not reviews:
            # No reviews collected, return first candidate as winner
            return [], VoteResult(
                winner_id=valid[0].id,
                rankings=[c.id for c in valid],
                scores={c.id: 0.5 for c in valid},
                vote_breakdown={},
                confidence=1.0,
            )

        vote_result = self._aggregate(valid, reviews)
        return reviews, vote_result

    async def _collect_reviews(
        self,
        task: str,
        candidates: list[ExecutionResult],
    ) -> list[Review]:
        """Collect reviews from all reviewers for all candidates."""

        async def review_one(
            reviewer: str,
            candidate: ExecutionResult,
        ) -> Review | None:
            # Don't allow self-review
            if reviewer == candidate.agent:
                return None

            adapter = self.adapters.get(reviewer)
            if not adapter:
                return None

            # Build criteria text
            criteria_text = "\n".join(f"- {c}: {self._describe_criterion(c)}" for c in self.criteria)
            tests_section = "No tests were run."
            if candidate.validation_result:
                vr = candidate.validation_result
                tests_section = f"Status: {vr.summary}\n"
                if vr.tests_run > 0:
                    tests_section += f"Tests: {vr.tests_passed}/{vr.tests_run} passed"
                    if vr.tests_failed > 0:
                        tests_section += f", {vr.tests_failed} failed"
                    tests_section += "\n"
                if vr.regression_detected:
                    tests_section += "WARNING: Regression detected - existing tests were broken.\n"
                if not vr.passed:
                    # Include failure details for reviewers
                    failure_log = vr.failure_log
                    if failure_log:
                        tests_section += f"\nFailure Details:\n{failure_log[:1500]}"
                    elif vr.stderr:
                        tests_section += f"\nError Output:\n{vr.stderr[:1000]}"

            prompt = REVIEW_PROMPT.format(
                task=task,
                summary=candidate.summary,
                diff=candidate.diff or "(no diff)",
                tests_section=tests_section,
                criteria=criteria_text,
                scale=self.scale,
            )

            try:
                response = await adapter.call(prompt)
                self.budget.record_usage(reviewer, response.token_usage)
                return self._parse_review(
                    reviewer,
                    candidate.id,
                    response.content,
                    response.token_usage,
                    response.raw_response,
                )
            except Exception as e:
                print(f"Warning: {reviewer} review of {candidate.id} failed: {e}")
                return None

        # Create all review tasks
        tasks = [review_one(r, c) for r in self.agents for c in candidates]
        results = await asyncio.gather(*tasks)
        return [r for r in results if r is not None]

    def _parse_review(
        self,
        reviewer: str,
        candidate_id: str,
        response: str,
        tokens: int,
        raw_response: dict | None,
    ) -> Review:
        """Parse a review response into a Review object."""
        scale_max = self._score_upper_bound()
        default_raw = scale_max / 2 if scale_max > 0 else 5.0

        parsed = extract_tool_call(raw_response, response, "submit_review")
        if parsed:
            scores, computed_overall = self._build_scores(
                parsed.get("scores"),
                scale_max,
                default_raw,
            )

            overall_override = parsed.get("overall") or parsed.get("overall_score")
            overall_score = (
                self._normalize_score(overall_override, scale_max, default_raw)
                if overall_override is not None
                else computed_overall
            )

            return Review(
                reviewer=reviewer,
                candidate_id=candidate_id,
                scores=scores,
                overall_score=overall_score,
                recommendation=self._parse_recommendation(parsed.get("verdict") or parsed.get("recommendation")),
                comments=parsed.get("reasoning") or parsed.get("comments") or parsed.get("feedback"),
                token_usage=tokens,
            )

        # If parsing fails, return a neutral review
        neutral_scores = [Score(c, 0.5, default_raw) for c in self.criteria]
        return Review(
            reviewer=reviewer,
            candidate_id=candidate_id,
            scores=neutral_scores,
            overall_score=0.5,
            recommendation=Verdict.ACCEPT,
            comments=response[:500] if response else None,
            token_usage=tokens,
        )

    def _parse_recommendation(self, value: str | None) -> Verdict:
        """Normalize recommendation string to enum."""
        normalized = (value or "").strip().lower()
        if not normalized:
            return Verdict.ACCEPT
        for rec in Verdict:
            if normalized == rec.value:
                return rec
        if normalized == "approve":
            return Verdict.ACCEPT
        if normalized == "reject":
            return Verdict.REJECT
        return Verdict.REVISE

    def _score_upper_bound(self) -> float:
        """Parse the upper bound from the configured scale."""
        try:
            return float(str(self.scale).split("-")[-1])
        except Exception:
            return 10.0

    def _describe_criterion(self, name: str) -> str:
        """Get description for a criterion from provided map or defaults."""
        if self.criteria_descriptions and name in self.criteria_descriptions:
            return self.criteria_descriptions[name]
        return CRITERIA_DESCRIPTIONS.get(name, "Evaluate this criterion")

    def _normalize_score(self, raw_value: Any, scale_max: float, default_raw: float) -> float:
        """Normalize a raw score to 0-1, clamping to the scale."""
        try:
            raw = float(raw_value)
        except (TypeError, ValueError):
            raw = default_raw

        if scale_max <= 0:
            return 0.5

        normalized = raw / scale_max
        return max(0.0, min(1.0, normalized))

    def _coerce_raw_score(self, value: Any, default_raw: float) -> float:
        """Coerce raw score to float, defaulting when unparseable."""
        try:
            return float(value)
        except (TypeError, ValueError):
            return default_raw

    def _build_scores(
        self,
        raw_scores: dict | None,
        scale_max: float,
        default_raw: float,
    ) -> tuple[list[Score], float]:
        """Build Score objects and compute overall average."""
        scores: list[Score] = []
        total = 0.0

        for criterion in self.criteria:
            raw_value = raw_scores.get(criterion) if raw_scores else None
            raw = self._coerce_raw_score(raw_value, default_raw)
            normalized_value = self._normalize_score(raw, scale_max, default_raw)
            scores.append(
                Score(
                    criterion=criterion,
                    value=normalized_value,
                    raw_value=raw,
                )
            )
            total += normalized_value

        overall = total / len(scores) if scores else 0.5
        return scores, overall

    def _aggregate(
        self,
        candidates: list[ExecutionResult],
        reviews: list[Review],
    ) -> VoteResult:
        """Aggregate reviews into a voting result with validation gating."""
        # Build vote breakdown: reviewer -> candidate -> score
        vote_breakdown: dict[str, dict[str, float]] = {}
        vetoed: set[str] = set()
        for review in reviews:
            if review.reviewer not in vote_breakdown:
                vote_breakdown[review.reviewer] = {}
            vote_breakdown[review.reviewer][review.candidate_id] = review.overall_score
            if self.approval_threshold and self.reject_is_veto:
                if review.recommendation == Verdict.REJECT:
                    vetoed.add(review.candidate_id)

        candidate_ids = [c.id for c in candidates]

        # Build map of candidate ID to validation status
        validation_map: dict[str, bool] = {}  # True = passed, False = failed
        for c in candidates:
            if c.validation_result is not None:
                validation_map[c.id] = c.validation_result.passed

        # Apply the configured aggregation method
        if self.aggregation_method == "approval":
            scores = aggregate_approval(
                candidate_ids,
                vote_breakdown,
                threshold=self.approval_threshold,
            )
        elif self.aggregation_method == "weighted_borda":
            scores = aggregate_weighted_borda(candidate_ids, vote_breakdown)
        else:  # default to borda
            scores = aggregate_borda(candidate_ids, vote_breakdown)

        # Apply veto (set score to 0) if enabled
        if self.reject_is_veto:
            for cid in vetoed:
                scores[cid] = 0.0

        # Apply validation penalty/gating
        if validation_map:
            failing_candidates = {cid for cid, passed in validation_map.items() if not passed}
            passing_candidates = {cid for cid, passed in validation_map.items() if passed}

            if self.validation_required_for_winner and passing_candidates:
                # Set failing candidates' scores to 0 (they cannot win)
                for cid in failing_candidates:
                    scores[cid] = 0.0
            elif self.validation_penalty > 0:
                # Apply penalty to failing candidates
                for cid in failing_candidates:
                    scores[cid] = max(0.0, scores[cid] - self.validation_penalty)

        rankings = get_rankings(scores)
        confidence = calculate_confidence(scores)

        return VoteResult(
            winner_id=rankings[0] if rankings else candidate_ids[0],
            rankings=rankings,
            scores=scores,
            vote_breakdown=vote_breakdown,
            confidence=confidence,
        )
