"""Question routing logic.

Determines where questions should be routed based on:
- Available agents
- Question category
- Current phase
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from deliberate.mcp_server.state import SessionState


class RouteTarget(Enum):
    """Where to route a question."""

    USER = "user"  # Ask human user
    AGENTS = "agents"  # Ask other agents
    AUTO = "auto"  # Use provided suggestion


@dataclass
class RoutingDecision:
    """Decision about where to route a question."""

    target: RouteTarget
    agents: list[str] | None = None  # If target is AGENTS
    reason: str = ""


class QuestionRouter:
    """Routes questions based on available agents and question properties."""

    def __init__(self, session: SessionState):
        """Initialize router.

        Args:
            session: Session state with agent registry
        """
        self.session = session

    def route(
        self,
        asking_agent: str,
        question: dict,
    ) -> RoutingDecision:
        """Route a question to the appropriate handler.

        Simple routing strategy:
        1. If suggestions provided and urgency is low/medium: use first suggestion
        2. If other executors available: ask them
        3. Otherwise: ask user

        Args:
            asking_agent: Agent asking the question
            question: Question data (question, category, suggestions, urgency)

        Returns:
            Routing decision
        """
        question.get("category", "clarification")
        suggestions = question.get("suggestions", [])
        urgency = question.get("urgency", "medium")

        # Strategy 1: Auto-answer with suggestions if low/medium urgency
        if suggestions and urgency in ("low", "medium") and len(suggestions) >= 1:
            return RoutingDecision(
                target=RouteTarget.AUTO,
                reason=f"Using first suggestion (urgency: {urgency}, {len(suggestions)} options)",
            )

        # Strategy 2: Ask other executors
        # Get all registered executors except the asking agent
        all_agents = self.session.get_agents(role="executor")
        other_agents = [a.name for a in all_agents if a.name != asking_agent]

        if other_agents:
            return RoutingDecision(
                target=RouteTarget.AGENTS,
                agents=other_agents,
                reason=f"Routing to {len(other_agents)} other executor(s): {', '.join(other_agents)}",
            )

        # Strategy 3: Fallback to user
        return RoutingDecision(
            target=RouteTarget.USER,
            reason="No other executors available - escalating to user",
        )
