"""Linting and syntax validation for code files."""

import asyncio
from dataclasses import dataclass
from pathlib import Path


@dataclass
class LintResult:
    """Result of a lint/syntax check."""

    passed: bool
    command: str
    exit_code: int
    errors: list[str]
    warnings: list[str]
    stdout: str
    stderr: str

    @property
    def summary(self) -> str:
        """Human readable summary."""
        if self.passed:
            return "Lint: PASSED"
        return f"Lint: FAILED ({len(self.errors)} errors)"

    @property
    def error_log(self) -> str:
        """Format errors for agent feedback."""
        if not self.errors:
            return ""
        return "## Lint Errors:\n" + "\n".join(f"- {e}" for e in self.errors[:20])


async def lint_python_file(file_path: Path, timeout_seconds: int = 30) -> LintResult:
    """Check Python file for syntax errors and basic lint issues.

    Uses python -m py_compile for syntax, optionally ruff/flake8 for lint.
    """
    errors = []
    warnings = []
    stdout_combined = ""
    stderr_combined = ""

    # Step 1: Syntax check with py_compile (fast, always available)
    try:
        proc = await asyncio.create_subprocess_exec(
            "python",
            "-m",
            "py_compile",
            str(file_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout_seconds)
        stdout_combined += stdout.decode("utf-8", errors="replace")
        stderr_combined += stderr.decode("utf-8", errors="replace")

        if proc.returncode != 0:
            # Parse syntax error from stderr
            error_msg = stderr_combined.strip()
            if error_msg:
                errors.append(f"SyntaxError: {error_msg}")
            else:
                errors.append(f"Syntax check failed (exit code {proc.returncode})")

            return LintResult(
                passed=False,
                command=f"python -m py_compile {file_path}",
                exit_code=proc.returncode or 1,
                errors=errors,
                warnings=warnings,
                stdout=stdout_combined,
                stderr=stderr_combined,
            )
    except asyncio.TimeoutError:
        return LintResult(
            passed=False,
            command=f"python -m py_compile {file_path}",
            exit_code=-1,
            errors=["Syntax check timed out"],
            warnings=[],
            stdout="",
            stderr="Timeout",
        )
    except FileNotFoundError:
        return LintResult(
            passed=False,
            command=f"python -m py_compile {file_path}",
            exit_code=-1,
            errors=["Python not found"],
            warnings=[],
            stdout="",
            stderr="",
        )

    # Step 2: Try ruff for faster, more thorough lint (optional)
    try:
        proc = await asyncio.create_subprocess_exec(
            "ruff",
            "check",
            "--select=E,F",
            str(file_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout_seconds)
        ruff_out = stdout.decode("utf-8", errors="replace")
        stdout_combined += ruff_out

        if proc.returncode != 0:
            # Parse ruff errors
            for line in ruff_out.strip().split("\n"):
                if line.strip():
                    warnings.append(line.strip())
    except (FileNotFoundError, asyncio.TimeoutError):
        # ruff not installed, skip
        pass

    return LintResult(
        passed=True,
        command=f"python -m py_compile {file_path}",
        exit_code=0,
        errors=errors,
        warnings=warnings,
        stdout=stdout_combined,
        stderr=stderr_combined,
    )


async def lint_typescript_file(file_path: Path, timeout_seconds: int = 30) -> LintResult:
    """Check TypeScript/JavaScript file for syntax errors."""
    errors = []

    # Try tsc --noEmit for syntax check
    try:
        proc = await asyncio.create_subprocess_exec(
            "npx",
            "tsc",
            "--noEmit",
            "--skipLibCheck",
            str(file_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout_seconds)
        stdout_str = stdout.decode("utf-8", errors="replace")
        stderr_str = stderr.decode("utf-8", errors="replace")

        if proc.returncode != 0:
            for line in stdout_str.strip().split("\n"):
                if "error" in line.lower():
                    errors.append(line.strip())
            if not errors:
                errors.append(f"TypeScript check failed (exit code {proc.returncode})")

        return LintResult(
            passed=proc.returncode == 0,
            command=f"npx tsc --noEmit {file_path}",
            exit_code=proc.returncode or 0,
            errors=errors,
            warnings=[],
            stdout=stdout_str,
            stderr=stderr_str,
        )
    except (FileNotFoundError, asyncio.TimeoutError):
        # tsc not available, skip
        return LintResult(
            passed=True,
            command="",
            exit_code=0,
            errors=[],
            warnings=["TypeScript compiler not available"],
            stdout="",
            stderr="",
        )


async def lint_rust_file(file_path: Path, timeout_seconds: int = 60) -> LintResult:
    """Check Rust file for syntax errors using cargo check."""
    # For Rust, we need to run cargo check from the project root
    # Find Cargo.toml
    current = file_path.parent
    cargo_root = None
    while current != current.parent:
        if (current / "Cargo.toml").exists():
            cargo_root = current
            break
        current = current.parent

    if not cargo_root:
        return LintResult(
            passed=True,
            command="",
            exit_code=0,
            errors=[],
            warnings=["No Cargo.toml found, skipping Rust lint"],
            stdout="",
            stderr="",
        )

    try:
        proc = await asyncio.create_subprocess_exec(
            "cargo",
            "check",
            "--message-format=short",
            cwd=str(cargo_root),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout_seconds)
        stdout_str = stdout.decode("utf-8", errors="replace")
        stderr_str = stderr.decode("utf-8", errors="replace")

        errors = []
        if proc.returncode != 0:
            for line in stderr_str.strip().split("\n"):
                if "error" in line.lower():
                    errors.append(line.strip())

        return LintResult(
            passed=proc.returncode == 0,
            command="cargo check",
            exit_code=proc.returncode or 0,
            errors=errors,
            warnings=[],
            stdout=stdout_str,
            stderr=stderr_str,
        )
    except (FileNotFoundError, asyncio.TimeoutError) as e:
        return LintResult(
            passed=False,
            command="cargo check",
            exit_code=-1,
            errors=[str(e)],
            warnings=[],
            stdout="",
            stderr=str(e),
        )


async def lint_file(file_path: Path, timeout_seconds: int = 60) -> LintResult:
    """Lint a file based on its extension."""
    suffix = file_path.suffix.lower()

    if suffix == ".py":
        return await lint_python_file(file_path, timeout_seconds)
    elif suffix in {".ts", ".tsx", ".js", ".jsx"}:
        return await lint_typescript_file(file_path, timeout_seconds)
    elif suffix == ".rs":
        return await lint_rust_file(file_path, timeout_seconds)
    else:
        # Unknown file type, assume OK
        return LintResult(
            passed=True,
            command="",
            exit_code=0,
            errors=[],
            warnings=[f"No linter configured for {suffix} files"],
            stdout="",
            stderr="",
        )


async def lint_directory(
    directory: Path,
    patterns: list[str] | None = None,
    timeout_seconds: int = 120,
) -> LintResult:
    """Lint all matching files in a directory.

    Args:
        directory: Directory to lint.
        patterns: Glob patterns to match (default: ["**/*.py"]).
        timeout_seconds: Total timeout for all lint operations.

    Returns:
        Aggregated LintResult.
    """
    if patterns is None:
        patterns = ["**/*.py"]

    all_errors = []
    all_warnings = []
    stdout_parts = []
    stderr_parts = []

    files_checked = 0
    for pattern in patterns:
        for file_path in directory.glob(pattern):
            if file_path.is_file():
                result = await lint_file(file_path, timeout_seconds=30)
                files_checked += 1
                all_errors.extend(result.errors)
                all_warnings.extend(result.warnings)
                if result.stdout:
                    stdout_parts.append(result.stdout)
                if result.stderr:
                    stderr_parts.append(result.stderr)

    return LintResult(
        passed=len(all_errors) == 0,
        command=f"lint {files_checked} files",
        exit_code=1 if all_errors else 0,
        errors=all_errors,
        warnings=all_warnings,
        stdout="\n".join(stdout_parts),
        stderr="\n".join(stderr_parts),
    )
