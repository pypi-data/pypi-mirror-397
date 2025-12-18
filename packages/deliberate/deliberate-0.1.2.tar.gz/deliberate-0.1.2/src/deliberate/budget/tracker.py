"""Budget tracking and enforcement for LLM API usage."""

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from threading import RLock


class BudgetExceededError(Exception):
    """Exception raised when a budget limit is exceeded."""

    pass


# Warning thresholds (percentage of budget used)
WARNING_THRESHOLDS = [0.5, 0.75, 0.9]


@dataclass
class AgentUsage:
    """Track usage for a single agent."""

    tokens: int = 0
    requests: int = 0
    cost_usd: float = 0.0


@dataclass
class PhaseUsage:
    """Track usage for a workflow phase."""

    tokens: int = 0
    cost_usd: float = 0.0
    agent_usage: dict[str, AgentUsage] = field(default_factory=dict)


@dataclass
class BudgetTracker:
    """Thread-safe tracker for token/cost/time budgets.

    Enforces limits on:
    - Total tokens across all agents
    - Total cost in USD
    - Maximum requests per agent
    - Hard wallclock timeout
    """

    max_total_tokens: int = 500000
    max_cost_usd: float = 10.0
    max_requests_per_agent: int = 30
    hard_timeout_seconds: int = 2700  # 45 minutes

    start_time: float = field(default_factory=time.time)
    _usage: dict[str, AgentUsage] = field(default_factory=dict)
    _phase_usage: dict[str, PhaseUsage] = field(default_factory=dict)
    _lock: RLock = field(default_factory=RLock)
    _warned_thresholds: set[float] = field(default_factory=set)
    _warning_callback: Callable[[str, str], None] | None = None

    def set_warning_callback(self, callback: Callable[[str, str], None]) -> None:
        """Set callback for budget warnings.

        Args:
            callback: Function(message, level) to call when budget thresholds are reached.
                     level is 'warning' or 'error'.
        """
        self._warning_callback = callback

    def _emit_warning(self, message: str, level: str = "warning") -> None:
        """Emit a budget warning via callback if set."""
        if self._warning_callback:
            self._warning_callback(message, level)

    def record_usage(
        self,
        agent: str,
        tokens: int,
        cost_usd: float = 0.0,
        phase: str | None = None,
    ) -> None:
        """Record usage for an agent and check limits.

        Args:
            agent: Name of the agent.
            tokens: Number of tokens used.
            cost_usd: Cost in USD (optional).
            phase: Workflow phase name (planning, execution, review, refinement).

        Raises:
            BudgetExceededError: If any limit is exceeded.
        """
        with self._lock:
            # Track overall agent usage
            if agent not in self._usage:
                self._usage[agent] = AgentUsage()

            usage = self._usage[agent]
            usage.tokens += tokens
            usage.requests += 1
            usage.cost_usd += cost_usd

            # Track phase-specific usage if phase provided
            if phase:
                if phase not in self._phase_usage:
                    self._phase_usage[phase] = PhaseUsage()

                phase_usage = self._phase_usage[phase]
                phase_usage.tokens += tokens
                phase_usage.cost_usd += cost_usd

                if agent not in phase_usage.agent_usage:
                    phase_usage.agent_usage[agent] = AgentUsage()

                agent_in_phase = phase_usage.agent_usage[agent]
                agent_in_phase.tokens += tokens
                agent_in_phase.requests += 1
                agent_in_phase.cost_usd += cost_usd

            self._check_limits(agent)

    def check_before_call(self, agent: str, estimated_tokens: int = 0) -> None:
        """Check if a call can be made without exceeding limits.

        Args:
            agent: Name of the agent.
            estimated_tokens: Estimated tokens for the call.

        Raises:
            BudgetExceededError: If the call would exceed limits.
        """
        with self._lock:
            if not self.can_afford(estimated_tokens, agent):
                total_tokens = sum(u.tokens for u in self._usage.values())
                raise BudgetExceededError(
                    f"Cannot afford {estimated_tokens} tokens. Current total: {total_tokens}/{self.max_total_tokens}"
                )

    def _check_limits(self, agent: str) -> None:
        """Check all limits and raise if exceeded.

        Must be called with lock held.
        """
        total_tokens = sum(u.tokens for u in self._usage.values())
        total_cost = sum(u.cost_usd for u in self._usage.values())
        elapsed = time.time() - self.start_time
        agent_requests = self._usage[agent].requests

        # Check for warning thresholds before hard limits
        self._check_warning_thresholds(total_tokens, total_cost, elapsed)

        if total_tokens > self.max_total_tokens:
            raise BudgetExceededError(f"Token limit exceeded: {total_tokens:,} > {self.max_total_tokens:,}")

        if total_cost > self.max_cost_usd:
            raise BudgetExceededError(f"Cost limit exceeded: ${total_cost:.2f} > ${self.max_cost_usd:.2f}")

        if agent_requests > self.max_requests_per_agent:
            raise BudgetExceededError(
                f"Request limit for {agent} exceeded: {agent_requests} > {self.max_requests_per_agent}"
            )

        if elapsed > self.hard_timeout_seconds:
            raise BudgetExceededError(f"Time limit exceeded: {elapsed:.0f}s > {self.hard_timeout_seconds}s")

    def _check_warning_thresholds(self, total_tokens: int, total_cost: float, elapsed: float) -> None:
        """Emit warnings when budget thresholds are crossed.

        Must be called with lock held.
        """
        for threshold in WARNING_THRESHOLDS:
            if threshold in self._warned_thresholds:
                continue

            # Check token threshold
            token_ratio = total_tokens / self.max_total_tokens if self.max_total_tokens > 0 else 0
            if token_ratio >= threshold:
                self._warned_thresholds.add(threshold)
                pct = int(threshold * 100)
                self._emit_warning(
                    f"Token budget at {pct}%: {total_tokens:,}/{self.max_total_tokens:,}",
                    "warning" if threshold < 0.9 else "error",
                )
                continue

            # Check cost threshold
            cost_ratio = total_cost / self.max_cost_usd if self.max_cost_usd > 0 else 0
            if cost_ratio >= threshold:
                self._warned_thresholds.add(threshold)
                pct = int(threshold * 100)
                self._emit_warning(
                    f"Cost budget at {pct}%: ${total_cost:.2f}/${self.max_cost_usd:.2f}",
                    "warning" if threshold < 0.9 else "error",
                )
                continue

            # Check time threshold
            time_ratio = elapsed / self.hard_timeout_seconds if self.hard_timeout_seconds > 0 else 0
            if time_ratio >= threshold:
                self._warned_thresholds.add(threshold)
                pct = int(threshold * 100)
                remaining = self.hard_timeout_seconds - elapsed
                self._emit_warning(
                    f"Time budget at {pct}%: {remaining:.0f}s remaining",
                    "warning" if threshold < 0.9 else "error",
                )

    def can_afford(self, estimated_tokens: int, agent: str) -> bool:
        """Check if we can afford a call without exceeding limits.

        Args:
            estimated_tokens: Estimated tokens for the call.
            agent: Name of the agent.

        Returns:
            True if the call can be made without exceeding limits.
        """
        total = sum(u.tokens for u in self._usage.values())
        agent_reqs = self._usage.get(agent, AgentUsage()).requests
        elapsed = time.time() - self.start_time

        return (
            total + estimated_tokens <= self.max_total_tokens
            and agent_reqs < self.max_requests_per_agent
            and elapsed < self.hard_timeout_seconds
        )

    def get_totals(self) -> dict:
        """Get current usage totals.

        Returns:
            Dictionary with current usage statistics.
        """
        with self._lock:
            return {
                "tokens": sum(u.tokens for u in self._usage.values()),
                "cost_usd": sum(u.cost_usd for u in self._usage.values()),
                "requests_by_agent": {a: u.requests for a, u in self._usage.items()},
                "tokens_by_agent": {a: u.tokens for a, u in self._usage.items()},
                "elapsed_seconds": time.time() - self.start_time,
            }

    def get_remaining(self) -> dict:
        """Get remaining budget.

        Returns:
            Dictionary with remaining budget for each limit.
        """
        with self._lock:
            totals = self.get_totals()
            return {
                "tokens": self.max_total_tokens - totals["tokens"],
                "cost_usd": self.max_cost_usd - totals["cost_usd"],
                "time_seconds": self.hard_timeout_seconds - totals["elapsed_seconds"],
            }

    def reset(self) -> None:
        """Reset all usage counters."""
        with self._lock:
            self._usage.clear()
            self._phase_usage.clear()
            self.start_time = time.time()

    def has_refinement_budget_remaining(self, iteration: int) -> bool:
        """Check if budget remains for refinement iteration.

        Args:
            iteration: Refinement iteration number.

        Returns:
            True if there is budget remaining for refinement.
        """
        with self._lock:
            total_tokens = sum(u.tokens for u in self._usage.values())
            total_cost = sum(u.cost_usd for u in self._usage.values())

            # Check if we have capacity for more tokens and cost
            return total_tokens < self.max_total_tokens and total_cost < self.max_cost_usd

    def get_iteration_tokens(self, iteration: int) -> int:
        """Get tokens used in a specific refinement iteration.

        Note: This is a placeholder. Actual tracking would require
        storing iteration-specific data.

        Args:
            iteration: Refinement iteration number.

        Returns:
            Tokens used in the iteration.
        """
        # TODO: Track iteration-specific tokens
        return 0

    def get_phase_usage(self, phase: str) -> PhaseUsage:
        """Get usage statistics for a specific phase.

        Args:
            phase: Phase name (planning, execution, review, refinement).

        Returns:
            PhaseUsage object for the phase.
        """
        with self._lock:
            return self._phase_usage.get(phase, PhaseUsage())

    def get_all_phase_usage(self) -> dict[str, PhaseUsage]:
        """Get usage statistics for all phases.

        Returns:
            Dictionary mapping phase names to PhaseUsage objects.
        """
        with self._lock:
            return dict(self._phase_usage)
