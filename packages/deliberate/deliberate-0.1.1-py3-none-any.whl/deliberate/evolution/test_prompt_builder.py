"""Prompt builder for adversarial test generation.

Builds prompts that guide LLMs to generate tests that:
- Challenge existing implementations
- Discover edge cases
- Verify correctness rigorously
"""

from typing import Any

from .types import Program, ProgramMetrics


class TestGenerationPromptBuilder:
    """Builds prompts for adversarial test generation.

    The goal is to generate tests that expose weaknesses in
    champion implementations by finding edge cases, boundary
    conditions, and subtle bugs.
    """

    def __init__(
        self,
        include_champion_code: bool = True,
        include_metrics: bool = True,
        include_inspirations: int = 2,
        max_champion_lines: int = 200,
    ):
        """Initialize the prompt builder.

        Args:
            include_champion_code: Whether to include champion code in prompt.
            include_metrics: Whether to include test metrics.
            include_inspirations: Number of inspiration tests to include.
            max_champion_lines: Max lines of champion code to include.
        """
        self.include_champion_code = include_champion_code
        self.include_metrics = include_metrics
        self.include_inspirations = include_inspirations
        self.max_champion_lines = max_champion_lines

    def build_test_evolution_prompt(
        self,
        task: str,
        champion_code: str,
        parent_test: Program | None = None,
        inspiration_tests: list[Program] | None = None,
        feedback: str | None = None,
        iteration: int = 0,
        known_edge_cases: list[str] | None = None,
    ) -> str:
        """Build prompt for evolving adversarial tests.

        Args:
            task: The problem/task description.
            champion_code: The current champion implementation to challenge.
            parent_test: The parent test program to evolve from.
            inspiration_tests: Other test programs for inspiration.
            feedback: Feedback from previous test evaluation.
            iteration: Current iteration number.
            known_edge_cases: Edge cases already covered by existing tests.

        Returns:
            Complete prompt string for test generation.
        """
        sections = []

        # Task context
        sections.append(self._build_task_section(task))

        # Champion implementation to challenge
        if self.include_champion_code:
            sections.append(self._build_champion_section(champion_code))

        # Parent test to evolve
        if parent_test:
            sections.append(self._build_parent_test_section(parent_test))

        # Inspiration tests
        if inspiration_tests:
            sections.append(self._build_inspiration_tests_section(inspiration_tests))

        # Known edge cases to avoid duplicating
        if known_edge_cases:
            sections.append(self._build_known_edge_cases_section(known_edge_cases))

        # Feedback from previous evaluation
        if feedback:
            sections.append(self._build_feedback_section(feedback))

        # Instructions
        sections.append(
            self._build_test_instructions_section(
                has_parent=parent_test is not None,
                iteration=iteration,
            )
        )

        return "\n\n".join(sections)

    def build_initial_test_prompt(
        self,
        task: str,
        champion_code: str,
        example_tests: list[str] | None = None,
    ) -> str:
        """Build prompt for generating initial adversarial tests.

        Args:
            task: The problem/task description.
            champion_code: The current champion implementation.
            example_tests: Optional example test structures.

        Returns:
            Prompt for generating initial test suite.
        """
        sections = []

        sections.append(self._build_task_section(task))
        sections.append(self._build_champion_section(champion_code))

        if example_tests:
            sections.append("## Example Test Structure\n")
            for i, example in enumerate(example_tests[:2], 1):
                sections.append(f"""### Example {i}
```python
{example}
```
""")

        sections.append("""## Instructions

Generate a comprehensive test suite to challenge the champion implementation.

Your tests should:
1. Target edge cases and boundary conditions
2. Test error handling and invalid inputs
3. Verify correctness for unusual but valid inputs
4. Check for performance issues with large inputs
5. Test combinations of parameters

**Goal**: Find inputs that cause the implementation to fail or behave incorrectly.

Test Format:
- Use pytest conventions
- Include descriptive test names explaining what's being tested
- Add docstrings explaining why each test case matters

Provide your test suite:

```python
import pytest
# Your tests here
```
""")

        return "\n\n".join(sections)

    def _build_task_section(self, task: str) -> str:
        """Build the task description section."""
        return f"""# Task Context

The following describes what the implementation should do:

{task}
"""

    def _build_champion_section(self, champion_code: str) -> str:
        """Build section showing the champion implementation."""
        # Truncate very long code
        lines = champion_code.split("\n")
        if len(lines) > self.max_champion_lines:
            code_display = "\n".join(lines[: self.max_champion_lines])
            code_display += f"\n# ... ({len(lines) - self.max_champion_lines} more lines)"
        else:
            code_display = champion_code

        return f"""## Champion Implementation (Target)

This is the current best implementation. Your goal is to write tests that
find bugs, edge cases, or incorrect behavior in this code.

```python
{code_display}
```
"""

    def _build_parent_test_section(self, parent_test: Program) -> str:
        """Build section showing the parent test to evolve."""
        metrics_text = ""
        if self.include_metrics:
            m = parent_test.metrics
            metrics_text = f"""
**Current Test Metrics:**
- Kill Rate: {m.champion_kill_rate:.1%} (fraction of champions this test breaks)
- Test Cases: {m.test_cases_generated}
- Generation: {m.generation}
"""
            if m.covers_edge_cases:
                cases = ", ".join(m.covers_edge_cases[:5])
                if len(m.covers_edge_cases) > 5:
                    cases += f", ... (+{len(m.covers_edge_cases) - 5} more)"
                metrics_text += f"- Edge Cases Covered: {cases}\n"

        return f"""## Parent Test (to evolve from)

The following test is your starting point. You will improve upon it to find
more bugs or cover more edge cases.
{metrics_text}
```python
{parent_test.code}
```
"""

    def _build_inspiration_tests_section(self, inspiration_tests: list[Program]) -> str:
        """Build section showing inspiration tests."""
        if not inspiration_tests:
            return ""

        parts = ["## Inspiration Tests\n"]
        parts.append("Study these tests for useful patterns and edge case ideas:\n")

        for i, test in enumerate(inspiration_tests[: self.include_inspirations], 1):
            kill_rate = test.metrics.champion_kill_rate
            parts.append(f"""### Inspiration {i} (kill rate: {kill_rate:.1%})
```python
{test.code}
```
""")

        return "\n".join(parts)

    def _build_known_edge_cases_section(self, known_edge_cases: list[str]) -> str:
        """Build section listing known edge cases to avoid duplicating."""
        if not known_edge_cases:
            return ""

        cases_list = "\n".join(f"- {case}" for case in known_edge_cases[:20])
        if len(known_edge_cases) > 20:
            cases_list += f"\n- ... and {len(known_edge_cases) - 20} more"

        return f"""## Already Covered Edge Cases

These edge cases are already tested. Focus on discovering NEW edge cases:

{cases_list}
"""

    def _build_feedback_section(self, feedback: str) -> str:
        """Build section with evaluation feedback."""
        return f"""## Evaluation Feedback

The parent test received the following feedback:

{feedback}

Use this feedback to improve your test suite.
"""

    def _build_test_instructions_section(
        self,
        has_parent: bool,
        iteration: int,
    ) -> str:
        """Build the instructions section for test evolution."""
        if has_parent:
            return f"""## Instructions (Iteration {iteration})

Improve the parent test by:
1. Adding new test cases for uncovered edge cases
2. Making existing tests more thorough
3. Targeting weaknesses suggested by feedback

Focus on tests that are likely to FAIL on the champion implementation.

**Legitimate Test Requirements:**
- Tests must reflect actual business requirements
- Tests should not be "trick tests" with impossible requirements
- Edge cases must be reasonable for the problem domain

Provide your improved test suite:

```python
import pytest
# Your improved tests here
```
"""
        else:
            return f"""## Instructions (Iteration {iteration})

Generate adversarial tests that challenge the champion implementation.

**Strategy:**
1. Identify boundary conditions (empty inputs, max values, etc.)
2. Test error handling for invalid inputs
3. Check for off-by-one errors
4. Verify correct handling of special characters/values
5. Test with concurrent or parallel inputs if applicable

**Legitimate Test Requirements:**
- Tests must reflect actual business requirements
- Tests should not be "trick tests" with impossible requirements
- Edge cases must be reasonable for the problem domain

Provide your test suite:

```python
import pytest
# Your tests here
```
"""

    def build_feedback_from_test_metrics(
        self,
        metrics: ProgramMetrics,
        kill_details: list[dict[str, Any]] | None = None,
        validation_output: str | None = None,
    ) -> str:
        """Build feedback text from test evaluation metrics.

        Args:
            metrics: The test program's evaluation metrics.
            kill_details: Details about which champions were killed.
            validation_output: Validation output if available.

        Returns:
            Formatted feedback string.
        """
        parts = []

        # Kill rate summary
        if metrics.champion_kill_rate > 0:
            parts.append(
                f"Kill Rate: {metrics.champion_kill_rate:.1%} "
                f"(your tests found bugs in {metrics.champion_kill_rate:.0%} of champions)"
            )
        else:
            parts.append("Kill Rate: 0% (your tests did not find any bugs in the champions)")

        # Test validation
        if metrics.is_valid_test:
            parts.append(f"Test Validity: PASSED ({metrics.test_cases_generated} test cases)")
        else:
            parts.append("Test Validity: FAILED (tests did not pass validation)")
            if validation_output:
                truncated = validation_output[:1000]
                if len(validation_output) > 1000:
                    truncated += "\n... (truncated)"
                parts.append(f"Validation Output:\n```\n{truncated}\n```")

        # Kill details
        if kill_details:
            parts.append("\n**Champions Killed:**")
            for detail in kill_details[:5]:
                champ_id = detail.get("champion_id", "unknown")
                test_name = detail.get("test_name", "unknown")
                error = detail.get("error", "")[:200]
                parts.append(f"- {champ_id}: {test_name} - {error}")
            if len(kill_details) > 5:
                parts.append(f"- ... and {len(kill_details) - 5} more")

        # Edge cases covered
        if metrics.covers_edge_cases:
            cases = ", ".join(metrics.covers_edge_cases[:10])
            parts.append(f"\nEdge Cases Covered: {cases}")

        # Overall score
        parts.append(f"\n**Test Score: {metrics.overall_score:.3f}**")

        return "\n".join(parts)
