"""Shared constants for deliberate."""

# Default strategy profiles shipped out of the box. These overlay onto user config.
DEFAULT_PROFILES = {
    "cheap": {
        "description": "Minimize cost, single shot execution, fast review",
        "workflow": {
            "planning": {"enabled": False},
            "execution": {"parallelism": {"enabled": False}},
            "refinement": {"enabled": False},
        },
        # Use cheapest/fastest model variants
        "agent_overrides": {
            "claude": {"model": "claude-sonnet-4-5-20250514"},
            "gemini": {"model": "gemini-2.0-flash-exp"},
            "codex": {"model": "gpt-5.1-codex-mini"},
        },
    },
    "balanced": {
        "description": "Default trade-off between cost and quality",
        "workflow": {
            "planning": {"enabled": True},
            "refinement": {"enabled": True, "max_iterations": 2},
            "execution": {"validation": {"devcontainer": {"enabled": True}}},
        },
        # Mid-tier models for balance of cost and capability
        "agent_overrides": {
            "claude": {"model": "claude-sonnet-4-5-20250514"},
            "gemini": {"model": "gemini-2.5-pro"},
            "codex": {"model": "gpt-5.1-codex-mini"},
        },
    },
    "powerful": {
        "description": "Exhaustive search, debate, and deep refinement with top-tier models",
        "workflow": {
            "planning": {"debate": {"enabled": True, "rounds": 2}},
            "execution": {
                "parallelism": {"enabled": True, "max_parallel": 3},
                "validation": {"devcontainer": {"enabled": True}},
            },
            "refinement": {"max_iterations": 5, "rereview_all": True},
        },
        # Most powerful model variants
        "agent_overrides": {
            "claude": {"model": "claude-opus-4-5-20251101"},
            "gemini": {"model": "gemini-3.0-pro"},
            "codex": {"model": "gpt-5.2"},
        },
    },
    # Alias for backwards compatibility
    "max_quality": {
        "description": "Alias for 'powerful' profile",
        "workflow": {
            "planning": {"debate": {"enabled": True, "rounds": 2}},
            "execution": {
                "parallelism": {"enabled": True, "max_parallel": 3},
                "validation": {"devcontainer": {"enabled": True}},
            },
            "refinement": {"max_iterations": 5, "rereview_all": True},
        },
        "agent_overrides": {
            "claude": {"model": "claude-opus-4-5-20251101"},
            "gemini": {"model": "gemini-3.0-pro"},
            "codex": {"model": "gpt-5.2"},
        },
    },
}
