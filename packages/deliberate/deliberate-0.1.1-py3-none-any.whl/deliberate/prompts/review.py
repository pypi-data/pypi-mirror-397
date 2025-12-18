"""Prompt templates for the review phase."""

REVIEW_PROMPT = """Review this code change for the given task.

## Task
{task}

## Summary of Changes
{summary}

## Diff
```diff
{diff}
```

## Tests
{tests_section}

## Scoring Criteria
Score each criterion on a scale of {scale}:
{criteria}

## Instructions
Evaluate the changes and respond by calling the `submit_review` tool with:
- scores: A JSON object with one entry per criterion on the {scale} scale
- verdict: "accept", "reject", or "revise"
- reasoning: Brief explanation of your evaluation

Return ONLY the tool call JSON, no prose or commentary.

Be fair and thorough in your evaluation."""

CRITERIA_DESCRIPTIONS = {
    "correctness": "Does the code correctly implement the required functionality?",
    "code_quality": "Is the code clean, readable, and following best practices?",
    "completeness": "Are all aspects of the task addressed, including edge cases?",
    "risk": "Are there potential issues, bugs, or security concerns? (lower is better for risk)",
}

CRITERIA_CONTEXT_PROMPT = """You are selecting review criteria for a code review.

## Task
{task}

## Repository Snapshot
{repo_summary}

Respond ONLY by calling the `set_review_criteria` tool with:
- criteria: array of 3-{max_criteria} objects, each with fields:
  - name: short criterion name (e.g., "Query Performance")
  - description: 1 sentence on how to evaluate it

Focus on the task-specific quality, risk, and performance concerns surfaced by the repo context."""
