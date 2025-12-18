"""Live tests for Dev Container support.

These tests require Docker to be installed and running.
They are skipped by default unless RUN_LIVE_TESTS=1 is set.
"""

import json
import os
import shutil
from pathlib import Path

import pytest

# Skip all tests in this module unless explicitly enabled
pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(
        os.environ.get("RUN_LIVE_TESTS") != "1",
        reason="Live tests disabled (set RUN_LIVE_TESTS=1 to enable)",
    ),
    pytest.mark.skipif(
        shutil.which("docker") is None,
        reason="Docker not available",
    ),
]


class TestDevContainerDetection:
    """Tests for DevContainer config detection with real files."""

    def test_detects_python_devcontainer(self, tmp_path: Path) -> None:
        """Detect a typical Python devcontainer config."""
        from deliberate.validation import detect_devcontainer

        devcontainer_dir = tmp_path / ".devcontainer"
        devcontainer_dir.mkdir()
        config_path = devcontainer_dir / "devcontainer.json"
        config_path.write_text(
            json.dumps(
                {
                    "name": "Python Development",
                    "image": "python:3.11-slim",
                    "postCreateCommand": "pip install -e .",
                    "customizations": {"vscode": {"extensions": ["ms-python.python"]}},
                }
            )
        )

        result = detect_devcontainer(tmp_path)

        assert result is not None
        assert result.name == "Python Development"
        assert result.image == "python:3.11-slim"
        assert not result.is_compose_based

    def test_detects_node_devcontainer(self, tmp_path: Path) -> None:
        """Detect a typical Node.js devcontainer config."""
        from deliberate.validation import detect_devcontainer

        devcontainer_dir = tmp_path / ".devcontainer"
        devcontainer_dir.mkdir()
        config_path = devcontainer_dir / "devcontainer.json"
        config_path.write_text(
            json.dumps(
                {
                    "name": "Node.js Development",
                    "image": "node:18-slim",
                    "postCreateCommand": "npm install",
                }
            )
        )

        result = detect_devcontainer(tmp_path)

        assert result is not None
        assert result.name == "Node.js Development"
        assert result.image == "node:18-slim"


class TestDevContainerDockerExecution:
    """Live tests for actual Docker container execution."""

    @pytest.fixture
    def python_devcontainer(self, tmp_path: Path) -> Path:
        """Create a minimal Python devcontainer for testing."""
        devcontainer_dir = tmp_path / ".devcontainer"
        devcontainer_dir.mkdir()
        config_path = devcontainer_dir / "devcontainer.json"
        config_path.write_text(
            json.dumps(
                {
                    "name": "Test Python Container",
                    "image": "python:3.11-slim",
                }
            )
        )

        # Create a simple Python file to test
        (tmp_path / "test_file.py").write_text('print("Hello from Python!")\n')

        return tmp_path

    @pytest.fixture
    def node_devcontainer(self, tmp_path: Path) -> Path:
        """Create a minimal Node.js devcontainer for testing."""
        devcontainer_dir = tmp_path / ".devcontainer"
        devcontainer_dir.mkdir()
        config_path = devcontainer_dir / "devcontainer.json"
        config_path.write_text(
            json.dumps(
                {
                    "name": "Test Node Container",
                    "image": "node:18-slim",
                }
            )
        )

        # Create a simple JS file to test
        (tmp_path / "test_file.js").write_text('console.log("Hello from Node!");\n')

        return tmp_path

    @pytest.fixture(autouse=True)
    def cleanup_containers(self, tmp_path: Path):
        """Clean up any containers created during tests."""
        yield
        # Cleanup after test
        container_name = f"deliberate-{tmp_path.name}"
        os.system(f"docker rm -f {container_name} 2>/dev/null")

    @pytest.mark.asyncio
    async def test_run_python_in_container(self, python_devcontainer: Path) -> None:
        """Execute Python inside a devcontainer.

        This test:
        1. Creates a minimal Python devcontainer config
        2. Starts the container via docker fallback
        3. Runs a Python command inside
        4. Verifies output

        Cost: $0 (no LLM calls, only Docker)
        """
        from deliberate.config import DevContainerConfig
        from deliberate.validation import ValidationRunner

        config = DevContainerConfig(enabled=True, auto_detect=True)
        runner = ValidationRunner(
            working_dir=python_devcontainer,
            command="python test_file.py",
            timeout_seconds=60,
            devcontainer_config=config,
        )

        assert runner._devcontainer_info is not None
        assert runner._devcontainer_info.name == "Test Python Container"
        assert runner._devcontainer_runner is not None

        result = await runner.run()

        assert result.passed, f"Validation failed: {result.stderr}"
        assert result.exit_code == 0
        assert "Hello from Python!" in result.stdout

    @pytest.mark.asyncio
    async def test_run_node_in_container(self, node_devcontainer: Path) -> None:
        """Execute Node.js inside a devcontainer.

        This test:
        1. Creates a minimal Node.js devcontainer config
        2. Starts the container via docker fallback
        3. Runs a Node command inside
        4. Verifies output

        Cost: $0 (no LLM calls, only Docker)
        """
        from deliberate.config import DevContainerConfig
        from deliberate.validation import ValidationRunner

        config = DevContainerConfig(enabled=True, auto_detect=True)
        runner = ValidationRunner(
            working_dir=node_devcontainer,
            command="node test_file.js",
            timeout_seconds=60,
            devcontainer_config=config,
        )

        assert runner._devcontainer_info is not None
        assert runner._devcontainer_info.name == "Test Node Container"

        result = await runner.run()

        assert result.passed, f"Validation failed: {result.stderr}"
        assert result.exit_code == 0
        assert "Hello from Node!" in result.stdout

    @pytest.mark.asyncio
    async def test_container_reuse(self, python_devcontainer: Path) -> None:
        """Verify container is reused for subsequent commands.

        This test:
        1. Runs first command (starts container)
        2. Runs second command (should reuse container)
        3. Both should succeed

        Cost: $0 (no LLM calls, only Docker)
        """
        from deliberate.config import DevContainerConfig
        from deliberate.validation import ValidationRunner

        config = DevContainerConfig(enabled=True, auto_detect=True)

        # First run - starts container
        runner1 = ValidationRunner(
            working_dir=python_devcontainer,
            command="python --version",
            timeout_seconds=60,
            devcontainer_config=config,
        )
        result1 = await runner1.run()
        assert result1.passed
        assert "Python" in result1.stdout

        # Second run - should reuse container
        runner2 = ValidationRunner(
            working_dir=python_devcontainer,
            command="python -c 'print(1+1)'",
            timeout_seconds=60,
            devcontainer_config=config,
        )
        result2 = await runner2.run()
        assert result2.passed
        assert "2" in result2.stdout

    @pytest.mark.asyncio
    async def test_failing_command_in_container(self, python_devcontainer: Path) -> None:
        """Verify failing commands are properly reported.

        Cost: $0 (no LLM calls, only Docker)
        """
        from deliberate.config import DevContainerConfig
        from deliberate.validation import ValidationRunner

        config = DevContainerConfig(enabled=True, auto_detect=True)
        runner = ValidationRunner(
            working_dir=python_devcontainer,
            command="python -c 'raise SystemExit(1)'",
            timeout_seconds=60,
            devcontainer_config=config,
        )

        result = await runner.run()

        assert not result.passed
        assert result.exit_code == 1

    @pytest.mark.asyncio
    async def test_workspace_files_visible(self, python_devcontainer: Path) -> None:
        """Verify workspace files are visible inside container.

        Cost: $0 (no LLM calls, only Docker)
        """
        from deliberate.config import DevContainerConfig
        from deliberate.validation import ValidationRunner

        # Create additional files
        (python_devcontainer / "data.txt").write_text("important data\n")
        (python_devcontainer / "config.json").write_text('{"key": "value"}\n')

        config = DevContainerConfig(enabled=True, auto_detect=True)
        runner = ValidationRunner(
            working_dir=python_devcontainer,
            command="ls -la && cat data.txt",
            timeout_seconds=60,
            devcontainer_config=config,
        )

        result = await runner.run()

        assert result.passed
        assert "test_file.py" in result.stdout
        assert "data.txt" in result.stdout
        assert "config.json" in result.stdout
        assert "important data" in result.stdout


class TestDevContainerWithPytest:
    """Live tests for running pytest inside devcontainer."""

    @pytest.fixture
    def pytest_project(self, tmp_path: Path) -> Path:
        """Create a minimal Python project with pytest tests."""
        devcontainer_dir = tmp_path / ".devcontainer"
        devcontainer_dir.mkdir()
        (devcontainer_dir / "devcontainer.json").write_text(
            json.dumps(
                {
                    "name": "Pytest Project",
                    "image": "python:3.11-slim",
                    "postCreateCommand": "pip install pytest",
                }
            )
        )

        # Create a simple module
        (tmp_path / "calculator.py").write_text(
            """
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b
"""
        )

        # Create tests
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        (tests_dir / "__init__.py").write_text("")
        (tests_dir / "test_calculator.py").write_text(
            """
import sys
sys.path.insert(0, '/workspace')
from calculator import add, multiply

def test_add():
    assert add(2, 3) == 5

def test_multiply():
    assert multiply(4, 5) == 20
"""
        )

        return tmp_path

    @pytest.fixture(autouse=True)
    def cleanup_containers(self, tmp_path: Path):
        """Clean up any containers created during tests."""
        yield
        container_name = f"deliberate-{tmp_path.name}"
        os.system(f"docker rm -f {container_name} 2>/dev/null")

    @pytest.mark.asyncio
    async def test_pytest_passes_in_container(self, pytest_project: Path) -> None:
        """Run pytest inside container and verify results.

        This is a realistic test of running a project's test suite in isolation.

        Cost: $0 (no LLM calls, only Docker)
        """
        from deliberate.config import DevContainerConfig
        from deliberate.validation import ValidationRunner

        config = DevContainerConfig(enabled=True, auto_detect=True)
        runner = ValidationRunner(
            working_dir=pytest_project,
            command="pip install pytest && pytest tests/ -v",
            timeout_seconds=120,
            devcontainer_config=config,
        )

        result = await runner.run()

        assert result.passed, f"Tests failed: {result.stdout}\n{result.stderr}"
        assert result.exit_code == 0
        assert "2 passed" in result.stdout or "PASSED" in result.stdout


class TestDevContainerDisabled:
    """Tests verifying host execution when devcontainer is disabled."""

    @pytest.mark.asyncio
    async def test_runs_on_host_when_disabled(self, tmp_path: Path) -> None:
        """Verify commands run on host when devcontainer.enabled=False.

        Cost: $0
        """
        from deliberate.config import DevContainerConfig
        from deliberate.validation import ValidationRunner

        # Create devcontainer config (should be ignored)
        devcontainer_dir = tmp_path / ".devcontainer"
        devcontainer_dir.mkdir()
        (devcontainer_dir / "devcontainer.json").write_text(json.dumps({"name": "Test", "image": "python:3.11"}))

        config = DevContainerConfig(enabled=False)
        runner = ValidationRunner(
            working_dir=tmp_path,
            command="echo 'running on host'",
            timeout_seconds=30,
            devcontainer_config=config,
        )

        # Should NOT have devcontainer runner
        assert runner._devcontainer_runner is None

        result = await runner.run()
        assert result.passed
        assert "running on host" in result.stdout

    @pytest.mark.asyncio
    async def test_runs_on_host_without_config(self, tmp_path: Path) -> None:
        """Verify commands run on host when no devcontainer.json exists.

        Cost: $0
        """
        from deliberate.config import DevContainerConfig
        from deliberate.validation import ValidationRunner

        # No devcontainer config
        config = DevContainerConfig(enabled=True, auto_detect=True)
        runner = ValidationRunner(
            working_dir=tmp_path,
            command="echo 'no container'",
            timeout_seconds=30,
            devcontainer_config=config,
        )

        # No devcontainer.json means no container
        assert runner._devcontainer_runner is None

        result = await runner.run()
        assert result.passed
        assert "no container" in result.stdout
