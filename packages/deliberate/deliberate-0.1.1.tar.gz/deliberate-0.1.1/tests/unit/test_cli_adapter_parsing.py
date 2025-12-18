from deliberate.adapters.cli_adapter import CLIAdapter, _looks_like_json, _repair_json


def test_repair_json_blank_returns_none():
    assert _repair_json("") is None
    assert _repair_json("   ") is None


def test_parse_json_response_blank_falls_back():
    adapter = CLIAdapter(name="test", command=["codex"])

    content, parsed = adapter._parse_json_response("")

    assert content == ""
    assert parsed is None


def test_parse_json_response_skips_non_json_logs():
    adapter = CLIAdapter(name="test", command=["codex"])
    loggy = "[INFO] hello\nsome log line"

    content, parsed = adapter._parse_json_response(loggy)

    assert content == loggy
    assert parsed is None


def test_looks_like_json_helper():
    assert _looks_like_json('  {"a":1}')
    assert _looks_like_json(" [1,2]")
    assert not _looks_like_json("INFO something")


def test_parse_json_response_with_prefix_logs_and_json():
    adapter = CLIAdapter(name="gemini", command=["gemini"], parser_type="gemini")
    raw = 'YOLO mode is enabled.\n{"response": "pong"}'

    content, parsed = adapter._parse_json_response(raw)

    assert content == "pong"
    assert isinstance(parsed, dict)


def test_parse_json_response_falls_back_to_combined_output():
    adapter = CLIAdapter(name="gemini", command=["gemini"], parser_type="gemini")
    raw = ""  # stdout empty
    combined = 'stderr log line\n{"response": "pong"}'

    content, parsed = adapter._parse_with_fallback(raw, combined)

    assert content == "pong"
    assert isinstance(parsed, dict)


def test_gemini_parser_extracts_tokens_from_nested_stats():
    """Test that GeminiCLIParser extracts tokens from stats.tokens structure."""
    from deliberate.adapters.cli_adapter import CLIResponseData, GeminiCLIParser

    parser = GeminiCLIParser()
    raw = """{
        "response": "Hello!",
        "stats": {
            "tokens": {"input": 42, "output": 17}
        }
    }"""

    content, parsed = parser.parse_output(raw)

    assert content == "Hello!"
    assert parsed is not None
    # Verify tokens are flattened to top level
    assert "tokens" in parsed
    assert parsed["tokens"]["input"] == 42
    assert parsed["tokens"]["output"] == 17

    # Verify CLIResponseData can extract them
    response_data = CLIResponseData.model_validate(parsed)
    input_tokens, output_tokens = response_data.get_token_counts()
    assert input_tokens == 42
    assert output_tokens == 17
