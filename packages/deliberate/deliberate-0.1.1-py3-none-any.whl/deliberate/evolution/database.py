"""Program Database with MAP-elites style storage.

Implements AlphaEvolve's Program Database concept:
- Multiple island populations for diversity
- MAP-elites style selection across metric dimensions
- Probabilistic sampling for parent selection
- Migration between islands for cross-pollination

Now with optional DuckDB persistence via SolutionStore (Phase 1.3 of Blackboard).
"""

from __future__ import annotations

import logging
import random
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Iterator

from .types import DatabaseConfig, Program, ProgramMetrics

if TYPE_CHECKING:
    from deliberate.tracking.solution_store import SolutionRecord, SolutionStore

logger = logging.getLogger(__name__)


@dataclass
class IslandPopulation:
    """A single island in the population.

    Islands evolve semi-independently, with occasional migration
    to share successful innovations across the population.
    """

    id: int
    programs: dict[str, Program] = field(default_factory=dict)
    champions: list[str] = field(default_factory=list)  # IDs of best programs

    # Statistics
    total_added: int = 0
    total_removed: int = 0
    best_score: float = 0.0
    average_score: float = 0.0

    def add(self, program: Program) -> None:
        """Add a program to this island."""
        self.programs[program.id] = program
        self.total_added += 1
        self._update_stats()

    def remove(self, program_id: str) -> Program | None:
        """Remove and return a program from this island."""
        program = self.programs.pop(program_id, None)
        if program:
            self.total_removed += 1
            if program_id in self.champions:
                self.champions.remove(program_id)
            self._update_stats()
        return program

    def get(self, program_id: str) -> Program | None:
        """Get a program by ID."""
        return self.programs.get(program_id)

    def _update_stats(self) -> None:
        """Update island statistics."""
        if not self.programs:
            self.best_score = 0.0
            self.average_score = 0.0
            return

        scores = [p.metrics.overall_score for p in self.programs.values()]
        self.best_score = max(scores)
        self.average_score = sum(scores) / len(scores)

        # Update champions (top 3)
        sorted_programs = sorted(self.programs.values(), key=lambda p: p.metrics.overall_score, reverse=True)
        self.champions = [p.id for p in sorted_programs[:3]]

    def sample(
        self,
        n: int = 1,
        temperature: float = 1.0,
        exclude: set[str] | None = None,
        rng: random.Random | None = None,
    ) -> list[Program]:
        """Sample programs from this island using softmax selection.

        Args:
            n: Number of programs to sample.
            temperature: Sampling temperature (higher = more random).
            exclude: Program IDs to exclude from sampling.
            rng: Random number generator for reproducibility.

        Returns:
            List of sampled programs.
        """
        if not self.programs:
            return []

        rng = rng or random.Random()
        exclude = exclude or set()

        eligible = [p for p in self.programs.values() if p.id not in exclude]
        if not eligible:
            return []

        # Compute softmax probabilities
        scores = [p.metrics.overall_score for p in eligible]
        if temperature <= 0:
            # Greedy selection
            sorted_eligible = sorted(eligible, key=lambda p: p.metrics.overall_score, reverse=True)
            return sorted_eligible[:n]

        # Apply temperature and softmax
        max_score = max(scores) if scores else 0
        exp_scores = [pow(2.71828, (s - max_score) / temperature) for s in scores]
        total = sum(exp_scores)
        probabilities = [e / total for e in exp_scores]

        # Sample without replacement
        sampled = []
        remaining_indices = list(range(len(eligible)))
        remaining_probs = probabilities.copy()

        for _ in range(min(n, len(eligible))):
            if not remaining_indices:
                break

            # Renormalize probabilities
            total_prob = sum(remaining_probs)
            if total_prob <= 0:
                break
            norm_probs = [p / total_prob for p in remaining_probs]

            # Sample one
            r = rng.random()
            cumsum = 0.0
            chosen_idx = 0
            for i, prob in enumerate(norm_probs):
                cumsum += prob
                if r <= cumsum:
                    chosen_idx = i
                    break

            # Get the program and remove from candidates
            actual_idx = remaining_indices[chosen_idx]
            sampled.append(eligible[actual_idx])
            remaining_indices.pop(chosen_idx)
            remaining_probs.pop(chosen_idx)

        return sampled

    def __len__(self) -> int:
        return len(self.programs)

    def __iter__(self) -> Iterator[Program]:
        return iter(self.programs.values())


class ProgramDatabase:
    """Database for storing and sampling programs during evolution.

    Implements MAP-elites style storage:
    - Programs are stored in "niches" based on behavioral characteristics
    - Each niche keeps only the best program for that behavioral profile
    - This maintains diversity while focusing on quality

    Also implements island-based populations:
    - Multiple semi-independent populations evolve in parallel
    - Periodic migration shares innovations across islands

    Optionally backed by DuckDB persistence via SolutionStore:
    - In-memory structures remain for fast hot-loop sampling
    - Batch writes (every N additions) to reduce disk I/O
    - Checkpoint persistence on champion updates
    - Explicit flush() for final persistence
    """

    # Batch size for async persistence
    PERSISTENCE_BATCH_SIZE = 10

    def __init__(
        self,
        config: DatabaseConfig | None = None,
        seed: int = 42,
        solution_store: SolutionStore | None = None,
        task_hash: str | None = None,
        load_champions: bool = True,
    ):
        """Initialize the Program Database.

        Args:
            config: Database configuration.
            seed: Random seed for reproducibility.
            solution_store: Optional SolutionStore for DuckDB persistence.
            task_hash: Task hash for filtering solutions (required if solution_store is set).
            load_champions: Whether to load champions from store on init.
        """
        self.config = config or DatabaseConfig()
        self.rng = random.Random(seed)
        self._solution_store = solution_store
        self._task_hash = task_hash

        # Island populations
        self.islands: list[IslandPopulation] = [IslandPopulation(id=i) for i in range(self.config.num_islands)]

        # Global tracking
        self._all_program_ids: set[str] = set()
        self._best_program: Program | None = None
        self._generation: int = 0
        self._additions_since_cleanup: int = 0

        # MAP-elites niches (niche_key -> program_id)
        self._niches: dict[str, str] = {}

        # Pending writes buffer for batch persistence
        self._pending_writes: list[Program] = []

        # Load champions from store if available
        if solution_store and task_hash and load_champions:
            self._load_from_store()

    def add(self, program: Program, island_id: int | None = None) -> bool:
        """Add a program to the database.

        Args:
            program: The program to add.
            island_id: Specific island to add to (random if None).

        Returns:
            True if the program was added, False if rejected.
        """
        # Check if already exists
        if program.id in self._all_program_ids:
            return False

        # Validate program
        if not program.is_valid:
            return False

        # Select island
        if island_id is None:
            island_id = self.rng.randint(0, len(self.islands) - 1)
        island = self.islands[island_id]

        # Check niche (MAP-elites style)
        niche_key = self._compute_niche_key(program)
        existing_id = self._niches.get(niche_key)

        if existing_id:
            # Compare with existing program in this niche
            existing = self._get_program_by_id(existing_id)
            if existing and existing.metrics.overall_score >= program.metrics.overall_score:
                # Existing program is better, reject new one
                return False
            # New program is better, remove old one
            self._remove_program(existing_id)

        # Add to island
        island.add(program)
        self._all_program_ids.add(program.id)
        self._niches[niche_key] = program.id

        # Track if this is a new champion
        was_champion_update = False

        # Update best program
        if self._best_program is None or program.metrics.overall_score > self._best_program.metrics.overall_score:
            self._best_program = program
            was_champion_update = True

        # Cleanup if needed
        self._additions_since_cleanup += 1
        if self._additions_since_cleanup >= self.config.cleanup_interval:
            self._cleanup()

        # Queue for persistence
        if self._solution_store and self._task_hash:
            self._pending_writes.append(program)
            # Checkpoint immediately on champion update
            if was_champion_update:
                self._flush_pending()
            # Otherwise batch writes
            elif len(self._pending_writes) >= self.PERSISTENCE_BATCH_SIZE:
                self._flush_pending()

        return True

    def sample(
        self,
        n_parents: int = 1,
        n_inspirations: int = 0,
        prefer_champions: bool = True,
    ) -> tuple[list[Program], list[Program]]:
        """Sample parent and inspiration programs for evolution.

        Args:
            n_parents: Number of parent programs to sample.
            n_inspirations: Number of inspiration programs to sample.
            prefer_champions: Whether to prefer champion programs.

        Returns:
            Tuple of (parents, inspirations).
        """
        parents = []
        inspirations = []

        if not self._all_program_ids:
            return parents, inspirations

        # Sample parents (prefer champions from random islands)
        used_ids: set[str] = set()

        for _ in range(n_parents):
            found = False

            if prefer_champions:
                # Try to get a champion first from shuffled islands
                shuffled_islands = list(self.islands)
                self.rng.shuffle(shuffled_islands)
                for island in shuffled_islands:
                    if island.champions:
                        unused_champions = [cid for cid in island.champions if cid not in used_ids]
                        if unused_champions:
                            champion_id = self.rng.choice(unused_champions)
                            program = island.get(champion_id)
                            if program:
                                parents.append(program)
                                used_ids.add(program.id)
                                found = True
                                break

            if not found:
                # Fall back to sampling from all islands
                shuffled_islands = list(self.islands)
                self.rng.shuffle(shuffled_islands)
                for island in shuffled_islands:
                    sampled = island.sample(
                        n=1,
                        temperature=self.config.selection_temperature,
                        exclude=used_ids,
                        rng=self.rng,
                    )
                    if sampled:
                        parents.append(sampled[0])
                        used_ids.add(sampled[0].id)
                        break

        # Sample inspirations (diverse programs from different niches)
        for _ in range(n_inspirations):
            # Sample from different islands for diversity
            shuffled_islands = list(self.islands)
            self.rng.shuffle(shuffled_islands)
            for island in shuffled_islands:
                sampled = island.sample(
                    n=1,
                    temperature=self.config.selection_temperature * 1.5,  # More random
                    exclude=used_ids,
                    rng=self.rng,
                )
                if sampled:
                    inspirations.append(sampled[0])
                    used_ids.add(sampled[0].id)
                    break

        return parents, inspirations

    def get_best(self) -> Program | None:
        """Get the best program in the database."""
        return self._best_program

    def get_champions(self, n: int = 10) -> list[Program]:
        """Get top N programs across all islands."""
        all_champions = []
        for island in self.islands:
            for champion_id in island.champions:
                program = island.get(champion_id)
                if program:
                    all_champions.append(program)

        # Sort by score and return top N
        all_champions.sort(key=lambda p: p.metrics.overall_score, reverse=True)
        return all_champions[:n]

    def migrate(self) -> int:
        """Perform migration between islands.

        Copies champion programs from one island to another.

        Returns:
            Number of programs migrated.
        """
        if len(self.islands) < 2:
            return 0

        migrations = 0
        for source_island in self.islands:
            if self.rng.random() > self.config.migration_rate:
                continue

            if not source_island.champions:
                continue

            # Select target island (different from source)
            target_islands = [i for i in self.islands if i.id != source_island.id]
            if not target_islands:
                continue
            target_island = self.rng.choice(target_islands)

            # Migrate a champion
            champion_id = self.rng.choice(source_island.champions)
            program = source_island.get(champion_id)
            if program:
                # Create a copy with new ID for the target island
                new_id = f"{program.id}_mig_{target_island.id}"
                if new_id not in self._all_program_ids:
                    migrated = program.clone(new_id)
                    migrated.is_valid = True
                    if self.add(migrated, island_id=target_island.id):
                        migrations += 1

        return migrations

    def _compute_niche_key(self, program: Program) -> str:
        """Compute the niche key for a program.

        The niche is determined by discretizing the program's metrics
        into buckets, similar to MAP-elites behavioral characterization.
        """
        parts = []
        metrics = program.metrics

        for dim in self.config.niche_dimensions:
            value = getattr(metrics, dim, 0)
            if isinstance(value, float):
                # Handle infinity values
                if value == float("inf") or value == float("-inf"):
                    bucket = 9 if value == float("inf") else 0
                else:
                    # Discretize float values into 10 buckets
                    bucket = min(9, max(0, int(value * 10)))
            else:
                # Use value directly for integers
                bucket = value % 100
            parts.append(f"{dim}:{bucket}")

        return "|".join(parts)

    def _get_program_by_id(self, program_id: str) -> Program | None:
        """Find a program by ID across all islands."""
        for island in self.islands:
            program = island.get(program_id)
            if program:
                return program
        return None

    def _remove_program(self, program_id: str) -> bool:
        """Remove a program from the database."""
        for island in self.islands:
            if island.get(program_id):
                island.remove(program_id)
                self._all_program_ids.discard(program_id)
                return True
        return False

    def _cleanup(self) -> None:
        """Clean up old or low-quality programs."""
        self._additions_since_cleanup = 0

        if len(self._all_program_ids) <= self.config.max_programs:
            return

        # Remove oldest programs that aren't champions
        programs_to_remove = []

        for island in self.islands:
            non_champions = [
                p
                for p in island
                if p.id not in island.champions and self._generation - p.generation > self.config.max_age_generations
            ]
            programs_to_remove.extend([p.id for p in non_champions])

        # If still over limit, remove lowest scoring
        if len(self._all_program_ids) - len(programs_to_remove) > self.config.max_programs:
            all_programs = []
            for island in self.islands:
                all_programs.extend(list(island))

            all_programs.sort(key=lambda p: p.metrics.overall_score)
            target_removals = len(self._all_program_ids) - self.config.max_programs
            for program in all_programs[:target_removals]:
                if program.id not in programs_to_remove:
                    # Don't remove champions
                    is_champion = any(program.id in island.champions for island in self.islands)
                    if not is_champion:
                        programs_to_remove.append(program.id)

        # Perform removals
        for program_id in programs_to_remove:
            self._remove_program(program_id)

    def increment_generation(self) -> int:
        """Increment and return the current generation."""
        self._generation += 1
        return self._generation

    @property
    def size(self) -> int:
        """Total number of programs in the database."""
        return len(self._all_program_ids)

    @property
    def generation(self) -> int:
        """Current generation number."""
        return self._generation

    def stats(self) -> dict:
        """Get database statistics."""
        island_stats = []
        for island in self.islands:
            island_stats.append(
                {
                    "id": island.id,
                    "size": len(island),
                    "best_score": island.best_score,
                    "avg_score": island.average_score,
                    "champions": len(island.champions),
                }
            )

        return {
            "total_programs": self.size,
            "generation": self._generation,
            "best_score": (self._best_program.metrics.overall_score if self._best_program else 0.0),
            "islands": island_stats,
            "niches_filled": len(self._niches),
        }

    # -------------------------------------------------------------------------
    # Persistence Methods (SolutionStore integration)
    # -------------------------------------------------------------------------

    def flush(self) -> int:
        """Flush all pending writes to the persistent store.

        Call this at the end of an evolution run to ensure all programs
        are persisted.

        Returns:
            Number of programs persisted.
        """
        return self._flush_pending()

    def _flush_pending(self) -> int:
        """Internal method to flush pending writes."""
        if not self._solution_store or not self._task_hash:
            self._pending_writes.clear()
            return 0

        if not self._pending_writes:
            return 0

        count = 0
        for program in self._pending_writes:
            try:
                record = self._program_to_record(program)
                self._solution_store.add(record, immediate=True)

                # Also update niche in store
                niche_key = self._compute_niche_key(program)
                niche_dims = self._get_niche_dimensions(program)
                self._solution_store.update_niche(program.id, niche_key, niche_dims)

                count += 1
            except Exception as e:
                logger.warning(f"Failed to persist program {program.id}: {e}")

        self._pending_writes.clear()
        return count

    def _load_from_store(self) -> int:
        """Load champion programs from the persistent store.

        Returns:
            Number of programs loaded.
        """
        if not self._solution_store or not self._task_hash:
            return 0

        try:
            # Get best programs for this task
            champions = self._solution_store.get_best_for_task(
                self._task_hash,
                limit=self.config.max_programs // 2,  # Leave room for new programs
                min_score=0.0,
                solution_type="evolution_program",
            )

            # Temporarily disable persistence to avoid re-writing loaded programs
            store = self._solution_store
            self._solution_store = None

            loaded = 0
            for record in champions:
                program = self._record_to_program(record)
                if self.add(program):
                    loaded += 1

            # Re-enable persistence
            self._solution_store = store

            if loaded > 0:
                logger.info(f"Loaded {loaded} programs from persistent store")

            return loaded

        except Exception as e:
            logger.warning(f"Failed to load from store: {e}")
            return 0

    def _program_to_record(self, program: Program) -> SolutionRecord:
        """Convert a Program to a SolutionRecord for persistence."""
        # Import here to avoid circular imports
        from deliberate.tracking.solution_store import SolutionRecord

        metrics = program.metrics
        return SolutionRecord(
            id=program.id,
            task_hash=self._task_hash or "",
            solution_type="evolution_program",
            agent=program.agent or "unknown",
            success=program.is_valid and metrics.test_score >= 1.0,
            overall_score=metrics.overall_score,
            code_content=program.code,
            diff_applied=program.diff_applied,
            test_score=metrics.test_score,
            tests_passed=metrics.tests_passed,
            tests_total=metrics.tests_total,
            lint_score=metrics.lint_score,
            runtime_ms=metrics.runtime_ms if metrics.runtime_ms < float("inf") else None,
            memory_mb=metrics.memory_mb if metrics.memory_mb < float("inf") else None,
            parent_solution_id=(program.parent_ids[0] if program.parent_ids else None),
            inspiration_ids=program.inspiration_ids,
            generation=metrics.generation,
            is_valid=program.is_valid,
            is_champion=program.is_champion,
        )

    def _record_to_program(self, record: SolutionRecord) -> Program:
        """Convert a SolutionRecord back to a Program."""
        from .types import EvaluationLevel

        metrics = ProgramMetrics(
            test_score=record.test_score or 0.0,
            tests_passed=record.tests_passed or 0,
            tests_total=record.tests_total or 0,
            lint_score=record.lint_score or 1.0,
            runtime_ms=record.runtime_ms if record.runtime_ms else float("inf"),
            memory_mb=record.memory_mb if record.memory_mb else float("inf"),
            generation=record.generation,
            parent_id=record.parent_solution_id,
            highest_level_passed=EvaluationLevel.UNIT_FULL if record.success else (EvaluationLevel.LINT),
        )

        return Program(
            id=record.id,
            code=record.code_content or "",
            metrics=metrics,
            parent_ids=[record.parent_solution_id] if record.parent_solution_id else [],
            inspiration_ids=record.inspiration_ids or [],
            agent=record.agent,
            diff_applied=record.diff_applied,
            created_at=record.created_at,
            evaluated_at=record.evaluated_at,
            is_valid=record.is_valid,
            is_champion=record.is_champion,
        )

    def _get_niche_dimensions(self, program: Program) -> dict[str, float]:
        """Get the dimension values for a program's niche."""
        metrics = program.metrics
        dims = {}
        for dim in self.config.niche_dimensions:
            value = getattr(metrics, dim, 0)
            if isinstance(value, float):
                if value == float("inf") or value == float("-inf"):
                    dims[dim] = 9.0 if value == float("inf") else 0.0
                else:
                    dims[dim] = float(min(9, max(0, int(value * 10)))) / 10.0
            else:
                dims[dim] = float(value % 100)
        return dims
