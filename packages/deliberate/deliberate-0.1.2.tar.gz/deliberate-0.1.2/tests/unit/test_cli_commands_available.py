"""Ensure advertised CLI commands are registered on the Typer app."""

from deliberate.cli import app


def _command_name(command) -> str:
    """Return the command name as it appears on the CLI."""

    if command.name:
        return command.name
    # Typer defaults to the callback name with dashes instead of underscores
    return command.callback.__name__.replace("_", "-")


def test_readme_commands_are_registered():
    """Commands documented in the README should exist on the CLI app.

    This protects against regressions where the Typer application name or
    registration could prevent users from invoking documented commands.
    """

    expected_commands = {
        "run",
        "github-handle",
        "maintain",
        "init",
        "validate",
        "stats",
        "clear-stats",
        "history",
        "plan",
        "work",
        "status",
        "merge",
        "abort",
    }

    registered = {_command_name(command) for command in app.registered_commands}

    missing = expected_commands - registered
    assert not missing, f"Missing CLI commands: {sorted(missing)}"
