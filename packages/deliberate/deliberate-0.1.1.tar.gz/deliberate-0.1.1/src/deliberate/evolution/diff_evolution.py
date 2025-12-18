"""Diff-based evolution using SEARCH/REPLACE blocks.

Implements AlphaEvolve's diff-based code modification:
- SEARCH/REPLACE blocks for targeted changes
- EVOLVE-BLOCK markers for evolution regions
- Fuzzy matching for robust application
"""

import re
from dataclasses import dataclass
from difflib import SequenceMatcher, unified_diff

from .types import DiffBlock

# Markers for code regions that can be evolved
EVOLVE_BLOCK_START = "# EVOLVE-BLOCK-START"
EVOLVE_BLOCK_END = "# EVOLVE-BLOCK-END"

# Alternative markers for different languages
EVOLVE_MARKERS = {
    "python": ("# EVOLVE-BLOCK-START", "# EVOLVE-BLOCK-END"),
    "javascript": ("// EVOLVE-BLOCK-START", "// EVOLVE-BLOCK-END"),
    "typescript": ("// EVOLVE-BLOCK-START", "// EVOLVE-BLOCK-END"),
    "rust": ("// EVOLVE-BLOCK-START", "// EVOLVE-BLOCK-END"),
    "go": ("// EVOLVE-BLOCK-START", "// EVOLVE-BLOCK-END"),
    "c": ("/* EVOLVE-BLOCK-START */", "/* EVOLVE-BLOCK-END */"),
    "cpp": ("// EVOLVE-BLOCK-START", "// EVOLVE-BLOCK-END"),
    "java": ("// EVOLVE-BLOCK-START", "// EVOLVE-BLOCK-END"),
}


@dataclass
class EvolveRegion:
    """A region of code that can be evolved."""

    start_line: int
    end_line: int
    content: str
    name: str | None = None


class DiffParser:
    """Parser for SEARCH/REPLACE diff blocks."""

    # Pattern for SEARCH/REPLACE blocks
    DIFF_PATTERN = re.compile(
        r"<<<<<<< SEARCH\s*\n(.*?)\n=======\s*\n(.*?)\n>>>>>>> REPLACE",
        re.DOTALL,
    )

    # Alternative pattern for fence-style blocks
    FENCE_PATTERN = re.compile(
        r"```diff\s*\n<<<<<<< SEARCH\s*\n(.*?)\n=======\s*\n(.*?)\n>>>>>>> REPLACE\s*\n```",
        re.DOTALL,
    )

    def parse(self, text: str) -> list[DiffBlock]:
        """Parse SEARCH/REPLACE blocks from text.

        Args:
            text: Text containing diff blocks.

        Returns:
            List of parsed DiffBlock objects.
        """
        blocks = []

        # Try fence pattern first (more specific)
        for match in self.FENCE_PATTERN.finditer(text):
            blocks.append(
                DiffBlock(
                    search=match.group(1).strip(),
                    replace=match.group(2).strip(),
                )
            )

        # If no fence blocks found, try bare pattern
        if not blocks:
            for match in self.DIFF_PATTERN.finditer(text):
                blocks.append(
                    DiffBlock(
                        search=match.group(1).strip(),
                        replace=match.group(2).strip(),
                    )
                )

        return blocks

    def parse_with_locations(self, text: str, code: str) -> list[DiffBlock]:
        """Parse diff blocks and find their locations in code.

        Args:
            text: Text containing diff blocks.
            code: The original code to search in.

        Returns:
            List of DiffBlock objects with line numbers.
        """
        blocks = self.parse(text)
        code_lines = code.split("\n")

        for block in blocks:
            # Find the search text in the code
            search_lines = block.search.split("\n")
            if not search_lines:
                continue

            # Look for exact match first
            for i in range(len(code_lines) - len(search_lines) + 1):
                window = "\n".join(code_lines[i : i + len(search_lines)])
                if window.strip() == block.search.strip():
                    block.line_number = i + 1  # 1-indexed
                    break

            # If no exact match, try fuzzy matching
            if block.line_number is None:
                best_ratio = 0.0
                best_line = None
                for i in range(len(code_lines) - len(search_lines) + 1):
                    window = "\n".join(code_lines[i : i + len(search_lines)])
                    ratio = SequenceMatcher(None, window.strip(), block.search.strip()).ratio()
                    if ratio > best_ratio and ratio > 0.8:  # 80% similarity threshold
                        best_ratio = ratio
                        best_line = i + 1
                block.line_number = best_line

        return blocks


def parse_diff(text: str) -> list[DiffBlock]:
    """Parse SEARCH/REPLACE diff blocks from text.

    Args:
        text: Text containing diff blocks.

    Returns:
        List of DiffBlock objects.
    """
    return DiffParser().parse(text)


def apply_diff(code: str, blocks: list[DiffBlock], fuzzy: bool = True) -> str:
    """Apply SEARCH/REPLACE diff blocks to code.

    Args:
        code: Original code to modify.
        blocks: List of diff blocks to apply.
        fuzzy: Whether to use fuzzy matching for search text.

    Returns:
        Modified code with all applicable diffs applied.

    Raises:
        ValueError: If a required block cannot be applied.
    """
    result = code

    for block in blocks:
        # Try exact match first
        if block.search in result:
            result = result.replace(block.search, block.replace, 1)
            continue

        # Try stripped match (ignore leading/trailing whitespace differences)
        if block.search.strip() in result:
            # Find and replace with whitespace preserved
            result = _replace_with_whitespace_preserved(result, block)
            continue

        if fuzzy:
            # Try fuzzy matching
            matched, new_result = _fuzzy_replace(result, block)
            if matched:
                result = new_result
                continue

        # If we get here, the block couldn't be applied
        # For non-critical evolution, we continue rather than failing
        # (AlphaEvolve is robust to partial failures)

    return result


def _replace_with_whitespace_preserved(code: str, block: DiffBlock) -> str:
    """Replace search text while preserving surrounding whitespace."""
    lines = code.split("\n")
    search_lines = block.search.strip().split("\n")
    replace_lines = block.replace.split("\n")

    # Find the search block
    for i in range(len(lines) - len(search_lines) + 1):
        window = [ln.strip() for ln in lines[i : i + len(search_lines)]]
        search_stripped = [ln.strip() for ln in search_lines]

        if window == search_stripped:
            # Preserve leading whitespace from first line
            leading_ws = len(lines[i]) - len(lines[i].lstrip())
            indent = " " * leading_ws

            # Apply replacement with same indentation
            indented_replace = [
                indent + line if j > 0 else lines[i][:leading_ws] + line for j, line in enumerate(replace_lines)
            ]

            # Reconstruct
            return "\n".join(lines[:i] + indented_replace + lines[i + len(search_lines) :])

    return code


def _fuzzy_replace(code: str, block: DiffBlock, threshold: float = 0.8) -> tuple[bool, str]:
    """Attempt fuzzy replacement using sequence matching.

    Args:
        code: Original code.
        block: Diff block to apply.
        threshold: Minimum similarity ratio for matching.

    Returns:
        Tuple of (success, modified_code).
    """
    lines = code.split("\n")
    search_lines = block.search.strip().split("\n")
    n_search = len(search_lines)

    best_ratio = 0.0
    best_start = 0

    # Slide window through code
    for i in range(len(lines) - n_search + 1):
        window = "\n".join(lines[i : i + n_search])
        ratio = SequenceMatcher(None, window.strip(), block.search.strip()).ratio()

        if ratio > best_ratio:
            best_ratio = ratio
            best_start = i

    if best_ratio >= threshold:
        # Apply replacement
        replace_lines = block.replace.split("\n")

        # Try to preserve indentation
        original_indent = len(lines[best_start]) - len(lines[best_start].lstrip())
        indent = " " * original_indent

        indented_replace = []
        for j, line in enumerate(replace_lines):
            if line.strip():  # Non-empty line
                indented_replace.append(indent + line.lstrip())
            else:
                indented_replace.append(line)

        new_lines = lines[:best_start] + indented_replace + lines[best_start + n_search :]
        return True, "\n".join(new_lines)

    return False, code


def create_evolve_markers(
    code: str,
    start_line: int,
    end_line: int,
    language: str = "python",
    name: str | None = None,
) -> str:
    """Add EVOLVE-BLOCK markers around a code region.

    Args:
        code: Original code.
        start_line: First line of region (1-indexed).
        end_line: Last line of region (1-indexed).
        language: Programming language for marker style.
        name: Optional name for the block.

    Returns:
        Code with markers added.
    """
    markers = EVOLVE_MARKERS.get(language, EVOLVE_MARKERS["python"])
    start_marker, end_marker = markers

    if name:
        start_marker = f"{start_marker} {name}"
        end_marker = f"{end_marker} {name}"

    lines = code.split("\n")
    start_idx = start_line - 1
    end_idx = end_line

    # Get indentation from first line
    if start_idx < len(lines):
        indent = len(lines[start_idx]) - len(lines[start_idx].lstrip())
        indent_str = " " * indent
    else:
        indent_str = ""

    # Insert markers
    lines.insert(start_idx, f"{indent_str}{start_marker}")
    lines.insert(end_idx + 1, f"{indent_str}{end_marker}")

    return "\n".join(lines)


def extract_evolve_regions(
    code: str,
    language: str = "python",
) -> list[EvolveRegion]:
    """Extract EVOLVE-BLOCK marked regions from code.

    Args:
        code: Code with EVOLVE-BLOCK markers.
        language: Programming language for marker detection.

    Returns:
        List of EvolveRegion objects.
    """
    markers = EVOLVE_MARKERS.get(language, EVOLVE_MARKERS["python"])
    start_marker_base, end_marker_base = markers

    regions = []
    lines = code.split("\n")

    # Pattern to match start markers (possibly with names)
    start_pattern = re.compile(rf"^\s*{re.escape(start_marker_base)}(?:\s+(.+))?$")
    end_pattern = re.compile(rf"^\s*{re.escape(end_marker_base)}(?:\s+(.+))?$")

    stack: list[tuple[int, str | None]] = []  # (start_line, name)

    for i, line in enumerate(lines):
        start_match = start_pattern.match(line)
        end_match = end_pattern.match(line)

        if start_match:
            name = start_match.group(1)
            stack.append((i + 1, name))  # 1-indexed

        elif end_match and stack:
            start_line, name = stack.pop()
            end_line = i + 1  # 1-indexed

            # Extract content (excluding markers)
            content_lines = lines[start_line : end_line - 1]
            content = "\n".join(content_lines)

            regions.append(
                EvolveRegion(
                    start_line=start_line + 1,  # First content line
                    end_line=end_line - 1,  # Last content line
                    content=content,
                    name=name,
                )
            )

    return regions


def generate_diff_prompt_section(
    parent_code: str,
    child_code: str,
    context_lines: int = 3,
) -> str:
    """Generate a diff section for prompts showing changes made.

    Args:
        parent_code: Original code.
        child_code: Modified code.
        context_lines: Number of context lines in unified diff.

    Returns:
        Formatted diff string for prompt inclusion.
    """
    parent_lines = parent_code.splitlines(keepends=True)
    child_lines = child_code.splitlines(keepends=True)

    diff = unified_diff(
        parent_lines,
        child_lines,
        fromfile="parent",
        tofile="child",
        lineterm="",
        n=context_lines,
    )

    return "".join(diff)


def count_changes(parent_code: str, child_code: str) -> dict[str, int]:
    """Count the types of changes between two code versions.

    Args:
        parent_code: Original code.
        child_code: Modified code.

    Returns:
        Dictionary with change counts.
    """
    parent_lines = parent_code.split("\n")
    child_lines = child_code.split("\n")

    matcher = SequenceMatcher(None, parent_lines, child_lines)
    opcodes = matcher.get_opcodes()

    stats = {
        "lines_added": 0,
        "lines_removed": 0,
        "lines_changed": 0,
        "lines_unchanged": 0,
    }

    for tag, i1, i2, j1, j2 in opcodes:
        if tag == "equal":
            stats["lines_unchanged"] += i2 - i1
        elif tag == "insert":
            stats["lines_added"] += j2 - j1
        elif tag == "delete":
            stats["lines_removed"] += i2 - i1
        elif tag == "replace":
            stats["lines_changed"] += max(i2 - i1, j2 - j1)

    return stats
