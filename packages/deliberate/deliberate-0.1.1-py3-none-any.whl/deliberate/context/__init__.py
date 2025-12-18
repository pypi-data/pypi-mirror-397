"""Execution context for the jury workflow.

Provides shared services and state for the workflow execution.
"""

from dataclasses import dataclass
from pathlib import Path

from deliberate.budget.tracker import BudgetTracker
from deliberate.config import DeliberateConfig
from deliberate.git.worktree import WorktreeManager


@dataclass
class JuryContext:
    """Shared context for jury workflow execution."""

    repo_root: Path
    budget: BudgetTracker
    config: DeliberateConfig
    worktree_mgr: WorktreeManager
