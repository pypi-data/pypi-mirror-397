"""Feedback building for iterative solving.

Generates structured feedback from evaluation results, similar to
poetiq's _build_feedback() function but generalized for different
evaluation domains.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from .types import FeedbackContext


@dataclass
class StructuredFeedback:
    """Structured feedback from an evaluation.

    Contains both human-readable feedback text and machine-parseable
    scores and metadata.
    """

    text: str  # Human-readable feedback
    score: float  # Overall soft score 0.0-1.0
    success: bool  # Did evaluation pass?
    per_item_scores: list[float]  # Scores per test case/example
    issues: list[str]  # Specific issues identified
    suggestions: list[str]  # Improvement suggestions
    metadata: dict[str, Any]  # Additional data


# Type variable for the evaluation result type
T = TypeVar("T")


class FeedbackBuilder(ABC, Generic[T]):
    """Abstract base class for building feedback from evaluations.

    Subclass this for specific evaluation domains:
    - TestFeedbackBuilder for test results
    - ReviewFeedbackBuilder for code review scores
    - ARCFeedbackBuilder for ARC-AGI style comparisons
    """

    @abstractmethod
    def build(self, evaluation: T, context: FeedbackContext) -> StructuredFeedback:
        """Build structured feedback from an evaluation result.

        Args:
            evaluation: The domain-specific evaluation result.
            context: Generic context about expected vs actual.

        Returns:
            Structured feedback for use in prompts.
        """
        pass


class TestFeedbackBuilder(FeedbackBuilder):
    """Builds feedback from test execution results.

    Converts test failures into structured feedback that helps
    the LLM understand what went wrong and how to fix it.
    """

    def build(
        self,
        evaluation: dict[str, Any],
        context: FeedbackContext,
    ) -> StructuredFeedback:
        """Build feedback from test results.

        Args:
            evaluation: Dict with keys like 'passed', 'failures', 'stderr', etc.
            context: Context with expected/actual comparison.

        Returns:
            Structured feedback for the LLM.
        """
        passed = evaluation.get("passed", False)
        failures = evaluation.get("failures", [])
        stderr = evaluation.get("stderr", "")
        exit_code = evaluation.get("exit_code", 1)

        issues = []
        suggestions = []
        per_item_scores = []

        if passed:
            text = "All tests passed successfully."
            score = 1.0
            per_item_scores = [1.0]
        else:
            # Parse failures into issues
            for failure in failures:
                test_name = failure.get("name", "unknown")
                message = failure.get("message", "")
                issues.append(f"Test '{test_name}' failed: {message[:200]}")
                per_item_scores.append(0.0)

            # Calculate soft score based on pass ratio if available
            total_tests = evaluation.get("total", len(failures) or 1)
            passed_tests = evaluation.get("passed_count", 0)
            score = passed_tests / total_tests if total_tests > 0 else 0.0

            # Generate suggestions
            if "assertion" in stderr.lower():
                suggestions.append("Check assertion conditions match expected behavior")
            if "import" in stderr.lower():
                suggestions.append("Verify all imports are correct")
            if "timeout" in stderr.lower():
                suggestions.append("Check for infinite loops or performance issues")

            # Build feedback text
            text = self._format_test_feedback(failures, stderr, exit_code, score, total_tests)

        return StructuredFeedback(
            text=text,
            score=score,
            success=passed,
            per_item_scores=per_item_scores,
            issues=issues,
            suggestions=suggestions,
            metadata={"exit_code": exit_code, "stderr": stderr[:500]},
        )

    def _format_test_feedback(
        self,
        failures: list[dict],
        stderr: str,
        exit_code: int,
        score: float,
        total: int,
    ) -> str:
        """Format test results into readable feedback text."""
        parts = []
        parts.append(f"Tests FAILED with exit code {exit_code}")
        parts.append(f"Score: {score:.2f} ({int(score * total)}/{total} tests passed)")

        if failures:
            parts.append("\n## Failed Tests:")
            for f in failures[:5]:  # Limit to 5 failures
                name = f.get("name", "unknown")
                msg = f.get("message", "no message")[:300]
                parts.append(f"- {name}: {msg}")

        if stderr and len(stderr) > 10:
            parts.append(f"\n## Error Output (truncated):\n```\n{stderr[:1000]}\n```")

        return "\n".join(parts)


class DiffFeedbackBuilder(FeedbackBuilder):
    """Builds feedback from array/grid comparisons.

    Similar to poetiq's _build_feedback() that shows cell-by-cell
    differences between expected and actual outputs.
    """

    def build(
        self,
        evaluation: dict[str, Any],
        context: FeedbackContext,
    ) -> StructuredFeedback:
        """Build feedback from diff comparison.

        Args:
            evaluation: Dict with 'expected', 'actual' arrays.
            context: Context with comparison metadata.

        Returns:
            Structured feedback showing differences.
        """
        expected = context.expected
        actual = context.actual

        issues = []
        suggestions = []

        # Get shapes for 2D lists
        expected_shape = self._get_shape(expected)
        actual_shape = self._get_shape(actual)

        # Check shape match
        if expected_shape != actual_shape:
            issues.append(f"Shape mismatch: got {actual_shape}, expected {expected_shape}")
            suggestions.append("Ensure output dimensions match expected dimensions")
            score = 0.0
            diff_text = f"Cannot compare arrays of different shapes: {actual_shape} vs {expected_shape}"
            shape_match = False
        else:
            # Calculate soft score (cell-by-cell accuracy)
            total_cells, matching_cells = self._count_matches(expected, actual)
            score = matching_cells / total_cells if total_cells > 0 else 0.0

            # Build diff visualization
            diff_text = self._build_diff_grid(expected, actual)

            if score < 1.0:
                n_wrong = total_cells - matching_cells
                issues.append(f"{n_wrong} cells differ from expected")
                suggestions.append("Review the diff below to identify patterns in errors")
            shape_match = True

        per_item_scores = [score]  # Single comparison = single score

        text = self._format_diff_feedback(context.match, score, diff_text, issues)

        return StructuredFeedback(
            text=text,
            score=score,
            success=context.match,
            per_item_scores=per_item_scores,
            issues=issues,
            suggestions=suggestions,
            metadata={"shape_match": shape_match},
        )

    def _get_shape(self, arr: Any) -> tuple:
        """Get shape of a 2D list or similar structure."""
        if not isinstance(arr, (list, tuple)):
            return ()
        if not arr:
            return (0,)
        if isinstance(arr[0], (list, tuple)):
            return (len(arr), len(arr[0]))
        return (len(arr),)

    def _count_matches(self, expected: list, actual: list) -> tuple[int, int]:
        """Count total cells and matching cells."""
        total = 0
        matches = 0
        for i, exp_row in enumerate(expected):
            if isinstance(exp_row, (list, tuple)):
                for j, exp_val in enumerate(exp_row):
                    total += 1
                    if i < len(actual) and j < len(actual[i]) and actual[i][j] == exp_val:
                        matches += 1
            else:
                total += 1
                if i < len(actual) and actual[i] == exp_row:
                    matches += 1
        return total, matches

    def _build_diff_grid(self, expected: list, actual: list) -> str:
        """Build a visual diff grid showing pred/expected for mismatches.

        Format: matching cells show value as-is, mismatches show "actual/expected"
        Similar to poetiq's _array_diff().
        """
        if not expected or not isinstance(expected[0], (list, tuple)):
            return f"Expected: {expected}\nActual: {actual}"

        lines = []
        for i, exp_row in enumerate(expected):
            row_parts = []
            for j, exp_val in enumerate(exp_row):
                act_val = actual[i][j] if i < len(actual) and j < len(actual[i]) else None
                if act_val == exp_val:
                    row_parts.append(str(act_val))
                else:
                    row_parts.append(f"{act_val}/{exp_val}")
            lines.append(" ".join(row_parts))

        return "\n".join(lines)

    def _format_diff_feedback(
        self,
        success: bool,
        score: float,
        diff_text: str,
        issues: list[str],
    ) -> str:
        """Format diff results into readable feedback text."""
        parts = []

        if success:
            parts.append("Output matches expected exactly!")
        else:
            parts.append(f"Output does NOT match expected. Accuracy: {score:.2%}")

            if issues:
                parts.append("\n## Issues:")
                for issue in issues:
                    parts.append(f"- {issue}")

            parts.append("\n## Diff Visualization:")
            parts.append("(Format: correct values shown as-is, errors as 'actual/expected')")
            parts.append(f"```\n{diff_text}\n```")

        return "\n".join(parts)


class CompositeFeedbackBuilder(FeedbackBuilder):
    """Combines multiple evaluations into unified feedback.

    Use when you have multiple evaluation criteria (e.g., tests + code review).
    """

    def __init__(self, builders: list[FeedbackBuilder], weights: list[float] | None = None):
        """Initialize with sub-builders.

        Args:
            builders: List of FeedbackBuilder instances.
            weights: Optional weights for combining scores (default: equal).
        """
        self.builders = builders
        self.weights = weights or [1.0 / len(builders)] * len(builders)

    def build(
        self,
        evaluation: list[tuple[Any, FeedbackContext]],
        context: FeedbackContext,  # Ignored, using per-evaluation contexts
    ) -> StructuredFeedback:
        """Build combined feedback from multiple evaluations.

        Args:
            evaluation: List of (evaluation, context) tuples for each builder.
            context: Ignored (each sub-evaluation has its own context).

        Returns:
            Combined structured feedback.
        """
        sub_feedbacks = []
        for builder, (eval_data, eval_context) in zip(self.builders, evaluation):
            sub_feedbacks.append(builder.build(eval_data, eval_context))

        # Combine scores with weights
        total_score = sum(fb.score * w for fb, w in zip(sub_feedbacks, self.weights))

        # Aggregate success (all must succeed)
        success = all(fb.success for fb in sub_feedbacks)

        # Combine all issues and suggestions
        all_issues = []
        all_suggestions = []
        all_scores = []
        for fb in sub_feedbacks:
            all_issues.extend(fb.issues)
            all_suggestions.extend(fb.suggestions)
            all_scores.extend(fb.per_item_scores)

        # Combine text
        text_parts = []
        for i, fb in enumerate(sub_feedbacks, 1):
            text_parts.append(f"## Evaluation {i} (weight: {self.weights[i - 1]:.2f}):")
            text_parts.append(fb.text)
            text_parts.append("")

        return StructuredFeedback(
            text="\n".join(text_parts),
            score=total_score,
            success=success,
            per_item_scores=all_scores,
            issues=all_issues,
            suggestions=all_suggestions,
            metadata={"sub_feedbacks": len(sub_feedbacks)},
        )


class PlanFeedbackBuilder(FeedbackBuilder):
    """Builds feedback from plan evaluation results.

    Converts PlanReviewEvaluator results into structured feedback
    for iterative plan improvement.
    """

    def __init__(self, success_threshold: float = 0.9):
        """Initialize the plan feedback builder.

        Args:
            success_threshold: Score threshold for success (default 0.9).
        """
        self.success_threshold = success_threshold

    def build(
        self,
        evaluation: dict[str, Any],
        context: FeedbackContext,
    ) -> StructuredFeedback:
        """Build feedback from plan evaluation results.

        Args:
            evaluation: Dict from PlanReviewEvaluator with keys:
                - structure: PlanStructureCheck object
                - critic: CriticResult object or None
                - passed: bool
                - score: float
                - suggestions: list[str]
            context: FeedbackContext with expected/actual.

        Returns:
            Structured feedback for the LLM.
        """
        structure = evaluation.get("structure")
        critic = evaluation.get("critic")
        score = evaluation.get("score", context.soft_score)
        passed = evaluation.get("passed", context.match)
        suggestions = evaluation.get("suggestions", [])

        issues = []
        per_item_scores = []

        # Extract structure issues
        if structure and hasattr(structure, "issues"):
            issues.extend(structure.issues)

        # Extract critic scores for per-item breakdown
        if critic:
            per_item_scores = [
                critic.feasibility,
                critic.completeness,
                critic.clarity,
                critic.risk_awareness,
            ]
            # Add critic suggestions
            if hasattr(critic, "suggestions"):
                suggestions.extend(critic.suggestions)
        else:
            # Structure-only evaluation
            per_item_scores = [score]

        # Build feedback text
        text = self._format_plan_feedback(
            passed=passed,
            score=score,
            structure=structure,
            critic=critic,
            issues=issues,
        )

        return StructuredFeedback(
            text=text,
            score=score,
            success=passed,
            per_item_scores=per_item_scores,
            issues=issues,
            suggestions=suggestions,
            metadata={
                "structure_valid": structure.valid if structure else None,
                "has_critic": critic is not None,
                "threshold": self.success_threshold,
            },
        )

    def _format_plan_feedback(
        self,
        passed: bool,
        score: float,
        structure: Any,
        critic: Any,
        issues: list[str],
    ) -> str:
        """Format plan evaluation into readable feedback text."""
        parts = []

        if passed:
            parts.append(f"Plan PASSED with score {score:.2f}")
        else:
            parts.append(f"Plan needs improvement. Score: {score:.2f}")
            parts.append(f"(Threshold: {self.success_threshold})")

        # Structure feedback
        if structure:
            parts.append("\n## Structure Analysis:")
            if structure.valid:
                parts.append(f"- Found {structure.step_count} implementation steps")
                if structure.has_risks:
                    parts.append("- Risk section present")
                else:
                    parts.append("- Missing risk analysis")
                if structure.has_files:
                    parts.append("- File list present")
                else:
                    parts.append("- Missing affected files list")
            else:
                parts.append("Structure is INVALID:")
                for issue in structure.issues:
                    parts.append(f"  - {issue}")

        # Critic feedback
        if critic:
            parts.append("\n## Critic Evaluation:")
            parts.append(f"- Feasibility: {critic.feasibility:.2f}")
            parts.append(f"- Completeness: {critic.completeness:.2f}")
            parts.append(f"- Clarity: {critic.clarity:.2f}")
            parts.append(f"- Risk Awareness: {critic.risk_awareness:.2f}")
            parts.append(f"- Overall: {critic.overall_score:.2f}")

            if critic.feedback:
                parts.append(f"\n**Detailed Feedback:**\n{critic.feedback[:500]}")

        # Issues summary
        if issues and not passed:
            parts.append("\n## Issues to Address:")
            for issue in issues[:10]:  # Limit to 10
                parts.append(f"- {issue}")

        return "\n".join(parts)


def build_iteration_prompt(
    task: str,
    history_context: str,
    feedback_prompt_template: str | None = None,
) -> str:
    """Build the prompt for an iteration with history context.

    Args:
        task: The original task description.
        history_context: Formatted history from SolutionHistory.format_for_prompt().
        feedback_prompt_template: Optional custom template.

    Returns:
        Complete prompt for the next iteration.
    """
    if not history_context:
        return task

    template = feedback_prompt_template or DEFAULT_FEEDBACK_TEMPLATE
    return task + "\n\n" + template.replace("$$feedback$$", history_context)


DEFAULT_FEEDBACK_TEMPLATE = """
**EXISTING PARTIAL/INCORRECT SOLUTIONS:**

Following are some of the best, though not completely correct, solutions so far.
For each solution, its code, corresponding feedback regarding its output,
and a numeric score between 0. (worst) and 1. (best) indicating the quality
of outputs is also provided.

Study these solutions and corresponding feedback and produce a new solution
fixing all the issues. Learn from the patterns in what worked and what didn't.

$$feedback$$

Based on this history, provide an improved solution that addresses all
identified issues while building on what worked.
"""
