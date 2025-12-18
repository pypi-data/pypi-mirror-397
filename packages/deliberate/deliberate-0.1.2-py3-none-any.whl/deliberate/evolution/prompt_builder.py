"""Prompt builder for evolution.

Builds prompts that include:
- Parent program context
- Inspiration programs
- Feedback from evaluation
- Instructions for diff-based changes
"""

from .types import Program, ProgramMetrics


class PromptBuilder:
    """Builds prompts for evolutionary code generation.

    Implements AlphaEvolve's prompt strategy:
    - Include parent program with its metrics
    - Add inspiration programs for cross-pollination
    - Include evaluation feedback for guidance
    - Request SEARCH/REPLACE format for targeted changes
    """

    def __init__(
        self,
        prefer_diffs: bool = True,
        include_metrics: bool = True,
        include_inspirations: int = 3,
    ):
        self.prefer_diffs = prefer_diffs
        self.include_metrics = include_metrics
        self.include_inspirations = include_inspirations

    def build_evolution_prompt(
        self,
        task: str,
        parent: Program | None = None,
        inspirations: list[Program] | None = None,
        feedback: str | None = None,
        iteration: int = 0,
        evolve_regions: list[tuple[int, int, str]] | None = None,
    ) -> str:
        """Build prompt for evolving code.

        Args:
            task: The problem/task description.
            parent: The parent program to evolve from.
            inspirations: Programs to draw inspiration from.
            feedback: Evaluation feedback to incorporate.
            iteration: Current iteration number.
            evolve_regions: List of (start_line, end_line, content) for evolve blocks.

        Returns:
            Complete prompt string.
        """
        sections = []

        # Task description
        sections.append(self._build_task_section(task))

        # Parent program
        if parent:
            sections.append(self._build_parent_section(parent))

        # Inspiration programs
        if inspirations:
            sections.append(self._build_inspirations_section(inspirations))

        # Evolution focus regions
        if evolve_regions:
            sections.append(self._build_evolve_regions_section(evolve_regions))

        # Feedback from previous evaluation
        if feedback:
            sections.append(self._build_feedback_section(feedback))

        # Instructions
        sections.append(
            self._build_instructions_section(
                has_parent=parent is not None,
                iteration=iteration,
            )
        )

        return "\n\n".join(sections)

    def build_initial_prompt(
        self,
        task: str,
        seed_code: str | None = None,
        examples: list[str] | None = None,
    ) -> str:
        """Build prompt for initial seed generation.

        Args:
            task: The problem/task description.
            seed_code: Optional starting code.
            examples: Optional example solutions.

        Returns:
            Prompt for generating initial solutions.
        """
        sections = []

        sections.append(self._build_task_section(task))

        if seed_code:
            sections.append(f"""## Starting Code

Here is a starting implementation to build upon:

```python
{seed_code}
```
""")

        if examples:
            sections.append("## Example Approaches\n")
            for i, example in enumerate(examples[:3], 1):
                sections.append(f"""### Example {i}
```python
{example}
```
""")

        sections.append("""## Instructions

Implement a complete solution for the task above.

Requirements:
1. Write clean, efficient code
2. Include docstrings and type hints
3. Handle edge cases appropriately
4. Optimize for both correctness and performance

Provide your implementation in a single code block:

```python
# Your implementation here
```
""")

        return "\n\n".join(sections)

    def _build_task_section(self, task: str) -> str:
        """Build the task description section."""
        return f"""# Task

{task}
"""

    def _build_parent_section(self, parent: Program) -> str:
        """Build section showing the parent program."""
        metrics_text = ""
        if self.include_metrics:
            m = parent.metrics
            metrics_text = f"""
**Current Metrics:**
- Test Score: {m.test_score:.2%} ({m.tests_passed}/{m.tests_total} passed)
- Lint Score: {m.lint_score:.2%}
- Overall Score: {m.overall_score:.3f}
- Generation: {m.generation}
"""

        return f"""## Parent Program (to evolve from)

The following program is your starting point. You will improve upon it.
{metrics_text}
```python
{parent.code}
```
"""

    def _build_inspirations_section(self, inspirations: list[Program]) -> str:
        """Build section showing inspiration programs."""
        if not inspirations:
            return ""

        parts = ["## Inspiration Programs\n"]
        parts.append("Study these programs for useful patterns and approaches:\n")

        for i, prog in enumerate(inspirations[: self.include_inspirations], 1):
            score_info = f"(score: {prog.metrics.overall_score:.3f})"
            parts.append(f"""### Inspiration {i} {score_info}
```python
{prog.code}
```
""")

        return "\n".join(parts)

    def _build_evolve_regions_section(
        self,
        evolve_regions: list[tuple[int, int, str]],
    ) -> str:
        """Build section highlighting evolution focus regions."""
        if not evolve_regions:
            return ""

        parts = ["## Evolution Focus Regions\n"]
        parts.append("The following regions are marked for evolution. Focus your changes here:\n")

        for i, (start, end, content) in enumerate(evolve_regions, 1):
            parts.append(f"""### Region {i} (lines {start}-{end})
```python
{content}
```
""")

        return "\n".join(parts)

    def _build_feedback_section(self, feedback: str) -> str:
        """Build section with evaluation feedback."""
        return f"""## Evaluation Feedback

The parent program received the following feedback:

{feedback}

Use this feedback to guide your improvements.
"""

    def _build_instructions_section(
        self,
        has_parent: bool,
        iteration: int,
    ) -> str:
        """Build the instructions section."""
        if has_parent and self.prefer_diffs:
            return f"""## Instructions (Iteration {iteration})

Improve the parent program by providing targeted changes in SEARCH/REPLACE format:

```diff
<<<<<<< SEARCH
# Code to find and replace
=======
# Improved code
>>>>>>> REPLACE
```

Guidelines:
1. Make minimal, targeted changes
2. Fix any failing tests first
3. Improve performance where possible
4. Maintain code style and structure
5. You may provide multiple SEARCH/REPLACE blocks

If the changes are too extensive, you may provide a complete rewrite instead:

```python
# Complete new implementation
```
"""
        else:
            return f"""## Instructions (Iteration {iteration})

Provide an improved implementation. Your code should:
1. Pass all tests
2. Be efficient and well-structured
3. Include proper error handling
4. Have good documentation

Provide your implementation:

```python
# Your implementation here
```
"""

    def build_feedback_from_metrics(
        self,
        metrics: ProgramMetrics,
        test_output: str | None = None,
        lint_output: str | None = None,
    ) -> str:
        """Build feedback text from evaluation metrics.

        Args:
            metrics: The program's evaluation metrics.
            test_output: Raw test output if available.
            lint_output: Lint checker output if available.

        Returns:
            Formatted feedback string.
        """
        parts = []

        # Test results
        if metrics.tests_total > 0:
            if metrics.test_score >= 1.0:
                parts.append("All tests passed!")
            else:
                parts.append(f"Tests: {metrics.tests_passed}/{metrics.tests_total} passed ({metrics.test_score:.1%})")
                if test_output:
                    # Truncate long output
                    truncated = test_output[:2000]
                    if len(test_output) > 2000:
                        truncated += "\n... (truncated)"
                    parts.append(f"\nTest Output:\n```\n{truncated}\n```")
        else:
            parts.append("No tests were run.")

        # Lint results
        if metrics.lint_score < 1.0:
            parts.append(f"\nLint Score: {metrics.lint_score:.1%}")
            if lint_output:
                truncated = lint_output[:1000]
                if len(lint_output) > 1000:
                    truncated += "\n... (truncated)"
                parts.append(f"Lint Issues:\n```\n{truncated}\n```")

        # Performance
        if metrics.runtime_ms < float("inf"):
            parts.append(f"\nRuntime: {metrics.runtime_ms:.1f}ms")

        # Evaluation level
        parts.append(f"\nHighest evaluation level passed: {metrics.highest_level_passed.name}")

        # Overall score
        parts.append(f"\n**Overall Score: {metrics.overall_score:.3f}**")

        return "\n".join(parts)

    def build_seed_prompt(
        self,
        task: str,
        language: str = "python",
        constraints: list[str] | None = None,
    ) -> str:
        """Build prompt for generating initial seed programs.

        Args:
            task: The problem description.
            language: Target programming language.
            constraints: Optional list of constraints.

        Returns:
            Prompt for seed generation.
        """
        constraints_text = ""
        if constraints:
            constraints_text = "\n## Constraints\n" + "\n".join(f"- {c}" for c in constraints)

        return f"""# Task

{task}
{constraints_text}

## Instructions

Generate an initial implementation for this task. Focus on:
1. Correctness over optimization
2. Clear, readable code
3. Proper error handling
4. Type hints and documentation

Provide your implementation in a code block:

```{language}
# Your implementation here
```
"""
