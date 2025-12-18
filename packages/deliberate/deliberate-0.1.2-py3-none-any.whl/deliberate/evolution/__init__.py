"""Evolution module implementing AlphaEvolve-inspired code evolution.

Key concepts from AlphaEvolve:
1. Program Database - MAP-elites style storage with island-based populations
2. LLM Ensemble - Fast models for throughput, powerful models for quality
3. Diff-based Evolution - SEARCH/REPLACE blocks for targeted code changes
4. Evaluation Cascade - Progressive test difficulty for early pruning
5. Multi-metric Optimization - Optimize multiple scores simultaneously

Usage:
    from deliberate.evolution import (
        ProgramDatabase,
        EvolutionController,
        EvolutionConfig,
        apply_diff,
        parse_diff,
    )

    # Create database and controller
    database = ProgramDatabase(config=DatabaseConfig())
    controller = EvolutionController(
        database=database,
        agents={"flash": flash_adapter, "pro": pro_adapter},
        evaluator=test_evaluator,
        config=EvolutionConfig(),
    )

    # Run evolution
    result = await controller.evolve(
        seed_program="def solve(): pass",
        task="Implement a sorting algorithm",
        max_iterations=100,
    )
"""

from .adversarial import (
    AdversarialConfig,
    AdversarialResult,
    AdversarialTestLoop,
    CycleResult,
)
from .controller import EvaluationResult, Evaluator, EvolutionController
from .database import IslandPopulation, ProgramDatabase
from .diff_evolution import (
    DiffParser,
    apply_diff,
    create_evolve_markers,
    extract_evolve_regions,
    parse_diff,
)
from .evaluator import InMemoryEvaluator, TDDEvaluator, TDDEvaluatorConfig
from .prompt_builder import PromptBuilder
from .test_evaluator import (
    KillResult,
    TestValidationEvaluator,
    TestValidationLevel,
    TestValidationResult,
)
from .test_prompt_builder import TestGenerationPromptBuilder
from .types import (
    DatabaseConfig,
    DiffBlock,
    EvaluationLevel,
    EvolutionConfig,
    EvolutionResult,
    Program,
    ProgramMetrics,
)

__all__ = [
    # Types
    "Program",
    "ProgramMetrics",
    "EvolutionConfig",
    "DatabaseConfig",
    "EvaluationLevel",
    "DiffBlock",
    "EvolutionResult",
    # Database
    "ProgramDatabase",
    "IslandPopulation",
    # Diff Evolution
    "apply_diff",
    "parse_diff",
    "create_evolve_markers",
    "extract_evolve_regions",
    "DiffParser",
    # Controller
    "EvolutionController",
    "Evaluator",
    "EvaluationResult",
    # Prompt Builder
    "PromptBuilder",
    # Evaluators
    "TDDEvaluator",
    "TDDEvaluatorConfig",
    "InMemoryEvaluator",
    # Test Generation
    "TestGenerationPromptBuilder",
    "TestValidationEvaluator",
    "TestValidationLevel",
    "TestValidationResult",
    "KillResult",
    # Adversarial Loop
    "AdversarialTestLoop",
    "AdversarialConfig",
    "AdversarialResult",
    "CycleResult",
]
