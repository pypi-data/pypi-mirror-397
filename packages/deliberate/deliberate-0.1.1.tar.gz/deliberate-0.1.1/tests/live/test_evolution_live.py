"""Live tests for the evolution module.

These tests require actual LLM API access and are designed to validate
the evolution system with real challenges.

Run with: uv run pytest tests/live/test_evolution_live.py -v -s
"""

import asyncio
from pathlib import Path

import pytest

from deliberate.evolution import (
    DatabaseConfig,
    EvaluationLevel,
    EvolutionConfig,
    EvolutionController,
    InMemoryEvaluator,
    Program,
    ProgramDatabase,
    ProgramMetrics,
)
from tests.live.challenges import (
    TWO_SUM,
)


class TestEvolutionWithInMemoryEvaluator:
    """Tests using InMemoryEvaluator for quick validation."""

    @pytest.fixture
    def evaluator_two_sum(self):
        """Create evaluator for Two Sum challenge."""
        # Two Sum takes (nums: list, target: int)
        # Dict keys are tuples of arguments: (arg1, arg2, ...)
        # When key is tuple, evaluator calls func(*key)
        test_cases = {
            ((2, 7, 11, 15), 9): [0, 1],
            ((3, 2, 4), 6): [1, 2],
            ((3, 3), 6): [0, 1],
            ((-1, -2, -3, -4, -5), -8): [2, 4],
            ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10), 19): [8, 9],
        }
        return InMemoryEvaluator(
            expected_outputs=test_cases,
            test_function="solve",
        )

    @pytest.fixture
    def database(self):
        """Create a fresh program database with diverse niches."""
        return ProgramDatabase(
            config=DatabaseConfig(
                max_programs=100,
                num_islands=2,
                niche_dimensions=["test_score", "coverage_score"],
            ),
            seed=42,
        )

    @pytest.mark.asyncio
    async def test_manual_evolution_two_sum(self, evaluator_two_sum, database):
        """Test manual evolution on Two Sum challenge.

        This test doesn't use LLMs - it manually adds programs
        to verify the evaluation and database work correctly.

        Workflow: evaluate first, then add with metrics from evaluation.
        """
        # Create and evaluate seed program (incorrect)
        seed = Program(
            id="seed_0",
            code=TWO_SUM.seed_code,
            metrics=ProgramMetrics(generation=0),
            is_valid=True,
        )

        # Evaluate seed
        result = await evaluator_two_sum.evaluate(seed, EvaluationLevel.UNIT_FAST)
        assert not result.passed  # Seed should fail
        assert result.metrics.test_score == 0.0

        # Update seed metrics and add to database
        seed.metrics = result.metrics
        seed.metrics.generation = 0
        database.add(seed)

        # Create and evaluate correct solution
        correct_code = """def solve(nums: list[int], target: int) -> list[int]:
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
"""
        correct = Program(
            id="correct_1",
            code=correct_code,
            metrics=ProgramMetrics(generation=1, parent_id="seed_0"),
            is_valid=True,
        )

        # Evaluate correct solution first
        result = await evaluator_two_sum.evaluate(correct, EvaluationLevel.UNIT_FAST)
        assert result.passed
        assert result.metrics.test_score == 1.0

        # Update metrics and add to database
        correct.metrics = result.metrics
        correct.metrics.generation = 1
        correct.metrics.parent_id = "seed_0"
        database.add(correct)

        # Check database state - correct should be best due to higher test_score
        best = database.get_best()
        assert best is not None
        assert best.id == "correct_1"

    @pytest.mark.asyncio
    async def test_evolution_with_partial_solutions(self, evaluator_two_sum, database):
        """Test evolution with programs of varying quality.

        Workflow: evaluate first, then add with metrics from evaluation.
        """
        # Create and evaluate partial solution (brute force O(n^2))
        partial_code = """def solve(nums: list[int], target: int) -> list[int]:
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []
"""
        partial = Program(
            id="partial_1",
            code=partial_code,
            metrics=ProgramMetrics(generation=1),
            is_valid=True,
        )

        # Evaluate partial solution first
        result = await evaluator_two_sum.evaluate(partial, EvaluationLevel.UNIT_FAST)
        assert result.passed  # Should pass all test cases
        assert result.metrics.test_score == 1.0

        # Update metrics and add to database
        partial.metrics = result.metrics
        partial.metrics.generation = 1
        database.add(partial)

        # Create and evaluate optimal solution
        optimal_code = """def solve(nums: list[int], target: int) -> list[int]:
    seen = {}
    for i, num in enumerate(nums):
        if target - num in seen:
            return [seen[target - num], i]
        seen[num] = i
    return []
"""
        optimal = Program(
            id="optimal_1",
            code=optimal_code,
            metrics=ProgramMetrics(generation=2),
            is_valid=True,
        )

        # Evaluate optimal solution first
        result = await evaluator_two_sum.evaluate(optimal, EvaluationLevel.UNIT_FAST)

        # Update metrics with different coverage to ensure different niche
        optimal.metrics = result.metrics
        optimal.metrics.generation = 2
        optimal.metrics.coverage_score = 0.5  # Different niche dimension
        database.add(optimal)

        # Both should be in database (different niches due to coverage_score)
        assert database.size >= 2

    @pytest.mark.asyncio
    async def test_evaluation_cascade(self, database):
        """Test that evaluation cascade works correctly."""
        evaluator = InMemoryEvaluator(
            expected_outputs={(5,): 10},
            test_function="double",
        )

        # Syntax error
        syntax_error = Program(
            id="syntax_error",
            code="def double(x): return x *",  # Missing operand
            is_valid=True,
        )

        result = await evaluator.evaluate(syntax_error, EvaluationLevel.SYNTAX)
        assert not result.passed
        assert "Syntax error" in result.feedback

        # Valid but wrong
        wrong = Program(
            id="wrong",
            code="def double(x): return x + 1",
            is_valid=True,
        )

        result = await evaluator.evaluate(wrong, EvaluationLevel.UNIT_FAST)
        assert not result.passed

        # Correct
        correct = Program(
            id="correct",
            code="def double(x): return x * 2",
            is_valid=True,
        )

        result = await evaluator.evaluate(correct, EvaluationLevel.UNIT_FAST)
        assert result.passed


class TestDatabaseOperations:
    """Tests for database operations."""

    def test_niche_based_storage(self):
        """Test that database properly uses niche-based storage."""
        db = ProgramDatabase(
            config=DatabaseConfig(
                num_islands=2,
                niche_dimensions=["test_score"],
            ),
            seed=42,
        )

        # Add program with score 0.5
        p1 = Program(
            id="p1",
            code="code1",
            metrics=ProgramMetrics(test_score=0.5),
            is_valid=True,
        )
        db.add(p1)

        # Add better program in same niche
        p2 = Program(
            id="p2",
            code="code2",
            metrics=ProgramMetrics(test_score=0.5, lint_score=1.0, coverage_score=0.5),
            is_valid=True,
        )
        db.add(p2)

        # p2 should have better overall score and either replace p1 or be added
        assert db.size >= 1
        best = db.get_best()
        assert best is not None

    def test_island_sampling(self):
        """Test sampling from different islands."""
        db = ProgramDatabase(
            config=DatabaseConfig(num_islands=4),
            seed=42,
        )

        # Add programs to different islands
        for i in range(20):
            db.add(
                Program(
                    id=f"p{i}",
                    code=f"code{i}",
                    metrics=ProgramMetrics(test_score=i / 20),
                    is_valid=True,
                ),
                island_id=i % 4,
            )

        # Sample should return diverse programs
        parents, inspirations = db.sample(n_parents=2, n_inspirations=3)
        assert len(parents) == 2
        assert len(inspirations) == 3

        # No duplicates
        all_ids = [p.id for p in parents + inspirations]
        assert len(all_ids) == len(set(all_ids))


@pytest.mark.skipif(
    not Path.home().joinpath(".anthropic").exists() and not Path.home().joinpath(".openai").exists(),
    reason="No API credentials found",
)
class TestEvolutionWithLLM:
    """Tests that actually use LLM APIs.

    These are marked for skip if no credentials are found.
    Run manually with: pytest tests/live/test_evolution_live.py -v -s -k TestEvolutionWithLLM
    """

    @pytest.mark.asyncio
    @pytest.mark.timeout(120)
    async def test_evolution_two_sum_with_llm(self):
        """Test actual evolution on Two Sum with LLM."""
        from deliberate.adapters.api_adapter import APIAdapter

        # Create adapter (will use ANTHROPIC_API_KEY or OPENAI_API_KEY from env)
        try:
            agent = APIAdapter(
                name="flash",
                model="claude-3-haiku-20240307",  # Fast, cheap model
            )
        except ImportError:
            pytest.skip("litellm not installed")

        # Create evaluator
        test_cases = {}
        for args, expected in TWO_SUM.test_cases.items():
            test_cases[args[0]] = expected
        evaluator = InMemoryEvaluator(
            expected_outputs=test_cases,
            test_function="solve",
        )

        # Create database
        db = ProgramDatabase(seed=42)

        # Create controller
        controller = EvolutionController(
            database=db,
            agents={"flash": agent},
            evaluator=evaluator,
            config=EvolutionConfig(
                max_iterations=5,  # Keep it short for testing
                target_score=1.0,
                fast_model_ratio=1.0,
            ),
        )

        # Run evolution
        result = await controller.evolve(
            task=TWO_SUM.get_task_prompt(),
            seed_program=TWO_SUM.seed_code,
        )

        print(f"\nEvolution Result: {result.summary}")
        print(f"Best Score: {result.best_program.metrics.overall_score if result.best_program else 0}")

        # Should make some progress
        assert result.programs_generated > 0
        if result.best_program:
            print(f"\nBest Code:\n{result.best_program.code}")


if __name__ == "__main__":
    # Run a quick test
    asyncio.run(
        TestEvolutionWithInMemoryEvaluator().test_manual_evolution_two_sum(
            InMemoryEvaluator(
                expected_outputs={
                    ([2, 7, 11, 15], 9): [0, 1],
                    ([3, 2, 4], 6): [1, 2],
                    ([3, 3], 6): [0, 1],
                },
                test_function="solve",
            ),
            ProgramDatabase(seed=42),
        )
    )
