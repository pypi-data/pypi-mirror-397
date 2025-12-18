"""Extractors for iterative solving.

Specialized SolutionExtractor implementations for different solution types:
- PlanExtractor: Extracts Plan objects from LLM responses
"""

import re
from dataclasses import dataclass
from typing import ClassVar

from deliberate.types import Plan

from .solver import SolutionExtractor


@dataclass
class ExtractionResult:
    """Result of attempting to extract a solution from LLM response."""

    success: bool
    content: str = ""
    format_detected: str = "unknown"
    error: str | None = None


class PlanExtractor(SolutionExtractor[Plan]):
    """Extracts Plan objects from LLM responses.

    Supports multiple formats:
    1. XML tags: <plan>...</plan>
    2. Markdown code blocks: ```plan ... ``` or ```markdown ... ```
    3. Plain text: The entire response is treated as the plan

    The extractor tries formats in order of specificity, preferring
    structured formats over plain text.
    """

    # Patterns for plan extraction
    XML_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"<plan>(.*?)</plan>", re.DOTALL | re.IGNORECASE)
    MARKDOWN_PLAN_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"```(?:plan|markdown)?\s*\n(.*?)```", re.DOTALL)

    def __init__(
        self,
        agent_name: str = "planner",
        prefer_xml: bool = True,
        strip_whitespace: bool = True,
        min_content_length: int = 10,
    ):
        """Initialize the plan extractor.

        Args:
            agent_name: Name to assign to extracted plans.
            prefer_xml: If True, try XML extraction first.
            strip_whitespace: If True, strip leading/trailing whitespace.
            min_content_length: Minimum content length for valid extraction.
        """
        self.agent_name = agent_name
        self.prefer_xml = prefer_xml
        self.strip_whitespace = strip_whitespace
        self.min_content_length = min_content_length

    def extract(self, response: str, context: dict | None = None) -> Plan | None:
        """Extract a Plan from an LLM response.

        Args:
            response: The raw LLM response text.
            context: Optional context dict with 'plan_id' key.

        Returns:
            A Plan object if extraction succeeds, None otherwise.
        """
        if not response or len(response.strip()) < self.min_content_length:
            return None

        result = self._try_extract(response)

        if not result.success:
            return None

        plan_id = (context or {}).get("plan_id", self._generate_plan_id())

        return Plan(
            id=plan_id,
            agent=self.agent_name,
            content=result.content,
        )

    def _try_extract(self, response: str) -> ExtractionResult:
        """Try to extract plan content using various formats.

        Returns:
            ExtractionResult with extracted content and format info.
        """
        extractors = [
            (self._extract_xml, "xml"),
            (self._extract_markdown, "markdown"),
            (self._extract_plain, "plain"),
        ]

        if not self.prefer_xml:
            # Try markdown first if not preferring XML
            extractors = [extractors[1], extractors[0], extractors[2]]

        for extractor, format_name in extractors:
            content = extractor(response)
            if content and len(content) >= self.min_content_length:
                if self.strip_whitespace:
                    content = content.strip()
                return ExtractionResult(
                    success=True,
                    content=content,
                    format_detected=format_name,
                )

        return ExtractionResult(
            success=False,
            error="Could not extract plan content from response",
        )

    def _extract_xml(self, response: str) -> str | None:
        """Extract content from <plan>...</plan> tags."""
        match = self.XML_PATTERN.search(response)
        if match:
            return match.group(1)
        return None

    def _extract_markdown(self, response: str) -> str | None:
        """Extract content from markdown code blocks."""
        match = self.MARKDOWN_PLAN_PATTERN.search(response)
        if match:
            return match.group(1)
        return None

    def _extract_plain(self, response: str) -> str | None:
        """Use the entire response as plan content.

        Optionally strip common preambles like "Here is the plan:" etc.
        """
        content = response.strip()

        # Remove common preambles
        preamble_patterns = [
            r"^(?:here(?:'s| is) (?:the|my|a) plan:?\s*)",
            r"^(?:implementation plan:?\s*)",
            r"^(?:plan:?\s*)",
        ]

        for pattern in preamble_patterns:
            content = re.sub(pattern, "", content, flags=re.IGNORECASE)

        return content.strip() if content else None

    def _generate_plan_id(self) -> str:
        """Generate a unique plan ID."""
        import uuid

        return f"plan-{uuid.uuid4().hex[:8]}"

    def get_extraction_format(self, response: str) -> str:
        """Detect which format would be used for extraction.

        Useful for debugging or logging.

        Args:
            response: The LLM response to analyze.

        Returns:
            Format name: 'xml', 'markdown', 'plain', or 'none'.
        """
        result = self._try_extract(response)
        return result.format_detected if result.success else "none"


class CodeExtractor(SolutionExtractor[str]):
    """Extracts code from LLM responses.

    Supports multiple formats:
    1. XML tags: <code>...</code>
    2. Markdown code blocks: ```python ... ``` or ```language ... ```
    3. Plain text: Best-effort extraction

    Primarily used for code-focused iterative solving.
    """

    # Patterns for code extraction
    XML_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"<code>(.*?)</code>", re.DOTALL | re.IGNORECASE)
    MARKDOWN_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"```(?:\w+)?\s*\n(.*?)```", re.DOTALL)

    def __init__(
        self,
        language: str | None = None,
        strip_whitespace: bool = True,
        min_content_length: int = 5,
    ):
        """Initialize the code extractor.

        Args:
            language: Expected language (for markdown block detection).
            strip_whitespace: If True, strip leading/trailing whitespace.
            min_content_length: Minimum content length for valid extraction.
        """
        self.language = language
        self.strip_whitespace = strip_whitespace
        self.min_content_length = min_content_length

        # Build language-specific pattern if provided
        if language:
            self.LANG_MARKDOWN_PATTERN = re.compile(
                rf"```{re.escape(language)}\s*\n(.*?)```", re.DOTALL | re.IGNORECASE
            )
        else:
            self.LANG_MARKDOWN_PATTERN = None

    def extract(self, response: str, context: dict | None = None) -> str | None:
        """Extract code from an LLM response.

        Args:
            response: The raw LLM response text.
            context: Optional context (unused).

        Returns:
            The extracted code string, or None if extraction fails.
        """
        if not response or len(response.strip()) < self.min_content_length:
            return None

        # Try language-specific markdown first
        if self.LANG_MARKDOWN_PATTERN:
            match = self.LANG_MARKDOWN_PATTERN.search(response)
            if match:
                content = match.group(1)
                content = content.strip() if self.strip_whitespace else content
                if len(content) >= self.min_content_length:
                    return content

        # Try XML
        match = self.XML_PATTERN.search(response)
        if match:
            content = match.group(1)
            content = content.strip() if self.strip_whitespace else content
            if len(content) >= self.min_content_length:
                return content

        # Try generic markdown
        match = self.MARKDOWN_PATTERN.search(response)
        if match:
            content = match.group(1)
            content = content.strip() if self.strip_whitespace else content
            if len(content) >= self.min_content_length:
                return content

        # For code, we don't want to return plain text as it's usually not code
        return None
