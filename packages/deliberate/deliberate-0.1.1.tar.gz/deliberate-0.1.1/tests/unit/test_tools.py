"""Tests for deliberate tools module."""

import pytest

from deliberate.tools import (
    AskQuestionTool,
    QuestionResult,
)


class TestAskQuestionTool:
    """Tests for AskQuestionTool."""

    def test_fail_strategy_not_enabled(self):
        """Tool with fail strategy should not be enabled."""
        tool = AskQuestionTool(strategy="fail", max_questions=5)
        assert not tool.is_enabled
        assert tool.questions_remaining == 5

    def test_prompt_user_strategy_enabled(self):
        """Tool with prompt_user strategy should be enabled."""
        tool = AskQuestionTool(strategy="prompt_user", max_questions=3)
        assert tool.is_enabled
        assert tool.questions_remaining == 3

    def test_auto_answer_strategy_enabled(self):
        """Tool with auto_answer strategy should be enabled."""
        tool = AskQuestionTool(strategy="auto_answer", max_questions=5)
        assert tool.is_enabled

    def test_questions_remaining_decreases(self):
        """Questions remaining should decrease as questions are asked."""
        tool = AskQuestionTool(strategy="prompt_user", max_questions=3)

        # Simulate questions being asked
        tool.questions_asked.append(QuestionResult(question="Q1", answered=True, answer="A1"))
        assert tool.questions_remaining == 2

        tool.questions_asked.append(QuestionResult(question="Q2", answered=True, answer="A2"))
        assert tool.questions_remaining == 1

    def test_prompt_injection_disabled_for_fail(self):
        """Prompt injection should be empty for fail strategy."""
        tool = AskQuestionTool(strategy="fail", max_questions=5)
        assert tool.to_prompt_injection() == ""

    def test_prompt_injection_enabled_for_prompt_user(self):
        """Prompt injection should contain instructions for prompt_user."""
        tool = AskQuestionTool(strategy="prompt_user", max_questions=3)
        prompt = tool.to_prompt_injection()

        assert "Ask Question Tool" in prompt
        assert "3 questions" in prompt
        assert "<ask_question>" in prompt

    def test_reset_clears_history(self):
        """Reset should clear question history."""
        tool = AskQuestionTool(strategy="prompt_user", max_questions=5)
        tool.questions_asked.append(QuestionResult(question="Q1", answered=True, answer="A1"))

        assert len(tool.questions_asked) == 1
        tool.reset()
        assert len(tool.questions_asked) == 0

    @pytest.mark.asyncio
    async def test_call_with_fail_strategy_raises(self):
        """Calling tool with fail strategy should raise."""
        tool = AskQuestionTool(strategy="fail", max_questions=5)

        with pytest.raises(RuntimeError, match="disabled"):
            await tool.call("What is X?")

    @pytest.mark.asyncio
    async def test_call_without_handler_raises(self):
        """Calling tool without handler should raise."""
        tool = AskQuestionTool(strategy="prompt_user", max_questions=5, handler=None)

        with pytest.raises(RuntimeError, match="No handler"):
            await tool.call("What is X?")

    @pytest.mark.asyncio
    async def test_call_with_handler_succeeds(self):
        """Calling tool with handler should return answer."""

        async def mock_handler(question: str) -> str:
            return f"Answer to: {question}"

        tool = AskQuestionTool(
            strategy="prompt_user",
            max_questions=5,
            handler=mock_handler,
        )

        result = await tool.call("What is X?")
        assert result.answered
        assert result.answer == "Answer to: What is X?"
        assert result.question == "What is X?"
        assert len(tool.questions_asked) == 1

    @pytest.mark.asyncio
    async def test_call_exceeds_max_questions(self):
        """Calling tool beyond max should raise."""

        async def mock_handler(question: str) -> str:
            return "answer"

        tool = AskQuestionTool(
            strategy="prompt_user",
            max_questions=2,
            handler=mock_handler,
        )

        await tool.call("Q1")
        await tool.call("Q2")

        with pytest.raises(RuntimeError, match="Maximum questions"):
            await tool.call("Q3")
