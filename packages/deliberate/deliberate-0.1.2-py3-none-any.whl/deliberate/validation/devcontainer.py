"""Dev Container detection and execution for isolated validation.

This module provides support for running validation commands inside Dev Containers,
providing isolation from the host system and consistent execution environments.
"""

import asyncio
import json
import logging
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from deliberate.utils.subprocess_manager import SubprocessManager

logger = logging.getLogger(__name__)


@dataclass
class DevContainerInfo:
    """Information about a detected Dev Container configuration."""

    config_path: Path
    workspace_folder: Path
    name: Optional[str] = None
    image: Optional[str] = None
    dockerfile_path: Optional[Path] = None
    docker_compose_file: Optional[Path] = None
    container_id: Optional[str] = None

    @property
    def is_compose_based(self) -> bool:
        """Check if this devcontainer uses docker-compose."""
        return self.docker_compose_file is not None


def detect_devcontainer(working_dir: Path) -> Optional[DevContainerInfo]:
    """Detect Dev Container configuration in the given directory.

    Searches for:
    1. .devcontainer/devcontainer.json
    2. .devcontainer.json (root level)

    Args:
        working_dir: Directory to search for devcontainer config.

    Returns:
        DevContainerInfo if found, None otherwise.
    """
    # Check .devcontainer/devcontainer.json first
    devcontainer_dir = working_dir / ".devcontainer"
    config_path = devcontainer_dir / "devcontainer.json"

    if not config_path.exists():
        # Check root level .devcontainer.json
        config_path = working_dir / ".devcontainer.json"

    if not config_path.exists():
        return None

    try:
        # Parse the devcontainer.json (strip comments for JSON5 compatibility)
        content = config_path.read_text()
        # Simple comment stripping - handles // comments
        lines = []
        for line in content.splitlines():
            stripped = line.strip()
            if not stripped.startswith("//"):
                # Remove trailing // comments
                comment_idx = line.find("//")
                if comment_idx > 0:
                    line = line[:comment_idx]
                lines.append(line)
        clean_content = "\n".join(lines)

        # Remove trailing commas (common in JSON5)
        clean_content = clean_content.replace(",]", "]").replace(",}", "}")

        config = json.loads(clean_content)
    except (json.JSONDecodeError, OSError) as e:
        logger.warning(f"Failed to parse devcontainer.json: {e}")
        return None

    info = DevContainerInfo(
        config_path=config_path,
        workspace_folder=working_dir,
        name=config.get("name"),
        image=config.get("image"),
    )

    # Check for Dockerfile
    dockerfile = config.get("dockerFile") or config.get("build", {}).get("dockerfile")
    if dockerfile:
        dockerfile_path = config_path.parent / dockerfile
        if dockerfile_path.exists():
            info.dockerfile_path = dockerfile_path

    # Check for docker-compose
    compose_file = config.get("dockerComposeFile")
    if compose_file:
        if isinstance(compose_file, list):
            compose_file = compose_file[0]
        compose_path = config_path.parent / compose_file
        if compose_path.exists():
            info.docker_compose_file = compose_path

    return info


class DevContainerRunner:
    """Runs commands inside a Dev Container.

    Supports both `devcontainer` CLI and direct `docker exec` approaches.
    """

    def __init__(
        self,
        info: DevContainerInfo,
        timeout_seconds: int = 300,
        use_devcontainer_cli: bool = True,
    ):
        """Initialize the runner.

        Args:
            info: Dev Container configuration info.
            timeout_seconds: Command timeout.
            use_devcontainer_cli: If True, prefer `devcontainer` CLI. Falls back to docker.
        """
        self.info = info
        self.timeout_seconds = timeout_seconds
        self.use_devcontainer_cli = use_devcontainer_cli
        self._container_id: Optional[str] = None

    @property
    def devcontainer_cli_available(self) -> bool:
        """Check if the devcontainer CLI is available."""
        return shutil.which("devcontainer") is not None

    @property
    def docker_available(self) -> bool:
        """Check if docker is available."""
        return shutil.which("docker") is not None

    async def ensure_running(self) -> bool:
        """Ensure the Dev Container is running.

        Returns:
            True if container is ready, False otherwise.
        """
        if self._container_id:
            return True

        if self.use_devcontainer_cli and self.devcontainer_cli_available:
            return await self._ensure_running_via_cli()
        elif self.docker_available:
            return await self._ensure_running_via_docker()
        else:
            logger.error("Neither devcontainer CLI nor docker is available")
            return False

    async def _ensure_running_via_cli(self) -> bool:
        """Start container using devcontainer CLI."""
        try:
            # Check if already running
            result = await SubprocessManager.run(
                [
                    "devcontainer",
                    "up",
                    "--workspace-folder",
                    str(self.info.workspace_folder),
                ],
                timeout=300,  # Container startup can take time
            )

            if result.returncode == 0:
                # Extract container ID from output
                stdout = result.stdout.decode("utf-8", errors="replace")
                # devcontainer up outputs JSON with containerId
                try:
                    for line in stdout.splitlines():
                        if line.strip().startswith("{"):
                            data = json.loads(line)
                            self._container_id = data.get("containerId")
                            break
                except json.JSONDecodeError:
                    pass

                logger.info(f"Dev Container started: {self._container_id or 'unknown'}")
                return True
            else:
                stderr = result.stderr.decode("utf-8", errors="replace")
                logger.error(f"Failed to start Dev Container: {stderr}")
                return False

        except Exception as e:
            logger.error(f"Error starting Dev Container: {e}")
            return False

    async def _ensure_running_via_docker(self) -> bool:
        """Start container using docker directly.

        For image-based devcontainers, we:
        1. Check if container already exists
        2. If not, run a new container with the workspace mounted
        3. Keep it running for subsequent exec commands
        """
        if not self.info.image:
            logger.error("Docker fallback requires an image-based devcontainer")
            return False

        # Generate a container name based on the workspace folder
        workspace_name = self.info.workspace_folder.name
        container_name = f"deliberate-{workspace_name}"

        try:
            # Check if container already exists and is running
            result = await SubprocessManager.run(
                ["docker", "ps", "-q", "-f", f"name={container_name}"],
                timeout=30,
            )
            existing_id = result.stdout.decode().strip()
            if existing_id:
                self._container_id = existing_id
                logger.info(f"Using existing container: {container_name} ({existing_id[:12]})")
                return True

            # Check if container exists but is stopped
            result = await SubprocessManager.run(
                ["docker", "ps", "-aq", "-f", f"name={container_name}"],
                timeout=30,
            )
            stopped_id = result.stdout.decode().strip()
            if stopped_id:
                # Start the stopped container
                result = await SubprocessManager.run(
                    ["docker", "start", stopped_id],
                    timeout=60,
                )
                if result.returncode == 0:
                    self._container_id = stopped_id
                    logger.info(f"Started existing container: {container_name}")
                    return True

            # Run a new container with the workspace mounted
            workspace_path = str(self.info.workspace_folder.absolute())
            result = await SubprocessManager.run(
                [
                    "docker",
                    "run",
                    "-d",
                    "--name",
                    container_name,
                    "-v",
                    f"{workspace_path}:/workspace",
                    "-w",
                    "/workspace",
                    self.info.image,
                    "tail",
                    "-f",
                    "/dev/null",  # Keep container running
                ],
                timeout=120,
            )

            if result.returncode == 0:
                self._container_id = result.stdout.decode().strip()
                logger.info(f"Started new container: {container_name} ({self._container_id[:12]})")
                return True
            else:
                stderr = result.stderr.decode("utf-8", errors="replace")
                logger.error(f"Failed to start container: {stderr}")
                return False

        except Exception as e:
            logger.error(f"Error in docker fallback: {e}")
            return False

    async def exec(self, command: str) -> tuple[int, str, str]:
        """Execute a command inside the Dev Container.

        Args:
            command: Shell command to execute.

        Returns:
            Tuple of (exit_code, stdout, stderr).
        """
        if not await self.ensure_running():
            return (-1, "", "Failed to start Dev Container")

        if self.use_devcontainer_cli and self.devcontainer_cli_available:
            return await self._exec_via_cli(command)
        else:
            return await self._exec_via_docker(command)

    async def _exec_via_cli(self, command: str) -> tuple[int, str, str]:
        """Execute command using devcontainer CLI."""
        try:
            result = await SubprocessManager.run(
                [
                    "devcontainer",
                    "exec",
                    "--workspace-folder",
                    str(self.info.workspace_folder),
                    "bash",
                    "-lc",
                    command,
                ],
                timeout=self.timeout_seconds,
            )

            stdout = result.stdout.decode("utf-8", errors="replace")
            stderr = result.stderr.decode("utf-8", errors="replace")
            return (result.returncode or 0, stdout, stderr)

        except asyncio.TimeoutError:
            return (-1, "", f"Command timed out after {self.timeout_seconds}s")
        except Exception as e:
            return (-1, "", str(e))

    async def _exec_via_docker(self, command: str) -> tuple[int, str, str]:
        """Execute command using docker exec."""
        if not self._container_id:
            return (-1, "", "No container ID available")

        try:
            result = await SubprocessManager.run(
                [
                    "docker",
                    "exec",
                    "-w",
                    "/workspace",  # Our docker fallback mounts to /workspace
                    self._container_id,
                    "bash",
                    "-lc",
                    command,
                ],
                timeout=self.timeout_seconds,
            )

            stdout = result.stdout.decode("utf-8", errors="replace")
            stderr = result.stderr.decode("utf-8", errors="replace")
            return (result.returncode or 0, stdout, stderr)

        except asyncio.TimeoutError:
            return (-1, "", f"Command timed out after {self.timeout_seconds}s")
        except Exception as e:
            return (-1, "", str(e))

    async def stop(self) -> None:
        """Stop the Dev Container if we started it."""
        # Currently we don't stop containers as they may be shared
        # with IDE sessions. Add explicit cleanup if needed.
        pass
