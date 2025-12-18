"""Tests for Dev Container detection and execution."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from deliberate.config import DevContainerConfig
from deliberate.validation.devcontainer import (
    DevContainerInfo,
    DevContainerRunner,
    detect_devcontainer,
)
from deliberate.validation.runner import ValidationRunner


class TestDetectDevcontainer:
    """Tests for detect_devcontainer function."""

    def test_detects_devcontainer_in_folder(self, tmp_path: Path) -> None:
        """Detects .devcontainer/devcontainer.json."""
        devcontainer_dir = tmp_path / ".devcontainer"
        devcontainer_dir.mkdir()
        config_path = devcontainer_dir / "devcontainer.json"
        config_path.write_text(
            json.dumps(
                {
                    "name": "Test Container",
                    "image": "python:3.11",
                }
            )
        )

        result = detect_devcontainer(tmp_path)

        assert result is not None
        assert result.config_path == config_path
        assert result.workspace_folder == tmp_path
        assert result.name == "Test Container"
        assert result.image == "python:3.11"

    def test_detects_devcontainer_at_root(self, tmp_path: Path) -> None:
        """Detects .devcontainer.json at root level."""
        config_path = tmp_path / ".devcontainer.json"
        config_path.write_text(
            json.dumps(
                {
                    "name": "Root Container",
                    "image": "node:18",
                }
            )
        )

        result = detect_devcontainer(tmp_path)

        assert result is not None
        assert result.config_path == config_path
        assert result.name == "Root Container"

    def test_returns_none_when_no_config(self, tmp_path: Path) -> None:
        """Returns None when no devcontainer config exists."""
        result = detect_devcontainer(tmp_path)
        assert result is None

    def test_handles_json5_comments(self, tmp_path: Path) -> None:
        """Handles JSON5-style comments in devcontainer.json."""
        devcontainer_dir = tmp_path / ".devcontainer"
        devcontainer_dir.mkdir()
        config_path = devcontainer_dir / "devcontainer.json"
        # Note: trailing comma before } is handled by the parser
        config_path.write_text(
            """{
            // This is a comment
            "name": "With Comments",
            "image": "ubuntu:22.04"
        }"""
        )

        result = detect_devcontainer(tmp_path)

        assert result is not None
        assert result.name == "With Comments"
        assert result.image == "ubuntu:22.04"

    def test_detects_dockerfile(self, tmp_path: Path) -> None:
        """Detects Dockerfile-based devcontainer."""
        devcontainer_dir = tmp_path / ".devcontainer"
        devcontainer_dir.mkdir()
        config_path = devcontainer_dir / "devcontainer.json"
        dockerfile = devcontainer_dir / "Dockerfile"
        dockerfile.write_text("FROM python:3.11\n")
        config_path.write_text(
            json.dumps(
                {
                    "name": "Dockerfile Container",
                    "dockerFile": "Dockerfile",
                }
            )
        )

        result = detect_devcontainer(tmp_path)

        assert result is not None
        assert result.dockerfile_path == dockerfile

    def test_detects_docker_compose(self, tmp_path: Path) -> None:
        """Detects docker-compose-based devcontainer."""
        devcontainer_dir = tmp_path / ".devcontainer"
        devcontainer_dir.mkdir()
        config_path = devcontainer_dir / "devcontainer.json"
        compose_file = devcontainer_dir / "docker-compose.yml"
        compose_file.write_text("version: '3'\n")
        config_path.write_text(
            json.dumps(
                {
                    "name": "Compose Container",
                    "dockerComposeFile": "docker-compose.yml",
                }
            )
        )

        result = detect_devcontainer(tmp_path)

        assert result is not None
        assert result.docker_compose_file == compose_file
        assert result.is_compose_based

    def test_handles_invalid_json(self, tmp_path: Path) -> None:
        """Returns None for invalid JSON."""
        devcontainer_dir = tmp_path / ".devcontainer"
        devcontainer_dir.mkdir()
        config_path = devcontainer_dir / "devcontainer.json"
        config_path.write_text("{ not valid json }")

        result = detect_devcontainer(tmp_path)

        assert result is None


class TestDevContainerInfo:
    """Tests for DevContainerInfo dataclass."""

    def test_is_compose_based_true(self, tmp_path: Path) -> None:
        """Returns True when docker_compose_file is set."""
        info = DevContainerInfo(
            config_path=tmp_path / "devcontainer.json",
            workspace_folder=tmp_path,
            docker_compose_file=tmp_path / "docker-compose.yml",
        )
        assert info.is_compose_based is True

    def test_is_compose_based_false(self, tmp_path: Path) -> None:
        """Returns False when docker_compose_file is not set."""
        info = DevContainerInfo(
            config_path=tmp_path / "devcontainer.json",
            workspace_folder=tmp_path,
        )
        assert info.is_compose_based is False


class TestDevContainerRunner:
    """Tests for DevContainerRunner class."""

    @pytest.fixture
    def devcontainer_info(self, tmp_path: Path) -> DevContainerInfo:
        """Create a test DevContainerInfo."""
        return DevContainerInfo(
            config_path=tmp_path / ".devcontainer" / "devcontainer.json",
            workspace_folder=tmp_path,
            name="Test Container",
        )

    def test_devcontainer_cli_available_check(self, devcontainer_info: DevContainerInfo) -> None:
        """Checks if devcontainer CLI is available."""
        runner = DevContainerRunner(devcontainer_info)
        # Result depends on system, just check property works
        assert isinstance(runner.devcontainer_cli_available, bool)

    def test_docker_available_check(self, devcontainer_info: DevContainerInfo) -> None:
        """Checks if docker is available."""
        runner = DevContainerRunner(devcontainer_info)
        # Result depends on system, just check property works
        assert isinstance(runner.docker_available, bool)

    @pytest.mark.asyncio
    async def test_exec_fails_without_container(self, devcontainer_info: DevContainerInfo) -> None:
        """Exec fails if container can't be started."""
        runner = DevContainerRunner(devcontainer_info)

        # Mock shutil.which to return None for both devcontainer and docker
        with patch("shutil.which", return_value=None):
            exit_code, stdout, stderr = await runner.exec("echo test")

        assert exit_code == -1
        assert "neither" in stderr.lower() or "failed" in stderr.lower()

    @pytest.mark.asyncio
    async def test_exec_via_cli_success(self, devcontainer_info: DevContainerInfo) -> None:
        """Exec via devcontainer CLI works when available."""
        runner = DevContainerRunner(devcontainer_info)
        runner._container_id = "test-container-id"

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = b"hello world\n"
        mock_result.stderr = b""

        # Mock shutil.which to return devcontainer path
        with patch(
            "shutil.which",
            side_effect=lambda x: "/usr/bin/devcontainer" if x == "devcontainer" else None,
        ):
            with patch(
                "deliberate.validation.devcontainer.SubprocessManager.run",
                new_callable=AsyncMock,
                return_value=mock_result,
            ):
                exit_code, stdout, stderr = await runner.exec("echo 'hello world'")

        assert exit_code == 0
        assert "hello world" in stdout


class TestValidationRunnerDevContainerIntegration:
    """Tests for ValidationRunner with DevContainer integration."""

    def test_runner_without_devcontainer_config(self, tmp_path: Path) -> None:
        """Runner works without devcontainer config."""
        runner = ValidationRunner(
            working_dir=tmp_path,
            command="echo test",
            timeout_seconds=30,
        )
        assert runner._devcontainer_runner is None

    def test_runner_with_devcontainer_disabled(self, tmp_path: Path) -> None:
        """Runner doesn't use devcontainer when disabled."""
        config = DevContainerConfig(enabled=False)
        runner = ValidationRunner(
            working_dir=tmp_path,
            command="echo test",
            devcontainer_config=config,
        )
        assert runner._devcontainer_runner is None

    def test_runner_with_devcontainer_enabled_no_config(self, tmp_path: Path) -> None:
        """Runner doesn't use devcontainer when no devcontainer.json exists."""
        config = DevContainerConfig(enabled=True, auto_detect=True)
        runner = ValidationRunner(
            working_dir=tmp_path,
            command="echo test",
            devcontainer_config=config,
        )
        assert runner._devcontainer_runner is None

    def test_runner_with_devcontainer_enabled_with_config(self, tmp_path: Path) -> None:
        """Runner detects and uses devcontainer when enabled and config exists."""
        # Create devcontainer config
        devcontainer_dir = tmp_path / ".devcontainer"
        devcontainer_dir.mkdir()
        config_path = devcontainer_dir / "devcontainer.json"
        config_path.write_text(
            json.dumps(
                {
                    "name": "Test",
                    "image": "python:3.11",
                }
            )
        )

        config = DevContainerConfig(enabled=True, auto_detect=True)
        runner = ValidationRunner(
            working_dir=tmp_path,
            command="pytest",
            devcontainer_config=config,
        )

        assert runner._devcontainer_info is not None
        assert runner._devcontainer_runner is not None
        assert runner._devcontainer_info.name == "Test"

    @pytest.mark.asyncio
    async def test_runner_runs_on_host_without_devcontainer(self, tmp_path: Path) -> None:
        """Runner executes on host when no devcontainer configured."""
        runner = ValidationRunner(
            working_dir=tmp_path,
            command="echo host-test",
            timeout_seconds=30,
        )

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = b"host-test\n"
        mock_result.stderr = b""

        with patch(
            "deliberate.validation.runner.SubprocessManager.run",
            new_callable=AsyncMock,
            return_value=mock_result,
        ):
            result = await runner.run()

        assert result.passed
        assert "host-test" in result.stdout

    @pytest.mark.asyncio
    async def test_runner_runs_in_devcontainer_when_configured(self, tmp_path: Path) -> None:
        """Runner executes in devcontainer when configured."""
        # Create devcontainer config
        devcontainer_dir = tmp_path / ".devcontainer"
        devcontainer_dir.mkdir()
        config_path = devcontainer_dir / "devcontainer.json"
        config_path.write_text(
            json.dumps(
                {
                    "name": "Test",
                    "image": "python:3.11",
                }
            )
        )

        config = DevContainerConfig(enabled=True, auto_detect=True)
        runner = ValidationRunner(
            working_dir=tmp_path,
            command="pytest",
            devcontainer_config=config,
        )

        # Mock the devcontainer runner's exec method
        async def mock_exec(command: str) -> tuple[int, str, str]:
            return (0, "container-test\n", "")

        runner._devcontainer_runner.exec = mock_exec  # type: ignore

        result = await runner.run()

        assert result.passed
        assert "container-test" in result.stdout
