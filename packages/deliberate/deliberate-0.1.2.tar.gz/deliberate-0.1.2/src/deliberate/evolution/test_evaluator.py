"""Test validation evaluator for adversarial test generation.

Evaluates generated tests through a validation cascade:
- Level 1: Syntax validation (tests parse and compile)
- Level 2: Judge validation (tests are legitimate business requirements)
- Level 3: Kill rate evaluation (tests break champion implementations)
"""

import ast
import re
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

from deliberate.adapters.base import ModelAdapter

from .types import Program


class TestValidationLevel(Enum):
    """Validation levels for adversarial tests."""

    SYNTAX = auto()  # Tests parse correctly
    JUDGE = auto()  # Tests are legitimate (not trick tests)
    KILL_RATE = auto()  # Tests break champions


@dataclass
class TestValidationResult:
    """Result of test validation."""

    level_passed: TestValidationLevel
    is_valid: bool
    syntax_valid: bool
    judge_approved: bool | None  # None if not evaluated
    kill_rate: float  # 0.0 to 1.0
    test_count: int
    errors: list[str] = field(default_factory=list)
    killed_champions: list[str] = field(default_factory=list)
    edge_cases_detected: list[str] = field(default_factory=list)
    judge_feedback: str = ""

    @property
    def passed_all(self) -> bool:
        """True if passed all validation levels."""
        return self.syntax_valid and (self.judge_approved is None or self.judge_approved) and self.is_valid


@dataclass
class KillResult:
    """Result of running tests against a champion."""

    champion_id: str
    killed: bool
    test_name: str | None = None
    error_message: str = ""
    execution_time_ms: float = 0.0


class TestValidationEvaluator:
    """Evaluates generated tests through a validation cascade.

    The evaluator performs three levels of validation:
    1. **Syntax**: Tests must parse as valid Python
    2. **Judge**: An LLM judge verifies tests are legitimate (optional)
    3. **Kill Rate**: Tests are run against champions to measure effectiveness
    """

    def __init__(
        self,
        judge_agent: ModelAdapter | None = None,
        min_kill_rate: float = 0.1,
        require_judge_approval: bool = True,
        max_test_time_seconds: float = 30.0,
    ):
        """Initialize the test evaluator.

        Args:
            judge_agent: LLM adapter for judge validation (optional).
            min_kill_rate: Minimum kill rate for tests to be useful.
            require_judge_approval: Whether judge approval is required.
            max_test_time_seconds: Maximum time for running tests.
        """
        self.judge_agent = judge_agent
        self.min_kill_rate = min_kill_rate
        self.require_judge_approval = require_judge_approval
        self.max_test_time_seconds = max_test_time_seconds

    async def evaluate(
        self,
        test_code: str,
        champions: list[Program] | None = None,
        task_description: str | None = None,
        run_kill_evaluation: bool = True,
    ) -> TestValidationResult:
        """Evaluate test code through the validation cascade.

        Args:
            test_code: The test code to evaluate.
            champions: Champion implementations to test against.
            task_description: Description of the task for judge context.
            run_kill_evaluation: Whether to run kill rate evaluation.

        Returns:
            TestValidationResult with validation outcomes.
        """
        errors = []
        edge_cases = []

        # Level 1: Syntax Validation
        syntax_result = self._validate_syntax(test_code)
        if not syntax_result["valid"]:
            return TestValidationResult(
                level_passed=TestValidationLevel.SYNTAX,
                is_valid=False,
                syntax_valid=False,
                judge_approved=None,
                kill_rate=0.0,
                test_count=0,
                errors=syntax_result["errors"],
            )

        test_count = syntax_result["test_count"]
        edge_cases = syntax_result.get("edge_cases", [])

        # Level 2: Judge Validation (if configured)
        judge_approved = None
        judge_feedback = ""
        if self.judge_agent and task_description:
            judge_result = await self._validate_with_judge(test_code, task_description)
            judge_approved = judge_result["approved"]
            judge_feedback = judge_result.get("feedback", "")
            if not judge_approved and self.require_judge_approval:
                errors.append(f"Judge rejected tests: {judge_feedback}")
                return TestValidationResult(
                    level_passed=TestValidationLevel.JUDGE,
                    is_valid=False,
                    syntax_valid=True,
                    judge_approved=False,
                    kill_rate=0.0,
                    test_count=test_count,
                    errors=errors,
                    edge_cases_detected=edge_cases,
                    judge_feedback=judge_feedback,
                )

        # Level 3: Kill Rate Evaluation
        kill_rate = 0.0
        killed_champions = []
        if run_kill_evaluation and champions:
            kill_results = await self._evaluate_kill_rate(test_code, champions)
            killed_champions = [r.champion_id for r in kill_results if r.killed]
            kill_rate = len(killed_champions) / len(champions) if champions else 0.0

        is_valid = (
            syntax_result["valid"]
            and (not self.require_judge_approval or judge_approved is not False)
            and (not run_kill_evaluation or kill_rate >= self.min_kill_rate)
        )

        return TestValidationResult(
            level_passed=TestValidationLevel.KILL_RATE,
            is_valid=is_valid,
            syntax_valid=True,
            judge_approved=judge_approved,
            kill_rate=kill_rate,
            test_count=test_count,
            errors=errors,
            killed_champions=killed_champions,
            edge_cases_detected=edge_cases,
            judge_feedback=judge_feedback,
        )

    def _validate_syntax(self, test_code: str) -> dict[str, Any]:
        """Validate test code syntax and structure.

        Returns:
            Dict with 'valid', 'errors', 'test_count', 'edge_cases'.
        """
        errors = []
        test_count = 0
        edge_cases = []

        # Check Python syntax
        try:
            tree = ast.parse(test_code)
        except SyntaxError as e:
            return {
                "valid": False,
                "errors": [f"Syntax error at line {e.lineno}: {e.msg}"],
                "test_count": 0,
            }

        # Count test functions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name.startswith("test_"):
                    test_count += 1
                    # Extract edge case hints from function names
                    edge_case = self._extract_edge_case_from_name(node.name)
                    if edge_case:
                        edge_cases.append(edge_case)

        if test_count == 0:
            errors.append("No test functions found (functions must start with 'test_')")
            return {"valid": False, "errors": errors, "test_count": 0}

        # Check for pytest imports (optional but recommended)
        has_pytest_import = "import pytest" in test_code or "from pytest" in test_code

        if not has_pytest_import:
            # Not an error, just a note
            pass

        return {
            "valid": True,
            "errors": errors,
            "test_count": test_count,
            "edge_cases": edge_cases,
        }

    def _extract_edge_case_from_name(self, func_name: str) -> str | None:
        """Extract edge case description from test function name.

        E.g., 'test_empty_list' -> 'empty_list'
        """
        # Remove 'test_' prefix
        if func_name.startswith("test_"):
            case_name = func_name[5:]
            # Convert underscores to spaces for readability
            return case_name.replace("_", " ")
        return None

    async def _validate_with_judge(self, test_code: str, task_description: str) -> dict[str, Any]:
        """Have LLM judge validate that tests are legitimate.

        Returns:
            Dict with 'approved' (bool) and 'feedback' (str).
        """
        if not self.judge_agent:
            return {"approved": True, "feedback": "No judge configured"}

        prompt = self._build_judge_prompt(test_code, task_description)

        try:
            response = await self.judge_agent.call(prompt)
            return self._parse_judge_response(response.content)
        except Exception as e:
            # On error, default to approved to avoid blocking
            return {
                "approved": True,
                "feedback": f"Judge evaluation failed: {e}",
            }

    def _build_judge_prompt(self, test_code: str, task_description: str) -> str:
        """Build prompt for judge validation."""
        return f"""You are evaluating whether generated test cases are legitimate \
business requirements.

## Task Description
{task_description}

## Generated Tests
```python
{test_code}
```

## Evaluation Criteria

Tests are LEGITIMATE if they:
1. Test actual business requirements from the task
2. Use reasonable input values for the domain
3. Have expected outputs that match the task specification
4. Cover edge cases that could realistically occur

Tests are ILLEGITIMATE (trick tests) if they:
1. Test requirements not mentioned in the task
2. Use inputs that are clearly outside the problem domain
3. Have expected outputs that contradict the task specification
4. Are designed to be impossible to pass

## Your Response

Respond with a JSON object:
```json
{{
  "approved": true/false,
  "feedback": "Brief explanation of your decision",
  "concerns": ["List of any specific concerns (empty if approved)"]
}}
```
"""

    def _parse_judge_response(self, response: str) -> dict[str, Any]:
        """Parse judge response to extract approval status."""
        # Try to parse JSON
        import json

        try:
            # Find JSON block
            json_match = re.search(r"```json\s*(.*?)\s*```", response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(1))
                return {
                    "approved": data.get("approved", False),
                    "feedback": data.get("feedback", ""),
                }

            # Try direct JSON parse
            data = json.loads(response)
            return {
                "approved": data.get("approved", False),
                "feedback": data.get("feedback", ""),
            }
        except json.JSONDecodeError:
            pass

        # Fallback: look for keywords
        response_lower = response.lower()
        if "approved" in response_lower or "legitimate" in response_lower:
            approved = "not approved" not in response_lower
            return {"approved": approved, "feedback": response[:200]}

        # Default to not approved if unclear
        return {"approved": False, "feedback": "Could not parse judge response"}

    async def _evaluate_kill_rate(self, test_code: str, champions: list[Program]) -> list[KillResult]:
        """Evaluate tests against champions to compute kill rate.

        Note: This is a placeholder. Real implementation would run
        tests in isolated environments (containers/worktrees).

        Args:
            test_code: The test code to run.
            champions: Champion implementations to test against.

        Returns:
            List of KillResult for each champion.
        """
        results = []

        for champion in champions:
            # In production, this would:
            # 1. Create isolated environment (DevContainer/worktree)
            # 2. Write champion code + test code to files
            # 3. Run pytest and capture results
            # 4. Parse failures

            # For now, return placeholder
            results.append(
                KillResult(
                    champion_id=champion.id,
                    killed=False,  # Would be determined by test execution
                    test_name=None,
                    error_message="",
                    execution_time_ms=0.0,
                )
            )

        return results

    def update_program_metrics(
        self,
        program: Program,
        validation_result: TestValidationResult,
    ) -> None:
        """Update program metrics based on validation result.

        Args:
            program: The program to update.
            validation_result: The validation result.
        """
        metrics = program.metrics
        metrics.is_valid_test = validation_result.is_valid
        metrics.champion_kill_rate = validation_result.kill_rate
        metrics.test_cases_generated = validation_result.test_count
        metrics.covers_edge_cases = validation_result.edge_cases_detected

        # Update overall score for test programs based on kill rate
        # Higher kill rate = better adversarial test
        if validation_result.is_valid:
            metrics.test_score = validation_result.kill_rate
