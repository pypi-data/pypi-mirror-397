"""GitHub Bot integration for Deliberate.

This module provides GitHub Bot functionality to trigger deliberate workflows
from PR comments and deliver results as commits and comments.
"""

from deliberate.github.actions import (
    PREDEFINED_ACTIONS,
    PredefinedAction,
    format_task,
    get_predefined_action,
    list_actions,
)
from deliberate.github.bot import (
    ParsedCommand,
    format_failure_comment,
    format_plan_comment,
    format_rejected_comment,
    format_success_comment,
    format_timeout_comment,
    parse_command,
)

__all__ = [
    # actions
    "PredefinedAction",
    "PREDEFINED_ACTIONS",
    "format_task",
    "get_predefined_action",
    "list_actions",
    # bot
    "ParsedCommand",
    "parse_command",
    "format_plan_comment",
    "format_success_comment",
    "format_failure_comment",
    "format_timeout_comment",
    "format_rejected_comment",
]
