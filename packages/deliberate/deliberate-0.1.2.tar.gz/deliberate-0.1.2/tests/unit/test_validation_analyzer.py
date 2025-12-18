"""Tests for the LLM-based validation analyzer."""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from deliberate.validation.analyzer import (
    _compute_cache_key,
    analyze_environment,
    clear_cache,
    detect_test_command_llm,
)


@pytest.fixture(autouse=True)
def clear_env_cache():
    """Clear the analyzer cache before each test."""
    clear_cache()
    yield
    clear_cache()


@pytest.fixture
def mock_repo(tmp_path):
    """Create a mock repository structure."""
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "package.json").write_text('{"scripts": {"test": "echo test"}}')
    (repo / "src").mkdir()
    (repo / "src" / "index.js").write_text("console.log('hello');")
    return repo


@pytest.fixture
def mock_adapter():
    """Create a mock model adapter."""
    adapter = MagicMock()
    adapter.call = AsyncMock()
    return adapter


def test_compute_cache_key_changes(mock_repo):
    """Test that cache key changes when files change."""
    key1 = _compute_cache_key(mock_repo)

    # Modify a config file
    (mock_repo / "package.json").write_text('{"scripts": {"test": "echo new"}}')
    key2 = _compute_cache_key(mock_repo)

    assert key1 != key2


def test_compute_cache_key_stable(mock_repo):
    """Test that cache key is stable for same content."""
    key1 = _compute_cache_key(mock_repo)
    key2 = _compute_cache_key(mock_repo)
    assert key1 == key2


@pytest.mark.asyncio
async def test_analyze_environment_caching(mock_repo, mock_adapter):
    """Test that results are cached to disk."""
    # Mock LLM response
    mock_adapter.call.return_value.raw_response = {
        "structured_output": {
            "test_command": "npm test",
            "confidence": 0.9,
            "project_types": ["node"],
        }
    }

    # 1. First call - should hit LLM
    result1 = await analyze_environment(mock_repo, mock_adapter, use_cache=True)
    assert result1.test_command == "npm test"
    assert mock_adapter.call.call_count == 1

    # Verify cache file exists
    cache_file = mock_repo / ".deliberate" / "cache.json"
    assert cache_file.exists()
    cache_content = json.loads(cache_file.read_text())
    assert len(cache_content) == 1

    # 2. Second call - should use cache (no LLM call)
    result2 = await analyze_environment(mock_repo, mock_adapter, use_cache=True)
    assert result2.test_command == "npm test"
    assert mock_adapter.call.call_count == 1  # Count should not increase


@pytest.mark.asyncio
async def test_detect_test_command_llm_fallback(mock_repo, mock_adapter):
    """Test fallback to heuristics when LLM fails or has low confidence."""

    # Case 1: LLM returns low confidence
    mock_adapter.call.return_value.raw_response = {
        "structured_output": {
            "test_command": "unknown command",
            "confidence": 0.1,
        }
    }

    # We rely on the heuristic detector which should see package.json
    # The heuristic detector for node checks for 'test' script and lockfiles
    # Our mock_repo has package.json with "test" script but no lockfile -> defaults to npm test

    cmd = await detect_test_command_llm(mock_repo, mock_adapter, fallback_to_heuristics=True)
    assert cmd == "npm test"  # From heuristic fallback


@pytest.mark.asyncio
async def test_detect_test_command_llm_success(mock_repo, mock_adapter):
    """Test successful LLM detection."""
    mock_adapter.call.return_value.raw_response = {
        "structured_output": {
            "test_command": "npm run custom-test",
            "confidence": 0.95,
        }
    }

    cmd = await detect_test_command_llm(mock_repo, mock_adapter)
    assert cmd == "npm run custom-test"
