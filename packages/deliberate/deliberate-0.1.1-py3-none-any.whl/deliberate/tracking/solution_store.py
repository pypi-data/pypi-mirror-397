"""Solution storage for unified feedback memory.

Provides a Data Access Layer (DAL) for the solutions table, enabling
both iteration.SolutionHistory and evolution.ProgramDatabase to share
a common persistence layer.
"""

import json
import logging
import random
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal

logger = logging.getLogger(__name__)


@dataclass
class SolutionRecord:
    """A unified solution record for both iteration attempts and evolution programs."""

    id: str
    task_hash: str
    solution_type: Literal["iteration_attempt", "evolution_program"]
    agent: str
    success: bool
    overall_score: float

    # Optional fields
    workflow_id: str | None = None
    task_preview: str | None = None
    code_content: str | None = None
    diff_applied: str | None = None

    # Test metrics
    test_score: float | None = None
    tests_passed: int | None = None
    tests_total: int | None = None

    # Quality metrics
    lint_score: float | None = None
    runtime_ms: float | None = None
    memory_mb: float | None = None

    # Performance flags
    needs_optimization: bool = False
    performance_issue: str | None = None  # 'none'|'slow_execution'|'high_memory'|'timeout'

    # Feedback
    feedback_summary: str | None = None
    error_message: str | None = None

    # Lineage
    parent_solution_id: str | None = None
    inspiration_ids: list[str] = field(default_factory=list)
    generation: int = 0

    # Flags
    is_valid: bool = False
    is_champion: bool = False

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    evaluated_at: datetime | None = None

    # Resource usage
    token_usage: int | None = None
    duration_seconds: float | None = None

    # Tags for filtering
    tags: list[str] = field(default_factory=list)

    @classmethod
    def new_id(cls) -> str:
        """Generate a new unique ID."""
        return f"sol_{uuid.uuid4().hex[:12]}"

    def to_metrics_dict(self) -> dict[str, Any]:
        """Extract metrics as a dictionary."""
        return {
            "test_score": self.test_score,
            "tests_passed": self.tests_passed,
            "tests_total": self.tests_total,
            "lint_score": self.lint_score,
            "runtime_ms": self.runtime_ms,
            "memory_mb": self.memory_mb,
        }


class SolutionStore:
    """Data Access Layer for the solutions table.

    Provides CRUD operations and efficient queries for retrieving
    high-scoring solutions, champions, and samples for evolution.

    Thread-safe with internal locking.
    """

    def __init__(self, tracker: Any):  # AgentPerformanceTracker
        """Initialize the store.

        Args:
            tracker: AgentPerformanceTracker instance providing DB connection.
        """
        self._tracker = tracker
        self._lock = threading.RLock()

        # Batch write buffer for async persistence
        self._write_buffer: list[SolutionRecord] = []
        self._batch_size = 10

    def _get_conn(self):
        """Get the underlying database connection."""
        return self._tracker.get_connection()

    def _is_duckdb(self) -> bool:
        """Check if using DuckDB (vs SQLite)."""
        return self._tracker._use_duckdb

    def _execute(self, query: str, params: tuple | list = ()) -> list[dict]:
        """Execute query and return results as list of dicts."""
        conn = self._get_conn()
        if self._is_duckdb():
            result = conn.execute(query, params)
            columns = [desc[0] for desc in result.description] if result.description else []
            rows = result.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        else:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def _execute_one(self, query: str, params: tuple | list = ()) -> dict | None:
        """Execute query and return single result."""
        results = self._execute(query, params)
        return results[0] if results else None

    # -------------------------------------------------------------------------
    # CRUD Operations
    # -------------------------------------------------------------------------

    def add(self, record: SolutionRecord, immediate: bool = False) -> str:
        """Add a solution record.

        Args:
            record: The solution to add.
            immediate: If True, write immediately. Otherwise buffer for batch.

        Returns:
            The solution ID.
        """
        if not record.id:
            record.id = SolutionRecord.new_id()

        if immediate:
            self._write_record(record)
        else:
            with self._lock:
                self._write_buffer.append(record)
                if len(self._write_buffer) >= self._batch_size:
                    self.flush()

        return record.id

    def _write_record(self, record: SolutionRecord) -> None:
        """Write a single record to the database."""
        with self._lock:
            conn = self._get_conn()
            query = """
                INSERT INTO solutions (
                    id, workflow_id, task_hash, task_preview, code_content,
                    diff_applied, solution_type, agent, success, overall_score,
                    test_score, tests_passed, tests_total, lint_score,
                    runtime_ms, memory_mb, needs_optimization, performance_issue,
                    feedback_summary, error_message, parent_solution_id,
                    inspiration_ids, generation, is_valid, is_champion,
                    created_at, evaluated_at, token_usage, duration_seconds, tags
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            """
            params = (
                record.id,
                record.workflow_id,
                record.task_hash,
                record.task_preview,
                record.code_content,
                record.diff_applied,
                record.solution_type,
                record.agent,
                record.success,
                record.overall_score,
                record.test_score,
                record.tests_passed,
                record.tests_total,
                record.lint_score,
                record.runtime_ms,
                record.memory_mb,
                record.needs_optimization,
                record.performance_issue,
                record.feedback_summary,
                record.error_message,
                record.parent_solution_id,
                json.dumps(record.inspiration_ids),
                record.generation,
                record.is_valid,
                record.is_champion,
                record.created_at.isoformat(),
                record.evaluated_at.isoformat() if record.evaluated_at else None,
                record.token_usage,
                record.duration_seconds,
                json.dumps(record.tags),
            )

            try:
                conn.execute(query, params)
                if not self._is_duckdb():
                    conn.commit()
            except Exception as e:
                logger.error(f"Failed to write solution {record.id}: {e}")
                raise

    def flush(self) -> int:
        """Flush buffered writes to database.

        Returns:
            Number of records written.
        """
        with self._lock:
            if not self._write_buffer:
                return 0

            records = self._write_buffer[:]
            self._write_buffer.clear()

        count = 0
        for record in records:
            try:
                self._write_record(record)
                count += 1
            except Exception as e:
                logger.warning(f"Failed to flush record {record.id}: {e}")

        return count

    def get_by_id(self, solution_id: str) -> SolutionRecord | None:
        """Get a solution by ID."""
        with self._lock:
            row = self._execute_one(
                "SELECT * FROM solutions WHERE id = ?",
                (solution_id,),
            )
            return self._row_to_record(row) if row else None

    def update(self, record: SolutionRecord) -> bool:
        """Update an existing solution record.

        Args:
            record: The solution with updated fields.

        Returns:
            True if updated, False if not found.
        """
        with self._lock:
            conn = self._get_conn()
            query = """
                UPDATE solutions SET
                    success = ?, overall_score = ?, test_score = ?,
                    tests_passed = ?, tests_total = ?, lint_score = ?,
                    runtime_ms = ?, memory_mb = ?, needs_optimization = ?,
                    performance_issue = ?, feedback_summary = ?, error_message = ?,
                    is_valid = ?, is_champion = ?, evaluated_at = ?,
                    token_usage = ?, duration_seconds = ?, tags = ?
                WHERE id = ?
            """
            params = (
                record.success,
                record.overall_score,
                record.test_score,
                record.tests_passed,
                record.tests_total,
                record.lint_score,
                record.runtime_ms,
                record.memory_mb,
                record.needs_optimization,
                record.performance_issue,
                record.feedback_summary,
                record.error_message,
                record.is_valid,
                record.is_champion,
                record.evaluated_at.isoformat() if record.evaluated_at else None,
                record.token_usage,
                record.duration_seconds,
                json.dumps(record.tags),
                record.id,
            )

            try:
                conn.execute(query, params)
                if not self._is_duckdb():
                    conn.commit()
                return True
            except Exception as e:
                logger.error(f"Failed to update solution {record.id}: {e}")
                return False

    def delete(self, solution_id: str) -> bool:
        """Delete a solution by ID."""
        with self._lock:
            conn = self._get_conn()
            try:
                conn.execute("DELETE FROM solutions WHERE id = ?", (solution_id,))
                if not self._is_duckdb():
                    conn.commit()
                return True
            except Exception as e:
                logger.error(f"Failed to delete solution {solution_id}: {e}")
                return False

    # -------------------------------------------------------------------------
    # Query Operations
    # -------------------------------------------------------------------------

    def get_best_for_task(
        self,
        task_hash: str,
        limit: int = 5,
        min_score: float = 0.5,
        solution_type: str | None = None,
    ) -> list[SolutionRecord]:
        """Get best solutions for a specific task.

        Args:
            task_hash: Hash of the task to query.
            limit: Maximum number of solutions to return.
            min_score: Minimum overall score to include.
            solution_type: Filter by type ('iteration_attempt' or 'evolution_program').

        Returns:
            List of solutions ordered by score descending.
        """
        with self._lock:
            query = """
                SELECT * FROM solutions
                WHERE task_hash = ?
                AND overall_score >= ?
                AND is_valid = TRUE
            """
            params: list[Any] = [task_hash, min_score]

            if solution_type:
                query += " AND solution_type = ?"
                params.append(solution_type)

            query += " ORDER BY overall_score DESC LIMIT ?"
            params.append(limit)

            rows = self._execute(query, tuple(params))
            return [self._row_to_record(row) for row in rows]

    def get_champions(
        self,
        limit: int = 10,
        task_hash: str | None = None,
    ) -> list[SolutionRecord]:
        """Get champion solutions.

        Args:
            limit: Maximum number of champions to return.
            task_hash: Optional filter by task.

        Returns:
            List of champion solutions.
        """
        with self._lock:
            if task_hash:
                query = """
                    SELECT * FROM solutions
                    WHERE is_champion = TRUE AND task_hash = ?
                    ORDER BY overall_score DESC
                    LIMIT ?
                """
                params = (task_hash, limit)
            else:
                query = """
                    SELECT * FROM solutions
                    WHERE is_champion = TRUE
                    ORDER BY overall_score DESC
                    LIMIT ?
                """
                params = (limit,)

            rows = self._execute(query, params)
            return [self._row_to_record(row) for row in rows]

    def get_by_workflow(self, workflow_id: str) -> list[SolutionRecord]:
        """Get all solutions for a workflow."""
        with self._lock:
            rows = self._execute(
                """
                SELECT * FROM solutions
                WHERE workflow_id = ?
                ORDER BY created_at ASC
                """,
                (workflow_id,),
            )
            return [self._row_to_record(row) for row in rows]

    def sample_for_evolution(
        self,
        task_hash: str,
        num_parents: int = 2,
        num_inspirations: int = 3,
        prefer_champions: bool = True,
        temperature: float = 1.0,
    ) -> tuple[list[SolutionRecord], list[SolutionRecord]]:
        """Sample solutions for evolutionary parent selection.

        Args:
            task_hash: Hash of the task.
            num_parents: Number of parent solutions to select.
            num_inspirations: Number of inspiration solutions.
            prefer_champions: Weight champions higher in selection.
            temperature: Higher = more random, lower = more greedy.

        Returns:
            Tuple of (parents, inspirations).
        """
        with self._lock:
            # Get candidate pool
            query = """
                SELECT * FROM solutions
                WHERE task_hash = ?
                AND is_valid = TRUE
                ORDER BY overall_score DESC
                LIMIT 100
            """
            rows = self._execute(query, (task_hash,))
            candidates = [self._row_to_record(row) for row in rows]

            if not candidates:
                return [], []

            # Softmax selection with temperature
            def softmax_sample(pool: list[SolutionRecord], n: int) -> list[SolutionRecord]:
                if len(pool) <= n:
                    return pool

                # Calculate weights
                weights = []
                for sol in pool:
                    w = sol.overall_score
                    if prefer_champions and sol.is_champion:
                        w *= 2.0  # Double weight for champions
                    weights.append(w ** (1.0 / temperature))

                total = sum(weights)
                if total == 0:
                    return random.sample(pool, min(n, len(pool)))

                probs = [w / total for w in weights]

                # Sample without replacement
                selected = []
                remaining = list(zip(pool, probs))
                for _ in range(min(n, len(pool))):
                    if not remaining:
                        break
                    items, ps = zip(*remaining)
                    ps_normalized = [p / sum(ps) for p in ps]
                    idx = random.choices(range(len(items)), weights=ps_normalized, k=1)[0]
                    selected.append(items[idx])
                    remaining = [r for i, r in enumerate(remaining) if i != idx]

                return selected

            parents = softmax_sample(candidates, num_parents)

            # For inspirations, exclude parents
            parent_ids = {p.id for p in parents}
            inspiration_pool = [c for c in candidates if c.id not in parent_ids]
            inspirations = softmax_sample(inspiration_pool, num_inspirations)

            return parents, inspirations

    def count_by_task(self, task_hash: str) -> int:
        """Count solutions for a task."""
        with self._lock:
            result = self._execute_one(
                "SELECT COUNT(*) as count FROM solutions WHERE task_hash = ?",
                (task_hash,),
            )
            return result["count"] if result else 0

    # -------------------------------------------------------------------------
    # Niche Operations (for MAP-Elites)
    # -------------------------------------------------------------------------

    def update_niche(
        self,
        solution_id: str,
        niche_key: str,
        dimensions: dict[str, float],
    ) -> None:
        """Update or insert a niche entry.

        Args:
            solution_id: The solution occupying this niche.
            niche_key: Unique key for the niche.
            dimensions: Dimension values for the niche.
        """
        with self._lock:
            conn = self._get_conn()
            now = datetime.now()
            dimensions_json = json.dumps(dimensions)
            if self._is_duckdb():
                query = """
                    INSERT INTO solution_niches (niche_key, solution_id, dimensions, updated_at)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT (niche_key) DO UPDATE SET
                        solution_id = EXCLUDED.solution_id,
                        dimensions = EXCLUDED.dimensions,
                        updated_at = EXCLUDED.updated_at
                """
            else:
                query = """
                    INSERT OR REPLACE INTO solution_niches
                    (niche_key, solution_id, dimensions, updated_at)
                    VALUES (?, ?, ?, ?)
                """
            conn.execute(query, (niche_key, solution_id, dimensions_json, now))
            if not self._is_duckdb():
                conn.commit()

    def get_niche_occupant(self, niche_key: str) -> SolutionRecord | None:
        """Get the solution currently occupying a niche."""
        with self._lock:
            row = self._execute_one(
                """
                SELECT s.* FROM solutions s
                JOIN solution_niches n ON s.id = n.solution_id
                WHERE n.niche_key = ?
                """,
                (niche_key,),
            )
            return self._row_to_record(row) if row else None

    def get_all_niches(self, task_hash: str | None = None) -> dict[str, SolutionRecord]:
        """Get all occupied niches.

        Args:
            task_hash: Optional filter by task.

        Returns:
            Dict mapping niche_key to solution.
        """
        with self._lock:
            if task_hash:
                query = """
                    SELECT n.niche_key, s.* FROM solution_niches n
                    JOIN solutions s ON n.solution_id = s.id
                    WHERE s.task_hash = ?
                """
                rows = self._execute(query, (task_hash,))
            else:
                query = """
                    SELECT n.niche_key, s.* FROM solution_niches n
                    JOIN solutions s ON n.solution_id = s.id
                """
                rows = self._execute(query, ())

            result = {}
            for row in rows:
                niche_key = row.pop("niche_key")
                result[niche_key] = self._row_to_record(row)
            return result

    # -------------------------------------------------------------------------
    # Helper Methods
    # -------------------------------------------------------------------------

    def _row_to_record(self, row: dict) -> SolutionRecord:
        """Convert a database row to a SolutionRecord."""
        # Parse JSON fields
        inspiration_ids = row.get("inspiration_ids")
        if isinstance(inspiration_ids, str):
            inspiration_ids = json.loads(inspiration_ids)
        elif inspiration_ids is None:
            inspiration_ids = []

        tags = row.get("tags")
        if isinstance(tags, str):
            tags = json.loads(tags)
        elif tags is None:
            tags = []

        # Parse timestamps
        created_at = row.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        elif created_at is None:
            created_at = datetime.now()

        evaluated_at = row.get("evaluated_at")
        if isinstance(evaluated_at, str):
            evaluated_at = datetime.fromisoformat(evaluated_at)

        return SolutionRecord(
            id=row["id"],
            workflow_id=row.get("workflow_id"),
            task_hash=row["task_hash"],
            task_preview=row.get("task_preview"),
            code_content=row.get("code_content"),
            diff_applied=row.get("diff_applied"),
            solution_type=row["solution_type"],
            agent=row["agent"],
            success=bool(row["success"]),
            overall_score=float(row["overall_score"]),
            test_score=row.get("test_score"),
            tests_passed=row.get("tests_passed"),
            tests_total=row.get("tests_total"),
            lint_score=row.get("lint_score"),
            runtime_ms=row.get("runtime_ms"),
            memory_mb=row.get("memory_mb"),
            needs_optimization=bool(row.get("needs_optimization", False)),
            performance_issue=row.get("performance_issue"),
            feedback_summary=row.get("feedback_summary"),
            error_message=row.get("error_message"),
            parent_solution_id=row.get("parent_solution_id"),
            inspiration_ids=inspiration_ids,
            generation=row.get("generation", 0),
            is_valid=bool(row.get("is_valid", False)),
            is_champion=bool(row.get("is_champion", False)),
            created_at=created_at,
            evaluated_at=evaluated_at,
            token_usage=row.get("token_usage"),
            duration_seconds=row.get("duration_seconds"),
            tags=tags,
        )

    def mark_champion(self, solution_id: str, is_champion: bool = True) -> bool:
        """Mark or unmark a solution as champion."""
        with self._lock:
            conn = self._get_conn()
            try:
                conn.execute(
                    "UPDATE solutions SET is_champion = ? WHERE id = ?",
                    (is_champion, solution_id),
                )
                if not self._is_duckdb():
                    conn.commit()
                return True
            except Exception as e:
                logger.error(f"Failed to mark champion {solution_id}: {e}")
                return False

    def clear_champions(self, task_hash: str) -> int:
        """Clear all champion flags for a task.

        Returns:
            Number of solutions updated.
        """
        with self._lock:
            conn = self._get_conn()
            query = """
                UPDATE solutions SET is_champion = FALSE
                WHERE task_hash = ? AND is_champion = TRUE
            """
            conn.execute(query, (task_hash,))
            if not self._is_duckdb():
                conn.commit()
            # Return count is tricky without rowcount, skip for now
            return 0
