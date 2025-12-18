"""Dynamic review criteria generation based on task and repo context."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Iterable

from deliberate.adapters.base import ModelAdapter
from deliberate.prompts.review import CRITERIA_CONTEXT_PROMPT
from deliberate.utils.structured_output import extract_tool_call


def summarize_repository(repo_root: Path, max_files: int = 200) -> str:
    """Build a lightweight textual summary of the repository."""
    repo_root = repo_root.resolve()
    top_levels = [p.name for p in repo_root.iterdir() if p.is_dir() and not p.name.startswith(".")]

    # Count extensions to infer dominant languages
    exts = Counter()
    files_scanned = 0
    for path in repo_root.rglob("*"):
        if not path.is_file():
            continue
        if path.name.startswith("."):
            continue
        ext = path.suffix.lower()
        if ext:
            exts[ext] += 1
        files_scanned += 1
        if files_scanned >= max_files:
            break

    dominant = ", ".join(f"{ext}({count})" for ext, count in exts.most_common(5)) or "unknown"

    readme_snippet = ""
    for candidate in ("README.md", "README", "readme.md", "readme"):
        readme_path = repo_root / candidate
        if readme_path.exists():
            readme_snippet = readme_path.read_text(errors="ignore")[:400]
            break

    return (
        f"Top-level: {', '.join(top_levels[:8]) or 'none'}\n"
        f"Dominant file types: {dominant}\n"
        f"README preview: {readme_snippet or 'none'}"
    )


async def generate_review_criteria(
    task: str,
    repo_root: Path,
    adapter: ModelAdapter,
    max_criteria: int = 5,
) -> tuple[list[str], dict[str, str], int] | None:
    """Use the designated adapter to generate task-specific review criteria.

    Returns:
        Tuple of (criteria_names, descriptions, token_usage) or None if generation fails.
    """
    repo_summary = summarize_repository(repo_root)
    prompt = CRITERIA_CONTEXT_PROMPT.format(
        task=task,
        repo_summary=repo_summary,
        max_criteria=max_criteria,
    )

    response = await adapter.call(prompt)
    selection = extract_tool_call(response.raw_response, response.content, "set_review_criteria")
    if not selection:
        return None

    raw_criteria: Iterable = selection.get("criteria") or []
    names: list[str] = []
    descriptions: dict[str, str] = {}
    for item in raw_criteria:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or "").strip()
        desc = str(item.get("description") or "").strip()
        if not name:
            continue
        names.append(name)
        if desc:
            descriptions[name] = desc

    if not names:
        return None

    return names, descriptions, response.token_usage
