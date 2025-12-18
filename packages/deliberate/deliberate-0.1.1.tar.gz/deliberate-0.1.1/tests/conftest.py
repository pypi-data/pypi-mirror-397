"""Shared test fixtures for deliberate."""

import subprocess
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_git_repo():
    """Create a temporary git repository for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir) / "repo"
        repo.mkdir()

        # Initialize git repo with explicit main branch
        subprocess.run(
            ["git", "init", "-b", "main"],
            cwd=repo,
            check=True,
            capture_output=True,
        )

        # Configure git user
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=repo,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=repo,
            check=True,
            capture_output=True,
        )
        # Disable commit signing for test repo (may be enabled globally)
        subprocess.run(
            ["git", "config", "commit.gpgsign", "false"],
            cwd=repo,
            check=True,
            capture_output=True,
        )

        # Create initial commit
        (repo / "README.md").write_text("# Test Repository\n")
        subprocess.run(
            ["git", "add", "."],
            cwd=repo,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=repo,
            check=True,
            capture_output=True,
        )

        yield repo


@pytest.fixture
def minimal_config():
    """Create a minimal config for testing."""
    from deliberate.config import (
        AgentConfig,
        DeliberateConfig,
        ExecutionConfig,
        LimitsConfig,
        PlanningConfig,
        ReviewConfig,
        WorkflowConfig,
    )

    return DeliberateConfig(
        agents={
            "fake": AgentConfig(
                type="fake",
                behavior="planner",
                capabilities=["planner", "executor", "reviewer"],
            ),
        },
        workflow=WorkflowConfig(
            planning=PlanningConfig(
                enabled=True,
                agents=["fake"],
            ),
            execution=ExecutionConfig(
                enabled=True,
                agents=["fake"],
            ),
            review=ReviewConfig(
                enabled=False,
                agents=[],
            ),
        ),
        limits=LimitsConfig(),
    )
