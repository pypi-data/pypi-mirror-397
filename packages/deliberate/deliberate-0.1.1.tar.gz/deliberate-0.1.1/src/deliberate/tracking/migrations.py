"""Database migration system for deliberate tracking.

Handles schema versioning and applying SQL migrations.
"""

import logging
from typing import Any, Protocol


# Define protocol for connection to support both DuckDB and SQLite
class DBConnection(Protocol):
    def execute(self, query: str, parameters: tuple | list | None = None) -> Any: ...
    def executescript(self, script: str) -> Any: ...  # SQLite only
    def commit(self) -> None: ...
    def close(self) -> None: ...


logger = logging.getLogger(__name__)

# Migration scripts
# Dict mapping version number to SQL script
MIGRATIONS = {
    1: """
    -- Initial Schema (Consolidated from tracker.py)
    CREATE SEQUENCE IF NOT EXISTS seq_workflows;
    CREATE SEQUENCE IF NOT EXISTS seq_planning;
    CREATE SEQUENCE IF NOT EXISTS seq_execution;
    CREATE SEQUENCE IF NOT EXISTS seq_review;

    CREATE TABLE IF NOT EXISTS workflows (
        id INTEGER PRIMARY KEY DEFAULT nextval('seq_workflows'),
        workflow_id TEXT UNIQUE NOT NULL,
        task_hash TEXT NOT NULL,
        task_preview TEXT,
        success INTEGER NOT NULL,
        total_duration_seconds DOUBLE,
        total_tokens INTEGER,
        total_cost_usd DOUBLE,
        selected_planner TEXT,
        winning_executor TEXT,
        refinement_triggered INTEGER DEFAULT 0,
        final_score DOUBLE,
        initial_score DOUBLE,
        refinement_token_usage INTEGER DEFAULT 0,
        timestamp TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS planning_records (
        id INTEGER PRIMARY KEY DEFAULT nextval('seq_planning'),
        workflow_id TEXT NOT NULL,
        agent TEXT NOT NULL,
        was_selected INTEGER NOT NULL,
        led_to_success INTEGER NOT NULL,
        final_score DOUBLE,
        token_usage INTEGER,
        timestamp TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS execution_records (
        id INTEGER PRIMARY KEY DEFAULT nextval('seq_execution'),
        workflow_id TEXT NOT NULL,
        agent TEXT NOT NULL,
        was_winner INTEGER NOT NULL,
        success INTEGER NOT NULL,
        error_category TEXT,
        score DOUBLE,
        rank INTEGER,
        total_candidates INTEGER,
        token_usage INTEGER,
        duration_seconds DOUBLE,
        timestamp TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS review_records (
        id INTEGER PRIMARY KEY DEFAULT nextval('seq_review'),
        workflow_id TEXT NOT NULL,
        agent TEXT NOT NULL,
        candidate_id TEXT NOT NULL,
        score_given DOUBLE NOT NULL,
        review_comment TEXT,
        was_candidate_winner INTEGER NOT NULL,
        final_winner_score DOUBLE,
        timestamp TEXT NOT NULL
    );

    CREATE INDEX IF NOT EXISTS idx_planning_agent ON planning_records(agent);
    CREATE INDEX IF NOT EXISTS idx_execution_agent ON execution_records(agent);
    CREATE INDEX IF NOT EXISTS idx_review_agent ON review_records(agent);
    CREATE INDEX IF NOT EXISTS idx_workflows_timestamp ON workflows(timestamp);
    """,
    2: """
    -- Enhanced tracking: Prompts, Refinement, Configs

    ALTER TABLE execution_records ADD COLUMN prompt TEXT;
    ALTER TABLE planning_records ADD COLUMN prompt TEXT;

    CREATE TABLE IF NOT EXISTS agent_configs (
        id VARCHAR PRIMARY KEY,
        agent_name VARCHAR NOT NULL,
        config_json JSON,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    ALTER TABLE planning_records ADD COLUMN config_id VARCHAR;
    ALTER TABLE execution_records ADD COLUMN config_id VARCHAR;
    ALTER TABLE review_records ADD COLUMN config_id VARCHAR;

    -- Add sequences for new tables if needed, or use UUIDs/auto-increment
    CREATE SEQUENCE IF NOT EXISTS seq_refinement;

    CREATE TABLE IF NOT EXISTS refinement_iterations (
        id INTEGER PRIMARY KEY DEFAULT nextval('seq_refinement'),
        workflow_id VARCHAR NOT NULL,
        iteration_num INTEGER NOT NULL,
        candidate_id VARCHAR,
        pre_refinement_score DOUBLE,
        post_refinement_score DOUBLE,
        diff TEXT,
        feedback TEXT,
        token_usage INTEGER,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_refinement_workflow ON refinement_iterations(workflow_id);
    """,
    3: """
    -- Session State Unification (from mcp_server/state.py)

    CREATE TABLE IF NOT EXISTS session_messages (
        id VARCHAR PRIMARY KEY,
        session_id VARCHAR NOT NULL,
        agent VARCHAR NOT NULL,
        type VARCHAR NOT NULL,
        content JSON NOT NULL,
        reply_to VARCHAR,
        visibility VARCHAR DEFAULT 'all',
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        resolved BOOLEAN DEFAULT FALSE,
        resolution VARCHAR
    );

    CREATE TABLE IF NOT EXISTS session_agents (
        name VARCHAR PRIMARY KEY,
        session_id VARCHAR NOT NULL,
        role VARCHAR NOT NULL,
        status VARCHAR DEFAULT 'idle',
        worktree_path VARCHAR,
        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Rename/merge votes from session state if needed, or keep separate
    -- Session votes are distinct from ReviewRecords (which are formal jury votes)
    CREATE TABLE IF NOT EXISTS session_votes (
        id VARCHAR PRIMARY KEY,
        message_id VARCHAR NOT NULL,
        voter VARCHAR NOT NULL,
        score DOUBLE NOT NULL,
        reasoning VARCHAR,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_messages_session ON session_messages(session_id);
    """,
    4: """
    -- Unified Feedback Memory ("Blackboard")
    -- Consolidates iteration.SolutionHistory and evolution.ProgramDatabase
    -- into a single persistent knowledge base

    CREATE SEQUENCE IF NOT EXISTS seq_solutions;

    CREATE TABLE IF NOT EXISTS solutions (
        id VARCHAR PRIMARY KEY,
        workflow_id VARCHAR,
        task_hash VARCHAR NOT NULL,
        task_embedding FLOAT[],  -- Nullable vector for future semantic search
        task_preview TEXT,
        code_content TEXT,
        diff_applied TEXT,
        solution_type VARCHAR NOT NULL,  -- 'iteration_attempt' | 'evolution_program'
        agent VARCHAR NOT NULL,
        success BOOLEAN NOT NULL,
        overall_score DOUBLE NOT NULL,
        test_score DOUBLE,
        tests_passed INTEGER,
        tests_total INTEGER,
        lint_score DOUBLE,
        runtime_ms DOUBLE,
        memory_mb DOUBLE,
        needs_optimization BOOLEAN DEFAULT FALSE,
        performance_issue VARCHAR,  -- 'none' | 'slow_execution' | 'high_memory' | 'timeout'
        feedback_summary TEXT,
        error_message TEXT,
        parent_solution_id VARCHAR,
        inspiration_ids JSON,  -- Array of solution IDs used as inspiration
        generation INTEGER DEFAULT 0,
        is_valid BOOLEAN DEFAULT FALSE,
        is_champion BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        evaluated_at TIMESTAMP,
        token_usage INTEGER,
        duration_seconds DOUBLE,
        tags JSON  -- Array of string tags for filtering
    );

    -- Niche storage for MAP-Elites style population management
    CREATE TABLE IF NOT EXISTS solution_niches (
        niche_key VARCHAR PRIMARY KEY,
        solution_id VARCHAR NOT NULL,
        dimensions JSON NOT NULL,  -- {"test_score": 0.8, "runtime_ms": 100, ...}
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Performance indexes
    CREATE INDEX IF NOT EXISTS idx_solutions_task_hash ON solutions(task_hash);
    CREATE INDEX IF NOT EXISTS idx_solutions_workflow ON solutions(workflow_id);
    CREATE INDEX IF NOT EXISTS idx_solutions_score ON solutions(overall_score DESC);
    CREATE INDEX IF NOT EXISTS idx_solutions_champion ON solutions(is_champion);
    CREATE INDEX IF NOT EXISTS idx_solutions_type ON solutions(solution_type);
    CREATE INDEX IF NOT EXISTS idx_solutions_agent ON solutions(agent);
    CREATE INDEX IF NOT EXISTS idx_solution_niches_solution ON solution_niches(solution_id);
    """,
}


class Migrator:
    """Handles database migrations."""

    def __init__(self, conn: DBConnection, is_duckdb: bool = True):
        self.conn = conn
        self.is_duckdb = is_duckdb

    def _init_version_table(self):
        """Ensure schema_version table exists."""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        if not self.is_duckdb:
            self.conn.commit()

    def get_current_version(self) -> int:
        """Get the current schema version."""
        self._init_version_table()
        try:
            result = self.conn.execute("SELECT MAX(version) FROM schema_version")
            if self.is_duckdb:
                row = result.fetchone()
                return row[0] if row and row[0] is not None else 0
            else:
                row = result.fetchone()
                return row[0] if row and row[0] is not None else 0
        except Exception:
            return 0

    def migrate(self):
        """Apply pending migrations."""
        current_version = self.get_current_version()
        latest_version = max(MIGRATIONS.keys())

        if current_version >= latest_version:
            return

        logger.info(f"Migrating database from version {current_version} to {latest_version}")

        for version in range(current_version + 1, latest_version + 1):
            script = MIGRATIONS[version]
            if not self.is_duckdb:
                # SQLite adjustment: sequences and JSON might need tweaks
                # For now, we assume the script is compatible or we modify it for SQLite
                # Simple replacement for sequences in SQLite: AUTOINCREMENT handles it
                # JSON type in SQLite is just TEXT usually, or handled by extension
                # This basic replacer is fragile but sufficient for this specific schema
                script = script.replace("DEFAULT nextval('seq_workflows')", "AUTOINCREMENT")
                script = script.replace("DEFAULT nextval('seq_planning')", "AUTOINCREMENT")
                script = script.replace("DEFAULT nextval('seq_execution')", "AUTOINCREMENT")
                script = script.replace("DEFAULT nextval('seq_review')", "AUTOINCREMENT")
                script = script.replace("DEFAULT nextval('seq_refinement')", "AUTOINCREMENT")
                script = script.replace("DEFAULT nextval('seq_solutions')", "AUTOINCREMENT")
                script = script.replace("JSON", "TEXT")  # SQLite doesn't have native JSON
                script = script.replace("DOUBLE", "REAL")
                script = script.replace("FLOAT[]", "TEXT")  # SQLite: store as JSON string
                # Remove CREATE SEQUENCE statements for SQLite
                import re

                script = re.sub(r"CREATE SEQUENCE.*?;", "", script, flags=re.DOTALL)

            try:
                if self.is_duckdb:
                    self.conn.execute(script)
                else:
                    self.conn.executescript(script)

                self.conn.execute("INSERT INTO schema_version (version) VALUES (?)", (version,))
                if not self.is_duckdb:
                    self.conn.commit()
                logger.info(f"Applied migration {version}")
            except Exception as e:
                logger.error(f"Migration {version} failed: {e}")
                raise
