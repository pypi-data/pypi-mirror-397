"""Tests for TestValidationEvaluator."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from deliberate.adapters.base import AdapterResponse, ModelAdapter
from deliberate.evolution.test_evaluator import (
    KillResult,
    TestValidationEvaluator,
    TestValidationLevel,
    TestValidationResult,
)
from deliberate.evolution.types import Program, ProgramMetrics


def _make_program(code: str, program_id: str = "prog-1") -> Program:
    """Helper to create a Program."""
    return Program(
        id=program_id,
        code=code,
        metrics=ProgramMetrics(),
    )


class TestTestValidationResult:
    """Tests for TestValidationResult dataclass."""

    def test_passed_all_true_when_valid(self):
        """passed_all is True when all validations pass."""
        result = TestValidationResult(
            level_passed=TestValidationLevel.KILL_RATE,
            is_valid=True,
            syntax_valid=True,
            judge_approved=True,
            kill_rate=0.5,
            test_count=3,
        )

        assert result.passed_all is True

    def test_passed_all_false_when_syntax_fails(self):
        """passed_all is False when syntax validation fails."""
        result = TestValidationResult(
            level_passed=TestValidationLevel.SYNTAX,
            is_valid=False,
            syntax_valid=False,
            judge_approved=None,
            kill_rate=0.0,
            test_count=0,
        )

        assert result.passed_all is False

    def test_passed_all_false_when_judge_rejects(self):
        """passed_all is False when judge rejects."""
        result = TestValidationResult(
            level_passed=TestValidationLevel.JUDGE,
            is_valid=False,
            syntax_valid=True,
            judge_approved=False,
            kill_rate=0.0,
            test_count=2,
        )

        assert result.passed_all is False

    def test_passed_all_with_no_judge(self):
        """passed_all is True when judge_approved is None."""
        result = TestValidationResult(
            level_passed=TestValidationLevel.KILL_RATE,
            is_valid=True,
            syntax_valid=True,
            judge_approved=None,  # No judge configured
            kill_rate=0.3,
            test_count=2,
        )

        assert result.passed_all is True


class TestKillResult:
    """Tests for KillResult dataclass."""

    def test_create_kill_result(self):
        """Can create a KillResult."""
        result = KillResult(
            champion_id="champ-1",
            killed=True,
            test_name="test_empty",
            error_message="AssertionError",
            execution_time_ms=50.0,
        )

        assert result.champion_id == "champ-1"
        assert result.killed is True
        assert result.test_name == "test_empty"
        assert result.error_message == "AssertionError"


class TestTestValidationEvaluatorInit:
    """Tests for TestValidationEvaluator initialization."""

    def test_default_values(self):
        """Default values are sensible."""
        evaluator = TestValidationEvaluator()

        assert evaluator.judge_agent is None
        assert evaluator.min_kill_rate == 0.1
        assert evaluator.require_judge_approval is True
        assert evaluator.max_test_time_seconds == 30.0

    def test_custom_values(self):
        """Can set custom configuration."""
        mock_judge = MagicMock(spec=ModelAdapter)
        evaluator = TestValidationEvaluator(
            judge_agent=mock_judge,
            min_kill_rate=0.2,
            require_judge_approval=False,
            max_test_time_seconds=60.0,
        )

        assert evaluator.judge_agent is mock_judge
        assert evaluator.min_kill_rate == 0.2
        assert evaluator.require_judge_approval is False
        assert evaluator.max_test_time_seconds == 60.0


class TestSyntaxValidation:
    """Tests for syntax validation."""

    @pytest.mark.asyncio
    async def test_valid_test_code(self):
        """Valid test code passes syntax validation."""
        evaluator = TestValidationEvaluator()
        code = """
def test_example():
    assert 1 + 1 == 2

def test_another():
    assert True
"""
        result = await evaluator.evaluate(code, run_kill_evaluation=False)

        assert result.syntax_valid is True
        assert result.test_count == 2

    @pytest.mark.asyncio
    async def test_invalid_python_syntax(self):
        """Invalid Python syntax fails validation."""
        evaluator = TestValidationEvaluator()
        code = """
def test_bad(:
    assert True
"""
        result = await evaluator.evaluate(code, run_kill_evaluation=False)

        assert result.syntax_valid is False
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert "Syntax error" in result.errors[0]

    @pytest.mark.asyncio
    async def test_no_test_functions(self):
        """Code without test functions fails validation."""
        evaluator = TestValidationEvaluator()
        code = """
def helper():
    return 42

def another_helper():
    pass
"""
        result = await evaluator.evaluate(code, run_kill_evaluation=False)

        assert result.syntax_valid is False
        assert result.is_valid is False
        assert "No test functions found" in result.errors[0]

    @pytest.mark.asyncio
    async def test_extracts_edge_cases_from_names(self):
        """Extracts edge case hints from test function names."""
        evaluator = TestValidationEvaluator()
        code = """
def test_empty_list():
    assert sort([]) == []

def test_single_element():
    assert sort([1]) == [1]

def test_negative_numbers():
    assert sort([-1, -2]) == [-2, -1]
"""
        result = await evaluator.evaluate(code, run_kill_evaluation=False)

        assert result.syntax_valid is True
        assert "empty list" in result.edge_cases_detected
        assert "single element" in result.edge_cases_detected
        assert "negative numbers" in result.edge_cases_detected


class TestJudgeValidation:
    """Tests for judge validation."""

    @pytest.mark.asyncio
    async def test_judge_approves_legitimate_tests(self):
        """Judge approves legitimate test cases."""
        mock_judge = MagicMock(spec=ModelAdapter)
        mock_judge.call = AsyncMock()
        mock_judge.call.return_value = AdapterResponse(
            content='```json\n{"approved": true, "feedback": "Tests are legitimate"}\n```',
            token_usage=100,
            duration_seconds=1.0,
        )

        evaluator = TestValidationEvaluator(
            judge_agent=mock_judge,
            require_judge_approval=True,
        )

        code = "def test_example(): assert True"
        result = await evaluator.evaluate(
            code,
            task_description="Test a function",
            run_kill_evaluation=False,
        )

        assert result.judge_approved is True
        assert "legitimate" in result.judge_feedback.lower()

    @pytest.mark.asyncio
    async def test_judge_rejects_trick_tests(self):
        """Judge rejects trick tests."""
        mock_judge = MagicMock(spec=ModelAdapter)
        mock_judge.call = AsyncMock()
        mock_judge.call.return_value = AdapterResponse(
            content='```json\n{"approved": false, "feedback": "Tests require impossible behavior"}\n```',
            token_usage=100,
            duration_seconds=1.0,
        )

        evaluator = TestValidationEvaluator(
            judge_agent=mock_judge,
            require_judge_approval=True,
        )

        code = "def test_example(): assert True"
        result = await evaluator.evaluate(
            code,
            task_description="Test a function",
            run_kill_evaluation=False,
        )

        assert result.judge_approved is False
        assert result.is_valid is False
        assert "impossible behavior" in result.judge_feedback.lower()

    @pytest.mark.asyncio
    async def test_skip_judge_without_task_description(self):
        """Skips judge validation without task description."""
        mock_judge = MagicMock(spec=ModelAdapter)
        mock_judge.call = AsyncMock()

        evaluator = TestValidationEvaluator(judge_agent=mock_judge)

        code = "def test_example(): assert True"
        result = await evaluator.evaluate(
            code,
            task_description=None,  # No task description
            run_kill_evaluation=False,
        )

        # Judge should not be called
        mock_judge.call.assert_not_called()
        assert result.judge_approved is None

    @pytest.mark.asyncio
    async def test_continues_without_judge_when_not_required(self):
        """Continues when judge rejects but not required."""
        mock_judge = MagicMock(spec=ModelAdapter)
        mock_judge.call = AsyncMock()
        mock_judge.call.return_value = AdapterResponse(
            content='{"approved": false, "feedback": "Rejected"}',
            token_usage=50,
            duration_seconds=0.5,
        )

        evaluator = TestValidationEvaluator(
            judge_agent=mock_judge,
            require_judge_approval=False,  # Not required
        )

        code = "def test_example(): assert True"
        result = await evaluator.evaluate(
            code,
            task_description="Test",
            run_kill_evaluation=False,
        )

        # Should still be valid since judge is not required
        assert result.judge_approved is False
        assert result.is_valid is True  # Still valid

    @pytest.mark.asyncio
    async def test_judge_error_defaults_to_approved(self):
        """Judge errors default to approved to avoid blocking."""
        mock_judge = MagicMock(spec=ModelAdapter)
        mock_judge.call = AsyncMock()
        mock_judge.call.side_effect = RuntimeError("API Error")

        evaluator = TestValidationEvaluator(judge_agent=mock_judge)

        code = "def test_example(): assert True"
        result = await evaluator.evaluate(
            code,
            task_description="Test",
            run_kill_evaluation=False,
        )

        assert result.judge_approved is True
        assert "failed" in result.judge_feedback.lower()


class TestJudgeResponseParsing:
    """Tests for parsing judge responses."""

    @pytest.mark.asyncio
    async def test_parse_json_code_block(self):
        """Parses JSON in code block."""
        mock_judge = MagicMock(spec=ModelAdapter)
        mock_judge.call = AsyncMock()
        mock_judge.call.return_value = AdapterResponse(
            content='Here is my analysis:\n```json\n{"approved": true, "feedback": "Good tests"}\n```',
            token_usage=50,
            duration_seconds=0.5,
        )

        evaluator = TestValidationEvaluator(judge_agent=mock_judge)

        code = "def test_x(): assert True"
        result = await evaluator.evaluate(code, task_description="Test", run_kill_evaluation=False)

        assert result.judge_approved is True
        assert result.judge_feedback == "Good tests"

    @pytest.mark.asyncio
    async def test_parse_plain_json(self):
        """Parses plain JSON response."""
        mock_judge = MagicMock(spec=ModelAdapter)
        mock_judge.call = AsyncMock()
        mock_judge.call.return_value = AdapterResponse(
            content='{"approved": false, "feedback": "Invalid tests"}',
            token_usage=50,
            duration_seconds=0.5,
        )

        evaluator = TestValidationEvaluator(
            judge_agent=mock_judge,
            require_judge_approval=False,
        )

        code = "def test_x(): assert True"
        result = await evaluator.evaluate(code, task_description="Test", run_kill_evaluation=False)

        assert result.judge_approved is False
        assert result.judge_feedback == "Invalid tests"

    @pytest.mark.asyncio
    async def test_parse_text_fallback(self):
        """Falls back to text parsing when JSON fails."""
        mock_judge = MagicMock(spec=ModelAdapter)
        mock_judge.call = AsyncMock()
        mock_judge.call.return_value = AdapterResponse(
            content="These tests are approved and legitimate.",
            token_usage=50,
            duration_seconds=0.5,
        )

        evaluator = TestValidationEvaluator(judge_agent=mock_judge)

        code = "def test_x(): assert True"
        result = await evaluator.evaluate(code, task_description="Test", run_kill_evaluation=False)

        assert result.judge_approved is True


class TestKillRateEvaluation:
    """Tests for kill rate evaluation."""

    @pytest.mark.asyncio
    async def test_evaluates_against_champions(self):
        """Evaluates tests against champions."""
        evaluator = TestValidationEvaluator(min_kill_rate=0.0)
        champions = [
            _make_program("def solve(): pass", "champ-1"),
            _make_program("def solve(): return 1", "champ-2"),
        ]

        code = "def test_x(): assert True"
        result = await evaluator.evaluate(
            code,
            champions=champions,
            run_kill_evaluation=True,
        )

        # Placeholder implementation returns 0 kills
        assert result.kill_rate == 0.0
        assert result.killed_champions == []

    @pytest.mark.asyncio
    async def test_skip_kill_evaluation_when_disabled(self):
        """Skips kill evaluation when disabled."""
        evaluator = TestValidationEvaluator()
        champions = [_make_program("def solve(): pass")]

        code = "def test_x(): assert True"
        result = await evaluator.evaluate(
            code,
            champions=champions,
            run_kill_evaluation=False,  # Disabled
        )

        # Should not fail due to kill rate when evaluation is disabled
        assert result.is_valid is True


class TestUpdateProgramMetrics:
    """Tests for update_program_metrics."""

    def test_updates_metrics_from_result(self):
        """Updates program metrics from validation result."""
        evaluator = TestValidationEvaluator()
        program = _make_program("def test_x(): pass")

        result = TestValidationResult(
            level_passed=TestValidationLevel.KILL_RATE,
            is_valid=True,
            syntax_valid=True,
            judge_approved=True,
            kill_rate=0.5,
            test_count=5,
            edge_cases_detected=["empty", "null"],
        )

        evaluator.update_program_metrics(program, result)

        assert program.metrics.is_valid_test is True
        assert program.metrics.champion_kill_rate == 0.5
        assert program.metrics.test_cases_generated == 5
        assert program.metrics.covers_edge_cases == ["empty", "null"]
        assert program.metrics.test_score == 0.5  # Based on kill rate

    def test_updates_metrics_for_invalid_result(self):
        """Updates metrics when validation fails."""
        evaluator = TestValidationEvaluator()
        program = _make_program("def bad(): pass")

        result = TestValidationResult(
            level_passed=TestValidationLevel.SYNTAX,
            is_valid=False,
            syntax_valid=False,
            judge_approved=None,
            kill_rate=0.0,
            test_count=0,
        )

        evaluator.update_program_metrics(program, result)

        assert program.metrics.is_valid_test is False
        assert program.metrics.champion_kill_rate == 0.0
        assert program.metrics.test_cases_generated == 0
