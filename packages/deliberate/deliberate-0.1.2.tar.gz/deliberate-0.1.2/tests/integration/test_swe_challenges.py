"""Integration tests for SWE challenge fixtures.

These tests verify that the SWE challenge fixtures are properly set up
and can be used with deliberate's workflow.
"""

from pathlib import Path

import pytest

FIXTURES_ROOT = Path(__file__).parent.parent / "fixtures" / "swe-challenges"


class TestPythonBugFix:
    """Test the Python bug-fix challenge fixture."""

    @pytest.fixture
    def challenge_dir(self):
        return FIXTURES_ROOT / "python-bug-fix"

    def test_fixture_exists(self, challenge_dir):
        """Verify all required files exist."""
        assert challenge_dir.exists()
        assert (challenge_dir / "calculator.py").exists()
        assert (challenge_dir / "test_calculator.py").exists()
        assert (challenge_dir / "pyproject.toml").exists()
        assert (challenge_dir / "TASK.md").exists()

    def test_task_description(self, challenge_dir):
        """Verify task description is meaningful."""
        task = (challenge_dir / "TASK.md").read_text()
        assert "Fix" in task or "Bug" in task
        assert "calculator" in task.lower()

    def test_code_has_bugs(self, challenge_dir):
        """Verify the code actually has the documented bugs."""
        code = (challenge_dir / "calculator.py").read_text()

        # Bug 1: No division by zero handling
        assert "ZeroDivisionError" not in code

        # Bug 2: Missing else clause for unknown operators
        assert "raise ValueError" not in code or code.count("raise ValueError") == 1


class TestTypeScriptFeature:
    """Test the TypeScript feature addition challenge fixture."""

    @pytest.fixture
    def challenge_dir(self):
        return FIXTURES_ROOT / "typescript-feature"

    def test_fixture_exists(self, challenge_dir):
        """Verify all required files exist."""
        assert challenge_dir.exists()
        assert (challenge_dir / "src" / "utils.ts").exists()
        assert (challenge_dir / "src" / "utils.test.ts").exists()
        assert (challenge_dir / "package.json").exists()
        assert (challenge_dir / "tsconfig.json").exists()
        assert (challenge_dir / "TASK.md").exists()

    def test_task_description(self, challenge_dir):
        """Verify task description is meaningful."""
        task = (challenge_dir / "TASK.md").read_text()
        assert "email" in task.lower() or "validation" in task.lower()

    def test_function_missing(self, challenge_dir):
        """Verify the isValidEmail function is not implemented yet."""
        code = (challenge_dir / "src" / "utils.ts").read_text()
        assert "isValidEmail" not in code or "TODO" in code


class TestRustCompileFix:
    """Test the Rust compile-fix challenge fixture."""

    @pytest.fixture
    def challenge_dir(self):
        return FIXTURES_ROOT / "rust-compile-fix"

    def test_fixture_exists(self, challenge_dir):
        """Verify all required files exist."""
        assert challenge_dir.exists()
        assert (challenge_dir / "src" / "lib.rs").exists()
        assert (challenge_dir / "Cargo.toml").exists()
        assert (challenge_dir / "TASK.md").exists()

    def test_task_description(self, challenge_dir):
        """Verify task description is meaningful."""
        task = (challenge_dir / "TASK.md").read_text()
        assert "compilation" in task.lower() or "error" in task.lower()

    def test_code_has_errors(self, challenge_dir):
        """Verify the code has documented compilation errors."""
        code = (challenge_dir / "src" / "lib.rs").read_text()

        # Error 1: Wrong return type
        assert "-> i32" in code  # Should be usize

        # Error 2: Missing &mut self
        assert "fn delete(&self" in code  # Should be &mut self

        # Error 3: Missing Default impl
        assert "impl Default for Store" not in code or "// ERROR" in code


class TestChallengeIntegration:
    """Integration tests for using challenges with deliberate."""

    def test_python_challenge_pytest_detects_failures(self, tmp_path):
        """Verify pytest detects the expected failures in Python challenge."""
        import subprocess

        challenge_dir = FIXTURES_ROOT / "python-bug-fix"

        # Run pytest on the fixture
        result = subprocess.run(
            ["uv", "run", "pytest", str(challenge_dir), "-v", "--tb=no"],
            capture_output=True,
            text=True,
            cwd=challenge_dir,
        )

        # Should have some failures (the bugs)
        assert "FAILED" in result.stdout or result.returncode != 0

    def test_rust_challenge_cargo_check_fails(self, tmp_path):
        """Verify cargo check detects compilation errors."""
        import shutil
        import subprocess

        challenge_dir = FIXTURES_ROOT / "rust-compile-fix"

        # Skip if cargo not available
        if not shutil.which("cargo"):
            pytest.skip("cargo not installed")

        result = subprocess.run(
            ["cargo", "check"],
            capture_output=True,
            text=True,
            cwd=challenge_dir,
        )

        # Should fail compilation
        assert result.returncode != 0
        assert "error" in result.stderr.lower()
