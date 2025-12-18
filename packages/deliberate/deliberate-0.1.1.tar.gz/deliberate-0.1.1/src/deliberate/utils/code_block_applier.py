"""Utility to apply code blocks from text to files."""

import re
from pathlib import Path


def apply_code_blocks_from_text(text: str, working_dir: Path) -> list[str]:
    """Parse text for code blocks with filenames and apply them.

    Supports formats:
    ```python:src/main.py
    code
    ```

    or

    ```python
    # filename: src/main.py
    code
    ```

    Args:
        text: The LLM response text.
        working_dir: The directory to write files to.

    Returns:
        List of files modified.
    """
    modified_files = []

    # Regex for ```lang:path/to/file
    # Capture group 2 is path
    regex_header = re.compile(r"```\w*:([^\n]+)\n(.*?)```", re.DOTALL)

    matches = regex_header.findall(text)
    for path_str, content in matches:
        path_str = path_str.strip()
        if not path_str:
            continue

        file_path = working_dir / path_str
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            modified_files.append(str(file_path))
        except Exception:
            pass

    # Regex for comment filename inside block
    # ```python
    # # filename: path
    regex_comment = re.compile(r"```\w+\n(?:\s*#\s*filename:\s*([^\n]+)\n)(.*?)```", re.DOTALL)

    matches = regex_comment.findall(text)
    for path_str, content in matches:
        path_str = path_str.strip()
        if not path_str:
            continue

        file_path = working_dir / path_str
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            modified_files.append(str(file_path))
        except Exception:
            pass

    return modified_files
