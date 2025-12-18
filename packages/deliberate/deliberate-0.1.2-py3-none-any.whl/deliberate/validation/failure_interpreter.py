"""Failure interpretation with heuristic and LLM-backed strategies.

This module unifies how we extract failing tests or errors from raw run
artifacts. Today we use simple heuristics, but it is structured so we can
swap in an LLM-based interpreter without changing callers.
"""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Any, Callable

from deliberate.validation.types import RunArtifacts


@dataclass
class FailureInterpretation:
    """Structured interpretation of a failed test run.

    Contains:
    - failed_tests: List of fully-qualified test names that failed
    - summary: Human-readable summary of the interpretation
    - raw: Raw data from the interpretation source

    Optionally contains test counts (from JUnit XML):
    - tests_run, tests_passed, tests_failed, tests_skipped
    """

    failed_tests: list[str] = field(default_factory=list)
    summary: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    # Optional test counts (populated from JUnit XML if available)
    tests_run: int | None = None
    tests_passed: int | None = None
    tests_failed: int | None = None
    tests_skipped: int | None = None


class FailureInterpreter:
    """Interpret test run artifacts to extract failures.

    Heuristic parsing is used by default. If an LLM callable is provided, it
    will be used as a fallback when heuristics find nothing.
    """

    def __init__(
        self,
        llm_handler: Callable[[str], str] | None = None,
    ):
        """
        Args:
            llm_handler: Optional callable that takes a prompt string and
                returns a string response (expected JSON). This keeps the
                interpreter decoupled from any specific adapter.
        """
        self.llm_handler = llm_handler

    def interpret(self, artifacts: RunArtifacts) -> FailureInterpretation:
        """Interpret a run's artifacts."""
        # 1) Heuristics first
        failed = set()
        summary_parts: list[str] = []

        # Test counts from JUnit XML (optional)
        tests_run: int | None = None
        tests_passed: int | None = None
        tests_failed: int | None = None
        tests_skipped: int | None = None

        # Parse junit if present
        if artifacts.junit_xml:
            try:
                tree = ET.fromstring(artifacts.junit_xml)

                # Extract counts from testsuite element(s)
                # JUnit XML can have nested testsuites or a single testsuite
                for testsuite in tree.findall(".//testsuite") or [tree]:
                    if testsuite.tag == "testsuite":
                        ts_tests = int(testsuite.get("tests", 0))
                        ts_failures = int(testsuite.get("failures", 0))
                        ts_errors = int(testsuite.get("errors", 0))
                        ts_skipped = int(testsuite.get("skipped", 0))

                        tests_run = (tests_run or 0) + ts_tests
                        tests_failed = (tests_failed or 0) + ts_failures + ts_errors
                        tests_skipped = (tests_skipped or 0) + ts_skipped

                if tests_run is not None and tests_failed is not None:
                    tests_passed = tests_run - tests_failed - (tests_skipped or 0)

                # Extract individual failure names
                for testcase in tree.findall(".//testcase"):
                    failure = testcase.find("failure")
                    error = testcase.find("error")
                    if failure is not None or error is not None:
                        class_name = testcase.get("classname") or ""
                        name = testcase.get("name") or ""
                        if class_name and name:
                            failed.add(f"{class_name}::{name}")

                if failed:
                    summary_parts.append("Parsed failures from JUnit XML")
            except ET.ParseError:
                summary_parts.append("JUnit XML present but could not parse")

        # Regex fallback on stdout/stderr
        for output in (artifacts.stdout or "", artifacts.stderr or ""):
            for line in output.splitlines():
                # pytest style: FAILED tests/test_foo.py::test_bar
                match = re.search(r"FAILED\s+([^\s]+::[^\s]+)", line)
                if match:
                    failed.add(match.group(1))
                # generic: FAIL test.module::test_name
                generic = re.search(r"fail(?:ed)?\s+([\w./:-]+::[\w./:-]+)", line, re.IGNORECASE)
                if generic:
                    failed.add(generic.group(1))

        if failed:
            return FailureInterpretation(
                failed_tests=sorted(failed),
                summary="; ".join(summary_parts) if summary_parts else "Heuristic parse",
                raw={"source": "heuristic"},
                tests_run=tests_run,
                tests_passed=tests_passed,
                tests_failed=tests_failed,
                tests_skipped=tests_skipped,
            )

        # 2) Optional LLM fallback
        if self.llm_handler:
            prompt = self._build_prompt(artifacts)
            try:
                resp = self.llm_handler(prompt)
                data = json.loads(resp)
                failed_tests = data.get("failed_tests") or []
                summary = data.get("summary") or "LLM interpretation"
                if isinstance(failed_tests, list) and failed_tests:
                    return FailureInterpretation(
                        failed_tests=[str(t) for t in failed_tests],
                        summary=summary,
                        raw=data,
                        tests_run=tests_run,
                        tests_passed=tests_passed,
                        tests_failed=tests_failed,
                        tests_skipped=tests_skipped,
                    )
            except Exception:
                # Fall through to empty result
                pass

        return FailureInterpretation(
            failed_tests=[],
            summary="No failures detected",
            tests_run=tests_run,
            tests_passed=tests_passed,
            tests_failed=tests_failed,
            tests_skipped=tests_skipped,
        )

    def _build_prompt(self, artifacts: RunArtifacts) -> str:
        """Construct a prompt for LLM extraction."""
        return (
            "You are extracting failed test identifiers from a test run.\n"
            "Return JSON with a 'failed_tests' array of fully-qualified test names "
            "(e.g., tests/test_foo.py::test_bar) and a short 'summary'.\n"
            f"Command: {artifacts.command}\n"
            f"Exit code: {artifacts.exit_code}\n"
            f"Stdout:\n{artifacts.stdout[:4000]}\n"
            f"Stderr:\n{artifacts.stderr[:4000]}\n"
        )
