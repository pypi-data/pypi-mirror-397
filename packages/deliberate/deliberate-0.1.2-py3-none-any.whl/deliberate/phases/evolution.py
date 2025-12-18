"""Evolution phase integrating AlphaEvolve-inspired code evolution into the workflow.

This phase takes a candidate execution result and iteratively evolves it
using evolutionary techniques:
- MAP-elites style population management
- LLM ensemble (fast models for throughput, powerful for quality)
- Diff-based code evolution
- Evaluation cascade for early pruning
"""

from pathlib import Path

from deliberate.adapters.base import ModelAdapter
from deliberate.budget.tracker import BudgetTracker
from deliberate.evolution import (
    DatabaseConfig,
    EvaluationLevel,
    EvolutionConfig,
    EvolutionController,
    EvolutionResult,
    ProgramDatabase,
    TDDEvaluator,
    TDDEvaluatorConfig,
)
from deliberate.git.worktree import WorktreeManager
from deliberate.types import ExecutionResult
from deliberate.verbose_logger import get_verbose_logger


class EvolutionPhase:
    """Evolution phase for iteratively improving code solutions.

    Integrates AlphaEvolve-style evolution into the deliberate workflow:
    1. Seeds database with winning candidate code
    2. Runs evolution loop with LLM ensemble
    3. Returns improved code with metrics
    """

    def __init__(
        self,
        agents: dict[str, ModelAdapter],
        budget_tracker: BudgetTracker,
        worktree_mgr: WorktreeManager | None = None,
        *,
        max_iterations: int = 10,
        target_score: float = 0.95,
        fast_model_ratio: float = 0.7,
        use_powerful_for_champions: bool = True,
        prefer_diffs: bool = True,
        cascade_levels: list[EvaluationLevel] | None = None,
        max_stagnant_iterations: int = 5,
        test_command: str | None = None,
        lint_command: str | None = None,
    ):
        """Initialize the evolution phase.

        Args:
            agents: Dictionary of agent name -> adapter (should include fast and powerful models).
            budget_tracker: Budget tracker for cost management.
            worktree_mgr: Optional worktree manager for isolated execution.
            max_iterations: Maximum evolution iterations.
            target_score: Score threshold to stop evolution.
            fast_model_ratio: Fraction of iterations using fast model.
            use_powerful_for_champions: Use powerful model for top candidates.
            prefer_diffs: Prefer diff-based evolution over full rewrites.
            cascade_levels: Evaluation cascade levels.
            max_stagnant_iterations: Stop after N iterations without improvement.
            test_command: Override test command for evaluation.
            lint_command: Override lint command for evaluation.
        """
        self.agents = agents
        self.budget = budget_tracker
        self.worktree_mgr = worktree_mgr

        # Evolution config
        self.max_iterations = max_iterations
        self.target_score = target_score
        self.fast_model_ratio = fast_model_ratio
        self.use_powerful_for_champions = use_powerful_for_champions
        self.prefer_diffs = prefer_diffs
        self.cascade_levels = cascade_levels or [
            EvaluationLevel.SYNTAX,
            EvaluationLevel.UNIT_FAST,
        ]
        self.max_stagnant_iterations = max_stagnant_iterations
        self.test_command = test_command
        self.lint_command = lint_command

        self._verbose_logger = get_verbose_logger()

    async def run(
        self,
        task: str,
        execution_result: ExecutionResult,
        working_dir: Path,
    ) -> EvolutionResult:
        """Run evolution on a candidate execution result.

        Args:
            task: Original task description.
            execution_result: The execution result to evolve.
            working_dir: Working directory for evaluation.

        Returns:
            EvolutionResult with best evolved code and metrics.
        """
        self._verbose_logger.log_event(
            f"Starting evolution phase with {len(self.agents)} agents",
            "info",
        )

        # Create program database
        db_config = DatabaseConfig(
            max_programs=100,
            num_islands=min(4, len(self.agents)),
            elite_fraction=0.1,  # Top 10% are elite
        )
        database = ProgramDatabase(config=db_config)

        # Create evaluator based on working directory
        evaluator = TDDEvaluator(
            config=TDDEvaluatorConfig(
                working_dir=working_dir,
                test_command=self.test_command,
                lint_command=self.lint_command,
                timeout_seconds=60,
            )
        )

        # Create evolution config
        evo_config = EvolutionConfig(
            max_iterations=self.max_iterations,
            target_score=self.target_score,
            fast_model_ratio=self.fast_model_ratio,
            use_powerful_for_champions=self.use_powerful_for_champions,
            prefer_diffs=self.prefer_diffs,
            cascade_levels=self.cascade_levels,
            max_stagnant_iterations=self.max_stagnant_iterations,
            include_inspirations=2,
            use_evolve_markers=True,
        )

        # Create controller
        controller = EvolutionController(
            database=database,
            agents=self.agents,
            evaluator=evaluator,
            config=evo_config,
            budget_tracker=self.budget,
        )

        # Set up logging callbacks
        def on_iteration(iteration: int, program):
            status = "improved" if program else "no improvement"
            self._verbose_logger.log_event(
                f"Evolution iteration {iteration}: {status}",
                "info" if program else "debug",
            )

        def on_improvement(program):
            self._verbose_logger.log_event(
                f"New best score: {program.metrics.overall_score:.2f}",
                "success",
            )

        controller.on_iteration = on_iteration
        controller.on_improvement = on_improvement

        # Extract seed code from execution result
        seed_code = self._extract_code_from_result(execution_result)

        # Run evolution
        result = await controller.evolve(
            task=task,
            seed_program=seed_code,
            working_dir=working_dir,
        )

        best_score = result.best_program.metrics.overall_score if result.best_program else 0.0
        self._verbose_logger.log_event(
            f"Evolution complete: {result.iterations_completed} iterations, "
            f"{result.programs_valid}/{result.programs_generated} valid, "
            f"best score: {best_score:.2f}",
            "success" if result.success else "info",
        )

        return result

    def _extract_code_from_result(self, result: ExecutionResult) -> str | None:
        """Extract code from an execution result's diff."""
        if result.diff:
            # For now, return the diff as context - the evolution
            # will work on the actual files in the worktree
            return result.diff
        return None


def create_evolution_phase_from_config(
    config,  # EvolutionWorkflowConfig
    agents: dict[str, ModelAdapter],
    budget_tracker: BudgetTracker,
    worktree_mgr: WorktreeManager | None = None,
) -> EvolutionPhase:
    """Factory to create EvolutionPhase from config.

    Args:
        config: EvolutionWorkflowConfig from DeliberateConfig.
        agents: Available model adapters.
        budget_tracker: Budget tracker.
        worktree_mgr: Optional worktree manager.

    Returns:
        Configured EvolutionPhase instance.
    """
    # Filter agents based on evolution config
    evolution_agents = {}
    for name in config.agents:
        if name in agents:
            evolution_agents[name] = agents[name]

    # If no specific agents configured, use all
    if not evolution_agents:
        evolution_agents = agents

    return EvolutionPhase(
        agents=evolution_agents,
        budget_tracker=budget_tracker,
        worktree_mgr=worktree_mgr,
        max_iterations=config.max_iterations,
        target_score=config.target_score,
        fast_model_ratio=config.fast_model_ratio,
        use_powerful_for_champions=config.use_powerful_for_champions,
        prefer_diffs=config.prefer_diffs,
        max_stagnant_iterations=config.max_stagnant_iterations,
        test_command=config.test_command,
        lint_command=config.lint_command,
    )
