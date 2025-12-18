"""Configuration management for deliberate."""

import copy
from enum import Enum
from pathlib import Path
from typing import Literal

import platformdirs
import yaml
from pydantic import BaseModel, Field

from deliberate.constants import DEFAULT_PROFILES


class TriggerPolicy(str, Enum):
    """Policy for handling performance issues.

    Used by the Auto-Tuner to decide what to do when tests pass
    but performance is suboptimal.
    """

    WARN = "warn"  # Log warning but continue
    FAIL = "fail"  # Mark as failure, block acceptance
    EVOLVE = "evolve"  # Trigger evolution mode to optimize


class AgentCostConfig(BaseModel):
    """Cost configuration for an agent."""

    weight: float = 1.0
    tokens_per_dollar: int = 5000


class AgentRuntimeConfig(BaseModel):
    """Runtime configuration for an agent."""

    max_tokens: int = 8000
    timeout_seconds: int = 300


class AgentConfig(BaseModel):
    """Configuration for a single agent."""

    type: Literal["mcp", "cli", "api", "fake"]
    command: list[str] = Field(default_factory=list)
    env: dict[str, str] = Field(default_factory=dict)  # Environment variables for CLI agents
    mcp_endpoint: str | None = None
    model: str | None = None  # For API type agents (or model_id for CLI agents)
    parser: str | None = None  # Explicit parser type for CLI agents (claude, gemini, codex, opencode)
    telemetry_endpoint: str | None = None  # For CLI agents that accept telemetry flags
    telemetry_exporter: str | None = None  # none | otlp-http | otlp-grpc
    telemetry_environment: str | None = None
    telemetry_log_user_prompt: bool | None = None
    permission_mode: str | None = None  # For CLI agents: default, dontAsk, bypassPermissions, acceptEdits, plan
    capabilities: list[str] = Field(default_factory=lambda: ["planner", "executor", "reviewer"])
    behavior: str | None = None  # For fake agents: echo, planner, critic, flaky
    config: AgentRuntimeConfig = Field(default_factory=AgentRuntimeConfig)
    cost: AgentCostConfig = Field(default_factory=AgentCostConfig)


class MCPConfig(BaseModel):
    """MCP server configuration."""

    endpoint: str = "unix:///tmp/mcp-server.sock"
    tools: list[str] = Field(default_factory=lambda: ["fs", "git", "bash", "run_tests"])
    server_host: str = "127.0.0.1"
    server_port: int = 0  # 0 = dynamic port allocation
    disable_auth: bool = False  # Disable bearer token auth (for agents like Codex that can't pass dynamic tokens)
    static_tokens: dict[str, str] = Field(default_factory=dict)  # Pre-shared tokens: agent_name -> token
    static_token_env_var: str = "DELIBERATE_ORCHESTRATOR_TOKEN"  # Env var name for static token


class DebateConfig(BaseModel):
    """Debate configuration for planning phase."""

    enabled: bool = False
    rounds: int = 1
    max_messages_per_agent: int = 3
    turn_timeout_seconds: int = 60


class SelectionConfig(BaseModel):
    """Plan selection configuration."""

    method: Literal["llm_judge", "borda", "first"] = "first"
    judge: str | None = None


class PlanningConfig(BaseModel):
    """Planning phase configuration."""

    enabled: bool = True
    agents: list[str] = Field(default_factory=list)
    debate: DebateConfig = Field(default_factory=DebateConfig)
    selection: SelectionConfig = Field(default_factory=SelectionConfig)


class ParallelismConfig(BaseModel):
    """Execution parallelism configuration."""

    enabled: bool = False
    max_parallel: int = 1


class WorktreeConfig(BaseModel):
    """Worktree configuration for execution."""

    enabled: bool = True
    root: str = ".deliberate/worktrees"
    cleanup: bool = True
    apply_strategy: Literal["merge", "squash", "copy"] = "merge"


class QuestionsConfig(BaseModel):
    """Configuration for handling agent questions during execution."""

    strategy: Literal["prompt_user", "auto_answer", "fail"] = "fail"
    auto_answer_agent: str | None = None
    max_questions: int = 5


class EnvironmentAnalyzerConfig(BaseModel):
    """Configuration for LLM-based environment analysis.

    The environment analyzer uses a small, fast LLM to intelligently detect
    the correct test/lint commands for a project, handling edge cases that
    heuristics miss (monorepos, custom npm scripts, docker-based runners).
    """

    enabled: bool = False  # Disabled by default, uses heuristics
    agent: str | None = None  # Agent name to use for analysis (should be fast/cheap)
    fallback_to_heuristics: bool = True  # Use heuristics if LLM fails
    cache_results: bool = True  # Cache analysis results per project


class DevContainerConfig(BaseModel):
    """Configuration for Dev Container-based validation isolation.

    When enabled, validation commands are executed inside a Dev Container,
    providing isolation from the host system and consistent execution environments.
    """

    enabled: bool = False  # Disabled by default, uses host execution
    auto_detect: bool = True  # Auto-detect .devcontainer/devcontainer.json
    use_devcontainer_cli: bool = True  # Prefer devcontainer CLI over docker exec
    startup_timeout_seconds: int = 300  # Timeout for container startup
    keep_running: bool = True  # Keep container running between executions


class ValidationConfig(BaseModel):
    """Configuration for test validation during execution."""

    enabled: bool = False  # Disabled by default for backward compatibility
    command: str | None = None  # Override auto-detection
    lint_command: str | None = None  # Override lint command auto-detection
    timeout_seconds: int = 300
    run_baseline: bool = True  # Run tests before changes to detect regressions
    fail_on_regression: bool = True  # Block candidates that break existing tests
    required_for_winner: bool = True  # Winner must pass validation (if enabled)
    analyzer: EnvironmentAnalyzerConfig = Field(default_factory=EnvironmentAnalyzerConfig)
    devcontainer: DevContainerConfig = Field(default_factory=DevContainerConfig)


class ExecutionConfig(BaseModel):
    """Execution phase configuration."""

    enabled: bool = True
    agents: list[str] = Field(default_factory=list)
    parallelism: ParallelismConfig = Field(default_factory=ParallelismConfig)
    worktree: WorktreeConfig = Field(default_factory=WorktreeConfig)
    questions: QuestionsConfig = Field(default_factory=QuestionsConfig)
    validation: ValidationConfig = Field(default_factory=ValidationConfig)


class ScoringConfig(BaseModel):
    """Review scoring configuration."""

    criteria: list[str] = Field(default_factory=lambda: ["correctness", "code_quality", "completeness", "risk"])
    scale: str = "1-10"


class CriteriaAnalysisConfig(BaseModel):
    """Dynamic criteria generation configuration."""

    enabled: bool = False
    # TODO should use an type alias or better enum variant:
    agent: str | None = None  # Preferred agent for criteria generation (uses first non-fake if unset)
    max_criteria: int = 5


class AggregationConfig(BaseModel):
    """Vote aggregation configuration."""

    method: Literal["borda", "approval", "weighted_borda"] = "borda"
    min_approval_ratio: float = 0.7
    reject_is_veto: bool = False


class SynthesisConfig(BaseModel):
    """Synthesis configuration for review phase."""

    enabled: bool = False
    rounds: int = 1
    synthesizers: list[str] = Field(default_factory=list)


class ReviewConfig(BaseModel):
    """Review phase configuration."""

    enabled: bool = True
    agents: list[str] = Field(default_factory=list)
    scoring: ScoringConfig = Field(default_factory=ScoringConfig)
    context_analysis: CriteriaAnalysisConfig = Field(default_factory=CriteriaAnalysisConfig)
    aggregation: AggregationConfig = Field(default_factory=AggregationConfig)
    synthesis: SynthesisConfig = Field(default_factory=SynthesisConfig)


class TDDLoopConfig(BaseModel):
    """Configuration for the TDD (Test-Driven Development) inner loop.

    The TDD loop runs BEFORE expensive LLM reviews, using cheap test execution
    to fix obvious issues. This significantly reduces cost by avoiding LLM
    reviews of broken code.

    Workflow:
    1. Lint check (syntax errors)
    2. Run tests
    3. If fail -> feed stderr to agent -> fix -> retry
    4. Only after tests pass (or max iterations) -> LLM review
    """

    enabled: bool = True  # Enabled by default (it saves money!)
    max_fix_iterations: int = 3  # Max test->fail->fix cycles
    lint_before_test: bool = True  # Run linter before tests (catches syntax errors)
    lint_patterns: list[str] = Field(default_factory=lambda: ["**/*.py"])
    require_tests_pass: bool = True  # Block LLM review until tests pass
    test_command: str | None = None  # Override auto-detection
    test_timeout_seconds: int = 300
    lint_timeout_seconds: int = 60


class RefinementConfig(BaseModel):
    """Configuration for the refinement phase."""

    enabled: bool = False  # Disabled by default for backward compatibility

    # Trigger conditions (any condition met triggers refinement)
    min_confidence: float = 0.3  # Trigger if confidence < threshold
    min_winner_score: float = 0.6  # Trigger if winner score < threshold
    trigger_on_revise: bool = True  # Trigger if any reviewer recommends "revise"

    # Iteration controls
    max_iterations: int = 3
    min_improvement_threshold: float = 0.05  # Stop if improvement < x%

    # Candidate selection
    refine_top_n: int = 1  # How many candidates to refine (1 = winner only)

    # Re-review strategy
    rereview_all: bool = False  # If False, only low-scoring reviewers re-review
    rereview_score_threshold: float = 0.5  # Re-review if original score < threshold

    # Budget management
    budget_reserve_pct: float = 0.3  # Reserve 30% of total budget for refinement
    per_iteration_budget_pct: float = 0.5  # Each iteration can use 50% of reserve

    # Behavior on regression
    revert_on_regression: bool = True  # Revert to previous iteration if scores decrease
    allow_score_decrease: float = 0.1  # Allow up to 10% score decrease before reverting

    # TDD inner loop configuration
    tdd: TDDLoopConfig = Field(default_factory=TDDLoopConfig)


class EvolutionWorkflowConfig(BaseModel):
    """Configuration for the evolution phase (AlphaEvolve-inspired).

    The evolution phase iteratively improves code solutions using:
    - MAP-elites style population management with island-based diversity
    - LLM ensemble (fast models for throughput, powerful for quality)
    - Diff-based code evolution (SEARCH/REPLACE blocks)
    - Evaluation cascade for early pruning of bad solutions
    - Multi-metric optimization (correctness, quality, performance)
    """

    enabled: bool = False  # Disabled by default

    # Agents to use for evolution (should include fast and powerful models)
    agents: list[str] = Field(default_factory=list)

    # Evolution parameters
    max_iterations: int = 10  # Maximum evolution iterations
    target_score: float = 0.95  # Stop when this score is reached
    fast_model_ratio: float = 0.7  # Fraction using fast model (throughput)
    use_powerful_for_champions: bool = True  # Use powerful model for top candidates

    # Evolution strategy
    prefer_diffs: bool = True  # Use SEARCH/REPLACE over full rewrites
    max_stagnant_iterations: int = 5  # Stop after N iterations without improvement

    # Test/validation commands
    test_command: str | None = None  # Override test command
    lint_command: str | None = None  # Override lint command

    # Trigger conditions
    trigger_on_low_confidence: bool = True  # Evolve if review confidence < threshold
    min_confidence_threshold: float = 0.5  # Confidence threshold for triggering
    trigger_on_test_failure: bool = True  # Evolve if tests fail

    # Budget management
    budget_reserve_pct: float = 0.2  # Reserve 20% of budget for evolution


class AutoTunerConfig(BaseModel):
    """Configuration for dynamic mode switching based on performance.

    The Auto-Tuner monitors test execution performance and can automatically
    trigger evolution mode when correctness passes but performance is suboptimal.

    This enables "optimize until good enough" workflows where the system:
    1. First ensures correctness via standard execution/review
    2. Then optimizes performance via evolution if thresholds are exceeded
    """

    enabled: bool = False  # Disabled by default

    # Policy for handling slow execution
    on_slow_execution: TriggerPolicy = TriggerPolicy.WARN
    on_high_memory: TriggerPolicy = TriggerPolicy.WARN

    # Performance thresholds
    latency_threshold_ms: float = 500.0  # Flag tests slower than this
    memory_threshold_mb: float = 512.0  # Flag memory usage above this

    # Evolution iteration limits (to prevent infinite loops)
    max_evolution_attempts: int = 3  # Max times to trigger evolution for perf
    max_total_iterations: int = 10  # Hard cap across all modes

    # Optimization target priority
    optimization_target: Literal["latency", "memory", "token_count"] = "latency"

    # Integration with ValidationRunner
    propagate_to_runner: bool = True  # Pass thresholds to runner


class WorkflowConfig(BaseModel):
    """Workflow configuration."""

    planning: PlanningConfig = Field(default_factory=PlanningConfig)
    execution: ExecutionConfig = Field(default_factory=ExecutionConfig)
    review: ReviewConfig = Field(default_factory=ReviewConfig)
    refinement: RefinementConfig = Field(default_factory=RefinementConfig)
    evolution: EvolutionWorkflowConfig = Field(default_factory=EvolutionWorkflowConfig)
    auto_tuner: AutoTunerConfig = Field(default_factory=AutoTunerConfig)
    require_tests: bool = False


class BudgetConfig(BaseModel):
    """Budget limits configuration."""

    max_total_tokens: int = 500000
    max_cost_usd: float = 10.0
    max_requests_per_agent: int = 30


class TimeConfig(BaseModel):
    """Time limits configuration."""

    hard_timeout_minutes: int = 45
    phase_timeouts: dict[str, int] = Field(default_factory=lambda: {"planning": 10, "execution": 25, "review": 10})


class SafetyConfig(BaseModel):
    """Safety configuration."""

    require_human_approval: bool = False
    dry_run: bool = False


class LimitsConfig(BaseModel):
    """Resource limits configuration."""

    budget: BudgetConfig = Field(default_factory=BudgetConfig)
    time: TimeConfig = Field(default_factory=TimeConfig)
    safety: SafetyConfig = Field(default_factory=SafetyConfig)


class CIOutputConfig(BaseModel):
    """CI output configuration."""

    format: Literal["json", "markdown", "patch"] = "json"
    path: str = "deliberate-result.json"


class CIConfig(BaseModel):
    """CI mode configuration."""

    enabled: bool = False
    mode: Literal["suggest_only", "auto_apply"] = "suggest_only"
    output: CIOutputConfig = Field(default_factory=CIOutputConfig)
    fail_on: list[str] = Field(default_factory=lambda: ["test_failure", "low_confidence", "budget_exceeded"])


class TrackingConfig(BaseModel):
    """Agent performance tracking configuration."""

    enabled: bool = True  # Enabled by default
    db_path: str | None = None  # If None, uses user data directory


class TelemetryConfig(BaseModel):
    """Global telemetry configuration."""

    endpoint: str | None = None
    exporter: str | None = None  # otlp-http | otlp-grpc | none
    environment: str | None = None
    log_user_prompt: bool | None = None


class ProfileConfig(BaseModel):
    """Named configuration profile for workflow execution."""

    description: str = "Custom profile"
    workflow: WorkflowConfig | None = None
    agent_overrides: dict[str, dict] = Field(default_factory=dict)
    limits: LimitsConfig | None = None


class DeliberateConfig(BaseModel):
    """Root configuration for deliberate."""

    agents: dict[str, AgentConfig] = Field(default_factory=dict)
    mcp: MCPConfig = Field(default_factory=MCPConfig)
    workflow: WorkflowConfig = Field(default_factory=WorkflowConfig)
    limits: LimitsConfig = Field(default_factory=LimitsConfig)
    ci: CIConfig = Field(default_factory=CIConfig)
    tracking: TrackingConfig = Field(default_factory=TrackingConfig)
    telemetry: TelemetryConfig = Field(default_factory=TelemetryConfig)
    profiles: dict[str, ProfileConfig] = Field(default_factory=dict)
    default_profile: str = "balanced"

    @classmethod
    def load(cls, path: str | Path) -> "DeliberateConfig":
        """Load configuration from a YAML file."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")

        data = yaml.safe_load(path.read_text())
        return cls.model_validate(data)

    @classmethod
    def get_user_config_dir(cls) -> Path:
        """Get the OS-specific user configuration directory for deliberate."""
        return Path(platformdirs.user_config_dir("deliberate", appauthor=False))

    @classmethod
    def get_config_search_paths(cls) -> list[Path]:
        """Get list of paths to search for configuration files, in priority order.

        Priority:
        1. Current directory .deliberate.yaml
        2. Current directory deliberate.yaml
        3. User config directory ~/.deliberate/config.yaml (OS-specific)
        """
        user_config_dir = cls.get_user_config_dir()
        return [
            Path(".deliberate.yaml"),
            Path("deliberate.yaml"),
            user_config_dir / "config.yaml",
        ]

    @classmethod
    def load_or_default(cls, path: str | Path | None = None) -> "DeliberateConfig":
        """Load configuration from file or return default config.

        If path is None, searches in order:
        1. ./.deliberate.yaml (current directory)
        2. ./deliberate.yaml (current directory)
        3. ~/.deliberate/config.yaml (OS-specific user config directory)

        If no config file is found, returns default configuration.

        Args:
            path: Optional explicit path to configuration file

        Returns:
            Loaded configuration or default config
        """
        if path is not None:
            # Explicit path provided - check if it exists
            path = Path(path)
            if path.exists():
                return cls.load(path)
            # Explicit path doesn't exist, return default
            return cls()

        # Search for config files in priority order
        for candidate in cls.get_config_search_paths():
            if candidate.exists():
                return cls.load(candidate)

        # Return default configuration
        return cls()

    def get_agent(self, name: str) -> AgentConfig:
        """Get agent configuration by name."""
        if name not in self.agents:
            raise KeyError(f"Agent not found: {name}")
        return self.agents[name]

    def get_planners(self) -> list[str]:
        """Get list of agents with planner capability."""
        return [
            name
            for name, cfg in self.agents.items()
            if "planner" in cfg.capabilities and name in self.workflow.planning.agents
        ]

    def get_executors(self) -> list[str]:
        """Get list of agents with executor capability."""
        return [
            name
            for name, cfg in self.agents.items()
            if "executor" in cfg.capabilities and name in self.workflow.execution.agents
        ]

    def get_reviewers(self) -> list[str]:
        """Get list of agents with reviewer capability."""
        return [
            name
            for name, cfg in self.agents.items()
            if "reviewer" in cfg.capabilities and name in self.workflow.review.agents
        ]

    def apply_profile(self, profile_name: str) -> "DeliberateConfig":
        """Return a new config instance with the profile applied."""
        profile: ProfileConfig

        if profile_name in self.profiles:
            profile = self.profiles[profile_name]
        elif profile_name in DEFAULT_PROFILES:
            profile = ProfileConfig.model_validate(DEFAULT_PROFILES[profile_name])
        else:
            raise ValueError(f"Unknown profile: {profile_name}")

        base_dict = self.model_dump()
        merged = copy.deepcopy(base_dict)

        # Workflow overrides
        if profile.workflow:
            merged["workflow"] = _deep_merge_dicts(
                merged.get("workflow", {}),
                profile.workflow.model_dump(exclude_defaults=True),
            )

        # Limits overrides
        if profile.limits:
            merged["limits"] = _deep_merge_dicts(
                merged.get("limits", {}),
                profile.limits.model_dump(exclude_defaults=True),
            )

        # Agent overrides (per-agent partial config) - only apply to existing agents
        if profile.agent_overrides:
            merged.setdefault("agents", {})
            for agent_name, overrides in profile.agent_overrides.items():
                if agent_name in merged["agents"]:
                    current = merged["agents"][agent_name]
                    merged["agents"][agent_name] = _deep_merge_dicts(current, overrides)

        return DeliberateConfig.model_validate(merged)


# todo move to util and test
def _deep_merge_dicts(base: dict, overrides: dict) -> dict:
    """Recursively merge override dict into base dict without mutating inputs."""
    result = copy.deepcopy(base)
    for key, value in overrides.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge_dicts(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result
