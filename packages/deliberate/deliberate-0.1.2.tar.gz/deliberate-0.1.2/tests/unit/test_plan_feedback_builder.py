"""Tests for PlanFeedbackBuilder."""

from deliberate.iteration.evaluators import CriticResult, PlanStructureCheck
from deliberate.iteration.feedback import PlanFeedbackBuilder
from deliberate.iteration.types import FeedbackContext


def _make_structure_check(
    valid: bool = True,
    has_steps: bool = True,
    has_risks: bool = True,
    has_files: bool = True,
    step_count: int = 3,
    issues: list[str] | None = None,
) -> PlanStructureCheck:
    """Helper to create a PlanStructureCheck."""
    return PlanStructureCheck(
        valid=valid,
        has_steps=has_steps,
        has_risks=has_risks,
        has_files=has_files,
        step_count=step_count,
        issues=issues or [],
    )


def _make_critic_result(
    feasibility: float = 0.9,
    completeness: float = 0.85,
    clarity: float = 0.8,
    risk_awareness: float = 0.75,
    overall_score: float = 0.82,
    feedback: str = "Good plan",
    suggestions: list[str] | None = None,
) -> CriticResult:
    """Helper to create a CriticResult."""
    return CriticResult(
        feasibility=feasibility,
        completeness=completeness,
        clarity=clarity,
        risk_awareness=risk_awareness,
        overall_score=overall_score,
        feedback=feedback,
        suggestions=suggestions or [],
    )


def _make_context(
    match: bool = True,
    soft_score: float = 0.9,
) -> FeedbackContext:
    """Helper to create a FeedbackContext."""
    return FeedbackContext(
        expected="Plan score >= 0.9",
        actual="Plan score: 0.90",
        match=match,
        soft_score=soft_score,
    )


class TestPlanFeedbackBuilderBasic:
    """Basic tests for PlanFeedbackBuilder."""

    def test_builds_feedback_for_passing_plan(self):
        """Builds success feedback for passing plan."""
        builder = PlanFeedbackBuilder(success_threshold=0.9)

        evaluation = {
            "structure": _make_structure_check(),
            "critic": _make_critic_result(overall_score=0.92),
            "passed": True,
            "score": 0.92,
            "suggestions": ["Minor polish needed"],
        }
        context = _make_context(match=True, soft_score=0.92)

        feedback = builder.build(evaluation, context)

        assert feedback.success is True
        assert feedback.score == 0.92
        assert "PASSED" in feedback.text

    def test_builds_feedback_for_failing_plan(self):
        """Builds failure feedback for failing plan."""
        builder = PlanFeedbackBuilder(success_threshold=0.9)

        evaluation = {
            "structure": _make_structure_check(valid=False, issues=["Missing steps"]),
            "critic": None,
            "passed": False,
            "score": 0.3,
            "suggestions": [],
        }
        context = _make_context(match=False, soft_score=0.3)

        feedback = builder.build(evaluation, context)

        assert feedback.success is False
        assert feedback.score == 0.3
        assert "improvement" in feedback.text.lower()

    def test_includes_structure_issues_in_issues_list(self):
        """Structure issues are included in feedback issues."""
        builder = PlanFeedbackBuilder()

        evaluation = {
            "structure": _make_structure_check(
                valid=False,
                issues=["Missing numbered steps", "No risk section"],
            ),
            "critic": None,
            "passed": False,
            "score": 0.0,
            "suggestions": [],
        }
        context = _make_context(match=False, soft_score=0.0)

        feedback = builder.build(evaluation, context)

        assert "Missing numbered steps" in feedback.issues
        assert "No risk section" in feedback.issues

    def test_includes_critic_suggestions(self):
        """Critic suggestions are included in feedback suggestions."""
        builder = PlanFeedbackBuilder()

        evaluation = {
            "structure": _make_structure_check(),
            "critic": _make_critic_result(suggestions=["Add error handling", "Consider edge cases"]),
            "passed": True,
            "score": 0.91,
            "suggestions": ["More tests needed"],
        }
        context = _make_context(match=True, soft_score=0.91)

        feedback = builder.build(evaluation, context)

        # Should include both existing and critic suggestions
        assert "More tests needed" in feedback.suggestions
        assert "Add error handling" in feedback.suggestions
        assert "Consider edge cases" in feedback.suggestions


class TestPlanFeedbackBuilderScores:
    """Tests for score handling."""

    def test_per_item_scores_from_critic(self):
        """Per-item scores contain critic criteria scores."""
        builder = PlanFeedbackBuilder()

        evaluation = {
            "structure": _make_structure_check(),
            "critic": _make_critic_result(
                feasibility=0.9,
                completeness=0.8,
                clarity=0.7,
                risk_awareness=0.6,
            ),
            "passed": True,
            "score": 0.75,
            "suggestions": [],
        }
        context = _make_context()

        feedback = builder.build(evaluation, context)

        assert feedback.per_item_scores == [0.9, 0.8, 0.7, 0.6]

    def test_per_item_scores_without_critic(self):
        """Per-item scores use overall score when no critic."""
        builder = PlanFeedbackBuilder()

        evaluation = {
            "structure": _make_structure_check(),
            "critic": None,
            "passed": True,
            "score": 0.85,
            "suggestions": [],
        }
        context = _make_context(soft_score=0.85)

        feedback = builder.build(evaluation, context)

        assert feedback.per_item_scores == [0.85]

    def test_uses_context_score_as_fallback(self):
        """Falls back to context score when not in evaluation."""
        builder = PlanFeedbackBuilder()

        evaluation = {
            "structure": _make_structure_check(),
            "critic": None,
            "passed": True,
            # No 'score' key
            "suggestions": [],
        }
        context = _make_context(soft_score=0.77)

        feedback = builder.build(evaluation, context)

        assert feedback.score == 0.77


class TestPlanFeedbackBuilderMetadata:
    """Tests for feedback metadata."""

    def test_metadata_includes_structure_validity(self):
        """Metadata contains structure validity."""
        builder = PlanFeedbackBuilder(success_threshold=0.85)

        evaluation = {
            "structure": _make_structure_check(valid=True),
            "critic": None,
            "passed": True,
            "score": 0.9,
            "suggestions": [],
        }
        context = _make_context()

        feedback = builder.build(evaluation, context)

        assert feedback.metadata["structure_valid"] is True
        assert feedback.metadata["threshold"] == 0.85

    def test_metadata_includes_critic_presence(self):
        """Metadata indicates whether critic was used."""
        builder = PlanFeedbackBuilder()

        # With critic
        evaluation_with_critic = {
            "structure": _make_structure_check(),
            "critic": _make_critic_result(),
            "passed": True,
            "score": 0.9,
            "suggestions": [],
        }
        feedback1 = builder.build(evaluation_with_critic, _make_context())
        assert feedback1.metadata["has_critic"] is True

        # Without critic
        evaluation_without_critic = {
            "structure": _make_structure_check(),
            "critic": None,
            "passed": True,
            "score": 0.9,
            "suggestions": [],
        }
        feedback2 = builder.build(evaluation_without_critic, _make_context())
        assert feedback2.metadata["has_critic"] is False


class TestPlanFeedbackBuilderTextFormatting:
    """Tests for feedback text formatting."""

    def test_text_includes_structure_analysis(self):
        """Feedback text shows structure analysis."""
        builder = PlanFeedbackBuilder()

        evaluation = {
            "structure": _make_structure_check(
                valid=True,
                step_count=5,
                has_risks=True,
                has_files=False,
            ),
            "critic": None,
            "passed": True,
            "score": 0.8,
            "suggestions": [],
        }
        context = _make_context()

        feedback = builder.build(evaluation, context)

        assert "Structure Analysis" in feedback.text
        assert "5 implementation steps" in feedback.text
        assert "Risk section present" in feedback.text
        assert "Missing affected files" in feedback.text

    def test_text_includes_critic_scores(self):
        """Feedback text shows critic evaluation scores."""
        builder = PlanFeedbackBuilder()

        evaluation = {
            "structure": _make_structure_check(),
            "critic": _make_critic_result(
                feasibility=0.95,
                completeness=0.88,
                clarity=0.92,
                risk_awareness=0.85,
                overall_score=0.90,
                feedback="Excellent detailed plan",
            ),
            "passed": True,
            "score": 0.90,
            "suggestions": [],
        }
        context = _make_context()

        feedback = builder.build(evaluation, context)

        assert "Critic Evaluation" in feedback.text
        assert "Feasibility: 0.95" in feedback.text
        assert "Completeness: 0.88" in feedback.text
        assert "Clarity: 0.92" in feedback.text
        assert "Risk Awareness: 0.85" in feedback.text
        assert "Overall: 0.90" in feedback.text
        assert "Excellent detailed plan" in feedback.text

    def test_text_includes_issues_when_failing(self):
        """Feedback text lists issues when plan fails."""
        builder = PlanFeedbackBuilder()

        evaluation = {
            "structure": _make_structure_check(
                valid=False,
                issues=["Missing numbered steps", "No risk section"],
            ),
            "critic": None,
            "passed": False,
            "score": 0.2,
            "suggestions": [],
        }
        context = _make_context(match=False, soft_score=0.2)

        feedback = builder.build(evaluation, context)

        assert "Issues to Address" in feedback.text
        assert "Missing numbered steps" in feedback.text
        assert "No risk section" in feedback.text

    def test_text_shows_threshold_when_failing(self):
        """Feedback text shows threshold when plan fails."""
        builder = PlanFeedbackBuilder(success_threshold=0.85)

        evaluation = {
            "structure": _make_structure_check(),
            "critic": _make_critic_result(overall_score=0.7),
            "passed": False,
            "score": 0.7,
            "suggestions": [],
        }
        context = _make_context(match=False, soft_score=0.7)

        feedback = builder.build(evaluation, context)

        assert "0.85" in feedback.text
        assert "needs improvement" in feedback.text.lower()


class TestPlanFeedbackBuilderEdgeCases:
    """Edge case tests."""

    def test_handles_missing_structure(self):
        """Handles evaluation without structure check."""
        builder = PlanFeedbackBuilder()

        evaluation = {
            "structure": None,
            "critic": _make_critic_result(),
            "passed": True,
            "score": 0.9,
            "suggestions": [],
        }
        context = _make_context()

        feedback = builder.build(evaluation, context)

        assert feedback.success is True
        assert feedback.metadata["structure_valid"] is None

    def test_handles_empty_evaluation(self):
        """Handles minimal evaluation dict."""
        builder = PlanFeedbackBuilder()

        evaluation = {}
        context = _make_context(match=True, soft_score=0.5)

        feedback = builder.build(evaluation, context)

        # Should use context values
        assert feedback.success is True
        assert feedback.score == 0.5

    def test_limits_issues_in_issues_section(self):
        """Limits number of issues in 'Issues to Address' section."""
        builder = PlanFeedbackBuilder()

        # Create 20 issues
        many_issues = [f"Issue {i}" for i in range(20)]

        evaluation = {
            "structure": _make_structure_check(valid=False, issues=many_issues),
            "critic": None,
            "passed": False,
            "score": 0.1,
            "suggestions": [],
        }
        context = _make_context(match=False, soft_score=0.1)

        feedback = builder.build(evaluation, context)

        # All issues should be in the issues list
        assert len(feedback.issues) == 20

        # Issues to Address section should be limited to 10
        issues_section_start = feedback.text.find("## Issues to Address:")
        if issues_section_start > 0:
            issues_section = feedback.text[issues_section_start:]
            # Count issues in just that section
            issue_count = issues_section.count("- Issue")
            assert issue_count == 10
