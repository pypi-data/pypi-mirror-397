"""Tests for PlanExtractor."""

from deliberate.iteration.extractors import (
    CodeExtractor,
    ExtractionResult,
    PlanExtractor,
)


class TestExtractionResult:
    """Tests for ExtractionResult dataclass."""

    def test_successful_result(self):
        """Successful extraction has content."""
        result = ExtractionResult(
            success=True,
            content="Plan content here",
            format_detected="xml",
        )
        assert result.success is True
        assert result.content == "Plan content here"
        assert result.format_detected == "xml"
        assert result.error is None

    def test_failed_result(self):
        """Failed extraction has error message."""
        result = ExtractionResult(
            success=False,
            error="Could not extract",
        )
        assert result.success is False
        assert result.content == ""
        assert result.error == "Could not extract"


class TestPlanExtractorXML:
    """Tests for XML extraction."""

    def test_extracts_from_xml_tags(self):
        """Extracts content from <plan> tags."""
        extractor = PlanExtractor()
        response = """
Here is the plan:
<plan>
1. First step
2. Second step
3. Third step
</plan>
That's my plan.
"""
        plan = extractor.extract(response)

        assert plan is not None
        assert "1. First step" in plan.content
        assert "2. Second step" in plan.content
        assert "3. Third step" in plan.content
        assert "Here is the plan" not in plan.content

    def test_case_insensitive_xml_tags(self):
        """Works with uppercase <PLAN> tags."""
        extractor = PlanExtractor()
        response = "<PLAN>The implementation plan</PLAN>"

        plan = extractor.extract(response)

        assert plan is not None
        assert plan.content == "The implementation plan"

    def test_xml_with_surrounding_text(self):
        """Extracts only content inside tags."""
        extractor = PlanExtractor()
        response = "Prefix text <plan>Actual plan</plan> Suffix text"

        plan = extractor.extract(response)

        assert plan is not None
        assert plan.content == "Actual plan"

    def test_first_xml_block_extracted(self):
        """Extracts first <plan> block when multiple exist."""
        extractor = PlanExtractor()
        response = "<plan>First plan</plan> and <plan>Second plan</plan>"

        plan = extractor.extract(response)

        assert plan is not None
        assert plan.content == "First plan"


class TestPlanExtractorMarkdown:
    """Tests for Markdown extraction."""

    def test_extracts_from_plan_code_block(self):
        """Extracts content from ```plan code blocks."""
        extractor = PlanExtractor()
        response = """
Here's my plan:
```plan
1. Step one
2. Step two
```
Done.
"""
        plan = extractor.extract(response)

        assert plan is not None
        assert "1. Step one" in plan.content
        assert "2. Step two" in plan.content

    def test_extracts_from_markdown_code_block(self):
        """Extracts content from ```markdown code blocks."""
        extractor = PlanExtractor()
        response = """
```markdown
# Implementation Plan
- Task 1
- Task 2
```
"""
        plan = extractor.extract(response)

        assert plan is not None
        assert "# Implementation Plan" in plan.content
        assert "- Task 1" in plan.content

    def test_extracts_from_generic_code_block(self):
        """Extracts content from ``` code blocks without language."""
        extractor = PlanExtractor()
        response = """
```
My plan content here
with multiple lines
```
"""
        plan = extractor.extract(response)

        assert plan is not None
        assert "My plan content here" in plan.content

    def test_prefers_xml_over_markdown_by_default(self):
        """XML is preferred when both exist."""
        extractor = PlanExtractor(prefer_xml=True)
        response = """
<plan>XML plan content</plan>
```plan
Markdown plan content
```
"""
        plan = extractor.extract(response)

        assert plan is not None
        assert plan.content == "XML plan content"

    def test_prefers_markdown_when_configured(self):
        """Markdown is preferred when prefer_xml=False."""
        extractor = PlanExtractor(prefer_xml=False)
        response = """
<plan>XML plan content</plan>
```plan
Markdown plan content
```
"""
        plan = extractor.extract(response)

        assert plan is not None
        assert plan.content == "Markdown plan content"


class TestPlanExtractorPlainText:
    """Tests for plain text extraction."""

    def test_falls_back_to_plain_text(self):
        """Uses entire response when no structured format found."""
        extractor = PlanExtractor()
        response = """
1. First implementation step
2. Second implementation step
3. Third implementation step
"""
        plan = extractor.extract(response)

        assert plan is not None
        assert "1. First implementation step" in plan.content

    def test_strips_common_preambles(self):
        """Removes 'Here is the plan:' and similar."""
        extractor = PlanExtractor()

        test_cases = [
            ("Here is the plan:\n1. Step one", "1. Step one"),
            ("Here's my plan:\n1. Step one", "1. Step one"),
            ("Implementation plan:\n1. Step one", "1. Step one"),
            ("Plan:\n1. Step one", "1. Step one"),
        ]

        for response, expected_content in test_cases:
            plan = extractor.extract(response)
            assert plan is not None
            assert plan.content == expected_content, f"Failed for: {response}"


class TestPlanExtractorValidation:
    """Tests for extraction validation."""

    def test_returns_none_for_empty_response(self):
        """Returns None for empty input."""
        extractor = PlanExtractor()
        assert extractor.extract("") is None
        assert extractor.extract("   ") is None

    def test_returns_none_for_short_response(self):
        """Returns None when below min_content_length."""
        extractor = PlanExtractor(min_content_length=20)
        assert extractor.extract("Short") is None
        assert extractor.extract("<plan>Hi</plan>") is None

    def test_custom_min_content_length(self):
        """Respects custom min_content_length setting."""
        extractor = PlanExtractor(min_content_length=5)
        plan = extractor.extract("<plan>12345</plan>")
        assert plan is not None
        assert plan.content == "12345"


class TestPlanExtractorMetadata:
    """Tests for plan metadata generation."""

    def test_assigns_agent_name(self):
        """Plan has correct agent name."""
        extractor = PlanExtractor(agent_name="my-planner")
        plan = extractor.extract("<plan>Content here</plan>")

        assert plan is not None
        assert plan.agent == "my-planner"

    def test_uses_provided_plan_id(self):
        """Uses plan_id from context when provided."""
        extractor = PlanExtractor()
        context = {"plan_id": "custom-id-123"}
        plan = extractor.extract("<plan>Content here</plan>", context)

        assert plan is not None
        assert plan.id == "custom-id-123"

    def test_generates_plan_id_when_not_provided(self):
        """Generates unique plan ID when not in context."""
        extractor = PlanExtractor()
        plan1 = extractor.extract("<plan>Content one</plan>")
        plan2 = extractor.extract("<plan>Content two</plan>")

        assert plan1 is not None
        assert plan2 is not None
        assert plan1.id.startswith("plan-")
        assert plan2.id.startswith("plan-")
        assert plan1.id != plan2.id


class TestPlanExtractorFormatDetection:
    """Tests for get_extraction_format method."""

    def test_detects_xml_format(self):
        """Correctly identifies XML format."""
        extractor = PlanExtractor(min_content_length=5)
        format_name = extractor.get_extraction_format("<plan>Content enough</plan>")
        assert format_name == "xml"

    def test_detects_markdown_format(self):
        """Correctly identifies markdown format."""
        extractor = PlanExtractor(min_content_length=5)
        format_name = extractor.get_extraction_format("```plan\nContent enough\n```")
        assert format_name == "markdown"

    def test_detects_plain_format(self):
        """Correctly identifies plain text format."""
        extractor = PlanExtractor()
        format_name = extractor.get_extraction_format("Just some text with steps listed")
        assert format_name == "plain"

    def test_detects_none_for_empty(self):
        """Returns 'none' for empty input."""
        extractor = PlanExtractor()
        format_name = extractor.get_extraction_format("")
        assert format_name == "none"


class TestCodeExtractor:
    """Tests for CodeExtractor."""

    def test_extracts_from_xml_tags(self):
        """Extracts content from <code> tags."""
        extractor = CodeExtractor()
        response = "<code>print('hello')</code>"

        code = extractor.extract(response)

        assert code == "print('hello')"

    def test_extracts_from_markdown_code_block(self):
        """Extracts content from markdown code blocks."""
        extractor = CodeExtractor()
        response = """
```python
def hello():
    print('hello')
```
"""
        code = extractor.extract(response)

        assert code is not None
        assert "def hello():" in code
        assert "print('hello')" in code

    def test_extracts_language_specific_block(self):
        """Prefers language-specific block when language is set."""
        extractor = CodeExtractor(language="python")
        response = """
```javascript
console.log('js');
```
```python
print('python')
```
"""
        code = extractor.extract(response)

        assert code is not None
        assert "print('python')" in code
        assert "console.log" not in code

    def test_returns_none_for_plain_text(self):
        """Does not extract plain text as code."""
        extractor = CodeExtractor()
        response = "This is just plain text, not code"

        code = extractor.extract(response)

        assert code is None

    def test_returns_none_for_empty(self):
        """Returns None for empty input."""
        extractor = CodeExtractor()
        assert extractor.extract("") is None
        assert extractor.extract("   ") is None

    def test_strips_whitespace(self):
        """Strips leading/trailing whitespace by default."""
        extractor = CodeExtractor()
        response = """
```
   code with spaces
```
"""
        code = extractor.extract(response)

        assert code == "code with spaces"

    def test_preserves_whitespace_when_configured(self):
        """Preserves whitespace when strip_whitespace=False."""
        extractor = CodeExtractor(strip_whitespace=False)
        response = """
```
   code with spaces
```
"""
        code = extractor.extract(response)

        assert code is not None
        assert code.startswith("   ")
        # The actual content extracted includes the trailing spaces
        assert "code with spaces" in code


class TestCodeExtractorMinLength:
    """Tests for CodeExtractor min_content_length."""

    def test_rejects_short_code(self):
        """Rejects code below min_content_length."""
        extractor = CodeExtractor(min_content_length=10)
        response = "<code>x=1</code>"

        code = extractor.extract(response)

        assert code is None

    def test_accepts_code_at_min_length(self):
        """Accepts code at exactly min_content_length."""
        extractor = CodeExtractor(min_content_length=5)
        response = "<code>12345</code>"

        code = extractor.extract(response)

        assert code == "12345"
