"""Tests for TestGenerationPromptBuilder."""

from deliberate.evolution.test_prompt_builder import TestGenerationPromptBuilder
from deliberate.evolution.types import Program, ProgramMetrics


def _make_program(
    code: str,
    generation: int = 0,
    champion_kill_rate: float = 0.0,
    is_valid_test: bool = True,
    test_cases_generated: int = 3,
    covers_edge_cases: list[str] | None = None,
) -> Program:
    """Helper to create a Program with test-specific metrics."""
    metrics = ProgramMetrics(
        generation=generation,
        champion_kill_rate=champion_kill_rate,
        is_valid_test=is_valid_test,
        test_cases_generated=test_cases_generated,
        covers_edge_cases=covers_edge_cases or [],
    )
    return Program(
        id=f"test-{generation}",
        code=code,
        metrics=metrics,
    )


class TestTestGenerationPromptBuilderInit:
    """Tests for TestGenerationPromptBuilder initialization."""

    def test_default_values(self):
        """Default values are sensible."""
        builder = TestGenerationPromptBuilder()

        assert builder.include_champion_code is True
        assert builder.include_metrics is True
        assert builder.include_inspirations == 2
        assert builder.max_champion_lines == 200

    def test_custom_values(self):
        """Can set custom configuration."""
        builder = TestGenerationPromptBuilder(
            include_champion_code=False,
            include_metrics=False,
            include_inspirations=5,
            max_champion_lines=100,
        )

        assert builder.include_champion_code is False
        assert builder.include_metrics is False
        assert builder.include_inspirations == 5
        assert builder.max_champion_lines == 100


class TestBuildTestEvolutionPrompt:
    """Tests for build_test_evolution_prompt method."""

    def test_basic_prompt_includes_task(self):
        """Prompt includes task description."""
        builder = TestGenerationPromptBuilder()
        prompt = builder.build_test_evolution_prompt(
            task="Implement a sorting function",
            champion_code="def sort(arr): return sorted(arr)",
        )

        assert "Implement a sorting function" in prompt

    def test_prompt_includes_champion_code(self):
        """Prompt includes champion implementation."""
        builder = TestGenerationPromptBuilder()
        prompt = builder.build_test_evolution_prompt(
            task="Sort numbers",
            champion_code="def sort(arr): return sorted(arr)",
        )

        assert "def sort(arr): return sorted(arr)" in prompt
        assert "Champion Implementation" in prompt

    def test_prompt_without_champion_code(self):
        """Can omit champion code from prompt."""
        builder = TestGenerationPromptBuilder(include_champion_code=False)
        prompt = builder.build_test_evolution_prompt(
            task="Sort numbers",
            champion_code="def sort(arr): return sorted(arr)",
        )

        assert "Champion Implementation" not in prompt

    def test_prompt_includes_parent_test(self):
        """Prompt includes parent test when provided."""
        builder = TestGenerationPromptBuilder()
        parent = _make_program(
            code="def test_empty(): assert sort([]) == []",
            generation=1,
            champion_kill_rate=0.25,
        )

        prompt = builder.build_test_evolution_prompt(
            task="Sort numbers",
            champion_code="def sort(arr): return sorted(arr)",
            parent_test=parent,
        )

        assert "Parent Test" in prompt
        assert "def test_empty(): assert sort([]) == []" in prompt

    def test_prompt_includes_parent_metrics(self):
        """Prompt includes parent test metrics."""
        builder = TestGenerationPromptBuilder()
        parent = _make_program(
            code="def test_x(): pass",
            generation=2,
            champion_kill_rate=0.5,
            test_cases_generated=4,
            covers_edge_cases=["empty", "single", "negative"],
        )

        prompt = builder.build_test_evolution_prompt(
            task="Sort numbers",
            champion_code="def sort(arr): pass",
            parent_test=parent,
        )

        assert "Kill Rate: 50.0%" in prompt
        assert "Test Cases: 4" in prompt
        assert "Generation: 2" in prompt
        assert "empty" in prompt
        assert "negative" in prompt

    def test_prompt_without_metrics(self):
        """Can omit metrics from prompt."""
        builder = TestGenerationPromptBuilder(include_metrics=False)
        parent = _make_program(
            code="def test_x(): pass",
            champion_kill_rate=0.5,
        )

        prompt = builder.build_test_evolution_prompt(
            task="Sort",
            champion_code="def sort(arr): pass",
            parent_test=parent,
        )

        assert "Kill Rate" not in prompt

    def test_prompt_includes_inspiration_tests(self):
        """Prompt includes inspiration tests."""
        builder = TestGenerationPromptBuilder(include_inspirations=2)
        inspirations = [
            _make_program("def test_a(): pass", champion_kill_rate=0.3),
            _make_program("def test_b(): pass", champion_kill_rate=0.4),
            _make_program("def test_c(): pass", champion_kill_rate=0.5),
        ]

        prompt = builder.build_test_evolution_prompt(
            task="Sort",
            champion_code="def sort(arr): pass",
            inspiration_tests=inspirations,
        )

        assert "Inspiration Tests" in prompt
        assert "def test_a(): pass" in prompt
        assert "def test_b(): pass" in prompt
        # Should only include first 2 due to include_inspirations=2
        assert "def test_c(): pass" not in prompt

    def test_prompt_includes_known_edge_cases(self):
        """Prompt includes known edge cases to avoid."""
        builder = TestGenerationPromptBuilder()

        prompt = builder.build_test_evolution_prompt(
            task="Sort",
            champion_code="def sort(arr): pass",
            known_edge_cases=["empty_list", "single_element", "duplicates"],
        )

        assert "Already Covered Edge Cases" in prompt
        assert "empty_list" in prompt
        assert "single_element" in prompt
        assert "duplicates" in prompt

    def test_prompt_includes_feedback(self):
        """Prompt includes evaluation feedback."""
        builder = TestGenerationPromptBuilder()

        prompt = builder.build_test_evolution_prompt(
            task="Sort",
            champion_code="def sort(arr): pass",
            feedback="Tests did not cover negative numbers",
        )

        assert "Evaluation Feedback" in prompt
        assert "did not cover negative numbers" in prompt

    def test_prompt_includes_iteration_number(self):
        """Prompt includes iteration number."""
        builder = TestGenerationPromptBuilder()

        prompt = builder.build_test_evolution_prompt(
            task="Sort",
            champion_code="def sort(arr): pass",
            iteration=5,
        )

        assert "Iteration 5" in prompt

    def test_prompt_truncates_long_champion_code(self):
        """Prompt truncates very long champion code."""
        builder = TestGenerationPromptBuilder(max_champion_lines=5)
        long_code = "\n".join([f"line_{i}" for i in range(100)])

        prompt = builder.build_test_evolution_prompt(
            task="Sort",
            champion_code=long_code,
        )

        assert "line_0" in prompt
        assert "line_4" in prompt
        assert "line_99" not in prompt
        assert "more lines" in prompt


class TestBuildInitialTestPrompt:
    """Tests for build_initial_test_prompt method."""

    def test_basic_initial_prompt(self):
        """Initial prompt includes task and champion."""
        builder = TestGenerationPromptBuilder()

        prompt = builder.build_initial_test_prompt(
            task="Implement fizzbuzz",
            champion_code="def fizzbuzz(n): pass",
        )

        assert "fizzbuzz" in prompt
        assert "Champion Implementation" in prompt
        assert "def fizzbuzz(n): pass" in prompt

    def test_initial_prompt_includes_instructions(self):
        """Initial prompt includes test generation instructions."""
        builder = TestGenerationPromptBuilder()

        prompt = builder.build_initial_test_prompt(
            task="Sort",
            champion_code="def sort(arr): pass",
        )

        assert "edge cases" in prompt.lower()
        assert "boundary conditions" in prompt.lower()
        assert "pytest" in prompt

    def test_initial_prompt_includes_examples(self):
        """Initial prompt includes example tests when provided."""
        builder = TestGenerationPromptBuilder()
        examples = [
            "def test_example(): assert True",
            "def test_other(): assert 1 == 1",
        ]

        prompt = builder.build_initial_test_prompt(
            task="Sort",
            champion_code="def sort(arr): pass",
            example_tests=examples,
        )

        assert "Example Test Structure" in prompt
        assert "def test_example(): assert True" in prompt
        assert "def test_other(): assert 1 == 1" in prompt


class TestBuildFeedbackFromTestMetrics:
    """Tests for build_feedback_from_test_metrics method."""

    def test_feedback_includes_kill_rate(self):
        """Feedback includes kill rate."""
        builder = TestGenerationPromptBuilder()
        metrics = ProgramMetrics(champion_kill_rate=0.75, is_valid_test=True)

        feedback = builder.build_feedback_from_test_metrics(metrics)

        assert "Kill Rate: 75.0%" in feedback

    def test_feedback_zero_kill_rate(self):
        """Feedback for zero kill rate is clear."""
        builder = TestGenerationPromptBuilder()
        metrics = ProgramMetrics(champion_kill_rate=0.0, is_valid_test=True)

        feedback = builder.build_feedback_from_test_metrics(metrics)

        assert "Kill Rate: 0%" in feedback
        assert "did not find any bugs" in feedback

    def test_feedback_includes_validation_status(self):
        """Feedback includes test validation status."""
        builder = TestGenerationPromptBuilder()
        metrics = ProgramMetrics(
            is_valid_test=True,
            test_cases_generated=5,
        )

        feedback = builder.build_feedback_from_test_metrics(metrics)

        assert "Test Validity: PASSED" in feedback
        assert "5 test cases" in feedback

    def test_feedback_failed_validation(self):
        """Feedback shows validation failure."""
        builder = TestGenerationPromptBuilder()
        metrics = ProgramMetrics(is_valid_test=False)

        feedback = builder.build_feedback_from_test_metrics(
            metrics,
            validation_output="SyntaxError: invalid syntax",
        )

        assert "Test Validity: FAILED" in feedback
        assert "SyntaxError" in feedback

    def test_feedback_includes_kill_details(self):
        """Feedback includes kill details when provided."""
        builder = TestGenerationPromptBuilder()
        metrics = ProgramMetrics(champion_kill_rate=0.5, is_valid_test=True)
        kill_details = [
            {"champion_id": "champ-1", "test_name": "test_empty", "error": "AssertionError"},
            {"champion_id": "champ-2", "test_name": "test_large", "error": "Timeout"},
        ]

        feedback = builder.build_feedback_from_test_metrics(
            metrics,
            kill_details=kill_details,
        )

        assert "Champions Killed" in feedback
        assert "champ-1" in feedback
        assert "test_empty" in feedback
        assert "AssertionError" in feedback

    def test_feedback_includes_edge_cases(self):
        """Feedback includes covered edge cases."""
        builder = TestGenerationPromptBuilder()
        metrics = ProgramMetrics(
            is_valid_test=True,
            covers_edge_cases=["empty", "null", "large"],
        )

        feedback = builder.build_feedback_from_test_metrics(metrics)

        assert "Edge Cases Covered" in feedback
        assert "empty" in feedback
        assert "null" in feedback

    def test_feedback_includes_overall_score(self):
        """Feedback includes overall test score."""
        builder = TestGenerationPromptBuilder()
        metrics = ProgramMetrics(
            test_score=0.8,
            is_valid_test=True,
        )

        feedback = builder.build_feedback_from_test_metrics(metrics)

        assert "Test Score" in feedback


class TestEdgeCases:
    """Edge case tests for TestGenerationPromptBuilder."""

    def test_empty_edge_cases_list(self):
        """Handles empty edge cases list gracefully."""
        builder = TestGenerationPromptBuilder()

        prompt = builder.build_test_evolution_prompt(
            task="Sort",
            champion_code="def sort(arr): pass",
            known_edge_cases=[],
        )

        assert "Already Covered Edge Cases" not in prompt

    def test_empty_inspirations_list(self):
        """Handles empty inspirations list gracefully."""
        builder = TestGenerationPromptBuilder()

        prompt = builder.build_test_evolution_prompt(
            task="Sort",
            champion_code="def sort(arr): pass",
            inspiration_tests=[],
        )

        assert "Inspiration Tests" not in prompt

    def test_many_edge_cases_truncated(self):
        """Many edge cases are truncated in prompt."""
        builder = TestGenerationPromptBuilder()
        many_cases = [f"case_{i}" for i in range(50)]

        prompt = builder.build_test_evolution_prompt(
            task="Sort",
            champion_code="def sort(arr): pass",
            known_edge_cases=many_cases,
        )

        # Should include first 20
        assert "case_0" in prompt
        assert "case_19" in prompt
        # Should not include beyond 20
        assert "case_49" not in prompt
        # Should indicate more exist
        assert "30 more" in prompt
