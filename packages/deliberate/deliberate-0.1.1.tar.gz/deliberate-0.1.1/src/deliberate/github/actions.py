"""Predefined actions for GitHub Bot commands.

Each action defines a task template that can be triggered via PR comments
like `/deliberate review` or `/deliberate optimize`.
"""

from dataclasses import dataclass


@dataclass
class PredefinedAction:
    """A predefined deliberate action that can be triggered via PR comments."""

    name: str
    description: str
    task_template: str
    default_profile: str = "balanced"


PREDEFINED_ACTIONS: dict[str, PredefinedAction] = {
    "review": PredefinedAction(
        name="review",
        description="Comprehensive PR review with suggestions",
        task_template="""Review this pull request comprehensively.

Analyze the changes and provide:
1. Code quality assessment (correctness, maintainability, readability)
2. Potential bugs or issues
3. Security concerns if any
4. Performance implications
5. Suggestions for improvement

Focus on actionable feedback that helps improve the code.""",
        default_profile="balanced",
    ),
    "optimize": PredefinedAction(
        name="optimize",
        description="Optimize code for performance and readability",
        task_template="""Optimize the code in this pull request.

Focus on:
1. Performance improvements (algorithmic complexity, caching, batching)
2. Code readability and maintainability
3. Reducing code duplication
4. Applying idiomatic patterns for the language/framework
5. Improving error handling

Make concrete changes that improve the code without changing functionality.""",
        default_profile="balanced",
    ),
    "test": PredefinedAction(
        name="test",
        description="Generate tests for the changes",
        task_template="""Generate comprehensive tests for the code changes in this PR.

Include:
1. Unit tests for new functions/methods
2. Edge case tests
3. Error handling tests
4. Integration tests if appropriate

Follow the existing test patterns and conventions in this repository.
Use the existing test framework and mocking patterns.""",
        default_profile="cheap",
    ),
    "implement": PredefinedAction(
        name="implement",
        description="Implement a custom task",
        task_template="{custom_task}",
        default_profile="balanced",
    ),
    "fix": PredefinedAction(
        name="fix",
        description="Fix issues identified in PR review comments",
        task_template="""Fix the issues identified in the PR review comments.

Address all actionable feedback from reviewers, including:
1. Bug fixes
2. Code style improvements
3. Logic corrections
4. Documentation updates

Prioritize correctness over aesthetics.""",
        default_profile="balanced",
    ),
    "docs": PredefinedAction(
        name="docs",
        description="Add or improve documentation",
        task_template="""Improve documentation for the code changes in this PR.

Include:
1. Docstrings for new functions/classes/methods
2. Inline comments for complex logic
3. Update README if public API changed
4. Add usage examples if appropriate

Follow the existing documentation style in this repository.""",
        default_profile="cheap",
    ),
}


def get_predefined_action(name: str) -> PredefinedAction | None:
    """Get a predefined action by name (case-insensitive)."""
    return PREDEFINED_ACTIONS.get(name.lower())


def format_task(action: PredefinedAction, custom_task: str | None = None) -> str:
    """Format the task template with optional custom task.

    Args:
        action: The predefined action to format
        custom_task: Optional custom task text for 'implement' action

    Returns:
        Formatted task string ready for deliberate
    """
    if action.name == "implement":
        if not custom_task:
            raise ValueError("Custom task required for 'implement' action")
        return action.task_template.format(custom_task=custom_task)
    return action.task_template


def list_actions() -> list[tuple[str, str]]:
    """List all available actions with descriptions."""
    return [(name, action.description) for name, action in PREDEFINED_ACTIONS.items()]
