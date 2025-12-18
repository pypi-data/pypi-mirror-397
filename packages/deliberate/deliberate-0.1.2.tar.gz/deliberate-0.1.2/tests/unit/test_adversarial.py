"""Tests for AdversarialTestLoop."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from deliberate.adapters.base import AdapterResponse, ModelAdapter
from deliberate.config import DevContainerConfig
from deliberate.evolution.adversarial import (
    AdversarialConfig,
    AdversarialResult,
    AdversarialTestLoop,
    CycleResult,
)


def _make_mock_adapter(name: str = "test-agent") -> ModelAdapter:
    """Create a mock model adapter."""
    mock = MagicMock(spec=ModelAdapter)
    mock.name = name
    mock.call = AsyncMock()
    mock.estimate_cost = MagicMock(return_value=0.001)
    return mock


class TestAdversarialConfig:
    """Tests for AdversarialConfig dataclass."""

    def test_default_values(self):
        """Default values are sensible."""
        config = AdversarialConfig()

        assert config.max_cycles == 3
        assert config.max_test_evolution_iterations == 10
        assert config.max_code_evolution_iterations == 10
        assert config.min_kill_rate == 0.1
        assert config.target_kill_rate == 0.5
        assert config.max_new_tests_per_cycle == 3
        assert config.require_isolation is True
        assert config.test_timeout_seconds == 30.0
        assert config.require_judge_approval is True

    def test_custom_values(self):
        """Can set custom configuration."""
        config = AdversarialConfig(
            max_cycles=5,
            min_kill_rate=0.2,
            target_kill_rate=0.8,
            require_isolation=False,
        )

        assert config.max_cycles == 5
        assert config.min_kill_rate == 0.2
        assert config.target_kill_rate == 0.8
        assert config.require_isolation is False


class TestAdversarialTestLoopInit:
    """Tests for AdversarialTestLoop initialization."""

    def test_init_with_devcontainer_isolation(self):
        """Can initialize with DevContainer isolation."""
        test_agent = _make_mock_adapter("test")
        code_agent = _make_mock_adapter("code")
        devcontainer = DevContainerConfig(enabled=True)

        loop = AdversarialTestLoop(
            test_agent=test_agent,
            code_agent=code_agent,
            devcontainer_config=devcontainer,
        )

        assert loop.test_agent is test_agent
        assert loop.code_agent is code_agent
        assert loop.devcontainer_config is devcontainer

    def test_init_with_worktree_isolation(self):
        """Can initialize with worktree isolation."""
        test_agent = _make_mock_adapter("test")
        code_agent = _make_mock_adapter("code")

        loop = AdversarialTestLoop(
            test_agent=test_agent,
            code_agent=code_agent,
            worktree_enabled=True,
        )

        assert loop.worktree_enabled is True

    def test_init_fails_without_isolation(self):
        """Raises error when isolation is required but not configured."""
        test_agent = _make_mock_adapter("test")
        code_agent = _make_mock_adapter("code")

        with pytest.raises(ValueError, match="requires isolation"):
            AdversarialTestLoop(
                test_agent=test_agent,
                code_agent=code_agent,
                # No isolation configured
            )

    def test_init_allows_no_isolation_when_disabled(self):
        """Can initialize without isolation when explicitly disabled."""
        test_agent = _make_mock_adapter("test")
        code_agent = _make_mock_adapter("code")
        config = AdversarialConfig(require_isolation=False)

        # Should not raise
        loop = AdversarialTestLoop(
            test_agent=test_agent,
            code_agent=code_agent,
            config=config,
        )

        assert loop.config.require_isolation is False


class TestAdversarialTestLoopRun:
    """Tests for AdversarialTestLoop.run method."""

    @pytest.fixture
    def mock_adapters(self):
        """Create mock adapters that return valid code."""
        test_agent = _make_mock_adapter("test")
        code_agent = _make_mock_adapter("code")

        # Test agent returns test code
        test_agent.call.return_value = AdapterResponse(
            content="""Here are the tests:
```python
def test_example():
    assert True

def test_empty():
    assert solve([]) == []
```
""",
            token_usage=100,
            duration_seconds=1.0,
        )

        # Code agent returns implementation
        code_agent.call.return_value = AdapterResponse(
            content="""Here is the fix:
```python
def solve(arr):
    if not arr:
        return []
    return sorted(arr)
```
""",
            token_usage=150,
            duration_seconds=1.5,
        )

        return test_agent, code_agent

    @pytest.mark.asyncio
    async def test_run_basic_cycle(self, mock_adapters):
        """Runs a basic adversarial cycle."""
        from unittest.mock import patch

        from deliberate.evolution.test_evaluator import TestValidationResult

        test_agent, code_agent = mock_adapters
        config = AdversarialConfig(
            require_isolation=False,
            max_cycles=1,
            max_test_evolution_iterations=1,
            max_code_evolution_iterations=1,
        )

        loop = AdversarialTestLoop(
            test_agent=test_agent,
            code_agent=code_agent,
            config=config,
        )

        # Mock the test evaluator to return valid results
        from deliberate.evolution.test_evaluator import TestValidationLevel

        mock_validation = TestValidationResult(
            level_passed=TestValidationLevel.KILL_RATE,
            is_valid=True,
            syntax_valid=True,
            judge_approved=True,
            kill_rate=0.5,
            test_count=2,
            errors=[],
            killed_champions=["champion"],
            edge_cases_detected=["empty input"],
            judge_feedback="Tests look good",
        )
        with patch.object(loop.test_evaluator, "evaluate", return_value=mock_validation):
            result = await loop.run(
                task="Sort an array",
                initial_code="def solve(arr): pass",
            )

        assert isinstance(result, AdversarialResult)
        assert result.total_cycles >= 1
        assert result.final_code != ""
        assert result.final_tests != ""

    @pytest.mark.asyncio
    async def test_run_with_initial_tests(self, mock_adapters):
        """Runs with provided initial tests."""
        test_agent, code_agent = mock_adapters
        config = AdversarialConfig(
            require_isolation=False,
            max_cycles=1,
            max_test_evolution_iterations=1,
            max_code_evolution_iterations=1,
        )

        loop = AdversarialTestLoop(
            test_agent=test_agent,
            code_agent=code_agent,
            config=config,
        )

        initial_tests = "def test_basic(): assert True"
        result = await loop.run(
            task="Sort an array",
            initial_code="def solve(arr): pass",
            initial_tests=initial_tests,
        )

        assert isinstance(result, AdversarialResult)

    @pytest.mark.asyncio
    async def test_run_handles_agent_failure(self, mock_adapters):
        """Handles agent call failures gracefully."""
        test_agent, code_agent = mock_adapters
        test_agent.call.side_effect = RuntimeError("API Error")

        config = AdversarialConfig(
            require_isolation=False,
            max_cycles=1,
            max_test_evolution_iterations=2,
            max_code_evolution_iterations=1,
        )

        loop = AdversarialTestLoop(
            test_agent=test_agent,
            code_agent=code_agent,
            config=config,
        )

        # Should not raise - handles errors internally
        result = await loop.run(
            task="Sort an array",
            initial_code="def solve(arr): pass",
        )

        assert isinstance(result, AdversarialResult)

    @pytest.mark.asyncio
    async def test_run_tracks_metrics(self, mock_adapters):
        """Tracks metrics during execution."""
        test_agent, code_agent = mock_adapters
        config = AdversarialConfig(
            require_isolation=False,
            max_cycles=2,
            max_test_evolution_iterations=1,
            max_code_evolution_iterations=1,
        )

        loop = AdversarialTestLoop(
            test_agent=test_agent,
            code_agent=code_agent,
            config=config,
        )

        result = await loop.run(
            task="Sort an array",
            initial_code="def solve(arr): pass",
        )

        assert result.total_time_seconds > 0
        assert len(result.cycle_results) > 0


class TestCycleResult:
    """Tests for CycleResult dataclass."""

    def test_create_cycle_result(self):
        """Can create a CycleResult."""
        result = CycleResult(
            cycle_number=1,
            tests_evolved=5,
            tests_valid=3,
            kill_rate=0.4,
            code_evolved=2,
            code_passes_tests=True,
            killed_champions=["champ-1"],
            new_edge_cases=["empty", "negative"],
            duration_seconds=10.5,
        )

        assert result.cycle_number == 1
        assert result.tests_evolved == 5
        assert result.tests_valid == 3
        assert result.kill_rate == 0.4
        assert result.code_passes_tests is True
        assert "champ-1" in result.killed_champions
        assert "empty" in result.new_edge_cases


class TestAdversarialResult:
    """Tests for AdversarialResult dataclass."""

    def test_create_adversarial_result(self):
        """Can create an AdversarialResult."""
        cycle = CycleResult(
            cycle_number=1,
            tests_evolved=3,
            tests_valid=2,
            kill_rate=0.5,
            code_evolved=1,
            code_passes_tests=True,
        )

        result = AdversarialResult(
            success=True,
            final_code="def solve(): pass",
            final_tests="def test_it(): assert True",
            total_cycles=1,
            cycle_results=[cycle],
            final_kill_rate=0.0,
            edge_cases_discovered=["empty", "large"],
            total_tests_generated=3,
            total_code_iterations=1,
            total_tokens=500,
            total_cost_usd=0.01,
            total_time_seconds=30.0,
            termination_reason="tests_cannot_break_code",
        )

        assert result.success is True
        assert result.termination_reason == "tests_cannot_break_code"
        assert len(result.cycle_results) == 1
        assert "empty" in result.edge_cases_discovered


class TestExtractCode:
    """Tests for code extraction from LLM responses."""

    @pytest.fixture
    def loop(self):
        """Create a loop instance for testing."""
        test_agent = _make_mock_adapter("test")
        code_agent = _make_mock_adapter("code")
        config = AdversarialConfig(require_isolation=False)
        return AdversarialTestLoop(
            test_agent=test_agent,
            code_agent=code_agent,
            config=config,
        )

    def test_extract_python_code_block(self, loop):
        """Extracts code from python code block."""
        text = """
Here is the solution:

```python
def solve():
    return 42
```

That's the implementation.
"""
        code = loop._extract_code(text)
        assert code == "def solve():\n    return 42"

    def test_extract_py_code_block(self, loop):
        """Extracts code from py code block."""
        text = """
```py
def test():
    pass
```
"""
        code = loop._extract_code(text)
        assert code == "def test():\n    pass"

    def test_extract_generic_code_block(self, loop):
        """Extracts code from generic code block."""
        text = """
```
def example():
    return 1
```
"""
        code = loop._extract_code(text)
        assert code == "def example():\n    return 1"

    def test_extract_no_code_block(self, loop):
        """Returns None when no code block found."""
        text = "Just some text without code."
        code = loop._extract_code(text)
        assert code is None


class TestBuildCodeEvolutionPrompt:
    """Tests for code evolution prompt building."""

    @pytest.fixture
    def loop(self):
        """Create a loop instance for testing."""
        test_agent = _make_mock_adapter("test")
        code_agent = _make_mock_adapter("code")
        config = AdversarialConfig(require_isolation=False)
        return AdversarialTestLoop(
            test_agent=test_agent,
            code_agent=code_agent,
            config=config,
        )

    def test_prompt_includes_task(self, loop):
        """Prompt includes the task description."""
        prompt = loop._build_code_evolution_prompt(
            task="Sort an array",
            current_code="def solve(arr): pass",
            tests="def test_it(): assert True",
            iteration=1,
        )

        assert "Sort an array" in prompt

    def test_prompt_includes_current_code(self, loop):
        """Prompt includes the current code."""
        prompt = loop._build_code_evolution_prompt(
            task="Sort",
            current_code="def solve(arr): return sorted(arr)",
            tests="def test_it(): assert True",
            iteration=1,
        )

        assert "def solve(arr): return sorted(arr)" in prompt

    def test_prompt_includes_tests(self, loop):
        """Prompt includes the tests to pass."""
        prompt = loop._build_code_evolution_prompt(
            task="Sort",
            current_code="def solve(arr): pass",
            tests="def test_empty(): assert solve([]) == []",
            iteration=1,
        )

        assert "def test_empty(): assert solve([]) == []" in prompt

    def test_prompt_includes_iteration(self, loop):
        """Prompt includes the iteration number."""
        prompt = loop._build_code_evolution_prompt(
            task="Sort",
            current_code="def solve(arr): pass",
            tests="def test_it(): assert True",
            iteration=5,
        )

        assert "Iteration 5" in prompt
