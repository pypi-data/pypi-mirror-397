"""Tests for the MaintenanceWorkflow (flaky test fixer).

Uses unittest.mock to mock subprocess calls and GitHub API calls.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from deliberate.maintenance import MaintenanceWorkflow


class TestDetectFlakes:
    """Tests for flaky test detection."""

    @patch("deliberate.maintenance.subprocess.run")
    @patch("deliberate.maintenance.FailureInterpreter.interpret")
    def test_no_flakes_detected(self, mock_interpret: MagicMock, mock_run: MagicMock) -> None:
        """Returns empty list when all test runs pass."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        mock_interpret.return_value.failed_tests = []

        workflow = MaintenanceWorkflow(
            test_command="pytest",
            github_token="token",
            repo_owner="owner",
            repo_name="repo",
        )
        flakes = workflow.detect_flakes(runs=3)

        assert flakes == []
        assert mock_run.call_count == 3
        assert mock_interpret.call_count == 3

    @patch("deliberate.maintenance.subprocess.run")
    @patch("deliberate.maintenance.FailureInterpreter.interpret")
    def test_detects_flaky_tests(self, mock_interpret: MagicMock, mock_run: MagicMock) -> None:
        """Detects and returns list of flaky test names."""
        mock_run.return_value = MagicMock(returncode=1, stdout="FAILED tests/test_foo.py::test_flaky", stderr="")

        # Simulate different runs: first empty, second has failures, third empty
        resp_empty = MagicMock(failed_tests=[])
        resp_flakes = MagicMock(failed_tests=["tests.test_foo::test_flaky", "tests.test_bar::test_also_flaky"])
        mock_interpret.side_effect = [resp_empty, resp_flakes, resp_empty]

        workflow = MaintenanceWorkflow(
            test_command="pytest",
            github_token="token",
            repo_owner="owner",
            repo_name="repo",
        )
        flakes = workflow.detect_flakes(runs=3)

        assert "tests.test_foo::test_flaky" in flakes
        assert "tests.test_bar::test_also_flaky" in flakes
        assert len(flakes) == 2
        assert mock_run.call_count == 3
        assert mock_interpret.call_count == 3

    @patch("deliberate.maintenance.subprocess.run")
    @patch("deliberate.maintenance.FailureInterpreter.interpret")
    def test_handles_failed_run_without_test_names(self, mock_interpret: MagicMock, mock_run: MagicMock) -> None:
        """Handles failed runs where no failures are extracted."""
        mock_run.return_value = MagicMock(
            returncode=1,  # Simulate a failed subprocess run
            stdout="Some error occurred",
            stderr="",
        )
        mock_interpret.return_value.failed_tests = []

        workflow = MaintenanceWorkflow(
            test_command="pytest",
            github_token="token",
            repo_owner="owner",
            repo_name="repo",
        )
        flakes = workflow.detect_flakes(runs=2)

        # Should return empty, as no test names are identified
        assert flakes == []
        assert mock_run.call_count == 2
        assert mock_interpret.call_count == 2


class TestVerifyFix:
    """Tests for fix verification."""

    @patch("deliberate.maintenance.subprocess.run")
    def test_verify_success(self, mock_run: MagicMock) -> None:
        """Returns True when all verification runs pass."""
        mock_run.return_value = MagicMock(returncode=0)

        workflow = MaintenanceWorkflow(
            test_command="pytest",
            github_token="token",
            repo_owner="owner",
            repo_name="repo",
        )
        result = workflow.verify_fix("pytest -k test_foo", runs=5)

        assert result is True
        assert mock_run.call_count == 5

    @patch("deliberate.maintenance.subprocess.run")
    def test_verify_failure(self, mock_run: MagicMock) -> None:
        """Returns False when any verification run fails."""
        # Third run fails
        mock_run.side_effect = [
            MagicMock(returncode=0),
            MagicMock(returncode=0),
            MagicMock(returncode=1),  # Failure
        ]

        workflow = MaintenanceWorkflow(
            test_command="pytest",
            github_token="token",
            repo_owner="owner",
            repo_name="repo",
        )
        result = workflow.verify_fix("pytest -k test_foo", runs=10)

        assert result is False
        # Should stop after first failure
        assert mock_run.call_count == 3


class TestRunGit:
    """Tests for git command execution."""

    @patch("deliberate.maintenance.subprocess.run")
    def test_run_git_command(self, mock_run: MagicMock) -> None:
        """Runs git commands correctly."""
        mock_run.return_value = MagicMock(returncode=0)

        workflow = MaintenanceWorkflow(
            test_command="pytest",
            github_token="token",
            repo_owner="owner",
            repo_name="repo",
        )
        workflow.run_git(["checkout", "main"])

        mock_run.assert_called_once_with(
            ["git", "checkout", "main"],
            check=True,
        )


class TestMaintenanceRun:
    """Tests for the full maintenance workflow run."""

    @pytest.fixture
    def mock_workflow_deps(self):
        """Mock all external dependencies for workflow tests."""
        with (
            patch("deliberate.maintenance.subprocess.run") as mock_run,
            patch("deliberate.maintenance.GitHubClient") as mock_gh_class,
            patch("deliberate.maintenance.DeliberateConfig") as mock_config_class,
            patch("deliberate.maintenance.Orchestrator") as mock_orch_class,
            patch("deliberate.maintenance.datetime") as mock_datetime,
        ):
            # Setup datetime mock
            mock_datetime.now.return_value.strftime.return_value = "20240101-120000"

            # Setup GitHub client mock
            mock_gh = MagicMock()
            mock_gh.create_pull_request.return_value = 42
            mock_gh_class.return_value = mock_gh

            # Setup config mock
            mock_config = MagicMock()
            mock_config.apply_profile.return_value = mock_config
            mock_config_class.load_or_default.return_value = mock_config

            # Setup orchestrator mock
            mock_orch = MagicMock()
            mock_result = MagicMock()
            mock_result.success = True
            mock_result.summary = "Fixed the flaky tests"
            mock_orch.run = AsyncMock(return_value=mock_result)
            mock_orch_class.return_value = mock_orch

            yield {
                "run": mock_run,
                "gh": mock_gh,
                "config": mock_config,
                "orchestrator": mock_orch,
            }

    @pytest.mark.asyncio
    async def test_run_no_flakes(self, mock_workflow_deps) -> None:
        """Exits early when no flakes are detected."""
        mock_run = mock_workflow_deps["run"]
        # All test runs pass
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        workflow = MaintenanceWorkflow(
            test_command="pytest",
            github_token="token",
            repo_owner="owner",
            repo_name="repo",
        )
        await workflow.run(detect_runs=3, verify_runs=10)

        # Should only have detection runs, no git operations
        assert mock_run.call_count == 3
        # No PR should be created
        mock_workflow_deps["gh"].create_pull_request.assert_not_called()

    @pytest.mark.asyncio
    async def test_run_full_workflow(self, mock_workflow_deps) -> None:
        """Runs full workflow: detect -> fix -> verify -> PR."""
        mock_run = mock_workflow_deps["run"]

        # Setup subprocess mock for different commands
        def subprocess_side_effect(*args, **kwargs):
            cmd = args[0] if args else kwargs.get("args", [])

            # Detection phase - first run fails with flaky test
            if isinstance(cmd, str) or (isinstance(cmd, list) and cmd[0] != "git"):
                # Test command runs
                if not hasattr(subprocess_side_effect, "test_call_count"):
                    subprocess_side_effect.test_call_count = 0
                subprocess_side_effect.test_call_count += 1

                # First detection run fails
                if subprocess_side_effect.test_call_count == 1:
                    return MagicMock(
                        returncode=1,
                        stdout="FAILED tests/test_foo.py::test_flaky",
                        stderr="",
                    )
                # Rest pass
                return MagicMock(returncode=0, stdout="", stderr="")

            # Git commands
            if isinstance(cmd, list) and cmd[0] == "git":
                if cmd[1] == "diff":
                    return MagicMock(returncode=1)  # Has changes
                return MagicMock(returncode=0)

            return MagicMock(returncode=0)

        mock_run.side_effect = subprocess_side_effect

        workflow = MaintenanceWorkflow(
            test_command="pytest",
            github_token="token",
            repo_owner="owner",
            repo_name="repo",
        )
        await workflow.run(detect_runs=2, verify_runs=3)

        # Verify PR was created
        mock_workflow_deps["gh"].create_pull_request.assert_called_once()
        call_kwargs = mock_workflow_deps["gh"].create_pull_request.call_args
        assert "tests/test_foo.py::test_flaky" in call_kwargs.kwargs["title"]
        assert "fix/flaky-tests-" in call_kwargs.kwargs["head"]

    @pytest.mark.asyncio
    async def test_run_orchestrator_failure(self, mock_workflow_deps) -> None:
        """Stops when orchestrator fails to fix the issue."""
        mock_run = mock_workflow_deps["run"]

        # Detection finds a flake
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="FAILED tests/test_foo.py::test_flaky",
            stderr="",
        )

        # Orchestrator fails
        mock_workflow_deps["orchestrator"].run.return_value = MagicMock(success=False)

        workflow = MaintenanceWorkflow(
            test_command="pytest",
            github_token="token",
            repo_owner="owner",
            repo_name="repo",
        )
        await workflow.run(detect_runs=1, verify_runs=10)

        # No PR should be created
        mock_workflow_deps["gh"].create_pull_request.assert_not_called()

    @pytest.mark.asyncio
    async def test_run_verification_failure(self, mock_workflow_deps) -> None:
        """Aborts PR when verification fails."""
        mock_run = mock_workflow_deps["run"]

        call_count = 0

        def subprocess_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            cmd = args[0] if args else kwargs.get("args", [])

            # First call is detection - find a flake
            if call_count == 1:
                return MagicMock(
                    returncode=1,
                    stdout="FAILED tests/test_foo.py::test_flaky",
                    stderr="",
                )

            # Git commands succeed
            if isinstance(cmd, list) and cmd[0] == "git":
                return MagicMock(returncode=0)

            # Verification runs fail
            return MagicMock(returncode=1)

        mock_run.side_effect = subprocess_side_effect

        workflow = MaintenanceWorkflow(
            test_command="pytest",
            github_token="token",
            repo_owner="owner",
            repo_name="repo",
        )
        await workflow.run(detect_runs=1, verify_runs=100)

        # No PR should be created
        mock_workflow_deps["gh"].create_pull_request.assert_not_called()


class TestGitBranchNaming:
    """Tests for git branch naming."""

    @patch("deliberate.maintenance.subprocess.run")
    @patch("deliberate.maintenance.datetime")
    def test_branch_name_format(self, mock_datetime: MagicMock, mock_run: MagicMock) -> None:
        """Branch name follows expected format."""
        mock_datetime.now.return_value.strftime.return_value = "20240315-143022"
        mock_run.return_value = MagicMock(returncode=0)

        workflow = MaintenanceWorkflow(
            test_command="pytest",
            github_token="token",
            repo_owner="owner",
            repo_name="repo",
        )

        # Access the branch creation via run_git
        workflow.run_git(["checkout", "-b", "fix/flaky-tests-20240315-143022"])

        # Verify the branch name format
        mock_run.assert_called_with(
            ["git", "checkout", "-b", "fix/flaky-tests-20240315-143022"],
            check=True,
        )
