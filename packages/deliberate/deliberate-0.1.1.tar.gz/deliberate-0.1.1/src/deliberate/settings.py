"""Pydantic settings for environment-based configuration."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AgentSettings(BaseSettings):
    """Environment-based settings for a specific agent.

    Each agent can have its own environment variables loaded from
    the system environment with agent-specific prefixes.
    """

    model_config = SettingsConfigDict(
        env_prefix="",  # Will be set dynamically per agent
        case_sensitive=False,
        extra="allow",  # Allow extra environment variables
    )


class ClaudeSettings(AgentSettings):
    """Settings for Claude CLI agent."""

    model_config = SettingsConfigDict(
        env_prefix="CLAUDE_",
        case_sensitive=False,
    )


class GeminiSettings(AgentSettings):
    """Settings for Gemini CLI agent."""

    api_key: str = Field(default="", description="Gemini API key")

    model_config = SettingsConfigDict(
        env_prefix="GEMINI_",
        case_sensitive=False,
    )


class CodexSettings(AgentSettings):
    """Settings for Codex CLI agent."""

    model_config = SettingsConfigDict(
        env_prefix="CODEX_",
        case_sensitive=False,
    )


class OpenCodeSettings(AgentSettings):
    """Settings for OpenCode CLI agent."""

    model_config = SettingsConfigDict(
        env_prefix="OPENCODE_",
        case_sensitive=False,
    )


class DeliberateSettings(BaseSettings):
    """Global settings for Deliberate."""

    # Agent settings loaded dynamically
    claude: ClaudeSettings = Field(default_factory=ClaudeSettings)
    gemini: GeminiSettings = Field(default_factory=GeminiSettings)
    codex: CodexSettings = Field(default_factory=CodexSettings)
    opencode: OpenCodeSettings = Field(default_factory=OpenCodeSettings)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


def get_agent_env_dict(agent_name: str, settings: DeliberateSettings | None = None) -> dict[str, str]:
    """Get environment variables for a specific agent.

    Args:
        agent_name: Name of the agent (claude, gemini, codex, opencode)
        settings: Optional settings instance (creates new one if not provided)

    Returns:
        Dictionary of environment variables for the agent
    """
    if settings is None:
        settings = DeliberateSettings()

    agent_settings_map = {
        "claude": settings.claude,
        "gemini": settings.gemini,
        "codex": settings.codex,
        "opencode": settings.opencode,
    }

    agent_settings = agent_settings_map.get(agent_name.lower())
    if agent_settings is None:
        return {}

    # Convert pydantic model to dict of environment variables
    env_dict = {}
    for field_name, field_value in agent_settings.model_dump().items():
        if field_value:  # Only include non-empty values
            # Convert to environment variable format
            env_var_name = f"{agent_name.upper()}_{field_name.upper()}"
            env_dict[env_var_name] = str(field_value)

    return env_dict
