"""Tests for PlanReviewEvaluator."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from deliberate.adapters.base import AdapterResponse
from deliberate.iteration.evaluators import (
    CriticResult,
    PlanReviewEvaluator,
    PlanStructureCheck,
)
from deliberate.types import Plan


class TestPlanStructureCheck:
    """Tests for PlanStructureCheck dataclass."""

    def test_score_invalid_returns_zero(self):
        """Invalid structure returns 0.0 score."""
        check = PlanStructureCheck(valid=False)
        assert check.score == 0.0

    def test_score_with_no_sections(self):
        """Valid but empty structure gets base score."""
        check = PlanStructureCheck(valid=True)
        assert check.score == 0.0  # 0/3 checks passed

    def test_score_with_steps_only(self):
        """Score with just steps."""
        check = PlanStructureCheck(valid=True, has_steps=True, step_count=2)
        assert check.score == pytest.approx(1 / 3)

    def test_score_with_all_sections(self):
        """Score with all sections present."""
        check = PlanStructureCheck(
            valid=True,
            has_steps=True,
            has_risks=True,
            has_files=True,
            step_count=2,
        )
        assert check.score == pytest.approx(1.0)

    def test_score_bonus_for_multiple_steps(self):
        """Bonus 0.1 for having 3+ steps."""
        check = PlanStructureCheck(
            valid=True,
            has_steps=True,
            has_risks=True,
            has_files=False,
            step_count=3,
        )
        # 2/3 = 0.667 + 0.1 = 0.767
        assert check.score == pytest.approx(2 / 3 + 0.1)

    def test_score_capped_at_one(self):
        """Score cannot exceed 1.0."""
        check = PlanStructureCheck(
            valid=True,
            has_steps=True,
            has_risks=True,
            has_files=True,
            step_count=5,  # Would add 0.1 bonus
        )
        assert check.score == 1.0


class TestCriticResult:
    """Tests for CriticResult dataclass."""

    def test_from_dict_with_all_fields(self):
        """Creates CriticResult from complete dict."""
        data = {
            "feasibility": 0.9,
            "completeness": 0.85,
            "clarity": 0.8,
            "risk_awareness": 0.75,
            "overall_score": 0.82,
            "feedback": "Good plan",
            "suggestions": ["Add more detail"],
        }
        result = CriticResult.from_dict(data)

        assert result.feasibility == 0.9
        assert result.completeness == 0.85
        assert result.clarity == 0.8
        assert result.risk_awareness == 0.75
        assert result.overall_score == 0.82
        assert result.feedback == "Good plan"
        assert result.suggestions == ["Add more detail"]

    def test_from_dict_with_missing_fields(self):
        """Creates CriticResult with defaults for missing fields."""
        data = {"feasibility": 0.9}
        result = CriticResult.from_dict(data)

        assert result.feasibility == 0.9
        assert result.completeness == 0.0
        assert result.clarity == 0.0
        assert result.risk_awareness == 0.0
        assert result.overall_score == 0.0
        assert result.feedback == ""
        assert result.suggestions == []


def _make_plan(content: str) -> Plan:
    """Helper to create a Plan with required fields."""
    return Plan(
        id="test-plan-1",
        agent="test-agent",
        content=content,
    )


class TestPlanReviewEvaluatorStructureCheck:
    """Tests for structure checking logic."""

    def test_detects_numbered_steps(self):
        """Finds numbered steps in plan content."""
        evaluator = PlanReviewEvaluator()
        plan_content = """
# Implementation Plan

1. First step to do something
2. Second step follows
3. Third step completes

## Risks
Some risk here

## Files
- src/main.py
"""
        check = evaluator._check_structure(plan_content)

        assert check.valid is True
        assert check.has_steps is True
        assert check.step_count == 3

    def test_detects_step_keyword_format(self):
        """Finds 'Step N' format."""
        evaluator = PlanReviewEvaluator()
        plan_content = """
Step 1: Do this
Step 2: Do that

Risks: Something might fail
File: src/main.py
"""
        check = evaluator._check_structure(plan_content)

        assert check.valid is True
        assert check.has_steps is True
        assert check.step_count == 2

    def test_detects_checkbox_steps(self):
        """Finds checkbox-style steps."""
        evaluator = PlanReviewEvaluator()
        plan_content = """
- [ ] First task
- [ ] Second task
- [x] Completed task

Risk: None
File: test.py
"""
        check = evaluator._check_structure(plan_content)

        assert check.valid is True
        assert check.has_steps is True
        assert check.step_count == 3

    def test_detects_bullet_steps(self):
        """Finds bullet-style steps."""
        evaluator = PlanReviewEvaluator()
        plan_content = """
* First item
* Second item

Risk involved
src/file.py affected
"""
        check = evaluator._check_structure(plan_content)

        assert check.valid is True
        assert check.has_steps is True
        assert check.step_count == 2

    def test_fails_without_enough_steps(self):
        """Invalid when fewer than 2 steps found."""
        evaluator = PlanReviewEvaluator()
        plan_content = """
1. Single step only

Risks and files mentioned
"""
        check = evaluator._check_structure(plan_content)

        assert check.valid is False
        assert check.has_steps is False
        assert check.step_count == 1
        assert "Missing numbered implementation steps" in check.issues[0]

    def test_detects_risk_section(self):
        """Finds risk keywords in content."""
        evaluator = PlanReviewEvaluator()

        for keyword in ["risk", "concern", "potential issue", "caveat", "warning"]:
            plan_content = f"""
1. Step one
2. Step two
{keyword}: Something to watch
"""
            check = evaluator._check_structure(plan_content)
            assert check.has_risks is True, f"Failed to detect keyword: {keyword}"

    def test_missing_risk_section(self):
        """Reports missing risk section."""
        evaluator = PlanReviewEvaluator()
        plan_content = """
1. Step one
2. Step two
src/main.py
"""
        check = evaluator._check_structure(plan_content)

        assert check.has_risks is False
        assert any("risk" in issue.lower() for issue in check.issues)

    def test_detects_file_references(self):
        """Finds file path patterns."""
        evaluator = PlanReviewEvaluator()

        test_cases = [
            "file.py",
            "src/main.ts",
            "lib/utils.js",
            "tests/test_main.py",
            "component.tsx",
            "app.jsx",
            "main.rs",
        ]

        for file_ref in test_cases:
            plan_content = f"""
1. Step one
2. Step two
Risk: none
{file_ref}
"""
            check = evaluator._check_structure(plan_content)
            assert check.has_files is True, f"Failed to detect file: {file_ref}"

    def test_missing_file_references(self):
        """Reports missing file list."""
        evaluator = PlanReviewEvaluator()
        # "file" keyword appears in the structure check keywords, so avoid that word
        plan_content = """
1. Step one
2. Step two
Risk: something
No code locations mentioned here
"""
        check = evaluator._check_structure(plan_content)

        assert check.has_files is False
        assert any("file" in issue.lower() for issue in check.issues)


def _make_adapter_response(content: str) -> AdapterResponse:
    """Helper to create an AdapterResponse with required fields."""
    return AdapterResponse(
        content=content,
        token_usage=100,
        duration_seconds=1.0,
    )


class TestPlanReviewEvaluatorEvaluate:
    """Tests for the evaluate method."""

    @pytest.mark.asyncio
    async def test_early_return_on_invalid_structure_when_required(self):
        """Returns early without LLM call when structure is invalid."""
        mock_agent = MagicMock()
        evaluator = PlanReviewEvaluator(critic_agent=mock_agent, require_structure=True)

        plan = _make_plan("No steps here")
        context = {"task": "Test task"}

        feedback, raw = await evaluator.evaluate(plan, context)

        # Should not call the critic agent
        mock_agent.call.assert_not_called()

        assert feedback.match is False
        assert feedback.soft_score == 0.0
        assert raw["passed"] is False
        assert raw["critic"] is None

    @pytest.mark.asyncio
    async def test_allows_invalid_structure_when_not_required(self):
        """Continues to LLM when structure check is disabled."""
        mock_agent = AsyncMock()
        mock_agent.call.return_value = _make_adapter_response(
            '{"feasibility": 0.5, "completeness": 0.5, '
            '"clarity": 0.5, "risk_awareness": 0.5, '
            '"overall_score": 0.5, "feedback": "OK"}'
        )
        evaluator = PlanReviewEvaluator(critic_agent=mock_agent, require_structure=False)

        plan = _make_plan("No steps here")
        context = {"task": "Test task"}

        feedback, raw = await evaluator.evaluate(plan, context)

        # Should call the critic agent
        mock_agent.call.assert_called_once()
        assert raw["critic"] is not None

    @pytest.mark.asyncio
    async def test_structure_only_when_no_critic_agent(self):
        """Returns structure-based score when no critic agent provided."""
        evaluator = PlanReviewEvaluator(critic_agent=None)

        plan = _make_plan("""
1. First step
2. Second step
3. Third step

Risk: Something might fail
File: src/main.py
""")
        context = {"task": "Test task"}

        feedback, raw = await evaluator.evaluate(plan, context)

        assert raw["critic"] is None
        assert feedback.soft_score == raw["structure"].score

    @pytest.mark.asyncio
    async def test_critic_score_used_when_available(self):
        """Uses critic score when agent is provided."""
        mock_agent = AsyncMock()
        mock_agent.call.return_value = _make_adapter_response(
            '{"feasibility": 0.95, "completeness": 0.9, '
            '"clarity": 0.92, "risk_awareness": 0.88, '
            '"overall_score": 0.91, "feedback": "Excellent plan", '
            '"suggestions": ["Minor improvement"]}'
        )
        evaluator = PlanReviewEvaluator(critic_agent=mock_agent, success_threshold=0.9)

        plan = _make_plan("""
1. First step
2. Second step

Risk: Considered
src/main.py
""")
        context = {"task": "Build a feature"}

        feedback, raw = await evaluator.evaluate(plan, context)

        assert raw["critic"] is not None
        assert raw["critic"].overall_score == 0.91
        assert feedback.soft_score == 0.91
        assert feedback.match is True  # 0.91 >= 0.9 threshold
        assert raw["passed"] is True

    @pytest.mark.asyncio
    async def test_below_threshold_fails(self):
        """Plan below threshold is marked as failure."""
        mock_agent = AsyncMock()
        mock_agent.call.return_value = _make_adapter_response(
            '{"feasibility": 0.7, "completeness": 0.6, '
            '"clarity": 0.7, "risk_awareness": 0.5, '
            '"overall_score": 0.65, "feedback": "Needs work"}'
        )
        evaluator = PlanReviewEvaluator(critic_agent=mock_agent, success_threshold=0.9)

        plan = _make_plan("""
1. Step 1
2. Step 2
Risk: noted
code.py
""")
        context = {"task": "Task"}

        feedback, raw = await evaluator.evaluate(plan, context)

        assert feedback.match is False
        assert raw["passed"] is False
        assert feedback.soft_score == 0.65

    @pytest.mark.asyncio
    async def test_handles_critic_exception(self):
        """Returns neutral scores when critic fails."""
        mock_agent = AsyncMock()
        mock_agent.call.side_effect = Exception("API error")
        evaluator = PlanReviewEvaluator(critic_agent=mock_agent)

        plan = _make_plan("""
1. Step 1
2. Step 2
Risk: noted
code.py
""")
        context = {"task": "Task"}

        feedback, raw = await evaluator.evaluate(plan, context)

        assert raw["critic"] is not None
        assert raw["critic"].overall_score == 0.5  # Neutral
        assert "failed" in raw["critic"].feedback.lower()

    @pytest.mark.asyncio
    async def test_metadata_includes_scores(self):
        """Feedback context metadata contains detailed scores."""
        mock_agent = AsyncMock()
        mock_agent.call.return_value = _make_adapter_response(
            '{"feasibility": 0.9, "completeness": 0.85, '
            '"clarity": 0.8, "risk_awareness": 0.75, '
            '"overall_score": 0.82, "feedback": "Good"}'
        )
        evaluator = PlanReviewEvaluator(critic_agent=mock_agent)

        plan = _make_plan("""
1. Step 1
2. Step 2
Risk: noted
code.py
""")
        context = {"task": "Task"}

        feedback, _ = await evaluator.evaluate(plan, context)

        assert "structure_check" in feedback.metadata
        assert "critic_scores" in feedback.metadata
        assert feedback.metadata["critic_scores"]["feasibility"] == 0.9
        assert feedback.metadata["critic_scores"]["completeness"] == 0.85


class TestPlanReviewEvaluatorIsSuccess:
    """Tests for is_success method."""

    def test_success_at_threshold(self):
        """Returns True when score equals threshold."""
        evaluator = PlanReviewEvaluator(success_threshold=0.9)
        from deliberate.iteration.types import FeedbackContext

        feedback = FeedbackContext(expected="", actual="", match=True, soft_score=0.9)
        assert evaluator.is_success(feedback) is True

    def test_success_above_threshold(self):
        """Returns True when score exceeds threshold."""
        evaluator = PlanReviewEvaluator(success_threshold=0.9)
        from deliberate.iteration.types import FeedbackContext

        feedback = FeedbackContext(expected="", actual="", match=True, soft_score=0.95)
        assert evaluator.is_success(feedback) is True

    def test_failure_below_threshold(self):
        """Returns False when score below threshold."""
        evaluator = PlanReviewEvaluator(success_threshold=0.9)
        from deliberate.iteration.types import FeedbackContext

        feedback = FeedbackContext(expected="", actual="", match=False, soft_score=0.85)
        assert evaluator.is_success(feedback) is False


class TestPlanReviewEvaluatorCriticParsing:
    """Tests for critic response parsing."""

    def test_parses_valid_json(self):
        """Extracts scores from valid JSON response."""
        evaluator = PlanReviewEvaluator()
        response = """
Here is my evaluation:

```json
{
  "feasibility": 0.85,
  "completeness": 0.9,
  "clarity": 0.8,
  "risk_awareness": 0.7,
  "overall_score": 0.81,
  "feedback": "Good plan with room for improvement",
  "suggestions": ["Add error handling", "Consider edge cases"]
}
```
"""
        result = evaluator._parse_critic_response(response)

        assert result.feasibility == 0.85
        assert result.completeness == 0.9
        assert result.clarity == 0.8
        assert result.risk_awareness == 0.7
        assert result.overall_score == 0.81

    def test_extracts_scores_from_text(self):
        """Falls back to regex extraction when JSON fails."""
        evaluator = PlanReviewEvaluator()
        response = """
My evaluation:
- feasibility: 0.8
- completeness: 0.75
- clarity: 0.9
- risk_awareness: 0.6

Overall this is decent.
"""
        result = evaluator._parse_critic_response(response)

        assert result.feasibility == 0.8
        assert result.completeness == 0.75
        assert result.clarity == 0.9
        assert result.risk_awareness == 0.6

    def test_defaults_for_unparseable_response(self):
        """Returns neutral 0.5 scores when parsing fails completely."""
        evaluator = PlanReviewEvaluator()
        response = "This response has no scores at all."

        result = evaluator._parse_critic_response(response)

        assert result.feasibility == 0.5
        assert result.completeness == 0.5
        assert result.clarity == 0.5
        assert result.risk_awareness == 0.5

    def test_calculates_overall_when_missing(self):
        """Calculates weighted overall score if not in response."""
        evaluator = PlanReviewEvaluator(
            weights={
                "feasibility": 0.3,
                "completeness": 0.3,
                "clarity": 0.2,
                "risk_awareness": 0.2,
            }
        )
        response = """
{
  "feasibility": 1.0,
  "completeness": 1.0,
  "clarity": 1.0,
  "risk_awareness": 1.0,
  "feedback": "Perfect"
}
"""
        result = evaluator._parse_critic_response(response)

        # Should calculate: 1.0*0.3 + 1.0*0.3 + 1.0*0.2 + 1.0*0.2 = 1.0
        assert result.overall_score == 1.0

    def test_caps_scores_at_one(self):
        """Ensures extracted scores don't exceed 1.0."""
        evaluator = PlanReviewEvaluator()
        response = "feasibility: 1.5"  # Invalid score > 1.0

        result = evaluator._parse_critic_response(response)

        assert result.feasibility == 1.0


class TestPlanReviewEvaluatorPromptBuilding:
    """Tests for critic prompt construction."""

    def test_prompt_includes_task(self):
        """Critic prompt contains original task."""
        evaluator = PlanReviewEvaluator()
        prompt = evaluator._build_critic_prompt("Plan content", "Build authentication")

        assert "Build authentication" in prompt
        assert "Original Task" in prompt

    def test_prompt_includes_plan(self):
        """Critic prompt contains plan content."""
        evaluator = PlanReviewEvaluator()
        prompt = evaluator._build_critic_prompt("My detailed plan here", "Task")

        assert "My detailed plan here" in prompt
        assert "Plan to Review" in prompt

    def test_prompt_includes_weights(self):
        """Critic prompt shows criterion weights."""
        evaluator = PlanReviewEvaluator(
            weights={
                "feasibility": 0.4,
                "completeness": 0.3,
                "clarity": 0.2,
                "risk_awareness": 0.1,
            }
        )
        prompt = evaluator._build_critic_prompt("Plan", "Task")

        assert "40%" in prompt
        assert "30%" in prompt
        assert "20%" in prompt
        assert "10%" in prompt

    def test_prompt_requests_json_format(self):
        """Critic prompt asks for JSON response."""
        evaluator = PlanReviewEvaluator()
        prompt = evaluator._build_critic_prompt("Plan", "Task")

        assert "json" in prompt.lower()
        assert "feasibility" in prompt
        assert "completeness" in prompt
        assert "clarity" in prompt
        assert "risk_awareness" in prompt
