"""Prompt templates for deliberate phases."""

from deliberate.prompts.execution import EXECUTION_PROMPT
from deliberate.prompts.planning import DEBATE_PROMPT, JUDGE_PROMPT, PLANNING_PROMPT
from deliberate.prompts.review import REVIEW_PROMPT

__all__ = [
    "PLANNING_PROMPT",
    "DEBATE_PROMPT",
    "JUDGE_PROMPT",
    "EXECUTION_PROMPT",
    "REVIEW_PROMPT",
]
