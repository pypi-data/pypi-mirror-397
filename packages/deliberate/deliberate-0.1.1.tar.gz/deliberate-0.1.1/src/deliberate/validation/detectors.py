"""Heuristics to detect test runners in a repository.

Enhanced to handle:
- Monorepos with multiple project types
- Docker-wrapped test runners
- Custom npm scripts (test:unit, test:integration)
- Complex Makefile setups (check, ci targets)
- CI workflow inspection for command hints
"""

import json
import re
from pathlib import Path
from typing import Optional


def detect_test_command(repo_root: Path) -> Optional[str]:
    """Attempt to detect the correct test command for the repo.

    Inspects common project files to determine the appropriate test framework.
    Checks for Docker-based runners first, then language-specific patterns.

    Args:
        repo_root: Path to the repository root.

    Returns:
        Test command string, or None if no test framework detected.
    """
    # 0. Check for Docker-based test runners first
    docker_cmd = _detect_docker_test_command(repo_root)
    if docker_cmd:
        return docker_cmd

    # 1. Python projects
    if _is_python_project(repo_root):
        return _detect_python_test_command(repo_root)

    # 2. Node.js projects
    node_cmd = _detect_node_test_command(repo_root)
    if node_cmd:
        return node_cmd

    # 3. Rust projects
    if (repo_root / "Cargo.toml").exists():
        return _detect_rust_test_command(repo_root)

    # 4. Go projects
    if (repo_root / "go.mod").exists():
        return "go test ./..."

    # 5. Generic Makefile
    makefile_cmd = _detect_makefile_test(repo_root)
    if makefile_cmd:
        return makefile_cmd

    # 6. Check CI workflows as last resort
    ci_cmd = _detect_from_ci_workflow(repo_root)
    if ci_cmd:
        return ci_cmd

    return None


def _is_python_project(repo_root: Path) -> bool:
    """Check if this is a Python project."""
    python_indicators = [
        "pyproject.toml",
        "setup.py",
        "setup.cfg",
        "requirements.txt",
        "pytest.ini",
        "tox.ini",
        ".python-version",
    ]
    return any((repo_root / f).exists() for f in python_indicators)


def _detect_python_test_command(repo_root: Path) -> str:
    """Detect the best test command for a Python project."""
    # Check pyproject.toml for test configuration
    pyproject = repo_root / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text()
            # Check for pytest configuration
            if "[tool.pytest" in content or "pytest" in content.lower():
                return _get_python_runner(repo_root, "pytest")
            # Check for unittest
            if "unittest" in content:
                return _get_python_runner(repo_root, "python -m unittest discover")
        except Exception:
            import logging

            logging.warning("Failed to read pyproject.toml for test detection", exc_info=True)

    # Check for pytest.ini
    if (repo_root / "pytest.ini").exists():
        return _get_python_runner(repo_root, "pytest")

    # Check for conftest.py (pytest indicator)
    if (repo_root / "conftest.py").exists() or list(repo_root.glob("**/conftest.py")):
        return _get_python_runner(repo_root, "pytest")

    # Check for tests directory
    tests_dir = repo_root / "tests"
    if tests_dir.exists() and tests_dir.is_dir():
        # Look for test files
        test_files = list(tests_dir.glob("test_*.py")) + list(tests_dir.glob("*_test.py"))
        if test_files:
            return _get_python_runner(repo_root, "pytest")

    # Default to pytest for Python projects
    return _get_python_runner(repo_root, "pytest")


def _get_python_runner(repo_root: Path, base_cmd: str) -> str:
    """Determine if we should use uv or direct command."""
    # Check for uv.lock or pyproject.toml with uv markers
    if (repo_root / "uv.lock").exists():
        return f"uv run {base_cmd}"

    # Check for poetry
    pyproject = repo_root / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text()
            if "[tool.poetry]" in content:
                return f"poetry run {base_cmd}"
        except Exception:
            import logging

            logging.warning("Failed to read pyproject.toml for poetry detection", exc_info=True)

    return base_cmd


def _detect_node_test_command(repo_root: Path) -> Optional[str]:
    """Detect test command for Node.js projects.

    Handles custom test scripts like test:unit, test:integration.
    Prefers more specific test scripts over generic 'test'.
    """
    package_json = repo_root / "package.json"
    if not package_json.exists():
        return None

    try:
        data = json.loads(package_json.read_text())
        scripts = data.get("scripts", {})

        # Determine package manager
        if (repo_root / "yarn.lock").exists():
            runner = "yarn"
        elif (repo_root / "pnpm-lock.yaml").exists():
            runner = "pnpm"
        else:
            runner = "npm run"

        # Check for specific test scripts first (more specific = better)
        # Order matters: prefer unit tests, then integration, then generic
        test_script_priority = [
            "test:unit",
            "test:all",
            "test",
            "test:integration",
            "test:e2e",
        ]

        for script_name in test_script_priority:
            if script_name in scripts:
                # Check if script is not just "echo 'no tests'" or similar placeholder
                script_content = scripts[script_name]
                if _is_real_test_script(script_content):
                    # npm has shortcuts for common scripts (test, start, etc.)
                    if runner == "npm run":
                        if script_name == "test":
                            return "npm test"
                        return f"npm run {script_name}"
                    return f"{runner} {script_name}"

        return None
    except Exception:
        import logging

        logging.warning("Failed to read package.json for test detection", exc_info=True)
        return None


def _is_real_test_script(script_content: str) -> bool:
    """Check if a script is a real test command, not a placeholder."""
    if not script_content:
        return False

    # Common placeholder patterns
    placeholder_patterns = [
        r"^echo\s+['\"]?(no test|error|todo)",
        r"^exit\s+[01]",
        r"^true$",
        r"^:$",  # Shell no-op
    ]

    script_lower = script_content.lower().strip()
    for pattern in placeholder_patterns:
        if re.match(pattern, script_lower, re.IGNORECASE):
            return False

    return True


def _detect_makefile_test(repo_root: Path) -> Optional[str]:
    """Check Makefile for test-related targets.

    Looks for common test targets: test, check, ci, tests, unittest.
    Returns the most specific one found.
    """
    makefile = repo_root / "Makefile"
    if not makefile.exists():
        return None

    try:
        content = makefile.read_text()

        # Check for test targets in priority order
        # More specific targets first
        test_targets = [
            "test",
            "tests",
            "check",
            "unittest",
            "unit-test",
            "unit_test",
            "ci",
        ]

        for target in test_targets:
            if re.search(rf"^{target}\s*:", content, re.MULTILINE):
                return f"make {target}"

        return None
    except Exception:
        import logging

        logging.warning("Failed to read Makefile for test detection", exc_info=True)
        return None


def detect_project_type(repo_root: Path) -> Optional[str]:
    """Detect the project type for informational purposes.

    Returns:
        String like 'python', 'node', 'rust', 'go', or None.
    """
    if _is_python_project(repo_root):
        return "python"
    if (repo_root / "package.json").exists():
        return "node"
    if (repo_root / "Cargo.toml").exists():
        return "rust"
    if (repo_root / "go.mod").exists():
        return "go"
    return None


def _detect_docker_test_command(repo_root: Path) -> Optional[str]:
    """Detect Docker-based test runners.

    Looks for docker-compose.yml with test services or Dockerfile patterns
    that suggest containerized testing.
    """
    # Check for docker-compose files
    compose_files = [
        "docker-compose.yml",
        "docker-compose.yaml",
        "docker-compose.test.yml",
        "docker-compose.test.yaml",
    ]

    for compose_file in compose_files:
        compose_path = repo_root / compose_file
        if compose_path.exists():
            try:
                content = compose_path.read_text()

                # Look for test service definitions
                # Common patterns: service named 'test', 'tests', or command containing pytest/jest
                if re.search(r"^\s+test[s]?:\s*$", content, re.MULTILINE):
                    return f"docker compose -f {compose_file} run test"

                # Check for pytest/jest in command
                if "pytest" in content or "jest" in content or "npm test" in content:
                    # Try to find the service name
                    service_match = re.search(
                        r"^\s+(\w+):\s*\n(?:.*\n)*?\s+command:.*(?:pytest|jest|npm test)",
                        content,
                        re.MULTILINE,
                    )
                    if service_match:
                        service = service_match.group(1)
                        return f"docker compose -f {compose_file} run {service}"

            except Exception:
                pass

    return None


def _detect_rust_test_command(repo_root: Path) -> str:
    """Detect test command for Rust projects.

    Handles workspaces and nextest.
    """
    cargo_toml = repo_root / "Cargo.toml"
    if not cargo_toml.exists():
        return "cargo test"

    try:
        content = cargo_toml.read_text()

        # Check if this is a workspace
        is_workspace = "[workspace]" in content

        # Check for nextest config
        nextest_config = repo_root / ".config" / "nextest.toml"
        has_nextest = nextest_config.exists()

        if has_nextest:
            if is_workspace:
                return "cargo nextest run --workspace"
            return "cargo nextest run"

        if is_workspace:
            return "cargo test --workspace"

        return "cargo test"
    except Exception:
        return "cargo test"


def _detect_from_ci_workflow(repo_root: Path) -> Optional[str]:
    """Extract test command from CI workflow files.

    Parses GitHub Actions workflows to find test commands.
    This is a last resort when other heuristics fail.
    """
    # GitHub Actions
    gh_workflows = repo_root / ".github" / "workflows"
    if gh_workflows.exists():
        for workflow_file in gh_workflows.glob("*.yml"):
            try:
                content = workflow_file.read_text()

                # Look for common test step patterns
                # e.g., "run: pytest" or "run: npm test"
                test_patterns = [
                    r"run:\s*(pytest[^\n]*)",
                    r"run:\s*(npm\s+(?:run\s+)?test[^\n]*)",
                    r"run:\s*(yarn\s+test[^\n]*)",
                    r"run:\s*(cargo\s+test[^\n]*)",
                    r"run:\s*(go\s+test[^\n]*)",
                    r"run:\s*(make\s+test[^\n]*)",
                    r"run:\s*(uv\s+run\s+pytest[^\n]*)",
                ]

                for pattern in test_patterns:
                    match = re.search(pattern, content)
                    if match:
                        cmd = match.group(1).strip()
                        # Clean up the command (remove shell operators, etc)
                        cmd = cmd.split("&&")[0].strip()
                        cmd = cmd.split("||")[0].strip()
                        if cmd and not cmd.startswith("$"):
                            return cmd

            except Exception:
                pass

    return None
