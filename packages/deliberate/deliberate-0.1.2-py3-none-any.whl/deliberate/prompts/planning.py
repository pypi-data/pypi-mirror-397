"""Prompt templates for the planning phase."""

PLANNING_PROMPT = """You are a senior software engineer. Create a detailed plan for this task.
Do NOT estimate time or hours. You may inspect the codebase using read-only tools (list/read
files, describe structure), build/compile code but do not perform writes during planning.

{task}

Provide:
1. Analysis of what needs to change
2. Step-by-step approach
3. Key components affected
4. Potential risks or edge cases

Be specific and actionable. Focus on technical details that will guide implementation."""

DEBATE_PROMPT = """You are reviewing another engineer's plan. Provide constructive feedback.

## Original Task
{task}

## Plan to Review
{plan}

Analyze the plan and provide:
1. Strengths of the approach
2. Potential issues or gaps
3. Suggestions for improvement
4. Alternative approaches to consider

Be constructive and specific."""

JUDGE_PROMPT = """Compare these {num_plans} plans for the task and select the best one.

## Task
{task}

---

{plans}

---

Evaluate each plan on:
- Completeness: Does it address all aspects of the task?
- Clarity: Is the approach well-explained and actionable?
- Risk awareness: Are potential issues identified?
- Practicality: Is the approach realistic and efficient?

Select the best plan by calling the `select_plan` tool with:
- plan_id: the integer plan number (1-based)
- reasoning: 1-2 sentences explaining the choice

Respond ONLY with the `select_plan` tool call. No prose."""
