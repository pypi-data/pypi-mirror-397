"""DuckDB-based agent performance tracker.

Tracks agent performance across workflow runs to identify which agents
are best at planning, execution, and reviewing.

Uses DuckDB for efficient analytical queries on agent statistics.
"""

import json
import threading
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Literal

import platformdirs

try:
    import duckdb

    HAS_DUCKDB = True
except ImportError:
    HAS_DUCKDB = False
    import sqlite3

from deliberate.config import DeliberateConfig  # Import DeliberateConfig
from deliberate.tracking.migrations import Migrator


@dataclass
class PlanningRecord:
    """Record of an agent's planning performance in a single workflow."""

    agent: str
    was_selected: bool  # Was this agent's plan selected?
    led_to_success: bool  # Did the workflow succeed with this plan?
    final_score: float | None  # Final score from reviews (if available)
    token_usage: int
    timestamp: datetime
    prompt: str | None = None
    config_id: str | None = None


@dataclass
class ExecutionRecord:
    """Record of an agent's execution performance in a single workflow."""

    agent: str
    was_winner: bool  # Was this agent's execution selected as winner?
    success: bool  # Did execution complete successfully?
    error_category: str | None  # Category of failure (e.g., syntax_error, timeout)
    score: float | None  # Review score for this execution
    rank: int | None  # Rank among all executions (1 = best)
    total_candidates: int  # Total number of execution candidates
    token_usage: int
    duration_seconds: float
    timestamp: datetime
    prompt: str | None = None
    config_id: str | None = None


@dataclass
class ReviewRecord:
    """Record of an agent's review accuracy."""

    agent: str
    candidate_id: str
    score_given: float  # Score this reviewer gave
    review_comment: str | None  # Text content of the review
    was_candidate_winner: bool  # Did this candidate win?
    final_winner_score: float | None  # What score did reviewer give to actual winner?
    timestamp: datetime
    config_id: str | None = None


@dataclass
class WorkflowRecord:
    """Complete record of a workflow run."""

    workflow_id: str
    task_hash: str  # Hash of task for grouping similar tasks
    task_preview: str  # First 200 chars of task
    success: bool
    total_duration_seconds: float
    total_tokens: int
    total_cost_usd: float
    selected_planner: str | None
    winning_executor: str | None
    refinement_triggered: bool
    final_score: float | None
    initial_score: float | None  # Score before refinement
    timestamp: datetime
    refinement_token_usage: int = 0  # Tokens spent on refinement


@dataclass
class RefinementRecord:
    """Record of a refinement iteration."""

    workflow_id: str
    iteration_num: int
    candidate_id: str | None
    pre_refinement_score: float | None
    post_refinement_score: float | None
    diff: str | None
    feedback: str | None
    token_usage: int
    timestamp: datetime


@dataclass
class AgentStats:
    """Aggregated statistics for an agent."""

    agent: str
    role: Literal["planner", "executor", "reviewer"]

    # Counts
    total_runs: int
    wins: int
    successes: int

    # Rates (0-1)
    win_rate: float
    success_rate: float

    # Scores
    avg_score: float | None
    best_score: float | None

    # For reviewers: accuracy in predicting winners
    review_accuracy: float | None

    # Efficiency
    avg_tokens: float
    avg_duration_seconds: float | None

    # Trend (recent performance vs overall)
    recent_win_rate: float | None  # Last 10 runs


class NoOpTracker:
    """A no-operation tracker for when tracking is disabled."""

    def record_workflow(self, record: WorkflowRecord) -> None:
        pass

    def record_planning(self, workflow_id: str, record: PlanningRecord) -> None:
        pass

    def record_execution(self, workflow_id: str, record: ExecutionRecord) -> None:
        pass

    def record_review(self, workflow_id: str, record: ReviewRecord) -> None:
        pass

    def record_refinement(self, record: RefinementRecord) -> None:
        pass

    def record_agent_config(self, agent_name: str, config: dict) -> str:
        return "noop-config-id"

    def get_planner_stats(self, agent: str | None = None) -> list[AgentStats]:
        return []

    def get_executor_stats(self, agent: str | None = None) -> list[AgentStats]:
        return []

    def get_reviewer_stats(self, agent: str | None = None) -> list[AgentStats]:
        return []

    def get_best_planners(self, limit: int = 5) -> list[AgentStats]:
        return []

    def get_best_executors(self, limit: int = 5) -> list[AgentStats]:
        return []

    def get_leaderboard(self) -> dict[str, list[AgentStats]]:
        return {"planners": [], "executors": [], "reviewers": []}

    def get_workflow_count(self) -> int:
        return 0

    def clear_all(self) -> int:
        return 0

    def get_recent_workflows(self, limit: int = 10) -> list[WorkflowRecord]:
        return []

    def export_stats(self) -> dict:
        return {}

    def close(self) -> None:
        pass

    def get_connection(self):
        return None  # No connection for NoOpTracker


# Module-level singleton
_tracker: "AgentPerformanceTracker | NoOpTracker | None" = None
_tracker_lock = threading.Lock()


def get_tracker(db_path: Path | None = None) -> "AgentPerformanceTracker | NoOpTracker":
    """Get the global performance tracker singleton.

    Args:
        db_path: Optional path to database. If None, uses user config directory.

    Returns:
        The global AgentPerformanceTracker instance.
    """
    global _tracker
    with _tracker_lock:
        if _tracker is None:
            # Check if tracking is enabled in the config
            try:
                cfg = DeliberateConfig.load_or_default()
                if not cfg.tracking.enabled:
                    _tracker = NoOpTracker()
                    return _tracker
            except Exception:
                # If config loading fails, assume tracking is enabled for safety
                pass

            _tracker = AgentPerformanceTracker(db_path)
        return _tracker


def reset_tracker() -> None:
    """Reset the global tracker singleton (for testing)."""
    global _tracker
    with _tracker_lock:
        if _tracker is not None:
            _tracker.close()
            _tracker = None


class AgentPerformanceTracker:
    """Tracks agent performance in a DuckDB database (with SQLite fallback).

    Stores performance records for planning, execution, and review phases
    to determine which agents are best at each role over time.

    Uses DuckDB for efficient analytical queries. Falls back to SQLite if
    DuckDB is not installed.
    """

    def __init__(self, db_path: Path | None = None):
        """Initialize the tracker.

        Args:
            db_path: Path to database file. If None, uses user data directory.
        """
        if db_path is None:
            config_dir = Path(platformdirs.user_data_dir("deliberate", appauthor=False))
            config_dir.mkdir(parents=True, exist_ok=True)
            suffix = ".duckdb" if HAS_DUCKDB else ".db"
            db_path = config_dir / f"agent_performance{suffix}"

        self.db_path = db_path
        self._conn = None
        self._lock = threading.RLock()
        self._use_duckdb = HAS_DUCKDB
        self._init_db()

    def _get_conn(self):
        """Get database connection, creating if needed."""
        if self._conn is None:
            if self._use_duckdb:
                self._conn = duckdb.connect(str(self.db_path))
            else:
                self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
                self._conn.row_factory = sqlite3.Row
        return self._conn

    def get_connection(self):
        """Public accessor for the underlying connection."""
        return self._get_conn()

    def _execute(self, query: str, params: tuple | list = ()) -> list[dict]:
        """Execute query and return results as list of dicts."""
        conn = self._get_conn()
        if self._use_duckdb:
            result = conn.execute(query, params)
            columns = [desc[0] for desc in result.description] if result.description else []
            rows = result.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        else:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def _execute_one(self, query: str, params: tuple | list = ()) -> dict | None:
        """Execute query and return single result as dict."""
        results = self._execute(query, params)
        return results[0] if results else None

    def _init_db(self) -> None:
        """Initialize the database schema using migrations."""
        with self._lock:
            conn = self._get_conn()
            migrator = Migrator(conn, self._use_duckdb)
            migrator.migrate()

    def close(self) -> None:
        """Close the database connection."""
        with self._lock:
            if self._conn is not None:
                self._conn.close()
                self._conn = None

    def record_workflow(self, record: WorkflowRecord) -> None:
        """Record a complete workflow run."""
        with self._lock:
            conn = self._get_conn()
            if self._use_duckdb:
                # DuckDB uses INSERT ... ON CONFLICT
                conn.execute(
                    """
                    INSERT INTO workflows (
                        workflow_id, task_hash, task_preview, success,
                        total_duration_seconds, total_tokens, total_cost_usd,
                        selected_planner, winning_executor, refinement_triggered,
                        final_score, initial_score, refinement_token_usage, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT (workflow_id) DO UPDATE SET
                        task_hash = EXCLUDED.task_hash,
                        task_preview = EXCLUDED.task_preview,
                        success = EXCLUDED.success,
                        total_duration_seconds = EXCLUDED.total_duration_seconds,
                        total_tokens = EXCLUDED.total_tokens,
                        total_cost_usd = EXCLUDED.total_cost_usd,
                        selected_planner = EXCLUDED.selected_planner,
                        winning_executor = EXCLUDED.winning_executor,
                        refinement_triggered = EXCLUDED.refinement_triggered,
                        final_score = EXCLUDED.final_score,
                        initial_score = EXCLUDED.initial_score,
                        refinement_token_usage = EXCLUDED.refinement_token_usage,
                        timestamp = EXCLUDED.timestamp
                """,
                    (
                        record.workflow_id,
                        record.task_hash,
                        record.task_preview,
                        int(record.success),
                        record.total_duration_seconds,
                        record.total_tokens,
                        record.total_cost_usd,
                        record.selected_planner,
                        record.winning_executor,
                        int(record.refinement_triggered),
                        record.final_score,
                        record.initial_score,
                        record.refinement_token_usage,
                        record.timestamp.isoformat(),
                    ),
                )
            else:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO workflows (
                        workflow_id, task_hash, task_preview, success,
                        total_duration_seconds, total_tokens, total_cost_usd,
                        selected_planner, winning_executor, refinement_triggered,
                        final_score, initial_score, refinement_token_usage, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        record.workflow_id,
                        record.task_hash,
                        record.task_preview,
                        int(record.success),
                        record.total_duration_seconds,
                        record.total_tokens,
                        record.total_cost_usd,
                        record.selected_planner,
                        record.winning_executor,
                        int(record.refinement_triggered),
                        record.final_score,
                        record.initial_score,
                        record.refinement_token_usage,
                        record.timestamp.isoformat(),
                    ),
                )
                conn.commit()

    def record_planning(self, workflow_id: str, record: PlanningRecord) -> None:
        """Record planning performance for an agent."""
        with self._lock:
            conn = self._get_conn()
            conn.execute(
                """
                INSERT INTO planning_records (
                    workflow_id, agent, was_selected, led_to_success,
                    final_score, token_usage, timestamp, prompt, config_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    workflow_id,
                    record.agent,
                    int(record.was_selected),
                    int(record.led_to_success),
                    record.final_score,
                    record.token_usage,
                    record.timestamp.isoformat(),
                    record.prompt,
                    record.config_id,
                ),
            )
            if not self._use_duckdb:
                conn.commit()

    def record_execution(self, workflow_id: str, record: ExecutionRecord) -> None:
        """Record execution performance for an agent."""
        with self._lock:
            conn = self._get_conn()
            conn.execute(
                """
                INSERT INTO execution_records (
                    workflow_id, agent, was_winner, success, error_category, score,
                    rank, total_candidates, token_usage, duration_seconds, timestamp,
                    prompt, config_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    workflow_id,
                    record.agent,
                    int(record.was_winner),
                    int(record.success),
                    record.error_category,
                    record.score,
                    record.rank,
                    record.total_candidates,
                    record.token_usage,
                    record.duration_seconds,
                    record.timestamp.isoformat(),
                    record.prompt,
                    record.config_id,
                ),
            )
            if not self._use_duckdb:
                conn.commit()

    def record_review(self, workflow_id: str, record: ReviewRecord) -> None:
        """Record review accuracy for an agent."""
        with self._lock:
            conn = self._get_conn()
            conn.execute(
                """
                INSERT INTO review_records (
                    workflow_id, agent, candidate_id, score_given, review_comment,
                    was_candidate_winner, final_winner_score, timestamp, config_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    workflow_id,
                    record.agent,
                    record.candidate_id,
                    record.score_given,
                    record.review_comment,
                    int(record.was_candidate_winner),
                    record.final_winner_score,
                    record.timestamp.isoformat(),
                    record.config_id,
                ),
            )
            if not self._use_duckdb:
                conn.commit()

    def record_refinement(self, record: RefinementRecord) -> None:
        """Record a refinement iteration."""
        with self._lock:
            conn = self._get_conn()
            conn.execute(
                """
                INSERT INTO refinement_iterations (
                    workflow_id, iteration_num, candidate_id,
                    pre_refinement_score, post_refinement_score,
                    diff, feedback, token_usage, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    record.workflow_id,
                    record.iteration_num,
                    record.candidate_id,
                    record.pre_refinement_score,
                    record.post_refinement_score,
                    record.diff,
                    record.feedback,
                    record.token_usage,
                    record.timestamp.isoformat(),
                ),
            )
            if not self._use_duckdb:
                conn.commit()

    def record_agent_config(self, agent_name: str, config: dict) -> str:
        """Record agent configuration and return its hash ID.

        If config already exists, returns existing ID.
        """
        import hashlib

        config_str = json.dumps(config, sort_keys=True)
        config_id = hashlib.sha256((agent_name + config_str).encode()).hexdigest()[:16]

        with self._lock:
            conn = self._get_conn()

            # Check if exists
            exists_query = "SELECT 1 FROM agent_configs WHERE id = ?"
            if self._use_duckdb:
                exists = conn.execute(exists_query, [config_id]).fetchone()
            else:
                cursor = conn.execute(exists_query, [config_id])
                exists = cursor.fetchone()

            if not exists:
                conn.execute(
                    """
                    INSERT INTO agent_configs (id, agent_name, config_json, created_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (config_id, agent_name, config_str, datetime.now().isoformat()),
                )
                if not self._use_duckdb:
                    conn.commit()

        return config_id

    def get_planner_stats(self, agent: str | None = None) -> list[AgentStats]:
        """Get planning statistics for agents.

        Args:
            agent: Optional agent name to filter. If None, returns all planners.

        Returns:
            List of AgentStats for planners, sorted by win rate descending.
        """
        with self._lock:
            query = """
                SELECT
                    agent,
                    COUNT(*) as total_runs,
                    SUM(was_selected) as wins,
                    SUM(CASE WHEN was_selected AND led_to_success THEN 1 ELSE 0 END) as successes,
                    AVG(CASE WHEN was_selected THEN final_score ELSE NULL END) as avg_score,
                    MAX(final_score) as best_score,
                    AVG(token_usage) as avg_tokens
                FROM planning_records
            """
            params: list = []

            if agent:
                query += " WHERE agent = ?"
                params.append(agent)

            query += " GROUP BY agent ORDER BY CAST(wins AS REAL) / total_runs DESC"

            rows = self._execute(query, params)

            stats = []
            for row in rows:
                total = row["total_runs"] or 1
                wins = row["wins"] or 0
                successes = row["successes"] or 0

                # Get recent win rate (last 10 runs)
                recent_query = """
                    SELECT AVG(was_selected) as recent_rate
                    FROM (
                        SELECT was_selected FROM planning_records
                        WHERE agent = ?
                        ORDER BY timestamp DESC
                        LIMIT 10
                    )
                """
                recent_row = self._execute_one(recent_query, (row["agent"],))
                recent_win_rate = recent_row["recent_rate"] if recent_row else None

                stats.append(
                    AgentStats(
                        agent=row["agent"],
                        role="planner",
                        total_runs=total,
                        wins=wins,
                        successes=successes,
                        win_rate=wins / total if total > 0 else 0.0,
                        success_rate=successes / wins if wins > 0 else 0.0,
                        avg_score=row["avg_score"],
                        best_score=row["best_score"],
                        review_accuracy=None,
                        avg_tokens=row["avg_tokens"] or 0,
                        avg_duration_seconds=None,
                        recent_win_rate=recent_win_rate,
                    )
                )

            return stats

    def get_executor_stats(self, agent: str | None = None) -> list[AgentStats]:
        """Get execution statistics for agents.

        Args:
            agent: Optional agent name to filter. If None, returns all executors.

        Returns:
            List of AgentStats for executors, sorted by win rate descending.
        """
        with self._lock:
            query = """
                SELECT
                    agent,
                    COUNT(*) as total_runs,
                    SUM(was_winner) as wins,
                    SUM(success) as successes,
                    AVG(score) as avg_score,
                    MAX(score) as best_score,
                    AVG(token_usage) as avg_tokens,
                    AVG(duration_seconds) as avg_duration
                FROM execution_records
            """
            params: list = []

            if agent:
                query += " WHERE agent = ?"
                params.append(agent)

            query += " GROUP BY agent ORDER BY CAST(wins AS REAL) / total_runs DESC"

            rows = self._execute(query, params)

            stats = []
            for row in rows:
                total = row["total_runs"] or 1
                wins = row["wins"] or 0
                successes = row["successes"] or 0

                # Get recent win rate (last 10 runs)
                recent_query = """
                    SELECT AVG(was_winner) as recent_rate
                    FROM (
                        SELECT was_winner FROM execution_records
                        WHERE agent = ?
                        ORDER BY timestamp DESC
                        LIMIT 10
                    )
                """
                recent_row = self._execute_one(recent_query, (row["agent"],))
                recent_win_rate = recent_row["recent_rate"] if recent_row else None

                stats.append(
                    AgentStats(
                        agent=row["agent"],
                        role="executor",
                        total_runs=total,
                        wins=wins,
                        successes=successes,
                        win_rate=wins / total if total > 0 else 0.0,
                        success_rate=successes / total if total > 0 else 0.0,
                        avg_score=row["avg_score"],
                        best_score=row["best_score"],
                        review_accuracy=None,
                        avg_tokens=row["avg_tokens"] or 0,
                        avg_duration_seconds=row["avg_duration"],
                        recent_win_rate=recent_win_rate,
                    )
                )

            return stats

    def get_reviewer_stats(self, agent: str | None = None) -> list[AgentStats]:
        """Get review statistics for agents.

        Tracks how accurately reviewers predict winners.

        Args:
            agent: Optional agent name to filter. If None, returns all reviewers.

        Returns:
            List of AgentStats for reviewers, sorted by accuracy descending.
        """
        with self._lock:
            # Review accuracy: did reviewer give highest score to actual winner?
            query = """
                SELECT
                    r.agent,
                    COUNT(DISTINCT r.workflow_id) as total_runs,
                    COUNT(*) as total_reviews,
                    AVG(r.score_given) as avg_score_given,
                    -- Accuracy: how often did they give highest score to winner?
                    AVG(CASE WHEN r.was_candidate_winner THEN 1.0 ELSE 0.0 END) as winner_detection_rate
                FROM review_records r
            """
            params: list = []

            if agent:
                query += " WHERE r.agent = ?"
                params.append(agent)

            query += " GROUP BY r.agent ORDER BY winner_detection_rate DESC"

            rows = self._execute(query, params)

            stats = []
            for row in rows:
                total = row["total_runs"] or 1

                stats.append(
                    AgentStats(
                        agent=row["agent"],
                        role="reviewer",
                        total_runs=total,
                        wins=row["total_reviews"] or 0,  # Total reviews given
                        successes=total,  # N/A for reviewers
                        win_rate=0.0,  # N/A for reviewers
                        success_rate=0.0,  # N/A for reviewers
                        avg_score=row["avg_score_given"],
                        best_score=None,
                        review_accuracy=row["winner_detection_rate"],
                        avg_tokens=0,
                        avg_duration_seconds=None,
                        recent_win_rate=None,
                    )
                )

            return stats

    def get_best_planners(self, limit: int = 5) -> list[AgentStats]:
        """Get top planners by win rate.

        Args:
            limit: Maximum number of planners to return.

        Returns:
            List of AgentStats for top planners.
        """
        stats = self.get_planner_stats()
        return stats[:limit]

    def get_best_executors(self, limit: int = 5) -> list[AgentStats]:
        """Get top executors by win rate.

        Args:
            limit: Maximum number of executors to return.

        Returns:
            List of AgentStats for top executors.
        """
        stats = self.get_executor_stats()
        return stats[:limit]

    def get_leaderboard(self) -> dict[str, list[AgentStats]]:
        """Get complete leaderboard for all roles.

        Returns:
            Dict with keys 'planners', 'executors', 'reviewers'.
        """
        return {
            "planners": self.get_planner_stats(),
            "executors": self.get_executor_stats(),
            "reviewers": self.get_reviewer_stats(),
        }

    def get_workflow_count(self) -> int:
        """Get total number of tracked workflows."""
        with self._lock:
            try:
                row = self._execute_one("SELECT COUNT(*) as cnt FROM workflows")
                return row["cnt"] if row else 0
            except Exception:
                # Table might not exist yet
                return 0

    def clear_all(self) -> int:
        """Clear all tracking data.

        Returns:
            Number of workflows that were deleted.
        """
        with self._lock:
            count = self.get_workflow_count()
            conn = self._get_conn()

            # Delete in order to respect foreign key relationships
            # Use try-catch or ensure tables exist first
            tables = [
                "review_records",
                "execution_records",
                "planning_records",
                "refinement_iterations",
                "workflows",
            ]
            for table in tables:
                try:
                    conn.execute(f"DELETE FROM {table}")
                except Exception:
                    pass

            if not self._use_duckdb:
                conn.commit()

            return count

    def get_recent_workflows(self, limit: int = 10) -> list[WorkflowRecord]:
        """Get recent workflow records.

        Args:
            limit: Maximum number of workflows to return.

        Returns:
            List of WorkflowRecords, most recent first.
        """
        with self._lock:
            try:
                rows = self._execute(
                    """
                    SELECT * FROM workflows
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (limit,),
                )

                return [
                    WorkflowRecord(
                        workflow_id=row["workflow_id"],
                        task_hash=row["task_hash"],
                        task_preview=row["task_preview"],
                        success=bool(row["success"]),
                        total_duration_seconds=row["total_duration_seconds"],
                        total_tokens=row["total_tokens"],
                        total_cost_usd=row["total_cost_usd"],
                        selected_planner=row["selected_planner"],
                        winning_executor=row["winning_executor"],
                        refinement_triggered=bool(row["refinement_triggered"]),
                        final_score=row["final_score"],
                        initial_score=row.get("initial_score"),  # Handle missing if column just added
                        refinement_token_usage=row.get("refinement_token_usage", 0),
                        timestamp=datetime.fromisoformat(row["timestamp"]),
                    )
                    for row in rows
                ]
            except Exception:
                return []

    def export_stats(self) -> dict:
        """Export all statistics as a dictionary.

        Returns:
            Dict containing all tracking data.
        """
        leaderboard = self.get_leaderboard()

        return {
            "total_workflows": self.get_workflow_count(),
            "planners": [
                {
                    "agent": s.agent,
                    "total_runs": s.total_runs,
                    "wins": s.wins,
                    "win_rate": s.win_rate,
                    "success_rate": s.success_rate,
                    "avg_score": s.avg_score,
                    "recent_win_rate": s.recent_win_rate,
                }
                for s in leaderboard["planners"]
            ],
            "executors": [
                {
                    "agent": s.agent,
                    "total_runs": s.total_runs,
                    "wins": s.wins,
                    "win_rate": s.win_rate,
                    "success_rate": s.success_rate,
                    "avg_score": s.avg_score,
                    "avg_duration_seconds": s.avg_duration_seconds,
                    "recent_win_rate": s.recent_win_rate,
                }
                for s in leaderboard["executors"]
            ],
            "reviewers": [
                {
                    "agent": s.agent,
                    "total_runs": s.total_runs,
                    "review_accuracy": s.review_accuracy,
                    "avg_score_given": s.avg_score,
                }
                for s in leaderboard["reviewers"]
            ],
        }
