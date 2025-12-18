"Enhanced CLI adapter with structured output and accurate cost tracking."

import asyncio
import json
import logging
import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, cast

from pydantic import BaseModel, ValidationError

from deliberate.adapters.base import AdapterResponse, ModelAdapter, ToolInfo
from deliberate.agent_context import AgentExecutionContext
from deliberate.settings import DeliberateSettings, get_agent_env_dict
from deliberate.tracing.setup import get_tracer
from deliberate.verbose_logger import get_verbose_logger


class UsageData(BaseModel):
    """Token usage data from CLI responses."""

    input_tokens: int = 0
    output_tokens: int = 0
    completion_tokens: int = 0  # OpenAI-style alias for output_tokens
    cache_creation_input_tokens: int = 0
    cache_read_input_tokens: int = 0
    total_cost_usd: float | None = None
    cost_usd: float | None = None

    model_config = {"extra": "ignore"}


class TokenData(BaseModel):
    """Alternative token format (input/output instead of input_tokens/output_tokens)."""

    input: int = 0
    output: int = 0

    model_config = {"extra": "ignore"}


class CLIResponseData(BaseModel):
    """Parsed CLI response with optional usage and cost information.

    Handles various CLI response formats:
    - Claude: usage.input_tokens, usage.output_tokens, total_cost_usd
    - Gemini: tokens.input, tokens.output
    - Codex: usage.input_tokens, usage.output_tokens
    """

    usage: UsageData | None = None
    tokens: TokenData | None = None
    total_cost_usd: float | None = None
    cost_usd: float | None = None

    model_config = {"extra": "ignore"}

    def get_token_counts(self) -> tuple[int, int]:
        """Extract input/output token counts from available data."""
        if self.usage:
            input_tokens = (
                self.usage.input_tokens + self.usage.cache_creation_input_tokens + self.usage.cache_read_input_tokens
            )
            output_tokens = self.usage.output_tokens or self.usage.completion_tokens
            return input_tokens, output_tokens

        if self.tokens:
            return self.tokens.input, self.tokens.output

        return 0, 0

    def get_cost(self) -> float | None:
        """Extract cost from available data."""
        return (
            self.total_cost_usd
            or self.cost_usd
            or (self.usage.total_cost_usd if self.usage else None)
            or (self.usage.cost_usd if self.usage else None)
        )


try:
    from genai_prices import calc_price as _calc_price
    from genai_prices import types as gp_types

    HAS_GENAI_PRICES = True
except ImportError:
    HAS_GENAI_PRICES = False

    def _calc_price(usage: Any, model_ref: str) -> Any:
        raise ImportError("genai-prices not installed")


@dataclass(frozen=True)
class CLIParser(ABC):
    """Abstract parser for CLI outputs."""

    name: str

    def __init__(self) -> None:  # pragma: no cover - trivial
        pass

    @abstractmethod
    def parse_output(self, content: str) -> tuple[str, dict | None]: ...


def _repair_json(text: str) -> Any:
    """Attempt to parse or repair malformed JSON using json-repair.

    Returns None for empty/whitespace input to avoid noisy warnings.
    """
    if not text or not str(text).strip():
        return None

    # First, try strict parsing (fastest)
    try:
        return json.loads(text)
    except Exception:
        pass

    # Helper to try parsing a substring
    def try_parse(candidate: str) -> Any | None:
        try:
            return json.loads(candidate)
        except Exception:
            try:
                import json_repair  # type: ignore

                repaired = json_repair.repair_json(candidate)
                return json.loads(repaired)
            except Exception:
                return None

    # Priority 1: Try to find a JSON Object {...}
    # This is preferred because agent outputs are typically objects.
    # Searching for '{' first avoids picking up [INFO] logs as lists.
    first_brace = text.find("{")
    if first_brace != -1:
        last_brace = text.rfind("}")
        if last_brace != -1 and last_brace >= first_brace:
            candidate = text[first_brace : last_brace + 1]
            result = try_parse(candidate)
            if result is not None:
                return result

    # Priority 2: Try to find a JSON List [...]
    # Only if object not found.
    first_bracket = text.find("[")
    if first_bracket != -1:
        last_bracket = text.rfind("]")
        if last_bracket != -1 and last_bracket >= first_bracket:
            candidate = text[first_bracket : last_bracket + 1]
            result = try_parse(candidate)
            if result is not None:
                return result

    # Fallback: try repairing the full text
    try:
        import json_repair  # type: ignore

        repaired = json_repair.repair_json(text)
        return json.loads(repaired)
    except Exception:
        logging.warning("Failed to repair JSON response", exc_info=True)
        return None


def _looks_like_json(text: str) -> bool:
    """Lightweight check to see if the text appears to be JSON.

    Avoids feeding loggy/stdout chatter into the JSON repair path for
    agents that already communicate via MCP or structured channels.
    """
    if not text:
        return False
    stripped = text.strip()
    return (stripped.startswith("{") and stripped.endswith("}")) or (
        stripped.startswith("[") and stripped.endswith("]")
    )


class ClaudeCLIParser(CLIParser):
    name = "claude"

    def parse_output(self, content: str) -> tuple[str, dict | None]:
        parsed = _repair_json(content)
        if not parsed:
            return content, None

        if "structured_output" in parsed:
            structured = parsed["structured_output"]
            return json.dumps(structured, indent=2), parsed

        if "result" in parsed:
            return parsed["result"], parsed
        if "content" in parsed:
            return parsed["content"], parsed
        return json.dumps(parsed, indent=2), parsed


class DefaultCLIParser(CLIParser):
    name = "default"

    def parse_output(self, content: str) -> tuple[str, dict | None]:
        parsed = _repair_json(content)
        if not parsed:
            return content, None

        if isinstance(parsed, dict):
            for key in ("content", "text", "message", "result"):
                if key in parsed:
                    return parsed[key], parsed
            return json.dumps(parsed, indent=2), parsed

        return str(parsed), {"raw_value": parsed}


class CodexCLIParser(CLIParser):
    """Parser for Codex CLI JSON lines output.

    Codex outputs one JSON object per line with various event types:
    - type="message.completed" contains the final message with content
    - type="item.completed" contains completed items (reasoning, text, etc.)
    - type="response.completed" may contain usage stats
    """

    name = "codex"

    def parse_output(self, content: str) -> tuple[str, dict | None]:
        # First, try to parse the entire content as a single JSON object
        try:
            obj = json.loads(content)
            # If it's a single object, process it as such
            if isinstance(obj, dict):
                event_type = obj.get("type", "")
                if event_type == "message.completed":
                    message = obj.get("message", {})
                    content_list = message.get("content", [])
                    for content_item in content_list:
                        if content_item.get("type") == "text":
                            text = content_item.get("text", "")
                            if text:
                                return text, obj
                elif event_type == "item.completed":
                    item = obj.get("item", {})
                    item_type = item.get("type", "")
                    if item_type in ("text", "output_text"):
                        text = item.get("text", "")
                        if text:
                            return text, obj
                # Fallback for single non-event JSON objects (e.g., raw tool output)
                return json.dumps(obj, indent=2), obj
            # If it's not a dict, return as string
            return str(obj), {"raw_value": obj}
        except json.JSONDecodeError:
            pass  # Not a single JSON object, proceed with line-by-line parsing

        text_parts: list[str] = []
        tokens: dict[str, int] = {"input": 0, "output": 0}
        cost = 0.0
        parsed_any = False
        last_message_content: str | None = None

        for line in content.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                parsed_any = True
                event_type = obj.get("type", "")

                # Handle message.completed - contains the final response content
                if event_type == "message.completed":
                    message = obj.get("message", {})
                    content_list = message.get("content", [])
                    for content_item in content_list:
                        if content_item.get("type") == "text":
                            text = content_item.get("text", "")
                            if text:
                                last_message_content = text

                # Handle item.completed - contains text/reasoning items
                elif event_type == "item.completed":
                    item = obj.get("item", {})
                    item_type = item.get("type", "")
                    if item_type in ("text", "output_text"):
                        text = item.get("text", "")
                        if text:
                            text_parts.append(text)

                # Handle response.completed - may contain usage stats
                elif event_type == "response.completed":
                    response = obj.get("response", {})
                    usage = response.get("usage", {})
                    tokens["input"] += usage.get("input_tokens", 0)
                    tokens["output"] += usage.get("output_tokens", 0)

            except json.JSONDecodeError:
                continue

        if not parsed_any:
            # Try single JSON object as fallback
            parsed = _repair_json(content)
            if not parsed:
                return content, None
            return DefaultCLIParser().parse_output(json.dumps(parsed))

        # Prefer the final message content if available, else join text parts
        full_text = last_message_content or "".join(text_parts).strip()
        metadata = {
            "tokens": tokens,
            "cost_usd": cost,
            "input_tokens": tokens["input"],
            "output_tokens": tokens["output"],
        }
        return full_text, metadata


class GeminiCLIParser(CLIParser):
    """Parser for Gemini CLI output.

    Gemini CLI outputs JSON with a "response" key containing the actual text.
    Stats are in a separate "stats" object with nested "tokens".

    Example Gemini response:
    {
        "response": "Hello!",
        "stats": {
            "tokens": {"input": 10, "output": 8}
        }
    }
    """

    name = "gemini"

    def parse_output(self, content: str) -> tuple[str, dict | None]:
        parsed = _repair_json(content)
        if not parsed:
            return content, None

        if not isinstance(parsed, dict):
            return str(parsed), {"raw_value": parsed}

        # Flatten stats.tokens to tokens for CLIResponseData compatibility
        if "stats" in parsed and isinstance(parsed["stats"], dict):
            stats = parsed["stats"]
            if "tokens" in stats and isinstance(stats["tokens"], dict):
                # Copy tokens to top level for CLIResponseData extraction
                parsed["tokens"] = stats["tokens"]

        # Gemini uses "response" key for the actual text content
        if "response" in parsed:
            return parsed["response"], parsed

        # Fall back to other common keys
        for key in ("content", "text", "message", "result"):
            if key in parsed:
                return parsed[key], parsed

        return json.dumps(parsed, indent=2), parsed


class OpenCodeCLIParser(CLIParser):
    """Parser for opencode JSON lines output.

    OpenCode outputs one JSON object per line:
    - type="text" contains the text response
    - type="step_finish" contains token usage and cost
    """

    name = "opencode"

    def parse_output(self, content: str) -> tuple[str, dict | None]:
        text_parts: list[str] = []
        tokens: dict[str, int] = {"input": 0, "output": 0}
        cost = 0.0
        parsed_any = False

        for line in content.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                parsed_any = True
                event_type = obj.get("type")
                part = obj.get("part", {})

                if event_type == "text":
                    text = part.get("text", "")
                    if text:
                        text_parts.append(text)

                elif event_type == "step_finish":
                    token_data = part.get("tokens", {})
                    tokens["input"] += token_data.get("input", 0)
                    tokens["output"] += token_data.get("output", 0)
                    cost += part.get("cost", 0)

            except json.JSONDecodeError:
                continue

        if not parsed_any:
            return content, None

        full_text = "".join(text_parts).strip()
        metadata = {
            "tokens": tokens,
            "cost_usd": cost,
            "input_tokens": tokens["input"],
            "output_tokens": tokens["output"],
        }
        return full_text, metadata


class CLIStrategy:
    """Strategy for CLI-specific behaviors."""

    def __init__(
        self,
        name: str,
        pipe_stdin: bool,
        add_structured: Callable[[list[str], str | None, Callable[[str], dict[str, Any] | None]], list[str]],
        parser: CLIParser,
        build_telemetry: Callable[
            [str | None, str | None, str | None, bool | None],
            tuple[list[str], dict[str, str]],
        ],
        build_gemini_json: Callable[
            [str | None, str | None, str | None, bool | None],
            dict[str, Any] | None,
        ] = lambda *args: None,
    ):
        self.name = name
        self.pipe_stdin = pipe_stdin
        self.add_structured = add_structured
        self.parser = parser
        self.build_telemetry = build_telemetry
        self.build_gemini_json = build_gemini_json


def _add_structured_claude(
    cmd: list[str],
    schema_name: str | None,
    schema_loader: Callable[[str], dict[str, Any] | None],
) -> list[str]:
    if "--output-format" not in cmd:
        cmd.extend(["--output-format", "json"])
    if schema_name:
        schema = schema_loader(schema_name)
        if schema:
            cmd.extend(["--json-schema", json.dumps(schema)])
    return cmd


def _add_structured_codex(
    cmd: list[str],
    schema_name: str | None,
    schema_loader: Callable[[str], dict[str, Any] | None],
) -> list[str]:
    if "--json" not in cmd:
        cmd.append("--json")
    return cmd


def _add_structured_noop(
    cmd: list[str],
    schema_name: str | None,
    schema_loader: Callable[[str], dict[str, Any] | None],
) -> list[str]:
    return cmd


def _get_standard_otel_env(
    endpoint: str | None,
    exporter: str | None,
    environment: str | None,
    service_name: str,
) -> dict[str, str]:
    """Build standard OpenTelemetry environment variables."""
    env: dict[str, str] = {}

    if endpoint:
        env["OTEL_EXPORTER_OTLP_ENDPOINT"] = endpoint

    if exporter:
        if exporter == "otlp-http":
            env["OTEL_EXPORTER_OTLP_PROTOCOL"] = "http/protobuf"
        elif exporter == "otlp-grpc":
            env["OTEL_EXPORTER_OTLP_PROTOCOL"] = "grpc"

    if environment:
        attr = f"deployment.environment={environment}"
        if "OTEL_RESOURCE_ATTRIBUTES" in os.environ:
            env["OTEL_RESOURCE_ATTRIBUTES"] = f"{os.environ['OTEL_RESOURCE_ATTRIBUTES']},{attr}"
        else:
            env["OTEL_RESOURCE_ATTRIBUTES"] = attr

    env["OTEL_SERVICE_NAME"] = service_name

    return env


def _build_telemetry_standard(
    endpoint: str | None,
    exporter: str | None,
    environment: str | None,
    log_user_prompt: bool | None,
) -> tuple[list[str], dict[str, str]]:
    """Build standard OpenTelemetry environment variables."""
    env = _get_standard_otel_env(endpoint, exporter, environment, "deliberate-agent")
    return [], env


def _build_gemini_json_content(
    endpoint: str | None,
    exporter: str | None,
    environment: str | None,
    log_user_prompt: bool | None,
) -> dict[str, Any] | None:
    """Build gemini.json telemetry content."""
    # Only create telemetry config if any relevant setting is provided
    if not endpoint and not exporter and environment is None and log_user_prompt is None:
        return None

    telemetry_config: dict[str, Any] = {"enabled": True}
    if endpoint:
        telemetry_config["otlpEndpoint"] = endpoint
    if exporter:
        # Map our exporter names to Gemini's protocol names
        if exporter == "otlp-http":
            telemetry_config["otlpProtocol"] = "http"
        elif exporter == "otlp-grpc":
            telemetry_config["otlpProtocol"] = "grpc"
    if log_user_prompt is not None:
        telemetry_config["logPrompts"] = log_user_prompt

    # Note: Gemini's settings.json has no direct equivalent for OTel deployment.environment
    # This is handled by the agent's internal config based on OTEL_RESOURCE_ATTRIBUTES

    return {"telemetry": telemetry_config}


def _build_gemini_mcp_config(
    mcp_servers: list["MCPServerConfig"],
) -> dict[str, Any]:
    """Build Gemini mcpServers config from MCPServerConfig list.

    Gemini settings.json supports:
    - stdio servers: {"command": "...", "args": [...], "env": {...}}
    - HTTP servers: {"httpUrl": "...", "headers": {...}}
    - SSE servers: {"url": "...", "trust": true}
    """
    if not mcp_servers:
        return {}

    mcp_config: dict[str, Any] = {}
    for server in mcp_servers:
        mcp_config[server.name] = server.to_gemini_dict()

    return {"mcpServers": mcp_config}


def _build_telemetry_gemini(
    endpoint: str | None,
    exporter: str | None,
    environment: str | None,
    log_user_prompt: bool | None,
) -> tuple[list[str], dict[str, str]]:
    """Build Gemini-specific OpenTelemetry config."""
    # Gemini relies on standard environment variables
    env = _get_standard_otel_env(endpoint, exporter, environment, "gemini-cli")
    return [], env


def _build_telemetry_codex(
    endpoint: str | None,
    exporter: str | None,
    environment: str | None,
    log_user_prompt: bool | None,
) -> tuple[list[str], dict[str, str]]:
    """Build Codex -c overrides for telemetry config."""
    # Codex uses standard environment variables internally, plus CLI flags for overrides
    env = _get_standard_otel_env(endpoint, exporter, environment, "codex-cli")

    overrides: list[str] = []
    if exporter:
        variant_key = f'"{exporter}"'
        exporter_fields = []
        if exporter == "otlp-http":
            exporter_fields.append('protocol="json"')
        elif exporter == "otlp-grpc":
            exporter_fields.append('protocol="binary"')
        if endpoint:
            exporter_fields.append(f'endpoint="{endpoint}"')
        inner = f"{{ {', '.join(exporter_fields)} }}" if exporter_fields else "{}"
        overrides.extend(["-c", f"otel.exporter={{ {variant_key} = {inner} }}"])
    if environment:
        overrides.extend(["-c", f'otel.environment="{environment}"'])
    if log_user_prompt is not None:
        overrides.extend(["-c", f"otel.log_user_prompt={str(log_user_prompt).lower()}"])
    return overrides, env


DEFAULT_STRATEGY = CLIStrategy(
    name="unknown",
    pipe_stdin=False,
    add_structured=_add_structured_noop,
    parser=DefaultCLIParser(),
    build_telemetry=_build_telemetry_standard,
)

CLI_STRATEGIES: dict[str, CLIStrategy] = {
    "claude": CLIStrategy(
        name="claude",
        pipe_stdin=False,
        add_structured=_add_structured_claude,
        parser=ClaudeCLIParser(),
        build_telemetry=_build_telemetry_standard,
    ),
    "gemini": CLIStrategy(
        name="gemini",
        pipe_stdin=True,
        add_structured=_add_structured_noop,
        parser=GeminiCLIParser(),
        build_telemetry=_build_telemetry_gemini,
        build_gemini_json=_build_gemini_json_content,
    ),
    "codex": CLIStrategy(
        name="codex",
        pipe_stdin=True,
        add_structured=_add_structured_codex,
        parser=CodexCLIParser(),
        build_telemetry=_build_telemetry_codex,
    ),
    "opencode": CLIStrategy(
        name="opencode",
        pipe_stdin=False,
        add_structured=_add_structured_noop,  # Already using --format json
        parser=OpenCodeCLIParser(),
        build_telemetry=_build_telemetry_standard,
    ),
}


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server to inject into the agent.

    Supports both stdio servers (command-based) and SSE/HTTP servers (URL-based).
    """

    name: str
    command: str = ""  # For stdio servers
    args: list[str] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)
    # For SSE/HTTP servers
    url: str = ""  # SSE endpoint URL
    headers: dict[str, str] = field(default_factory=dict)  # e.g., Authorization header

    @property
    def is_sse(self) -> bool:
        """Check if this is an SSE server (URL-based) vs stdio (command-based)."""
        return bool(self.url) and not self.command

    def to_dict(self) -> dict[str, Any]:
        """Convert to MCP config dict format (Claude-style)."""
        if self.is_sse:
            config: dict[str, Any] = {"type": "sse", "url": self.url}
            if self.headers:
                config["headers"] = self.headers
            return config
        else:
            config = {"command": self.command}
            if self.args:
                config["args"] = self.args
            if self.env:
                config["env"] = self.env
            return config

    def to_gemini_dict(self) -> dict[str, Any]:
        """Convert to Gemini settings.json format."""
        if self.is_sse:
            # Gemini SSE format: {"url": "...", "trust": true, "headers": {...}}
            config: dict[str, Any] = {"url": self.url}
            config["trust"] = True
            if self.headers:
                config["headers"] = self.headers
            return config
        else:
            # Gemini stdio format
            config = {"command": self.command}
            if self.args:
                config["args"] = self.args
            if self.env:
                config["env"] = self.env
            return config


@dataclass
class CLIAdapter(ModelAdapter):
    """CLI adapter with native structured output support."""

    name: str
    command: list[str]
    model_id: str | None = None  # For genai-prices lookup
    env: dict[str, str] = field(default_factory=dict)
    timeout_seconds: int = 300
    _call_count: int = field(default=0, repr=False)
    telemetry_endpoint: str | None = None  # For Codex OTEL endpoint
    telemetry_exporter: str | None = None  # none | otlp-http | otlp-grpc
    telemetry_environment: str | None = None
    telemetry_log_user_prompt: bool | None = None
    # Permission mode for handling agent questions (claude CLI specific)
    # Options: "default", "dontAsk", "bypassPermissions", "acceptEdits", "plan"
    permission_mode: str | None = None
    # Additional MCP servers to inject (claude CLI specific)
    mcp_servers: list[MCPServerConfig] = field(default_factory=list)
    # Explicit parser type (overrides auto-detection)
    parser_type: str | None = None

    def __post_init__(self) -> None:
        """Auto-detect CLI tool and model if not specified."""
        if not self.model_id and self.command:
            self.model_id = self._detect_model_id()

    def _detect_model_id(self) -> str | None:
        """Detect model ID from command for cost calculation."""
        cli_type = self._get_cli_type()
        model_defaults = {
            "claude": "claude-sonnet-4-5-20250929",
            "gemini": "gemini-2.0-flash-exp",
            "codex": "gpt-5.1-codex-mini",
        }
        return model_defaults.get(cli_type)

    def _get_cli_type(self) -> str:
        """Detect which CLI tool this is.

        Relies on explicit parser_type configuration.
        """
        if self.parser_type:
            return self.parser_type

        cli_name = ""
        if self.command:
            cli_name = str(self.command[0]).lower()
        elif self.name:
            cli_name = self.name.lower()

        if "claude" in cli_name:
            return "claude"
        if "gemini" in cli_name:
            return "gemini"
        if "codex" in cli_name:
            return "codex"
        if "opencode" in cli_name:
            return "opencode"

        return "unknown"

    def _load_schema(self, schema_name: str) -> dict[str, Any] | None:
        """Load a JSON schema file."""
        schema_path = Path(__file__).parent.parent / "schemas" / f"{schema_name}.json"
        if schema_path.exists():
            return cast(dict[str, Any], json.loads(schema_path.read_text()))
        return None

    def _get_strategy(self) -> CLIStrategy:
        """Return the strategy object for this CLI type."""
        return CLI_STRATEGIES.get(self._get_cli_type(), DEFAULT_STRATEGY)

    def _parse_json_response(self, content: str) -> tuple[str, dict | None]:
        """Parse JSON response using CLI-specific strategy."""
        if not content or not content.strip():
            return content, None

        has_json_braces = ("{" in content and "}" in content) or ("[" in content and "]" in content)
        looks_structured = has_json_braces and ('"' in content or ":" in content)
        if not looks_structured and not _looks_like_json(content):
            return content, None

        strategy = self._get_strategy()
        parser = strategy.parser
        try:
            result = parser.parse_output(content)
            if result is None:
                logging.error(f"Parser {parser.name} returned None for content: {content!r}")
            return result
        except json.JSONDecodeError:
            logging.warning("Failed to parse CLI response as JSON", exc_info=True)
            return content, None
        except Exception as exc:
            logging.warning("Falling back to raw CLI output because parsing failed: %s", exc, exc_info=True)
            return content, None

    def _parse_with_fallback(self, primary: str, combined: str | None) -> tuple[str, dict | None]:
        """Parse primary stdout first, then fall back to combined stdout+stderr."""
        content, parsed_json = self._parse_json_response(primary)
        if parsed_json is not None:
            return content, parsed_json

        if combined and combined != primary:
            alt_content, alt_parsed = self._parse_json_response(combined)
            if alt_parsed is not None:
                return alt_content, alt_parsed

        return content, parsed_json

    def _raise_if_error(self, parsed_json: dict | None, fallback_content: str) -> None:
        """Raise a RuntimeError if the parsed response indicates an error."""
        if not isinstance(parsed_json, dict):
            return

        is_error = parsed_json.get("is_error") is True
        type_field = str(parsed_json.get("type", "")).lower()
        subtype = str(parsed_json.get("subtype", "")).lower()
        permission_denials = parsed_json.get("permission_denials") or []

        # Treat explicit errors as fatal; permission_denials alone are warnings.
        if is_error or type_field.startswith("error") or "error" in subtype:
            detail = (
                parsed_json.get("result")
                or parsed_json.get("content")
                or parsed_json.get("message")
                or fallback_content
            )
            if permission_denials:
                detail = f"{detail} | permission_denials={permission_denials}"
            raise RuntimeError(f"{self.name} returned an error: {detail}")
        if permission_denials:
            logging.warning("%s encountered permission_denials: %s", self.name, permission_denials)

    def _extract_token_usage(self, parsed_json: dict | None) -> tuple[int, int, float | None]:
        """Extract input/output tokens and actual cost from parsed response.

        Uses Pydantic models to safely parse the response data, handling various
        CLI response formats (Claude, Gemini, Codex) gracefully.
        """
        if not parsed_json or not isinstance(parsed_json, dict):
            return 0, 0, None

        try:
            response_data = CLIResponseData.model_validate(parsed_json)
        except ValidationError:
            return 0, 0, None

        input_tokens, output_tokens = response_data.get_token_counts()
        actual_cost = response_data.get_cost()

        # Calculate cost using genai-prices if not provided in response
        if actual_cost is None and HAS_GENAI_PRICES and self.model_id:
            try:
                cache_write = response_data.usage.cache_creation_input_tokens if response_data.usage else None
                cache_read = response_data.usage.cache_read_input_tokens if response_data.usage else None
                price_result = _calc_price(
                    gp_types.Usage(
                        input_tokens=input_tokens or None,
                        output_tokens=output_tokens or None,
                        cache_write_tokens=cache_write,
                        cache_read_tokens=cache_read,
                    ),
                    self.model_id,
                )
                actual_cost = float(price_result.total_price)
            except Exception:
                pass

        return input_tokens, output_tokens, actual_cost

    def estimate_cost(self, tokens: int) -> float:
        """Estimate cost using genai-prices if available."""
        if not HAS_GENAI_PRICES or not self.model_id:
            return tokens / 5000

        try:
            # Split roughly in half for estimation
            input_tokens = tokens // 2
            output_tokens = tokens - input_tokens
            price = _calc_price(
                gp_types.Usage(input_tokens=input_tokens, output_tokens=output_tokens),
                self.model_id,
            )
            return float(price.total_price)
        except Exception:
            return tokens / 5000

    def estimate_cost_detailed(
        self,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """Estimate cost with separate input/output token counts."""
        if not HAS_GENAI_PRICES or not self.model_id:
            return (input_tokens + output_tokens) / 5000

        try:
            price = _calc_price(
                gp_types.Usage(
                    input_tokens=input_tokens or None,
                    output_tokens=output_tokens or None,
                ),
                self.model_id,
            )
            return float(price.total_price)
        except Exception:
            return (input_tokens + output_tokens) / 5000

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
        """Make a completion call with optional structured output."""
        start = time.monotonic()
        self._call_count += 1

        strategy = self._get_strategy()
        if strategy.name == "unknown":
            logging.warning("Unknown CLI strategy; ensure CLI emits strict JSON/structured output.")
        cmd = list(self.command)

        if system and strategy.name == "claude":
            cmd.extend(["--system", system])

        # Add telemetry config
        otel_args, otel_env = strategy.build_telemetry(
            self.telemetry_endpoint,
            self.telemetry_exporter,
            self.telemetry_environment,
            self.telemetry_log_user_prompt,
        )
        cmd.extend(otel_args)

        # Handle gemini settings.json for telemetry and MCP servers
        gemini_json_content = strategy.build_gemini_json(
            self.telemetry_endpoint,
            self.telemetry_exporter,
            self.telemetry_environment,
            self.telemetry_log_user_prompt,
        )

        # For Gemini, always copy global settings to local working directory
        # This ensures API keys and auth config are available in the worktree
        if strategy.name == "gemini" and working_dir:
            mcp_config = _build_gemini_mcp_config(list(self.mcp_servers))

            gemini_dir = Path(working_dir) / ".gemini"
            gemini_dir.mkdir(exist_ok=True)
            gemini_json_path = gemini_dir / "settings.json"

            # Start with user's global config to preserve API keys, auth, etc.
            global_settings_path = Path.home() / ".gemini" / "settings.json"
            full_config: dict[str, Any] = {}
            if global_settings_path.exists():
                try:
                    full_config = json.loads(global_settings_path.read_text())
                except Exception:
                    logging.debug("Failed to read global Gemini settings", exc_info=True)

            # Merge telemetry config
            if gemini_json_content:
                if "telemetry" in gemini_json_content:
                    full_config.setdefault("telemetry", {}).update(gemini_json_content["telemetry"])

            # Merge MCP servers
            if mcp_config and "mcpServers" in mcp_config:
                full_config.setdefault("mcpServers", {}).update(mcp_config["mcpServers"])

            # Only write if we have config to write
            if full_config:
                gemini_json_path.write_text(json.dumps(full_config, indent=2))
        elif gemini_json_content and working_dir:
            gemini_dir = Path(working_dir) / ".gemini"
            gemini_dir.mkdir(exist_ok=True)
            gemini_json_path = gemini_dir / "settings.json"
            gemini_json_path.write_text(json.dumps(gemini_json_content, indent=2))

        if schema_name:
            cmd = strategy.add_structured(cmd, schema_name, self._load_schema)

        # Add MCP config for CLIs that support it
        # Note: Codex uses global MCP config via `codex mcp add`, not --mcp-config
        if strategy.name in ("claude", "opencode"):
            cmd.extend(self._build_mcp_config_flags())

        cmd.append(prompt)

        # Merge env vars
        proc_env = self._get_env(otel_env)

        tracer = get_tracer()
        with tracer.start_as_current_span("cli.call") as span:
            span.set_attribute("gen_ai.system", self._get_cli_type())
            span.set_attribute("gen_ai.request.model", self.model_id or "unknown")
            span.set_attribute("command", str(cmd))

            try:
                from deliberate.utils.subprocess_manager import SubprocessManager

                result = await asyncio.wait_for(
                    SubprocessManager.run(
                        cmd,
                        cwd=working_dir,
                        env=proc_env,
                        timeout=self.timeout_seconds,
                    ),
                    timeout=self.timeout_seconds,
                )
            except asyncio.TimeoutError:
                span.set_attribute("error", True)
                span.set_attribute("error.type", "TimeoutError")
                raise TimeoutError(f"{self.name} timed out after {self.timeout_seconds}s")

            if result.returncode != 0:
                stderr_content = result.stderr.decode() if result.stderr else ""
                stdout_content = result.stdout.decode() if result.stdout else ""
                error_msg = stderr_content or stdout_content or "Unknown error"
                span.set_attribute("error", True)
                span.set_attribute("error.message", error_msg)
                raise RuntimeError(f"{self.name} failed with exit code {result.returncode}: {error_msg}")

            raw_content = result.stdout.decode()
            stderr_content = result.stderr.decode() if result.stderr else ""
            combined_output = raw_content + (("\n" + stderr_content) if stderr_content else "")
            span.set_attribute("gen_ai.response.content_length", len(raw_content))
        content, parsed_json = self._parse_with_fallback(raw_content, combined_output)
        self._raise_if_error(parsed_json, content)

        input_tokens, output_tokens, actual_cost = self._extract_token_usage(parsed_json)
        total_tokens = input_tokens + output_tokens or self.estimate_tokens(prompt + content)

        if parsed_json and actual_cost is not None:
            parsed_json["_actual_cost_usd"] = actual_cost

        final_content = content
        if (not str(content).strip()) and combined_output.strip():
            final_content = combined_output.strip()

        return AdapterResponse(
            content=final_content,
            token_usage=total_tokens,
            duration_seconds=time.monotonic() - start,
            raw_response=parsed_json,
            stdout=combined_output or None,
        )

    async def run_agentic(
        self,
        task: str,
        *,
        working_dir: str,
        timeout_seconds: int = 1200,
        on_question: Callable[[str], str] | None = None,
        schema_name: str | None = "execution",
        extra_mcp_servers: list[MCPServerConfig] | None = None,
    ) -> AdapterResponse:
        """Run agentic task with structured output.

        Args:
            task: The task description to execute.
            working_dir: Working directory for the agent.
            timeout_seconds: Maximum time for execution.
            on_question: Optional callback for handling questions.
                Note: Interactive question handling requires stream mode
                which is not yet implemented. For now, use permission_mode
                to control question behavior at the CLI level.
            schema_name: Optional JSON schema name for structured output.
            extra_mcp_servers: Additional MCP servers to inject for this call.
                These are merged with self.mcp_servers and passed via --mcp-config.

        Returns:
            AdapterResponse with execution results.
        """
        start = time.monotonic()
        self._call_count += 1

        strategy = self._get_strategy()
        if strategy.name == "unknown":
            logging.warning("Unknown CLI strategy; ensure CLI emits strict JSON/structured output.")
        cmd = strategy.add_structured(list(self.command), schema_name, self._load_schema)
        pipe_stdin = strategy.pipe_stdin

        # Add telemetry config
        otel_args, otel_env = strategy.build_telemetry(
            self.telemetry_endpoint,
            self.telemetry_exporter,
            self.telemetry_environment,
            self.telemetry_log_user_prompt,
        )
        cmd.extend(otel_args)

        # Handle gemini settings.json for telemetry and MCP servers
        gemini_json_content = strategy.build_gemini_json(
            self.telemetry_endpoint,
            self.telemetry_exporter,
            self.telemetry_environment,
            self.telemetry_log_user_prompt,
        )

        # For Gemini, always copy global settings to local working directory
        # This ensures API keys and auth config are available in the worktree
        if strategy.name == "gemini" and working_dir:
            all_mcp_servers = list(self.mcp_servers)
            if extra_mcp_servers:
                all_mcp_servers.extend(extra_mcp_servers)

            mcp_config = _build_gemini_mcp_config(all_mcp_servers)

            gemini_dir = Path(working_dir) / ".gemini"
            gemini_dir.mkdir(exist_ok=True)
            gemini_json_path = gemini_dir / "settings.json"

            # Start with user's global config to preserve API keys, auth, etc.
            global_settings_path = Path.home() / ".gemini" / "settings.json"
            full_config: dict[str, Any] = {}
            if global_settings_path.exists():
                try:
                    full_config = json.loads(global_settings_path.read_text())
                except Exception:
                    logging.debug("Failed to read global Gemini settings", exc_info=True)

            # Merge telemetry config (don't overwrite user's telemetry prefs)
            if gemini_json_content:
                if "telemetry" in gemini_json_content:
                    full_config.setdefault("telemetry", {}).update(gemini_json_content["telemetry"])

            # Merge MCP servers (add our servers to user's existing ones)
            if mcp_config and "mcpServers" in mcp_config:
                full_config.setdefault("mcpServers", {}).update(mcp_config["mcpServers"])

            # Only write if we have config to write
            if full_config:
                gemini_json_path.write_text(json.dumps(full_config, indent=2))
        elif gemini_json_content and working_dir:
            # Non-Gemini strategy but has gemini_json (shouldn't happen, but handle it)
            gemini_dir = Path(working_dir) / ".gemini"
            gemini_dir.mkdir(exist_ok=True)
            gemini_json_path = gemini_dir / "settings.json"
            gemini_json_path.write_text(json.dumps(gemini_json_content, indent=2))

        # Add MCP server config for CLIs that support it
        if strategy.name in ("claude", "opencode"):
            cmd.extend(self._build_mcp_config_flags(extra_mcp_servers))
            cmd.extend(self._build_claude_permission_flags(on_question))
        elif strategy.name == "codex":
            cmd.extend(self._build_codex_mcp_flags(extra_mcp_servers))
            cmd.extend(self._build_codex_permission_flags())

        if not pipe_stdin:
            cmd.append(task)

        # Merge env vars
        proc_env = self._get_env(otel_env)

        tracer = get_tracer()
        verbose_logger = get_verbose_logger()
        stdout_cb = stderr_cb = None
        if getattr(verbose_logger, "show_stdout", False) and verbose_logger.enabled:

            def stdout_cb(chunk):
                return verbose_logger.stream_output(self.name, chunk, "stdout")

            def stderr_cb(chunk):
                return verbose_logger.stream_output(self.name, chunk, "stderr")

        with tracer.start_as_current_span("cli.run_agentic") as span:
            span.set_attribute("gen_ai.system", self._get_cli_type())
            span.set_attribute("gen_ai.request.model", self.model_id or "unknown")
            span.set_attribute("command", str(cmd))

            try:
                from deliberate.utils.subprocess_manager import SubprocessManager

                result = await asyncio.wait_for(
                    SubprocessManager.run(
                        cmd,
                        cwd=working_dir,
                        env=proc_env,
                        timeout=timeout_seconds,
                        stdin_data=task.encode() if pipe_stdin else None,
                        stdout_callback=stdout_cb,
                        stderr_callback=stderr_cb,
                    ),
                    timeout=timeout_seconds,
                )
            except asyncio.TimeoutError:
                span.set_attribute("error", True)
                span.set_attribute("error.type", "TimeoutError")
                raise TimeoutError(f"{self.name} agentic task timed out after {timeout_seconds}s")

            raw_content = result.stdout.decode()
            stderr_content = result.stderr.decode() if result.stderr else ""
            combined_output = raw_content + (("\n" + stderr_content) if stderr_content else "")

            if result.returncode != 0:
                err_text = stderr_content or raw_content or "Unknown error"
                span.set_attribute("error", True)
                span.set_attribute("error.message", err_text)
                raise RuntimeError(f"{self.name} agentic task failed with exit code {result.returncode}: {err_text}")

            span.set_attribute("gen_ai.response.content_length", len(raw_content))

        try:
            content, parsed_json = self._parse_with_fallback(raw_content, combined_output)
            self._raise_if_error(parsed_json, content)

            input_tokens, output_tokens, actual_cost = self._extract_token_usage(parsed_json)

            # Ensure content is a string for token estimation
            content_str = content if isinstance(content, str) else str(content)
            total_tokens = input_tokens + output_tokens or self.estimate_tokens(task + content_str)

            if parsed_json and actual_cost is not None:
                parsed_json["_actual_cost_usd"] = actual_cost

            # Provide a more informative fallback when the CLI produced no structured content
            final_content = content
            if (not str(content).strip()) and combined_output.strip():
                final_content = combined_output.strip()

            return AdapterResponse(
                content=final_content,
                token_usage=total_tokens,
                duration_seconds=time.monotonic() - start,
                raw_response=parsed_json,
                stdout=combined_output or None,
            )
        except Exception as e:
            logging.error(f"Error processing CLI output: {e}", exc_info=True)
            # Re-raise to be caught by caller
            raise

    async def run_from_context(self, working_dir: Path) -> AdapterResponse:
        """Run agent using config from .deliberate/config.json.

        This method loads the AgentExecutionContext from the worktree and uses
        it to configure the agent execution, replacing explicit parameter passing.

        Args:
            working_dir: Path to the worktree containing .deliberate/config.json.

        Returns:
            AdapterResponse with execution results.

        Raises:
            FileNotFoundError: If config file doesn't exist.
            ValidationError: If config file is invalid.
        """
        context = AgentExecutionContext.load_from_worktree(working_dir)

        # Build MCP servers from context
        extra_mcp_servers: list[MCPServerConfig] = []

        # Add orchestrator MCP server if configured
        if context.mcp.orchestrator:
            extra_mcp_servers.append(
                MCPServerConfig(
                    name="orchestrator",
                    url=context.mcp.orchestrator.url,
                    headers={"Authorization": f"Bearer {context.mcp.orchestrator.token}"},
                )
            )

        # Add additional MCP servers
        for server in context.mcp.servers:
            extra_mcp_servers.append(
                MCPServerConfig(
                    name=server.name,
                    command=server.command or "",
                    args=server.args or [],
                    url=server.url or "",
                    env=server.env or {},
                )
            )

        # Build task prompt from context
        task = context.task.description
        if context.task.plan_content:
            task = f"{task}\n\n## Plan\n{context.task.plan_content}"

        return await self.run_agentic(
            task=task,
            working_dir=str(working_dir),
            timeout_seconds=context.execution.timeout_seconds,
            extra_mcp_servers=extra_mcp_servers if extra_mcp_servers else None,
        )

    async def list_tools(self, *, working_dir: str | None = None) -> list[ToolInfo]:
        """List available CLI tools and capabilities.

        Exposes information about the wrapped CLI tool, including its type,
        command, and supported features like structured output.

        Args:
            working_dir: Ignored for CLI adapter (included for interface consistency).

        Returns:
            List of ToolInfo describing the CLI and its capabilities.
        """
        cli_type = self._get_cli_type()
        strategy = self._get_strategy()

        # The CLI itself is exposed as a tool
        tools = [
            ToolInfo(
                name=f"{cli_type}_cli",
                description=f"Wrapped {cli_type} CLI for agentic code tasks",
                source="cli",
                metadata={
                    "cli_type": cli_type,
                    "command": self.command,
                    "model_id": self.model_id,
                    "pipe_stdin": strategy.pipe_stdin,
                    "supports_structured_output": strategy.name in ("claude", "codex"),
                },
            )
        ]

        # Add capability-specific tools based on CLI type
        if cli_type == "claude":
            tools.extend(
                [
                    ToolInfo(
                        name="structured_json",
                        description="JSON schema-based structured output",
                        source="cli",
                        metadata={"cli_type": cli_type, "flag": "--json-schema"},
                    ),
                    ToolInfo(
                        name="system_prompt",
                        description="Custom system prompt support",
                        source="cli",
                        metadata={"cli_type": cli_type, "flag": "--system"},
                    ),
                ]
            )
        elif cli_type == "codex":
            tools.append(
                ToolInfo(
                    name="json_output",
                    description="JSON output mode",
                    source="cli",
                    metadata={"cli_type": cli_type, "flag": "--json"},
                )
            )

        return tools

    def _get_env(self, extra_env: dict[str, str] | None = None) -> dict[str, str]:
        """Get merged environment variables."""
        merged_env = os.environ.copy()

        try:
            settings = DeliberateSettings()
            agent_env = get_agent_env_dict(self.name, settings)
            merged_env.update(agent_env)
        except Exception:
            pass

        # For Gemini, inject API key from user's global settings.json if not already set
        if self._get_cli_type() == "gemini" and "GEMINI_API_KEY" not in merged_env:
            global_settings_path = Path.home() / ".gemini" / "settings.json"
            if global_settings_path.exists():
                try:
                    settings_data = json.loads(global_settings_path.read_text())
                    api_key = settings_data.get("apiKey")
                    if api_key:
                        merged_env["GEMINI_API_KEY"] = api_key
                except Exception:
                    logging.debug("Failed to read Gemini API key from settings", exc_info=True)

        merged_env.update(self.env)
        if extra_env:
            merged_env.update(extra_env)
        return merged_env

    def _build_mcp_config_flags(
        self,
        extra_servers: list[MCPServerConfig] | None = None,
    ) -> list[str]:
        """Build --mcp-config flags for Claude CLI.

        Generates JSON config for MCP servers and returns CLI flags to inject them.

        Args:
            extra_servers: Additional MCP servers to inject for this call.

        Returns:
            List of CLI flags (e.g., ["--mcp-config", '{"mcpServers": {...}}'])
        """
        all_servers = list(self.mcp_servers)
        if extra_servers:
            all_servers.extend(extra_servers)

        if not all_servers:
            return []

        # Build MCP config JSON
        mcp_config = {"mcpServers": {server.name: server.to_dict() for server in all_servers}}

        return ["--mcp-config", json.dumps(mcp_config)]

    def _build_claude_permission_flags(
        self,
        on_question: Callable[[str], str] | None,
    ) -> list[str]:
        """Build Claude CLI permission flags based on configuration.

        Maps the adapter's permission_mode to Claude CLI flags. When running
        in deliberate's orchestrated mode, we use bypassPermissions by default
        since agents are isolated in worktrees for safety.

        Args:
            on_question: Optional callback for handling questions.
                Currently not used for interactive Q&A (requires stream mode).

        Returns:
            List of CLI flags for permission handling.
        """
        flags: list[str] = []

        # Use explicit permission_mode if set
        mode = self.permission_mode
        if mode:
            flags.extend(["--permission-mode", mode])
            return flags

        # Default to bypassPermissions since agents run in isolated worktrees
        # This allows MCP tool calls and file edits without prompts
        flags.extend(["--permission-mode", "bypassPermissions"])

        return flags

    def _build_codex_permission_flags(self) -> list[str]:
        """Build Codex permission flags, avoiding conflicts with --full-auto."""
        joined = " ".join(self.command)
        if "--full-auto" in joined:
            return []
        return ["--dangerously-bypass-approvals-and-sandbox"]

    def _build_codex_mcp_flags(
        self,
        extra_servers: list[MCPServerConfig] | None = None,
    ) -> list[str]:
        """Build -c config flags for Codex MCP servers."""
        all_servers = list(self.mcp_servers)
        if extra_servers:
            all_servers.extend(extra_servers)

        if not all_servers:
            return []

        flags = []
        for server in all_servers:
            # Construct TOML-style config overrides
            base_key = f"mcp_servers.{server.name}"

            if server.is_sse:
                flags.extend(["-c", f'{base_key}.type="sse"'])
                flags.extend(["-c", f'{base_key}.url="{server.url}"'])
                if server.headers:
                    # Codex might expect headers as a dictionary
                    # Flatten headers for TOML if simple key-value
                    # syntax: headers = { Auth = "..." }
                    headers_str = ", ".join(f'{k}="{v}"' for k, v in server.headers.items())
                    flags.extend(["-c", f"{base_key}.headers={{ {headers_str} }}"])
            else:
                flags.extend(["-c", f'{base_key}.command="{server.command}"'])
                if server.args:
                    args_str = ", ".join(f'"{arg}"' for arg in server.args)
                    flags.extend(["-c", f"{base_key}.args=[{args_str}]"])
                if server.env:
                    env_str = ", ".join(f'{k}="{v}"' for k, v in server.env.items())
                    flags.extend(["-c", f"{base_key}.env={{ {env_str} }}"])

        return flags

    @property
    def call_count(self) -> int:
        """Get call count."""
        return self._call_count

    def estimate_tokens(self, text: str) -> int:
        """Estimate tokens (~4 chars per token)."""
        return len(text) // 4
