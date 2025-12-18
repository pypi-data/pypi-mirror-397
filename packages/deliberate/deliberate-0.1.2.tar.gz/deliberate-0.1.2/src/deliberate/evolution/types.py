"""Type definitions for the evolution module.

Inspired by AlphaEvolve's architecture:
- Programs with multi-dimensional metrics
- Island-based populations for diversity
- Evaluation cascade levels
- Diff blocks for targeted evolution
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any


class EvaluationLevel(Enum):
    """Cascade evaluation levels (from cheapest to most expensive).

    Programs must pass each level before advancing to the next.
    This enables early pruning of bad solutions.
    """

    SYNTAX = auto()  # Parse/compile check (instant)
    LINT = auto()  # Style/lint check (fast)
    UNIT_FAST = auto()  # Fast unit tests (seconds)
    UNIT_FULL = auto()  # Full unit tests (minutes)
    INTEGRATION = auto()  # Integration tests (slower)
    BENCHMARK = auto()  # Performance benchmarks (expensive)


@dataclass
class ProgramMetrics:
    """Multi-dimensional metrics for a program.

    AlphaEvolve optimizes multiple metrics simultaneously.
    This enables MAP-elites style selection across different dimensions.
    """

    # Core correctness metrics
    tests_passed: int = 0
    tests_total: int = 0
    test_score: float = 0.0  # tests_passed / tests_total

    # Quality metrics
    lint_score: float = 1.0  # 0.0 = many issues, 1.0 = clean
    complexity_score: float = 1.0  # Lower cyclomatic complexity = higher score
    coverage_score: float = 0.0  # Test coverage percentage

    # Performance metrics
    runtime_ms: float = float("inf")
    memory_mb: float = float("inf")

    # Code metrics
    lines_of_code: int = 0
    lines_changed: int = 0

    # Evolution metrics
    generation: int = 0
    parent_id: str | None = None

    # Evaluation cascade tracking
    highest_level_passed: EvaluationLevel = EvaluationLevel.SYNTAX
    evaluation_time_ms: float = 0.0

    # Test-specific metrics (for adversarial test programs)
    champion_kill_rate: float = 0.0  # Fraction of champions this test breaks
    is_valid_test: bool = False  # Whether this is a valid test file
    test_cases_generated: int = 0  # Number of test cases in this test file
    covers_edge_cases: list[str] = field(default_factory=list)  # Edge cases covered

    @property
    def overall_score(self) -> float:
        """Compute weighted overall score for ranking."""
        # Correctness is most important
        correctness_weight = 0.6
        quality_weight = 0.2
        performance_weight = 0.2

        # Normalize performance (lower is better, cap at reasonable values)
        if self.runtime_ms < float("inf"):
            runtime_score = max(0.0, 1.0 - (self.runtime_ms / 10000.0))
        else:
            runtime_score = 0.0

        return (
            correctness_weight * self.test_score
            + quality_weight * (self.lint_score * 0.5 + self.coverage_score * 0.5)
            + performance_weight * runtime_score
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "tests_passed": self.tests_passed,
            "tests_total": self.tests_total,
            "test_score": self.test_score,
            "lint_score": self.lint_score,
            "complexity_score": self.complexity_score,
            "coverage_score": self.coverage_score,
            "runtime_ms": self.runtime_ms if self.runtime_ms < float("inf") else None,
            "memory_mb": self.memory_mb if self.memory_mb < float("inf") else None,
            "lines_of_code": self.lines_of_code,
            "lines_changed": self.lines_changed,
            "generation": self.generation,
            "parent_id": self.parent_id,
            "highest_level_passed": self.highest_level_passed.name,
            "evaluation_time_ms": self.evaluation_time_ms,
            "overall_score": self.overall_score,
            # Test-specific metrics
            "champion_kill_rate": self.champion_kill_rate,
            "is_valid_test": self.is_valid_test,
            "test_cases_generated": self.test_cases_generated,
            "covers_edge_cases": self.covers_edge_cases,
        }


@dataclass
class Program:
    """A program in the evolution database.

    Represents both the code artifact and its evaluation metrics.
    """

    id: str
    code: str
    metrics: ProgramMetrics = field(default_factory=ProgramMetrics)

    # Evolution lineage
    parent_ids: list[str] = field(default_factory=list)
    inspiration_ids: list[str] = field(default_factory=list)  # Programs that inspired this one

    # Metadata
    agent: str = ""  # Which LLM generated this
    prompt_template: str = ""  # Which prompt was used
    diff_applied: str | None = None  # The diff that created this from parent

    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    evaluated_at: datetime | None = None

    # Status
    is_valid: bool = False  # Passed at least syntax check
    is_champion: bool = False  # Currently best in its niche

    @property
    def generation(self) -> int:
        """Get generation number from metrics."""
        return self.metrics.generation

    def clone(self, new_id: str) -> "Program":
        """Create a copy with a new ID."""
        return Program(
            id=new_id,
            code=self.code,
            metrics=ProgramMetrics(
                generation=self.metrics.generation + 1,
                parent_id=self.id,
            ),
            parent_ids=[self.id] + self.parent_ids[:4],  # Keep last 5 ancestors
            agent=self.agent,
        )


@dataclass
class DiffBlock:
    """A SEARCH/REPLACE diff block for targeted code evolution.

    Format:
    <<<<<<< SEARCH
    # Original code block to be found and replaced
    =======
    # New code block to replace the original
    >>>>>>> REPLACE
    """

    search: str  # Code to find
    replace: str  # Code to replace with
    line_number: int | None = None  # Optional hint for location
    file_path: str | None = None  # Optional file path for multi-file diffs

    def to_string(self) -> str:
        """Convert to diff format string."""
        return f"""<<<<<<< SEARCH
{self.search}
=======
{self.replace}
>>>>>>> REPLACE"""


@dataclass
class DatabaseConfig:
    """Configuration for the Program Database."""

    # Population settings
    max_programs: int = 1000  # Maximum programs to store
    num_islands: int = 4  # Number of island populations
    migration_rate: float = 0.1  # Rate of cross-island migration

    # Selection settings
    elite_fraction: float = 0.1  # Top fraction to always keep
    selection_temperature: float = 1.0  # Higher = more exploration

    # Diversity settings
    min_edit_distance: int = 10  # Minimum edit distance for diversity
    niche_dimensions: list[str] = field(default_factory=lambda: ["test_score", "runtime_ms", "lines_of_code"])

    # Cleanup settings
    max_age_generations: int = 50  # Remove programs older than this
    cleanup_interval: int = 100  # Cleanup every N additions


@dataclass
class EvolutionConfig:
    """Configuration for the Evolution Controller."""

    # LLM ensemble settings
    fast_model_ratio: float = 0.8  # Use fast model this fraction of the time
    use_powerful_for_champions: bool = True  # Use powerful model for evolving champions

    # Evolution settings
    max_iterations: int = 1000
    max_stagnant_iterations: int = 50  # Stop if no improvement for this many iterations
    target_score: float = 1.0  # Stop if we reach this score

    # Prompt settings
    include_inspirations: int = 3  # Number of inspiration programs in prompt
    include_parent_history: int = 2  # Number of parent generations in prompt
    use_evolve_markers: bool = True  # Use EVOLVE-BLOCK markers

    # Diff settings
    prefer_diffs: bool = True  # Prefer SEARCH/REPLACE over full rewrites
    max_diff_blocks: int = 5  # Max diff blocks per evolution step

    # Evaluation cascade
    enable_cascade: bool = True
    cascade_levels: list[EvaluationLevel] = field(
        default_factory=lambda: [
            EvaluationLevel.SYNTAX,
            EvaluationLevel.LINT,
            EvaluationLevel.UNIT_FAST,
            EvaluationLevel.UNIT_FULL,
        ]
    )

    # Budget limits
    max_tokens: int | None = None
    max_cost_usd: float | None = None
    max_time_seconds: float | None = None


@dataclass
class EvolutionResult:
    """Result of an evolution run."""

    success: bool
    best_program: Program | None
    all_programs: list[Program]

    # Statistics
    iterations_completed: int
    programs_generated: int
    programs_valid: int

    # Timeline
    score_trajectory: list[float]
    generation_timeline: list[int]

    # Resource usage
    total_tokens: int
    total_cost_usd: float
    total_time_seconds: float

    # Termination info
    termination_reason: str
    stagnant_iterations: int

    @property
    def summary(self) -> str:
        """Human-readable summary."""
        status = "SUCCESS" if self.success else "INCOMPLETE"
        best_score = self.best_program.metrics.overall_score if self.best_program else 0.0
        return (
            f"Evolution: {status} after {self.iterations_completed} iterations, "
            f"{self.programs_valid}/{self.programs_generated} valid, "
            f"best score: {best_score:.3f}, reason: {self.termination_reason}"
        )
