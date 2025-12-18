"""MCP server for orchestrator functions.

This server exposes orchestrator functions that agents can call via MCP protocol.
It provides a unified interface for agents to:
- Report status and progress updates
- Ask questions with intelligent routing (user, agents, or auto-answer)
- Coordinate with the orchestrator during execution

Uses FastMCP for automatic HTTP/SSE transport handling.
Agent identity is determined via Bearer token authentication - each agent gets
a unique token, and ctx.client_id provides the agent name in tool handlers.
Session state is persisted in DuckDB for questions, answers, and agent registry.
"""

from __future__ import annotations

import asyncio
import contextvars
import logging
import secrets
import socket
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Annotated, Any, Literal, cast

import uvicorn
from mcp.server.auth.provider import AccessToken
from mcp.server.auth.settings import AuthSettings
from mcp.server.fastmcp import Context, FastMCP
from pydantic import AnyHttpUrl, Field

from deliberate.mcp_server.routing import QuestionRouter, RouteTarget
from deliberate.mcp_server.state import SessionState

# Context variable to pass authenticated agent name from verify_token to tool handlers
# This is a workaround because FastMCP doesn't propagate AccessToken.client_id to ctx.client_id
_current_agent: contextvars.ContextVar[str | None] = contextvars.ContextVar("current_agent", default=None)

logger = logging.getLogger(__name__)


class AgentTokenVerifier:
    """Token verifier that maps Bearer tokens to agent names.

    Each agent is issued a unique token at orchestration startup.
    When an agent calls an MCP tool, the token is verified and the
    agent name becomes available via ctx.client_id.
    """

    def __init__(self):
        self.tokens: dict[str, str] = {}  # token -> agent_name

    def create_token(self, agent_name: str) -> str:
        """Create a unique token for an agent.

        Args:
            agent_name: Name of the agent (e.g., 'claude', 'codex', 'gemini')

        Returns:
            Bearer token string
        """
        token = secrets.token_urlsafe(32)
        self.tokens[token] = agent_name
        return token

    def get_agent_name(self, token: str) -> str | None:
        """Get agent name for a token."""
        return self.tokens.get(token)

    def add_static_token(self, token: str, agent_name: str) -> None:
        """Add a pre-shared static token for an agent.

        Use this for agents that use global MCP configuration (like Codex)
        where the token must be known in advance and stored in an env var.

        Args:
            token: The pre-shared bearer token
            agent_name: Name of the agent this token authenticates
        """
        self.tokens[token] = agent_name

    async def verify_token(self, token: str) -> AccessToken | None:
        """Verify a Bearer token and return AccessToken with agent as client_id.

        This method is called by FastMCP's auth middleware for each request.
        Also sets the _current_agent context var as a workaround for ctx.client_id.
        """
        agent_name = self.tokens.get(token)
        if agent_name:
            logger.info(f"[MCP AUTH] Token verified for agent: {agent_name}")
            # Set context var as workaround since FastMCP doesn't propagate client_id
            _current_agent.set(agent_name)
            return AccessToken(
                token=token,
                client_id=agent_name,  # This should become ctx.client_id but doesn't work in FastMCP
                scopes=["update_status", "ask_question"],
            )
        logger.warning(f"[MCP AUTH] Token verification FAILED: {token[:20]}...")
        return None


@dataclass
class StatusUpdate:
    """Status update from an agent."""

    agent_name: str
    phase: str  # planning, execution, review, refinement
    status: str  # started, progress, completed, error
    message: str
    timestamp: datetime
    metadata: dict[str, Any] | None = None
    attachments: list[dict[str, Any]] | None = None


class OrchestratorServer:
    """MCP server for orchestrator functions.

    Exposes tools that agents can call to interact with the orchestrator.
    Provides status updates and intelligent question routing with DuckDB persistence.
    Agent identity is determined via Bearer token authentication.
    """

    def __init__(
        self,
        db_connection: Any | None = None,  # Shared DuckDB/SQLite connection
        agent_names: list[str] | None = None,
        callback: Callable[[StatusUpdate], None] | None = None,
        question_callback: Callable[[str, str], str] | None = None,
        session_id: str | None = None,
        host: str = "127.0.0.1",
        port: int = 0,  # 0 = auto-select available port
        disable_auth: bool = False,  # Disable bearer token auth
        static_tokens: dict[str, str] | None = None,  # Pre-shared tokens: agent_name -> token
    ):
        """Initialize the orchestrator MCP server.

        Args:
            db_connection: Shared database connection (optional).
            agent_names: List of agent names to generate tokens for.
            callback: Function to call when status updates are received
            question_callback: Function to call to ask user a question
            session_id: Session ID for state persistence (default: auto-generated)
            host: Host to bind the server to
            port: Port to bind the server to (0 for auto-select)
            disable_auth: Disable bearer token authentication (for agents that can't pass dynamic tokens)
            static_tokens: Pre-shared tokens for agents using global MCP config (e.g., Codex).
                           Maps agent_name -> token. These tokens are added in addition to
                           dynamically generated tokens for agent_names.
        """
        self.callback = callback
        self.question_callback = question_callback
        self.updates: list[StatusUpdate] = []
        self.host = host
        self.port = port
        self.actual_port: int | None = None

        # Use provided connection or create a new in-memory one
        if db_connection is None:
            try:
                import duckdb

                self._db_conn = duckdb.connect(":memory:")
                is_duckdb = True
            except ImportError:
                import sqlite3

                self._db_conn = sqlite3.connect(":memory:")
                self._db_conn.row_factory = sqlite3.Row
                is_duckdb = False

            # Apply migrations for standalone mode
            from deliberate.tracking.migrations import DBConnection, Migrator

            Migrator(cast(DBConnection, self._db_conn), is_duckdb).migrate()
        else:
            self._db_conn = db_connection

        # Initialize session state using shared connection
        self.session_id = session_id or f"session-{uuid.uuid4().hex[:8]}"
        self.session = SessionState(self.session_id, self._db_conn)
        self.router = QuestionRouter(self.session)

        # Setup token auth if agent names provided and auth not disabled
        self.token_verifier: AgentTokenVerifier | None = None
        self.agent_tokens: dict[str, str] = {}  # agent_name -> token
        self.disable_auth = disable_auth

        # Determine if we need auth: either dynamic agents or static tokens
        needs_auth = (agent_names and not disable_auth) or static_tokens

        if needs_auth:
            self.token_verifier = AgentTokenVerifier()

            # Add dynamically generated tokens for agent_names
            if agent_names and not disable_auth:
                for name in agent_names:
                    token = self.token_verifier.create_token(name)
                    self.agent_tokens[name] = token

            # Add pre-shared static tokens (e.g., for Codex global config)
            if static_tokens:
                for agent_name, token in static_tokens.items():
                    self.token_verifier.add_static_token(token, agent_name)
                    self.agent_tokens[agent_name] = token

            # Create FastMCP with auth
            base_url = f"http://{host}:{port or 9393}"
            auth_settings = AuthSettings(
                issuer_url=cast(AnyHttpUrl, base_url),
                resource_server_url=cast(AnyHttpUrl, base_url),
            )
            self.mcp = FastMCP(
                "deliberate-orchestrator",
                token_verifier=self.token_verifier,
                auth=auth_settings,
            )
        else:
            # No auth - backwards compatible mode or auth disabled
            self.mcp = FastMCP("deliberate-orchestrator")

        # Register tools
        self._register_tools()

    def _register_tools(self):
        """Register MCP tools using FastMCP decorators."""

        @self.mcp.tool()
        async def update_status(
            phase: Annotated[
                Literal["planning", "execution", "review", "refinement"],
                Field(description="Current workflow phase"),
            ],
            status: Annotated[
                Literal["started", "progress", "completed", "error"],
                Field(description="Status: started, progress, completed, or error"),
            ],
            message: Annotated[
                str,
                Field(description="Brief description of what you're doing or just accomplished"),
            ],
            ctx: Context,
            metadata: Annotated[
                dict[str, Any] | None,
                Field(description="Optional extra info like files_created, tests_passed, etc."),
            ] = None,
            attachments: Annotated[
                list[dict[str, Any]] | None,
                Field(description="Optional attachments (image, diff, etc.)"),
            ] = None,
            agent_name_override: Annotated[
                str | None,
                Field(description="Optional explicit agent name override"),
            ] = None,
        ) -> str:
            """Report your progress to the user watching your work.

            IMPORTANT: Call this at key milestones. You're running in a multi-agent
            orchestration and users cannot see your internal progress otherwise.

            Call when you: start a task, complete a step, finish work, or hit an error.

            Your agent identity is automatic from authentication.
            """
            logger.info(
                "[MCP TOOL] update_status called: phase=%s, status=%s, message=%s...",
                phase,
                status,
                message[:50],
            )

            # Get agent name from auth context, context var workaround, or fallback
            agent_name = agent_name_override or ctx.client_id or _current_agent.get() or "unknown"
            logger.info(
                "[MCP TOOL] Agent name resolved: %s (ctx.client_id=%s, context_var=%s)",
                agent_name,
                ctx.client_id,
                _current_agent.get(),
            )

            # Create status update
            update = StatusUpdate(
                agent_name=agent_name,
                phase=phase,
                status=status,
                message=message,
                timestamp=datetime.now(),
                metadata=metadata,
                attachments=attachments,
            )

            # Store update
            self.updates.append(update)

            # Call callback if provided
            if self.callback:
                self.callback(update)

            return f"Status update received: {status} - {message}"

        @self.mcp.tool()
        async def ask_question(
            question: Annotated[str, Field(description="The question you need answered")],
            ctx: Context,
            category: Annotated[
                Literal["factual", "clarification", "decision", "blocked"],
                Field(description="Question type: factual, clarification, decision, or blocked"),
            ] = "clarification",
            context: Annotated[str | None, Field(description="Additional context to help answer the question")] = None,
            suggestions: Annotated[
                list[str] | None,
                Field(description="Your suggested answers - first one may be auto-selected for low urgency"),
            ] = None,
            urgency: Annotated[
                Literal["low", "medium", "high"],
                Field(description="low/medium may auto-answer from suggestions; high always asks user"),
            ] = "medium",
        ) -> str:
            """Ask a question with intelligent routing.

            Routes based on urgency and available agents:
            - low/medium with suggestions: auto-answers with first suggestion
            - Other executor agents available: asks them
            - Otherwise: escalates to human user

            Your agent identity is automatic from authentication.
            """
            # Get agent name from auth context or context var workaround
            agent_name = ctx.client_id or _current_agent.get() or "unknown"
            # Add question to session state
            question_data = {
                "question": question,
                "category": category,
                "context": context,
                "suggestions": suggestions or [],
                "urgency": urgency,
            }

            question_id = self.session.add_question(
                agent=agent_name,
                question=question,
                category=category,
                context=context,
                suggestions=suggestions,
                urgency=urgency,
            )

            # Route the question
            decision = self.router.route(asking_agent=agent_name, question=question_data)

            # Log routing decision
            if self.callback:
                update = StatusUpdate(
                    agent_name=agent_name,
                    phase="execution",
                    status="progress",
                    message=f"Question: {question}",
                    timestamp=datetime.now(),
                    metadata={
                        "type": "question",
                        "question": question,
                        "question_id": question_id,
                        "routing": decision.target.value,
                        "routing_reason": decision.reason,
                    },
                )
                self.callback(update)

            # Execute routing decision
            answer: str
            if decision.target == RouteTarget.AUTO:
                # Use first suggestion
                answer = suggestions[0] if suggestions else "No suggestion available"
                self.session.add_answer(
                    agent="auto",
                    question_id=question_id,
                    answer=answer,
                    confidence=0.6,
                )

            elif decision.target == RouteTarget.AGENTS:
                # Ask other agents
                # For now, return a message indicating agents should be consulted
                # Full implementation would require async message passing to agents
                agent_list = ", ".join(decision.agents or [])
                answer = f"Question routed to agents: {agent_list}. (Full agent-to-agent messaging not yet implemented)"
                self.session.add_answer(
                    agent="router",
                    question_id=question_id,
                    answer=answer,
                    confidence=0.5,
                )

            elif decision.target == RouteTarget.USER:
                # Ask the human user
                if self.question_callback:
                    answer = self.question_callback(agent_name, question)
                    self.session.add_answer(
                        agent="user",
                        question_id=question_id,
                        answer=answer,
                        confidence=1.0,
                    )
                else:
                    answer = "No user prompt handler configured. Please answer: " + question
                    self.session.add_answer(
                        agent="system",
                        question_id=question_id,
                        answer=answer,
                        confidence=0.0,
                    )

            else:
                answer = "Unknown routing target"

            # Resolve question with answer
            self.session.resolve_question(question_id, answer)

            return answer

    def _find_free_port(self) -> int:
        """Find an available port to bind to.

        Returns:
            Available port number
        """
        if self.port != 0:
            return self.port

        # Auto-select a free port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            s.listen(1)
            port = s.getsockname()[1]
        return port

    async def run(self) -> None:
        """Run the MCP server using FastMCP's built-in transport."""
        # Find available port
        self.actual_port = self._find_free_port()

        # Run FastMCP server
        config = uvicorn.Config(
            self.mcp.sse_app(),
            host=self.host,
            port=self.actual_port,
            log_level="warning",
            access_log=False,
            lifespan="off",  # avoid lifespan CancelledError spam on shutdown
        )
        self._server = uvicorn.Server(config)
        try:
            await self._server.serve()
        except asyncio.CancelledError:
            # Expected on shutdown; avoid noisy tracebacks
            pass

    def get_url(self) -> str | None:
        """Get the server URL for MCP clients.

        Returns:
            Server URL or None if not started. The URL points to the SSE endpoint
            that FastMCP automatically provides.
        """
        if self.actual_port is None:
            return None
        return f"http://{self.host}:{self.actual_port}/sse"

    def get_updates(self, agent_name: str | None = None) -> list[StatusUpdate]:
        """Get status updates, optionally filtered by agent name.

        Args:
            agent_name: Optional agent name to filter by

        Returns:
            List of status updates
        """
        if agent_name:
            return [u for u in self.updates if u.agent_name == agent_name]
        return self.updates.copy()

    def get_token_for_agent(self, agent_name: str) -> str | None:
        """Get the Bearer token for a specific agent.

        Args:
            agent_name: Name of the agent

        Returns:
            Token string or None if auth not enabled or agent not found
        """
        return self.agent_tokens.get(agent_name)

    def get_mcp_config_for_agent(self, agent_name: str) -> dict[str, Any] | None:
        """Generate .mcp.json content for an agent.

        This config should be written to the agent's worktree so the agent
        can connect to the MCP server with proper authentication.

        Args:
            agent_name: Name of the agent

        Returns:
            Dict suitable for JSON serialization, or None if auth not enabled
        """
        token = self.get_token_for_agent(agent_name)
        if not token:
            return None

        url = self.get_url()
        if not url:
            # Server not started yet, use expected URL
            port = self.port if self.port != 0 else 9393
            url = f"http://{self.host}:{port}/sse"

        return {
            "mcpServers": {
                "deliberate-orchestrator": {
                    "type": "sse",
                    "url": url,
                    "headers": {"Authorization": f"Bearer {token}"},
                }
            }
        }

    def get_mcp_server_config(self, agent_name: str) -> Any | None:
        """Get MCPServerConfig for an agent to pass to run_agentic().

        This returns an MCPServerConfig object that can be passed via extra_mcp_servers
        to inject the orchestrator's SSE server into the agent's MCP config.

        Args:
            agent_name: Name of the agent

        Returns:
            MCPServerConfig object or None if auth not enabled
        """
        from deliberate.adapters.cli_adapter import MCPServerConfig

        token = self.get_token_for_agent(agent_name)
        if not token:
            return None

        url = self.get_url()
        if not url:
            port = self.port if self.port != 0 else 9393
            url = f"http://{self.host}:{port}/sse"

        return MCPServerConfig(
            name="deliberate-orchestrator",
            url=url,
            headers={"Authorization": f"Bearer {token}"},
        )

    async def shutdown(self) -> None:
        """Gracefully shutdown the server."""
        if hasattr(self, "_server") and self._server:
            self._server.should_exit = True
            # Allow time for cleanup
            await asyncio.sleep(0.1)


def create_orchestrator_server(
    db_connection: Any | None = None,
    agent_names: list[str] | None = None,
    callback: Callable[[StatusUpdate], None] | None = None,
    host: str = "127.0.0.1",
    port: int = 0,
) -> OrchestratorServer:
    """Create a new orchestrator MCP server.

    Args:
        db_connection: Shared database connection (optional).
        agent_names: List of agent names to enable token auth.
        callback: Function to call when status updates are received
        host: Host to bind the server to
        port: Port to bind the server to (0 for auto-select)

    Returns:
        OrchestratorServer instance
    """
    return OrchestratorServer(
        db_connection=db_connection,
        agent_names=agent_names,
        callback=callback,
        host=host,
        port=port,
    )


async def run_orchestrator_server(
    db_connection: Any | None = None,
    agent_names: list[str] | None = None,
    callback: Callable[[StatusUpdate], None] | None = None,
    host: str = "127.0.0.1",
    port: int = 0,
) -> None:
    """Run the orchestrator MCP server.

    Args:
        db_connection: Shared database connection (optional).
        agent_names: List of agent names to enable token auth.
        callback: Function to call when status updates are received
        host: Host to bind the server to
        port: Port to bind the server to (0 for auto-select)
    """
    server = create_orchestrator_server(db_connection, agent_names, callback, host, port)
    await server.run()


if __name__ == "__main__":
    # Run server in standalone mode
    print("Starting orchestrator MCP server...")

    # In standalone mode, use an in-memory DB and ensure migrations are run
    def print_update(update: StatusUpdate):
        print(f"[{update.timestamp}] {update.agent_name} ({update.phase}): {update.message}")

    asyncio.run(run_orchestrator_server(db_connection=None, callback=print_update))
