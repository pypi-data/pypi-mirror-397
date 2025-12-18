"""Iterative solving module implementing the meta-pattern.

Key concepts from poetiq-arc-agi-solver:
1. "The prompt is an interface, not the intelligence" - The system engages
   in an iterative problem-solving loop with structured feedback.
2. "Self-auditing" - The system autonomously decides when the solution is
   satisfactory, allowing early termination.

Usage:
    from deliberate.iteration import (
        IterativeSolver,
        IterationConfig,
        SolutionHistory,
        run_iterative_solver,
    )

    # Create solver with custom evaluator
    solver = IterativeSolver(
        agent=my_agent,
        evaluator=TestEvaluator(test_command="pytest"),
        extractor=CodeExtractor("python"),
        feedback_builder=TestFeedbackBuilder(),
        config=IterationConfig(max_iterations=10),
    )

    # Run iterative solving
    result = await solver.solve(
        task="Write a function that...",
        evaluation_context={"working_dir": "/path/to/code"},
    )

    if result.success:
        print(f"Solved in {result.iterations_completed} iterations!")
    else:
        print(f"Best attempt scored {result.final_score:.2f}")
"""

from .feedback import (
    DEFAULT_FEEDBACK_TEMPLATE,
    CompositeFeedbackBuilder,
    DiffFeedbackBuilder,
    FeedbackBuilder,
    StructuredFeedback,
    TestFeedbackBuilder,
    build_iteration_prompt,
)
from .history import SolutionHistory
from .solver import (
    CodeExtractor,
    IterativeSolver,
    PlainExtractor,
    SolutionEvaluator,
    SolutionExtractor,
    TestEvaluator,
    run_iterative_solver,
)
from .types import (
    FeedbackContext,
    IterationConfig,
    IterationResult,
    SolutionAttempt,
    TerminationReason,
)

__all__ = [
    # Types
    "FeedbackContext",
    "IterationConfig",
    "IterationResult",
    "SolutionAttempt",
    "TerminationReason",
    # History
    "SolutionHistory",
    # Feedback
    "FeedbackBuilder",
    "StructuredFeedback",
    "TestFeedbackBuilder",
    "DiffFeedbackBuilder",
    "CompositeFeedbackBuilder",
    "build_iteration_prompt",
    "DEFAULT_FEEDBACK_TEMPLATE",
    # Solver
    "IterativeSolver",
    "SolutionEvaluator",
    "SolutionExtractor",
    "CodeExtractor",
    "PlainExtractor",
    "TestEvaluator",
    "run_iterative_solver",
]
