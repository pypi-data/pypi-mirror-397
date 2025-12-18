"""Session state management with DuckDB persistence.

Manages agent Q&A, discussion history, and voting using DuckDB.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

try:
    import duckdb  # noqa: F401
except ImportError:
    pass


class MessageType(Enum):
    """Type of message in the discussion."""

    QUESTION = "question"
    ANSWER = "answer"
    DISCUSSION = "discussion"
    STATUS = "status"


@dataclass
class Message:
    """A message in the discussion."""

    id: str
    session_id: str
    agent: str
    type: MessageType
    content: dict[str, Any]
    reply_to: str | None
    visibility: str
    timestamp: datetime
    resolved: bool = False
    resolution: str | None = None


@dataclass
class RegisteredAgent:
    """An agent registered in the session."""

    name: str
    role: str  # planner, executor, reviewer
    status: str  # idle, working, blocked
    worktree_path: str | None
    joined_at: datetime
    last_seen: datetime


class SessionState:
    """Manages session state using a shared DuckDB connection.

    Tracks questions, answers, discussion, and agent registrations.
    """

    def __init__(self, session_id: str, connection: Any | None = None):
        """Initialize session state.

        Args:
            session_id: Unique session identifier
            connection: Shared database connection (DuckDB or SQLite). If None, uses in-memory SQLite.
        """
        import sqlite3

        self.session_id = session_id
        self.conn = connection or sqlite3.connect(":memory:")
        # Schema is now managed by global migrations in tracking/migrations.py

    def register_agent(
        self,
        name: str,
        role: str,
        status: str = "idle",
        worktree_path: str | None = None,
    ):
        """Register an agent in the session.

        Args:
            name: Agent name
            role: Agent role (planner, executor, reviewer)
            status: Initial status (default: idle)
            worktree_path: Path to agent's worktree if any
        """
        # SQLite doesn't support INSERT OR REPLACE syntax exactly like DuckDB in all contexts,
        # but standardized SQL is INSERT INTO ... ON CONFLICT DO UPDATE
        try:
            self.conn.execute(
                """
                INSERT INTO session_agents (name, session_id, role, status, worktree_path)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT (name) DO UPDATE SET
                    session_id = EXCLUDED.session_id,
                    role = EXCLUDED.role,
                    status = EXCLUDED.status,
                    worktree_path = EXCLUDED.worktree_path,
                    last_seen = CURRENT_TIMESTAMP
            """,
                [name, self.session_id, role, status, worktree_path],
            )
        except Exception:
            # Fallback for SQLite if ON CONFLICT syntax differs or other issues
            # Using INSERT OR REPLACE which is common in SQLite
            self.conn.execute(
                """
                INSERT OR REPLACE INTO session_agents (name, session_id, role, status, worktree_path)
                VALUES (?, ?, ?, ?, ?)
            """,
                [name, self.session_id, role, status, worktree_path],
            )

        if hasattr(self.conn, "commit"):
            self.conn.commit()

    def update_agent_status(self, name: str, status: str):
        """Update agent status.

        Args:
            name: Agent name
            status: New status
        """
        self.conn.execute(
            """
            UPDATE session_agents
            SET status = ?, last_seen = CURRENT_TIMESTAMP
            WHERE name = ?
        """,
            [status, name],
        )
        if hasattr(self.conn, "commit"):
            self.conn.commit()

    def get_agents(self, role: str | None = None, status: str | None = None) -> list[RegisteredAgent]:
        """Get registered agents.

        Args:
            role: Filter by role (optional)
            status: Filter by status (optional)

        Returns:
            List of registered agents
        """
        query = (
            "SELECT name, role, status, worktree_path, joined_at, last_seen FROM session_agents WHERE session_id = ?"
        )
        params = [self.session_id]

        if role:
            query += " AND role = ?"
            params.append(role)

        if status:
            query += " AND status = ?"
            params.append(status)

        result = self.conn.execute(query, params).fetchall()

        # Handle different result formats (DuckDB returns objects/tuples depending on config, SQLite tuples)
        # Assuming tuples here based on typical Python DBAPI
        return [
            RegisteredAgent(
                name=row[0],
                role=row[1],
                status=row[2],
                worktree_path=row[3],
                # Handle timestamp parsing if needed, depending on driver return type
                joined_at=row[4] if isinstance(row[4], datetime) else datetime.fromisoformat(str(row[4])),
                last_seen=row[5] if isinstance(row[5], datetime) else datetime.fromisoformat(str(row[5])),
            )
            for row in result
        ]

    def add_question(
        self,
        agent: str,
        question: str,
        category: str,
        context: str | None = None,
        suggestions: list[str] | None = None,
        urgency: str = "medium",
    ) -> str:
        """Add a question to the session.

        Args:
            agent: Agent asking the question
            question: Question text
            category: Question category (factual, clarification, decision, blocked)
            context: Additional context
            suggestions: Suggested answers
            urgency: Question urgency (low, medium, high)

        Returns:
            Question message ID
        """
        msg_id = f"q-{uuid.uuid4().hex[:8]}"

        content = {
            "question": question,
            "category": category,
            "context": context,
            "suggestions": suggestions or [],
            "urgency": urgency,
        }

        self.conn.execute(
            """
            INSERT INTO session_messages (id, session_id, agent, type, content, visibility)
            VALUES (?, ?, ?, ?, ?, 'all')
        """,
            [msg_id, self.session_id, agent, MessageType.QUESTION.value, json.dumps(content)],
        )
        if hasattr(self.conn, "commit"):
            self.conn.commit()

        return msg_id

    def add_answer(
        self,
        agent: str,
        question_id: str,
        answer: str,
        confidence: float = 0.7,
    ) -> str:
        """Add an answer to a question.

        Args:
            agent: Agent providing the answer
            question_id: ID of question being answered
            answer: Answer text
            confidence: Confidence level (0.0 to 1.0)

        Returns:
            Answer message ID
        """
        msg_id = f"a-{uuid.uuid4().hex[:8]}"

        content = {
            "answer": answer,
            "confidence": confidence,
        }

        self.conn.execute(
            """
            INSERT INTO session_messages (id, session_id, agent, type, content, reply_to, visibility)
            VALUES (?, ?, ?, ?, ?, ?, 'all')
        """,
            [
                msg_id,
                self.session_id,
                agent,
                MessageType.ANSWER.value,
                json.dumps(content),
                question_id,
            ],
        )
        if hasattr(self.conn, "commit"):
            self.conn.commit()

        return msg_id

    def get_question(self, question_id: str) -> dict[str, Any] | None:
        """Get a specific question.

        Args:
            question_id: Question message ID

        Returns:
            Question data or None if not found
        """
        result = self.conn.execute(
            """
            SELECT id, agent, content, timestamp, resolved, resolution
            FROM session_messages
            WHERE id = ? AND type = 'question'
        """,
            [question_id],
        ).fetchone()

        if not result:
            return None

        return {
            "id": result[0],
            "agent": result[1],
            "content": json.loads(result[2]),
            "timestamp": result[3] if isinstance(result[3], datetime) else datetime.fromisoformat(str(result[3])),
            "resolved": bool(result[4]),
            "resolution": result[5],
        }

    def get_pending_questions(self) -> list[dict[str, Any]]:
        """Get unresolved questions.

        Returns:
            List of pending questions
        """
        # SQLite uses 0/1 for booleans usually
        result = self.conn.execute(
            """
            SELECT id, agent, content, timestamp
            FROM session_messages
            WHERE session_id = ?
              AND type = 'question'
              AND (resolved = FALSE OR resolved = 0)
            ORDER BY timestamp ASC
        """,
            [self.session_id],
        ).fetchall()

        return [
            {
                "id": row[0],
                "agent": row[1],
                "content": json.loads(row[2]),
                "timestamp": row[3] if isinstance(row[3], datetime) else datetime.fromisoformat(str(row[3])),
            }
            for row in result
        ]

    def get_answers_for_question(self, question_id: str) -> list[dict[str, Any]]:
        """Get all answers for a question.

        Args:
            question_id: Question message ID

        Returns:
            List of answers with vote scores
        """
        result = self.conn.execute(
            """
            SELECT m.id, m.agent, m.content, m.timestamp,
                   COALESCE(AVG(v.score), 0) as avg_score,
                   COUNT(v.id) as vote_count
            FROM session_messages m
            LEFT JOIN session_votes v ON v.message_id = m.id
            WHERE m.session_id = ?
              AND m.type = 'answer'
              AND m.reply_to = ?
            GROUP BY m.id, m.agent, m.content, m.timestamp
            ORDER BY avg_score DESC
        """,
            [self.session_id, question_id],
        ).fetchall()

        return [
            {
                "id": row[0],
                "agent": row[1],
                "content": json.loads(row[2]),
                "timestamp": row[3] if isinstance(row[3], datetime) else datetime.fromisoformat(str(row[3])),
                "avg_score": row[4],
                "vote_count": row[5],
            }
            for row in result
        ]

    def resolve_question(self, question_id: str, resolution: str):
        """Mark a question as resolved.

        Args:
            question_id: Question message ID
            resolution: Resolution text (the accepted answer)
        """
        self.conn.execute(
            """
            UPDATE session_messages
            SET resolved = TRUE, resolution = ?
            WHERE id = ?
        """,
            [resolution, question_id],
        )
        if hasattr(self.conn, "commit"):
            self.conn.commit()

    def get_discussion_history(
        self,
        include_resolved: bool = True,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Get discussion history.

        Args:
            include_resolved: Include resolved questions
            limit: Maximum number of messages

        Returns:
            List of messages in chronological order
        """
        query = """
            SELECT id, agent, type, content, reply_to, timestamp, resolved, resolution
            FROM session_messages
            WHERE session_id = ?
        """
        params = [self.session_id]

        if not include_resolved:
            query += " AND (resolved = FALSE OR resolved = 0 OR type != 'question')"

        query += " ORDER BY timestamp ASC LIMIT ?"
        params.append(limit)

        result = self.conn.execute(query, params).fetchall()

        return [
            {
                "id": row[0],
                "agent": row[1],
                "type": row[2],
                "content": json.loads(row[3]),
                "reply_to": row[4],
                "timestamp": row[5] if isinstance(row[5], datetime) else datetime.fromisoformat(str(row[5])),
                "resolved": bool(row[6]),
                "resolution": row[7],
            }
            for row in result
        ]

    def close(self):
        """Close database connection (no-op as it's shared)."""
        pass

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
