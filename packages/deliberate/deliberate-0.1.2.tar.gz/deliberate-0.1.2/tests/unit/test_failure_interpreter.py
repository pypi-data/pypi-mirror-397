"""Unit tests for FailureInterpreter.

Tests the heuristic parsing of test run artifacts to extract failure information.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock

from deliberate.validation.failure_interpreter import (
    FailureInterpretation,
    FailureInterpreter,
)
from deliberate.validation.types import RunArtifacts


class TestFailureInterpreterHeuristics:
    """Tests for heuristic-based failure interpretation."""

    def create_artifacts(
        self,
        stdout: str = "",
        stderr: str = "",
        junit_xml: str | None = None,
        exit_code: int = 1,
    ) -> RunArtifacts:
        """Helper to create RunArtifacts for testing."""
        return RunArtifacts(
            command="pytest",
            cwd=Path.cwd(),
            exit_code=exit_code,
            duration_seconds=1.0,
            stdout=stdout,
            stderr=stderr,
            junit_xml=junit_xml,
        )

    def test_parses_junit_xml_failures(self) -> None:
        """Should extract failed test names from JUnit XML."""
        junit_xml = """<?xml version="1.0"?>
        <testsuite tests="3" failures="2" errors="0">
            <testcase classname="tests.test_foo" name="test_one" time="0.1"/>
            <testcase classname="tests.test_foo" name="test_two" time="0.2">
                <failure message="AssertionError">Expected 1, got 2</failure>
            </testcase>
            <testcase classname="tests.test_bar" name="test_three" time="0.3">
                <failure message="ValueError">Invalid value</failure>
            </testcase>
        </testsuite>
        """
        artifacts = self.create_artifacts(junit_xml=junit_xml)
        interpreter = FailureInterpreter()

        result = interpreter.interpret(artifacts)

        assert len(result.failed_tests) == 2
        assert "tests.test_foo::test_two" in result.failed_tests
        assert "tests.test_bar::test_three" in result.failed_tests
        assert "JUnit XML" in (result.summary or "")

    def test_parses_junit_xml_with_errors(self) -> None:
        """Should extract test names from error elements too."""
        junit_xml = """<?xml version="1.0"?>
        <testsuite tests="2" failures="0" errors="1">
            <testcase classname="tests.test_foo" name="test_one" time="0.1"/>
            <testcase classname="tests.test_foo" name="test_crash" time="0.0">
                <error message="RuntimeError">Unexpected crash</error>
            </testcase>
        </testsuite>
        """
        artifacts = self.create_artifacts(junit_xml=junit_xml)
        interpreter = FailureInterpreter()

        result = interpreter.interpret(artifacts)

        assert len(result.failed_tests) == 1
        assert "tests.test_foo::test_crash" in result.failed_tests

    def test_extracts_test_counts_from_junit_xml(self) -> None:
        """Should extract test counts from JUnit XML testsuite attributes."""
        junit_xml = """<?xml version="1.0"?>
        <testsuite tests="10" failures="2" errors="1" skipped="1">
            <testcase classname="tests.test_foo" name="test_fail1">
                <failure message="Error">Details</failure>
            </testcase>
            <testcase classname="tests.test_foo" name="test_fail2">
                <failure message="Error">Details</failure>
            </testcase>
            <testcase classname="tests.test_foo" name="test_error">
                <error message="Error">Details</error>
            </testcase>
        </testsuite>
        """
        artifacts = self.create_artifacts(junit_xml=junit_xml)
        interpreter = FailureInterpreter()

        result = interpreter.interpret(artifacts)

        # Test counts should be extracted
        assert result.tests_run == 10
        assert result.tests_failed == 3  # 2 failures + 1 error
        assert result.tests_skipped == 1
        assert result.tests_passed == 6  # 10 - 3 - 1

    def test_test_counts_none_without_junit(self) -> None:
        """Test counts should be None when no JUnit XML is available."""
        artifacts = self.create_artifacts(
            stdout="FAILED tests/test_foo.py::test_one",
        )
        interpreter = FailureInterpreter()

        result = interpreter.interpret(artifacts)

        assert result.tests_run is None
        assert result.tests_passed is None
        assert result.tests_failed is None
        assert result.tests_skipped is None

    def test_handles_invalid_junit_xml(self) -> None:
        """Should handle malformed JUnit XML gracefully."""
        artifacts = self.create_artifacts(
            junit_xml="<not valid xml",
            stdout="FAILED tests/test_foo.py::test_fallback",
        )
        interpreter = FailureInterpreter()

        result = interpreter.interpret(artifacts)

        # Should fall back to stdout parsing
        assert "tests/test_foo.py::test_fallback" in result.failed_tests

    def test_parses_pytest_stdout(self) -> None:
        """Should extract failures from pytest-style stdout."""
        stdout = """
        =========================== short test summary info ============================
        FAILED tests/test_example.py::test_one - AssertionError: expected 1
        FAILED tests/test_example.py::test_two - ValueError: invalid
        ============================== 2 failed in 0.5s ===============================
        """
        artifacts = self.create_artifacts(stdout=stdout)
        interpreter = FailureInterpreter()

        result = interpreter.interpret(artifacts)

        assert len(result.failed_tests) == 2
        assert "tests/test_example.py::test_one" in result.failed_tests
        assert "tests/test_example.py::test_two" in result.failed_tests

    def test_parses_pytest_stderr(self) -> None:
        """Should also check stderr for failure patterns."""
        stderr = """
        FAILED tests/test_stderr.py::test_from_stderr
        """
        artifacts = self.create_artifacts(stderr=stderr)
        interpreter = FailureInterpreter()

        result = interpreter.interpret(artifacts)

        assert "tests/test_stderr.py::test_from_stderr" in result.failed_tests

    def test_parses_generic_fail_patterns(self) -> None:
        """Should extract failures from generic FAIL patterns."""
        stdout = """
        Running tests...
        FAIL test.module::test_generic_one
        Failed test.other::test_generic_two
        OK test.passing::test_ok
        """
        artifacts = self.create_artifacts(stdout=stdout)
        interpreter = FailureInterpreter()

        result = interpreter.interpret(artifacts)

        assert "test.module::test_generic_one" in result.failed_tests
        assert "test.other::test_generic_two" in result.failed_tests
        # Should not include passing tests
        assert not any("test_ok" in t for t in result.failed_tests)

    def test_deduplicates_failures(self) -> None:
        """Should not duplicate failures found in multiple places."""
        junit_xml = """<?xml version="1.0"?>
        <testsuite tests="1" failures="1">
            <testcase classname="tests.test_foo" name="test_dup" time="0.1">
                <failure>Failed</failure>
            </testcase>
        </testsuite>
        """
        stdout = "FAILED tests.test_foo::test_dup - AssertionError"
        artifacts = self.create_artifacts(junit_xml=junit_xml, stdout=stdout)
        interpreter = FailureInterpreter()

        result = interpreter.interpret(artifacts)

        # Should only appear once
        assert len(result.failed_tests) == 1
        assert "tests.test_foo::test_dup" in result.failed_tests

    def test_no_failures_detected(self) -> None:
        """Should return empty list when no failures found."""
        artifacts = self.create_artifacts(
            stdout="All 10 tests passed!",
            exit_code=0,
        )
        interpreter = FailureInterpreter()

        result = interpreter.interpret(artifacts)

        assert result.failed_tests == []
        assert "No failures detected" in (result.summary or "")

    def test_returns_sorted_failures(self) -> None:
        """Should return failures in sorted order."""
        stdout = """
        FAILED tests/z_test.py::test_z
        FAILED tests/a_test.py::test_a
        FAILED tests/m_test.py::test_m
        """
        artifacts = self.create_artifacts(stdout=stdout)
        interpreter = FailureInterpreter()

        result = interpreter.interpret(artifacts)

        assert result.failed_tests == sorted(result.failed_tests)


class TestFailureInterpreterLLMFallback:
    """Tests for LLM fallback when heuristics fail."""

    def create_artifacts(
        self,
        stdout: str = "",
        stderr: str = "",
        exit_code: int = 1,
    ) -> RunArtifacts:
        """Helper to create RunArtifacts for testing."""
        return RunArtifacts(
            command="pytest",
            cwd=Path.cwd(),
            exit_code=exit_code,
            duration_seconds=1.0,
            stdout=stdout,
            stderr=stderr,
        )

    def test_uses_llm_when_heuristics_fail(self) -> None:
        """Should call LLM handler when heuristics find nothing."""
        # Output that heuristics won't parse
        artifacts = self.create_artifacts(
            stdout="Some obscure test output format that isn't recognized",
            exit_code=1,
        )

        # Mock LLM handler
        llm_response = json.dumps(
            {
                "failed_tests": ["obscure_test::test_one", "obscure_test::test_two"],
                "summary": "Parsed by LLM",
            }
        )
        mock_handler = MagicMock(return_value=llm_response)

        interpreter = FailureInterpreter(llm_handler=mock_handler)
        result = interpreter.interpret(artifacts)

        mock_handler.assert_called_once()
        assert len(result.failed_tests) == 2
        assert "obscure_test::test_one" in result.failed_tests
        assert "LLM" in result.summary

    def test_skips_llm_when_heuristics_succeed(self) -> None:
        """Should not call LLM when heuristics find failures."""
        artifacts = self.create_artifacts(
            stdout="FAILED tests/test_foo.py::test_bar",
        )

        mock_handler = MagicMock()
        interpreter = FailureInterpreter(llm_handler=mock_handler)
        result = interpreter.interpret(artifacts)

        mock_handler.assert_not_called()
        assert "tests/test_foo.py::test_bar" in result.failed_tests

    def test_handles_llm_json_error(self) -> None:
        """Should handle invalid JSON from LLM gracefully."""
        artifacts = self.create_artifacts(
            stdout="Unrecognized output",
            exit_code=1,
        )

        mock_handler = MagicMock(return_value="not valid json")
        interpreter = FailureInterpreter(llm_handler=mock_handler)
        result = interpreter.interpret(artifacts)

        # Should return empty result, not crash
        assert result.failed_tests == []

    def test_handles_llm_exception(self) -> None:
        """Should handle LLM handler exceptions gracefully."""
        artifacts = self.create_artifacts(
            stdout="Unrecognized output",
            exit_code=1,
        )

        mock_handler = MagicMock(side_effect=RuntimeError("LLM API error"))
        interpreter = FailureInterpreter(llm_handler=mock_handler)
        result = interpreter.interpret(artifacts)

        # Should return empty result, not crash
        assert result.failed_tests == []

    def test_handles_llm_empty_response(self) -> None:
        """Should handle empty failed_tests from LLM."""
        artifacts = self.create_artifacts(
            stdout="Unrecognized output",
            exit_code=1,
        )

        llm_response = json.dumps(
            {
                "failed_tests": [],
                "summary": "No failures found by LLM either",
            }
        )
        mock_handler = MagicMock(return_value=llm_response)

        interpreter = FailureInterpreter(llm_handler=mock_handler)
        result = interpreter.interpret(artifacts)

        # Should return empty result
        assert result.failed_tests == []


class TestFailureInterpretationDataclass:
    """Tests for the FailureInterpretation dataclass."""

    def test_default_values(self) -> None:
        """Should have sensible defaults."""
        interpretation = FailureInterpretation()

        assert interpretation.failed_tests == []
        assert interpretation.summary is None
        assert interpretation.raw == {}

    def test_with_values(self) -> None:
        """Should store provided values."""
        interpretation = FailureInterpretation(
            failed_tests=["test_a", "test_b"],
            summary="2 failures found",
            raw={"source": "heuristic"},
        )

        assert interpretation.failed_tests == ["test_a", "test_b"]
        assert interpretation.summary == "2 failures found"
        assert interpretation.raw["source"] == "heuristic"


class TestRunArtifactsIntegration:
    """Tests for RunArtifacts being passed correctly."""

    def test_interpreter_receives_all_artifact_fields(self) -> None:
        """Verify interpreter can access all RunArtifacts fields."""
        artifacts = RunArtifacts(
            command="pytest -v",
            cwd=Path("/some/path"),
            exit_code=1,
            duration_seconds=5.5,
            stdout="FAILED tests/test_foo.py::test_one",
            stderr="Some error output",
            junit_xml=None,
        )

        interpreter = FailureInterpreter()
        result = interpreter.interpret(artifacts)

        # Should parse stdout
        assert "tests/test_foo.py::test_one" in result.failed_tests

    def test_prompt_building_uses_artifacts(self) -> None:
        """Verify _build_prompt uses artifact fields correctly."""
        artifacts = RunArtifacts(
            command="pytest --verbose",
            cwd=Path("/project"),
            exit_code=2,
            duration_seconds=10.0,
            stdout="Test output here",
            stderr="Error output here",
        )

        interpreter = FailureInterpreter()
        prompt = interpreter._build_prompt(artifacts)

        assert "pytest --verbose" in prompt
        assert "Exit code: 2" in prompt
        assert "Test output here" in prompt
        assert "Error output here" in prompt
