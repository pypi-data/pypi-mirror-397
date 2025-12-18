from unittest.mock import MagicMock, patch

import pytest

from deliberate.adapters.api_adapter import APIAdapter


@pytest.fixture
def mock_litellm():
    with patch("deliberate.adapters.api_adapter.acompletion") as mock:
        yield mock


@pytest.fixture
def api_adapter():
    return APIAdapter(name="test-gpt", model="gpt-4o", config={"max_tokens": 100})


@pytest.mark.asyncio
async def test_api_call_success(api_adapter, mock_litellm):
    # Mock response
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Test response"
    mock_response.usage.total_tokens = 50
    mock_response._hidden_params.get.return_value = 0.001
    mock_response.model_dump.return_value = {"id": "123"}

    mock_litellm.return_value = mock_response

    response = await api_adapter.call("Hello")

    assert response.content == "Test response"
    assert response.token_usage == 50
    assert response.raw_response["id"] == "123"

    # Verify call arguments
    mock_litellm.assert_called_once()
    call_kwargs = mock_litellm.call_args.kwargs
    assert call_kwargs["model"] == "gpt-4o"
    assert call_kwargs["messages"] == [{"role": "user", "content": "Hello"}]


@pytest.mark.asyncio
async def test_api_call_with_system_prompt(api_adapter, mock_litellm):
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "OK"
    mock_litellm.return_value = mock_response

    await api_adapter.call("User msg", system="System msg")

    call_kwargs = mock_litellm.call_args.kwargs
    assert call_kwargs["messages"] == [
        {"role": "system", "content": "System msg"},
        {"role": "user", "content": "User msg"},
    ]


@pytest.mark.asyncio
async def test_api_run_agentic(api_adapter, mock_litellm):
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Agentic result"
    mock_litellm.return_value = mock_response

    await api_adapter.run_agentic("Do task", working_dir="/tmp")

    call_kwargs = mock_litellm.call_args.kwargs
    # Check that it uses a system prompt for agentic behavior
    messages = call_kwargs["messages"]
    assert messages[0]["role"] == "system"
    assert "expert software engineer" in messages[0]["content"]
    assert messages[1]["content"] == "Do task"
