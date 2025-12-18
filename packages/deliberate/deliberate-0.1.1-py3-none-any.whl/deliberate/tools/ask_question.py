"""Ask question tool for headless agents.

Provides a tool that agents can call to ask questions during execution.
Questions are routed based on the configured strategy (fail, prompt_user,
or auto_answer via another agent).
"""

from dataclasses import dataclass, field
from typing import Awaitable, Callable, Literal

QuestionHandler = Callable[[str], Awaitable[str]]


@dataclass
class QuestionResult:
    """Result of asking a question."""

    question: str
    answer: str | None = None
    answered: bool = False
    error: str | None = None


@dataclass
class AskQuestionTool:
    """Tool that agents can call to ask questions.

    This tool is a client-side wrapper that exposes the 'ask_question' capability
    to agents. In the new architecture, this tool's handler proxies requests
    to the Orchestrator's MCP server via the `ask_question` tool exposed there.

    Attributes:
        strategy: How to handle questions - "fail", "prompt_user", or "auto_answer".
        max_questions: Maximum number of questions allowed before failing.
        handler: Async callback that actually handles the question.
        questions_asked: History of questions asked during this session.
    """

    strategy: Literal["fail", "prompt_user", "auto_answer"] = "fail"
    max_questions: int = 5
    handler: QuestionHandler | None = None
    questions_asked: list[QuestionResult] = field(default_factory=list)

    # Tool metadata for MCP/prompt injection
    name: str = "ask_question"
    description: str = (
        "Ask a clarifying question when you need more information to complete the task. "
        "Use this sparingly - only when the task is genuinely ambiguous or you need "
        "critical information that isn't available in the codebase."
    )

    @property
    def input_schema(self) -> dict:
        """JSON schema for the tool's input parameters."""
        return {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": (
                        "The question to ask. Be specific and concise. Explain what information you need and why."
                    ),
                },
                "context": {
                    "type": "string",
                    "description": (
                        "Optional context about what you've tried or discovered that led to this question."
                    ),
                },
            },
            "required": ["question"],
        }

    @property
    def questions_remaining(self) -> int:
        """Number of questions remaining before hitting the limit."""
        return max(0, self.max_questions - len(self.questions_asked))

    @property
    def is_enabled(self) -> bool:
        """Whether the tool is enabled (strategy is not 'fail')."""
        return self.strategy != "fail"

    async def call(self, question: str, context: str | None = None) -> QuestionResult:
        """Handle a question from the agent.

        Args:
            question: The question being asked.
            context: Optional context about why the question is being asked.

        Returns:
            QuestionResult with the answer or error.

        Raises:
            RuntimeError: If max questions exceeded or strategy is 'fail'.
        """
        # Check if we've hit the limit
        if len(self.questions_asked) >= self.max_questions:
            result = QuestionResult(
                question=question,
                answered=False,
                error=f"Maximum questions ({self.max_questions}) exceeded",
            )
            self.questions_asked.append(result)
            raise RuntimeError(result.error)

        # Handle based on strategy
        if self.strategy == "fail":
            result = QuestionResult(
                question=question,
                answered=False,
                error="Question asking is disabled (strategy='fail')",
            )
            self.questions_asked.append(result)
            raise RuntimeError(result.error)

        if self.handler is None:
            result = QuestionResult(
                question=question,
                answered=False,
                error=f"No handler configured for strategy '{self.strategy}'",
            )
            self.questions_asked.append(result)
            raise RuntimeError(result.error)

        # Call the handler
        try:
            full_question = question
            if context:
                full_question = f"{question}\n\nContext: {context}"

            answer = await self.handler(full_question)
            result = QuestionResult(
                question=question,
                answer=answer,
                answered=True,
            )
            self.questions_asked.append(result)
            return result

        except Exception as e:
            result = QuestionResult(
                question=question,
                answered=False,
                error=str(e),
            )
            self.questions_asked.append(result)
            raise

    def to_prompt_injection(self) -> str:
        """Generate prompt text describing this tool for non-MCP agents.

        Returns:
            Prompt text that describes the ask_question capability.
        """
        if not self.is_enabled:
            return ""

        return f"""
## Ask Question Tool

You have access to an `ask_question` tool that allows you to ask clarifying questions.

**Usage:** When you encounter something ambiguous or need critical information:
1. Call the tool with your question
2. Wait for the response before proceeding

**Limits:** You can ask up to {self.max_questions} questions. Currently {self.questions_remaining} remaining.

**When to use:**
- The task requirements are genuinely ambiguous
- You need information not available in the codebase
- A decision significantly impacts the implementation

**When NOT to use:**
- You can make a reasonable assumption
- The answer is likely in the codebase (search first)
- It's a minor stylistic choice

To ask a question, output:
```
<ask_question>
Your question here. Be specific about what you need to know.
</ask_question>
```
"""

    def reset(self) -> None:
        """Reset the question history for a new session."""
        self.questions_asked.clear()
