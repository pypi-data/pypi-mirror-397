"""Tools that can be exposed to headless agents."""

from deliberate.tools.ask_question import (
    AskQuestionTool,
    QuestionHandler,
    QuestionResult,
)

__all__ = [
    # Prompt injection (for non-MCP agents)
    "AskQuestionTool",
    "QuestionHandler",
    "QuestionResult",
]
