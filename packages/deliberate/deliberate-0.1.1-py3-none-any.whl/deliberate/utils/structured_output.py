"""Helpers for extracting structured tool calls from model responses."""

from __future__ import annotations

import json
from typing import Any


def extract_tool_call(raw_response: Any, content: str | None, tool_name: str) -> dict | None:
    """Extract tool arguments from a response.

    Only uses the adapter's raw_response (structured/tool call payloads).
    Intentionally avoids parsing JSON from stdout/text content.
    """
    return _extract_from_raw_response(raw_response, tool_name)


def _extract_from_raw_response(raw_response: Any, tool_name: str) -> dict | None:
    """Handle common raw_response layouts (OpenAI-style, Claude structured_output)."""
    if not isinstance(raw_response, dict):
        return None

    # Direct structured outputs (e.g., Claude)
    structured = raw_response.get("structured_output")
    if structured:
        parsed = _parse_tool_payload(structured, tool_name)
        if parsed:
            return parsed

    # Top-level tool calls
    for tool in raw_response.get("tool_calls") or []:
        parsed = _parse_tool_payload(tool, tool_name)
        if parsed:
            return parsed

    # OpenAI-style choices with tool_calls
    choices = raw_response.get("choices")
    if isinstance(choices, list):
        for choice in choices:
            message = choice.get("message") if isinstance(choice, dict) else None
            if not isinstance(message, dict):
                continue

            for tool_call in message.get("tool_calls") or []:
                parsed = _parse_tool_payload(tool_call, tool_name)
                if parsed:
                    return parsed

            # Legacy/function_call field
            func_call = message.get("function_call")
            if func_call and func_call.get("name") == tool_name:
                parsed_args = _normalize_arguments(func_call.get("arguments"))
                if parsed_args:
                    return parsed_args

    # Fallback: treat raw_response itself as a potential payload
    return _parse_tool_payload(raw_response, tool_name)


def _parse_tool_payload(payload: Any, tool_name: str) -> dict | None:
    """Normalize various tool payload shapes."""
    if not isinstance(payload, dict):
        return None

    if payload.get("tool") == tool_name or payload.get("name") == tool_name:
        arguments = payload.get("arguments") or payload.get("args") or payload
        return _normalize_arguments(arguments)

    if tool_name in payload:
        return _normalize_arguments(payload.get(tool_name))

    function = payload.get("function")
    if isinstance(function, dict) and function.get("name") == tool_name:
        return _normalize_arguments(function.get("arguments") or function.get("args"))

    # Accept bare argument dictionaries when they look like the tool payload
    if tool_name == "select_plan" and "plan_id" in payload:
        return _normalize_arguments(payload)
    if tool_name == "submit_review" and ("scores" in payload or "verdict" in payload):
        return _normalize_arguments(payload)

    return None


def _normalize_arguments(arguments: Any) -> dict | None:
    """Coerce arguments into a dictionary if possible."""
    if isinstance(arguments, dict):
        return arguments
    if isinstance(arguments, str):
        try:
            parsed = json.loads(arguments)
            return parsed if isinstance(parsed, dict) else None
        except json.JSONDecodeError:
            return None
    return None
