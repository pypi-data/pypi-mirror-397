"""Direct API adapter using LiteLLM."""

import time
from dataclasses import dataclass, field
from typing import Any, Callable

from deliberate.adapters.base import AdapterResponse, ModelAdapter
from deliberate.adapters.cli_adapter import MCPServerConfig
from deliberate.settings import DeliberateSettings, get_agent_env_dict
from deliberate.tracing.setup import get_tracer

try:
    import litellm
    from litellm import acompletion

    HAS_LITELLM = True
except ImportError:
    HAS_LITELLM = False


@dataclass
class APIAdapter(ModelAdapter):
    """Adapter for direct API calls via LiteLLM.

    Supports OpenAI, Anthropic, Gemini, etc. via a unified interface.
    """

    name: str
    model: str
    env: dict[str, str] = field(default_factory=dict)
    timeout_seconds: int = 300
    config: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not HAS_LITELLM:
            raise ImportError("litellm is required for APIAdapter. Install with 'pip install litellm'")

        # Configure litellm if needed
        litellm.drop_params = True  # Auto-drop unsupported params

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
        """Make a completion call."""
        start = time.monotonic()

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        tracer = get_tracer()
        with tracer.start_as_current_span("api.call") as span:
            span.set_attribute("gen_ai.system", "litellm")
            span.set_attribute("gen_ai.request.model", self.model)

            try:
                # Merge env vars for API keys
                merged_env = self._get_env()
                for k, v in merged_env.items():
                    # LiteLLM looks for specific env vars (OPENAI_API_KEY etc)
                    # We temporarily set them in os.environ context if needed,
                    # but litellm typically reads from os.environ.
                    # For thread safety, passing api_key param is better if we can map it,
                    # but litellm handles many providers.
                    # Simple approach: assume standard env vars are set in process or passed in env
                    pass

                # If specific keys are in env, we might need to pass them to acompletion
                # but commonly users set OPENAI_API_KEY globally.
                # Let's trust litellm's env var detection for now.

                response = await acompletion(
                    model=self.model,
                    messages=messages,
                    max_tokens=max_tokens or self.config.get("max_tokens", 4096),
                    temperature=temperature,
                    timeout=self.timeout_seconds,
                    **self._get_provider_params(),
                )

                content = response.choices[0].message.content or ""
                usage = response.usage

                total_tokens = usage.total_tokens if usage else 0
                float(response._hidden_params.get("response_cost", 0.0))

                span.set_attribute("gen_ai.response.content_length", len(content))
                span.set_attribute("gen_ai.usage.total_tokens", total_tokens)

                return AdapterResponse(
                    content=content,
                    token_usage=total_tokens,
                    duration_seconds=time.monotonic() - start,
                    raw_response=response.model_dump(),
                    stdout=None,
                )

            except Exception as e:
                span.record_exception(e)
                raise RuntimeError(f"API call failed: {e}") from e

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
        """Run agentic task.

        For direct API, 'agentic' means a robust system-prompted loop or
        ReAct-style execution. Since LiteLLM is stateless, we treat this
        similarly to a standard call but with stronger system instructions
        and potentially tool use if we implemented it.

        For now, we map this to a direct call with an 'agentic' system prompt.
        Future: Implement actual tool loops with litellm tool calling.
        """
        system = (
            "You are an expert software engineer. "
            "Execute the requested task autonomously. "
            "Return the result in a clear, structured format."
        )

        return await self.call(
            prompt=task,
            system=system,
            max_tokens=self.config.get("max_tokens", 8000),
            working_dir=working_dir,
        )

    def _get_env(self) -> dict[str, str]:
        """Get merged environment variables."""
        merged_env = self.env.copy()
        try:
            settings = DeliberateSettings()
            agent_env = get_agent_env_dict(self.name, settings)
            merged_env.update(agent_env)
        except Exception:
            pass
        return merged_env

    def _get_provider_params(self) -> dict[str, Any]:
        """Get provider-specific parameters."""
        # Add logic here if specific models need specific params (e.g. top_k)
        return {}

    def estimate_tokens(self, text: str) -> int:
        """Estimate tokens using litellm tokenizer if possible."""
        try:
            return litellm.token_counter(model=self.model, text=text)
        except Exception:
            return len(text) // 4
