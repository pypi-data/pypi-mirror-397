"""Validation and test runner subsystem."""

from deliberate.validation.analyzer import (
    EnvironmentInfo,
    analyze_environment,
    detect_lint_command_llm,
    detect_test_command_llm,
)
from deliberate.validation.analyzer import (
    clear_cache as clear_analyzer_cache,
)
from deliberate.validation.detectors import detect_project_type, detect_test_command
from deliberate.validation.devcontainer import (
    DevContainerInfo,
    DevContainerRunner,
    detect_devcontainer,
)
from deliberate.validation.linter import (
    LintResult,
    lint_directory,
    lint_file,
    lint_python_file,
)
from deliberate.validation.runner import (
    ValidationRunner,
    run_validation,
    run_validation_with_fallback,
)
from deliberate.validation.tdd_loop import (
    TDDConfig,
    TDDIteration,
    TDDLoop,
    TDDLoopResult,
    run_tdd_loop,
)
from deliberate.validation.types import (
    CaseResult,
    CaseStatus,
    # Backwards compatibility aliases
    TestCaseResult,
    TestStatus,
    ValidationConfig,
    ValidationResult,
)

__all__ = [
    # Core validation
    "ValidationRunner",
    "ValidationResult",
    "ValidationConfig",
    "CaseResult",
    "CaseStatus",
    "TestCaseResult",  # Backwards compatibility
    "TestStatus",  # Backwards compatibility
    "detect_test_command",
    "detect_project_type",
    "run_validation",
    "run_validation_with_fallback",
    # LLM-based environment analysis
    "EnvironmentInfo",
    "analyze_environment",
    "detect_test_command_llm",
    "detect_lint_command_llm",
    "clear_analyzer_cache",
    # Dev Container support
    "DevContainerInfo",
    "DevContainerRunner",
    "detect_devcontainer",
    # Linting
    "LintResult",
    "lint_file",
    "lint_directory",
    "lint_python_file",
    # TDD Loop
    "TDDConfig",
    "TDDIteration",
    "TDDLoop",
    "TDDLoopResult",
    "run_tdd_loop",
]
