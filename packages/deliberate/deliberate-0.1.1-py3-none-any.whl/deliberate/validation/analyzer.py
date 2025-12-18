"""LLM-based environment analyzer for detecting test/lint commands.

Instead of hard-coded file checks, this module uses a small, fast LLM to
analyze project structure and configuration files to determine the correct
commands to run tests and linting.

This handles edge cases that heuristics miss:
- Monorepos with multiple project types
- Custom npm scripts (npm run test:unit vs npm test)
- Python projects with docker-based test runners
- Complex Makefile setups

IMPORTANT: This module requires an adapter that supports structured output
via JSON schema (e.g., Claude CLI with --json-schema). It does NOT parse
JSON from stdout - that approach is fragile and not allowed.
"""

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Protocol, runtime_checkable

from deliberate.adapters.base import AdapterResponse, ModelAdapter


@dataclass
class EnvironmentInfo:
    """Analyzed environment information."""

    test_command: Optional[str] = None
    lint_command: Optional[str] = None
    build_command: Optional[str] = None
    project_types: list[str] = field(default_factory=list)
    package_manager: Optional[str] = None  # npm, yarn, pnpm, pip, uv, poetry, cargo
    analysis_notes: Optional[str] = None  # LLM's reasoning/notes
    confidence: float = 1.0  # 0.0-1.0, how confident is the analyzer

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "test_command": self.test_command,
            "lint_command": self.lint_command,
            "build_command": self.build_command,
            "project_types": self.project_types,
            "package_manager": self.package_manager,
            "analysis_notes": self.analysis_notes,
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "EnvironmentInfo":
        """Load from dictionary."""
        return cls(
            test_command=data.get("test_command"),
            lint_command=data.get("lint_command"),
            build_command=data.get("build_command"),
            project_types=data.get("project_types", []),
            package_manager=data.get("package_manager"),
            analysis_notes=data.get("analysis_notes"),
            confidence=data.get("confidence", 1.0),
        )


# In-memory cache for current session
_analysis_cache: dict[str, EnvironmentInfo] = {}


ANALYZER_SYSTEM_PROMPT = """
You are an environment analyzer for software projects. Given a project's file
structure and configuration files, determine the correct commands to run tests
and linting.

IMPORTANT: Be specific. Don't assume standard commands work. For example:
- Many npm projects use `npm run test:unit` or `npm run test:integration` instead of `npm test`
- Python projects may require `docker compose run app pytest` or `tox -e py39`
- Python projects using uv should use `uv run pytest` not just `pytest`
- Rust workspaces may need `cargo test --workspace` or `cargo nextest run`

Look at:
1. package.json "scripts" section for npm/yarn/pnpm projects
2. pyproject.toml for Python projects (check for uv.lock, poetry.lock)
3. Makefile for make-based projects
4. CI workflow files (.github/workflows/) to see what commands CI uses
"""


@runtime_checkable
class StructuredOutputAdapter(Protocol):
    """Protocol for adapters that support structured output."""

    async def call(
        self,
        prompt: str,
        *,
        system: str | None = None,
        max_tokens: int | None = None,
        temperature: float = 0.7,
        working_dir: str | None = None,
        schema_name: str | None = None,
    ) -> AdapterResponse:
        """Call with optional schema_name for structured output."""
        ...


def _get_file_tree(repo_root: Path, max_depth: int = 3, max_files: int = 200) -> str:
    """Get a simplified file tree for LLM analysis.

    Args:
        repo_root: Path to repository root.
        max_depth: Maximum directory depth to traverse.
        max_files: Maximum number of files to include.

    Returns:
        String representation of file tree.
    """
    lines: list[str] = []
    file_count = 0

    def walk(path: Path, depth: int, prefix: str = "") -> None:
        nonlocal file_count

        if depth > max_depth or file_count >= max_files:
            return

        # Skip common directories that aren't useful for analysis
        skip_dirs = {
            ".git",
            "node_modules",
            "__pycache__",
            ".venv",
            "venv",
            "target",
            "dist",
            "build",
            ".next",
            ".nuxt",
            "coverage",
            ".pytest_cache",
            ".mypy_cache",
            ".tox",
            "eggs",
            "*.egg-info",
        }

        try:
            items = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name))
        except PermissionError:
            return

        for item in items:
            if file_count >= max_files:
                break

            name = item.name
            if name in skip_dirs or name.startswith("."):
                continue

            if item.is_dir():
                lines.append(f"{prefix}{name}/")
                walk(item, depth + 1, prefix + "  ")
            else:
                lines.append(f"{prefix}{name}")
                file_count += 1

    walk(repo_root, 0)
    return "\n".join(lines)


def _read_config_files(repo_root: Path) -> dict[str, str]:
    """Read relevant configuration files for analysis.

    Args:
        repo_root: Path to repository root.

    Returns:
        Dict mapping filename to contents.
    """
    config_files = [
        "package.json",
        "pyproject.toml",
        "setup.py",
        "setup.cfg",
        "tox.ini",
        "pytest.ini",
        "Makefile",
        "Cargo.toml",
        "go.mod",
        "docker-compose.yml",
        "docker-compose.yaml",
        ".github/workflows/ci.yml",
        ".github/workflows/ci.yaml",
        ".github/workflows/test.yml",
        ".github/workflows/test.yaml",
    ]

    contents: dict[str, str] = {}
    for filename in config_files:
        filepath = repo_root / filename
        if filepath.exists() and filepath.is_file():
            try:
                text = filepath.read_text(errors="replace")
                # Truncate very large files
                if len(text) > 5000:
                    text = text[:5000] + "\n... (truncated)"
                contents[filename] = text
            except Exception:
                pass

    return contents


def _build_analysis_prompt(repo_root: Path, include_system_prompt: bool = True) -> str:
    """Build the prompt for environment analysis.

    Args:
        repo_root: Path to repository root.
        include_system_prompt: If True, include the system prompt inline.
            This is needed for CLI adapters that don't support --system flag
            in certain modes (e.g., Claude CLI with -p).

    Returns:
        Prompt string for the LLM.
    """
    file_tree = _get_file_tree(repo_root)
    configs = _read_config_files(repo_root)

    parts = []

    # Include system prompt inline for CLI compatibility
    if include_system_prompt:
        parts.extend(
            [
                "# Instructions",
                ANALYZER_SYSTEM_PROMPT,
                "",
            ]
        )

    parts.extend(
        [
            "# Project Structure",
            "```",
            file_tree,
            "```",
            "",
            "# Configuration Files",
        ]
    )

    for filename, content in configs.items():
        parts.extend(
            [
                f"## {filename}",
                "```",
                content,
                "```",
                "",
            ]
        )

    parts.append("Analyze this project and provide the test/lint commands.")

    return "\n".join(parts)


def _compute_cache_key(repo_root: Path) -> str:
    """Compute a cache key based on file tree and config file hashes.

    Args:
        repo_root: Path to repository root.

    Returns:
        Hash string for caching.
    """
    hasher = hashlib.sha256()

    # Hash the file tree
    file_tree = _get_file_tree(repo_root, max_depth=2, max_files=100)
    hasher.update(file_tree.encode())

    # Hash config file contents
    configs = _read_config_files(repo_root)
    for filename in sorted(configs.keys()):
        hasher.update(filename.encode())
        hasher.update(configs[filename].encode())

    return hasher.hexdigest()[:16]


def _parse_structured_response(raw_response: dict | None) -> EnvironmentInfo:
    """Parse structured response from adapter.

    The adapter should have used --json-schema to get structured output.
    The structured_output field contains the validated response.

    Args:
        raw_response: The raw_response dict from AdapterResponse.

    Returns:
        EnvironmentInfo parsed from the response.
    """
    if not raw_response:
        return EnvironmentInfo(confidence=0.0)

    # Claude CLI puts structured output in "structured_output" field
    data = raw_response.get("structured_output", raw_response)

    if not isinstance(data, dict):
        return EnvironmentInfo(confidence=0.0)

    return EnvironmentInfo(
        test_command=data.get("test_command"),
        lint_command=data.get("lint_command"),
        build_command=data.get("build_command"),
        project_types=data.get("project_types", []),
        package_manager=data.get("package_manager"),
        analysis_notes=data.get("notes"),
        confidence=float(data.get("confidence", 0.8)),
    )


def _get_persistent_cache_path(repo_root: Path) -> Path:
    """Get the path to the persistent cache file."""
    cache_dir = repo_root / ".deliberate"
    cache_dir.mkdir(exist_ok=True)
    return cache_dir / "cache.json"


def _load_persistent_cache(repo_root: Path) -> None:
    """Load the persistent cache from disk."""
    cache_path = _get_persistent_cache_path(repo_root)
    if not cache_path.exists():
        return

    try:
        data = json.loads(cache_path.read_text())
        for key, value in data.items():
            _analysis_cache[key] = EnvironmentInfo.from_dict(value)
    except Exception:
        # Ignore cache errors (corrupt file, etc)
        pass


def _save_persistent_cache(repo_root: Path) -> None:
    """Save the cache to disk."""
    cache_path = _get_persistent_cache_path(repo_root)
    try:
        data = {k: v.to_dict() for k, v in _analysis_cache.items()}
        cache_path.write_text(json.dumps(data, indent=2))
    except Exception:
        pass


async def analyze_environment(
    repo_root: Path,
    adapter: ModelAdapter,
    *,
    use_cache: bool = True,
) -> EnvironmentInfo:
    """Analyze a repository to determine test/lint commands using an LLM.

    IMPORTANT: The adapter must support structured output via JSON schema.
    CLI adapters like Claude CLI support this via --json-schema flag.
    This function does NOT parse JSON from stdout.

    Args:
        repo_root: Path to the repository root.
        adapter: Model adapter that supports schema_name parameter.
        use_cache: Whether to use cached results.

    Returns:
        EnvironmentInfo with detected commands and metadata.

    Raises:
        TypeError: If adapter doesn't support structured output.
    """
    # Check cache first
    cache_key = _compute_cache_key(repo_root) if use_cache else None

    if use_cache:
        # Lazy load cache
        if not _analysis_cache:
            _load_persistent_cache(repo_root)

        if cache_key and cache_key in _analysis_cache:
            return _analysis_cache[cache_key]

    # Build prompt with system instructions inline (for CLI compatibility)
    prompt = _build_analysis_prompt(repo_root, include_system_prompt=True)

    # Call LLM with structured output
    try:
        # Check if adapter supports schema_name parameter
        if not isinstance(adapter, StructuredOutputAdapter):
            # Try calling anyway - duck typing
            pass

        # NOTE: We don't pass system= because some CLI adapters (e.g., Claude CLI
        # with -p flag) don't support the --system flag. Instead, the system
        # prompt is inlined into the user prompt.
        response: AdapterResponse = await adapter.call(
            prompt,
            max_tokens=500,
            temperature=0.0,  # Deterministic for consistency
            schema_name="environment_analysis",  # Use JSON schema for structured output
        )

        # Parse from raw_response which contains the structured output
        result = _parse_structured_response(response.raw_response)

    except TypeError as e:
        # Adapter doesn't support schema_name parameter
        result = EnvironmentInfo(
            confidence=0.0,
            analysis_notes=f"Adapter doesn't support structured output: {e}",
        )
    except Exception as e:
        # On any error, return empty result with low confidence
        result = EnvironmentInfo(
            confidence=0.0,
            analysis_notes=f"LLM analysis failed: {e}",
        )

    # Cache the result
    if cache_key:
        _analysis_cache[cache_key] = result
        if use_cache:
            _save_persistent_cache(repo_root)

    return result


def clear_cache() -> None:
    """Clear the analysis cache."""
    _analysis_cache.clear()


async def detect_test_command_llm(
    repo_root: Path,
    adapter: ModelAdapter,
    *,
    fallback_to_heuristics: bool = True,
) -> Optional[str]:
    """Detect test command using LLM with optional heuristic fallback.

    This is a convenience function that combines LLM analysis with the
    existing heuristic-based detection as a fallback.

    Args:
        repo_root: Path to the repository root.
        adapter: Model adapter to use for analysis.
        fallback_to_heuristics: If LLM fails or has low confidence, use heuristics.

    Returns:
        Test command string or None if not detected.
    """
    # Try LLM analysis first
    info = await analyze_environment(repo_root, adapter)

    if info.test_command and info.confidence >= 0.5:
        return info.test_command

    # Fall back to heuristics if LLM didn't give a confident answer
    if fallback_to_heuristics:
        from deliberate.validation.detectors import detect_test_command

        return detect_test_command(repo_root)

    return info.test_command


async def detect_lint_command_llm(
    repo_root: Path,
    adapter: ModelAdapter,
    *,
    fallback_to_heuristics: bool = True,
) -> Optional[str]:
    """Detect lint command using LLM with optional heuristic fallback.

    Args:
        repo_root: Path to the repository root.
        adapter: Model adapter to use for analysis.
        fallback_to_heuristics: If LLM fails or has low confidence, use heuristics.

    Returns:
        Lint command string or None if not detected.
    """
    # Try LLM analysis first
    info = await analyze_environment(repo_root, adapter)

    if info.lint_command and info.confidence >= 0.5:
        return info.lint_command

    # Fall back to heuristics if LLM didn't give a confident answer
    if fallback_to_heuristics:
        return _detect_lint_command_heuristic(repo_root)

    return info.lint_command


def _detect_lint_command_heuristic(repo_root: Path) -> Optional[str]:
    """Detect lint command using simple heuristics.

    Args:
        repo_root: Path to the repository root.

    Returns:
        Lint command string or None if not detected.
    """
    import json as json_module

    # Python projects
    if (repo_root / "pyproject.toml").exists() or (repo_root / "setup.py").exists():
        if (repo_root / "uv.lock").exists():
            return "uv run ruff check ."
        return "ruff check ."

    # Node.js projects
    package_json = repo_root / "package.json"
    if package_json.exists():
        try:
            data = json_module.loads(package_json.read_text())
            scripts = data.get("scripts", {})
            if "lint" in scripts:
                if (repo_root / "yarn.lock").exists():
                    return "yarn lint"
                if (repo_root / "pnpm-lock.yaml").exists():
                    return "pnpm lint"
                return "npm run lint"
        except Exception:
            pass

    # Rust projects
    if (repo_root / "Cargo.toml").exists():
        return "cargo clippy"

    # Go projects
    if (repo_root / "go.mod").exists():
        return "go vet ./..."

    return None
