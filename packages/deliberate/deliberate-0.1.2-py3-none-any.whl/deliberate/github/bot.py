"""GitHub Bot command parsing and handling.

Parses commands from PR comments like:
- /deliberate review
- /deliberate optimize --profile cheap
- /deliberate implement "add caching"
"""

import re
from dataclasses import dataclass

from deliberate.github.actions import PREDEFINED_ACTIONS, format_task, get_predefined_action


@dataclass
class ParsedCommand:
    """A parsed /deliberate command from a PR comment."""

    action: str
    custom_task: str | None
    profile: str
    raw_command: str
    valid: bool
    error: str | None = None

    @property
    def task(self) -> str:
        """Get the formatted task string for this command."""
        action_def = get_predefined_action(self.action)
        if not action_def:
            raise ValueError(f"Unknown action: {self.action}")
        return format_task(action_def, self.custom_task)


# Regex pattern for parsing /deliberate commands
# Matches: /deliberate <action> ["custom task"] [--profile <name>]
COMMAND_PATTERN = re.compile(
    r"""
    ^/deliberate\s+                      # Command prefix
    (?P<action>\w+)                      # Action name (review, optimize, etc.)
    (?:\s+"(?P<task>[^"]+)")?            # Optional quoted custom task
    (?:\s+--profile\s+(?P<profile>\w+))? # Optional profile flag
    \s*$                                 # End of command
    """,
    re.VERBOSE | re.IGNORECASE,
)

# Alternative pattern for multiline custom tasks
COMMAND_PATTERN_MULTILINE = re.compile(
    r"""
    ^/deliberate\s+                      # Command prefix
    (?P<action>\w+)                      # Action name
    (?:\s+--profile\s+(?P<profile>\w+))? # Optional profile flag
    \s*\n                                # Newline
    (?P<task>.+)                         # Everything after is the task
    """,
    re.VERBOSE | re.IGNORECASE | re.DOTALL,
)


def parse_command(comment_body: str) -> ParsedCommand:
    """Parse a /deliberate command from a PR comment body.

    Supports formats:
    - /deliberate review
    - /deliberate optimize --profile cheap
    - /deliberate implement "add error handling"
    - /deliberate implement --profile max_quality
      Multi-line task description here

    Args:
        comment_body: The full text of the PR comment

    Returns:
        ParsedCommand with parsed values or error information
    """
    # Strip leading/trailing whitespace
    body = comment_body.strip()

    # Check if this is a deliberate command at all
    if not body.lower().startswith("/deliberate"):
        return ParsedCommand(
            action="",
            custom_task=None,
            profile="balanced",
            raw_command=body,
            valid=False,
            error="Not a /deliberate command",
        )

    # Try single-line pattern first
    match = COMMAND_PATTERN.match(body)
    if match:
        action = match.group("action").lower()
        custom_task = match.group("task")
        profile = match.group("profile") or "balanced"

        # Validate action
        if action not in PREDEFINED_ACTIONS:
            return ParsedCommand(
                action=action,
                custom_task=custom_task,
                profile=profile,
                raw_command=body,
                valid=False,
                error=f"Unknown action: {action}. Available: {', '.join(PREDEFINED_ACTIONS.keys())}",
            )

        # Validate implement requires custom task
        if action == "implement" and not custom_task:
            return ParsedCommand(
                action=action,
                custom_task=custom_task,
                profile=profile,
                raw_command=body,
                valid=False,
                error="'implement' action requires a task description",
            )

        return ParsedCommand(
            action=action,
            custom_task=custom_task,
            profile=profile,
            raw_command=body,
            valid=True,
        )

    # Try multiline pattern
    match = COMMAND_PATTERN_MULTILINE.match(body)
    if match:
        action = match.group("action").lower()
        custom_task = match.group("task").strip()
        profile = match.group("profile") or "balanced"

        # Validate action
        if action not in PREDEFINED_ACTIONS:
            return ParsedCommand(
                action=action,
                custom_task=custom_task,
                profile=profile,
                raw_command=body,
                valid=False,
                error=f"Unknown action: {action}. Available: {', '.join(PREDEFINED_ACTIONS.keys())}",
            )

        return ParsedCommand(
            action=action,
            custom_task=custom_task,
            profile=profile,
            raw_command=body,
            valid=True,
        )

    # Failed to parse
    return ParsedCommand(
        action="",
        custom_task=None,
        profile="balanced",
        raw_command=body,
        valid=False,
        error='Invalid command format. Use: /deliberate <action> ["task"] [--profile name]',
    )


def format_plan_comment(
    action: str,
    profile: str,
    plan_content: str,
    requester: str,
    timeout_minutes: int = 5,
) -> str:
    """Format a plan comment for posting to GitHub.

    Args:
        action: The action being performed (review, optimize, etc.)
        profile: The profile being used
        plan_content: The generated plan content
        requester: Username who requested the action
        timeout_minutes: How long to wait for approval

    Returns:
        Formatted markdown comment body
    """
    return f"""## Deliberate Plan: `{action}`

**Requested by:** @{requester}
**Profile:** {profile}

### Proposed Plan

{plan_content}

---

**React with :+1: to approve** or **:-1: to reject** this plan.

The plan will execute automatically upon approval (timeout: {timeout_minutes} minutes).
"""


def format_success_comment(
    action: str,
    summary: str,
    duration_seconds: float,
    tokens: int,
    cost_usd: float,
    approver: str,
) -> str:
    """Format a success comment after execution completes.

    Args:
        action: The action that was performed
        summary: Execution summary
        duration_seconds: How long execution took
        tokens: Total tokens used
        cost_usd: Total cost

    Returns:
        Formatted markdown comment body
    """
    return f"""## Deliberate Success: `{action}`

### Summary

{summary}

### Stats

- **Duration:** {duration_seconds:.1f}s
- **Tokens:** {tokens:,}
- **Cost:** ${cost_usd:.4f}
- **Approved by:** @{approver}

---

*Powered by [Deliberate](https://github.com/hardbyte/deliberate)*
"""


def format_failure_comment(action: str, error: str) -> str:
    """Format a failure comment when execution fails."""
    return f"""## Deliberate Failed: `{action}`

Execution failed with error:

```
{error}
```

Check the workflow logs for details.
"""


def format_timeout_comment(action: str, timeout_minutes: int) -> str:
    """Format a timeout comment when approval times out."""
    return f"""## Deliberate Timeout: `{action}`

Plan approval timed out after {timeout_minutes} minutes.

To retry, post a new `/deliberate {action}` comment.
"""


def format_rejected_comment(action: str, rejector: str) -> str:
    """Format a rejection comment when plan is rejected."""
    return f"""## Deliberate Rejected: `{action}`

Plan was rejected by @{rejector}.

To provide feedback or request changes, reply to this thread.
"""
