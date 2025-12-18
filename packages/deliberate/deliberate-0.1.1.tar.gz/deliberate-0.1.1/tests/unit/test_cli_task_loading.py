"""Tests for CLI task loading from files."""

import pytest
import typer

from deliberate.cli import _load_task_content


class TestTaskLoading:
    """Tests for loading tasks from files."""

    def test_load_task_inline(self):
        """Should return inline task as-is."""
        task = "This is a simple task"
        result = _load_task_content(task)
        assert result == task

    def test_load_task_from_file(self, tmp_path):
        """Should load task content from file when prefixed with @."""
        task_file = tmp_path / "task.txt"
        task_file.write_text("This is a task from a file\nWith multiple lines")

        result = _load_task_content(f"@{task_file}")
        assert result == "This is a task from a file\nWith multiple lines"

    def test_load_task_from_file_strips_whitespace(self, tmp_path):
        """Should strip leading/trailing whitespace from file content."""
        task_file = tmp_path / "task.txt"
        task_file.write_text("  \n  Task with whitespace  \n\n  ")

        result = _load_task_content(f"@{task_file}")
        assert result == "Task with whitespace"

    def test_load_task_from_nonexistent_file_raises_exit(self, tmp_path):
        """Should raise typer.Exit when file doesn't exist."""
        nonexistent = tmp_path / "does_not_exist.txt"

        with pytest.raises(typer.Exit) as exc_info:
            _load_task_content(f"@{nonexistent}")
        assert exc_info.value.exit_code == 1

    def test_load_task_with_at_symbol_not_at_start(self):
        """Should not treat @ as file prefix if not at start."""
        task = "Send email @user about the task"
        result = _load_task_content(task)
        assert result == task

    def test_load_task_from_markdown_file(self, tmp_path):
        """Should load task from markdown file."""
        task_file = tmp_path / "task.md"
        task_file.write_text("""# Task Title

Description of the task with **markdown** formatting.

## Details
- Item 1
- Item 2
""")

        result = _load_task_content(f"@{task_file}")
        assert "# Task Title" in result
        assert "**markdown**" in result
        assert "- Item 1" in result
