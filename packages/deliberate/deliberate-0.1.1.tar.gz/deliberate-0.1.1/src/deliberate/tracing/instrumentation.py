"""Instrumentation decorators and utilities for tracing."""

from __future__ import annotations

import functools
import time
from typing import Any, Callable, TypeVar

from deliberate.tracing.setup import get_tracer

F = TypeVar("F", bound=Callable[..., Any])


def trace_adapter_call(
    adapter_name: str | None = None,
    operation: str = "call",
) -> Callable[[F], F]:
    """Decorator to trace adapter calls.

    Args:
        adapter_name: Name of the adapter. If None, uses self.name.
        operation: Type of operation (call, run_agentic, etc.).

    Returns:
        Decorated function with tracing.
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(self, *args, **kwargs):
            tracer = get_tracer()
            name = adapter_name or getattr(self, "name", "unknown")
            span_name = f"adapter.{name}.{operation}"

            with tracer.start_as_current_span(span_name) as span:
                span.set_attribute("adapter.name", name)
                span.set_attribute("adapter.operation", operation)

                # Add prompt info if available
                if args:
                    prompt = str(args[0])[:500]  # Truncate for safety
                    span.set_attribute("adapter.prompt_preview", prompt)

                start_time = time.monotonic()
                try:
                    result = await func(self, *args, **kwargs)

                    # Record response metrics
                    duration = time.monotonic() - start_time
                    span.set_attribute("adapter.duration_seconds", duration)

                    if hasattr(result, "token_usage"):
                        span.set_attribute("adapter.token_usage", result.token_usage)
                    if hasattr(result, "content"):
                        span.set_attribute("adapter.response_length", len(result.content))

                    return result

                except Exception as e:
                    span.record_exception(e)
                    _set_error_status(span)
                    raise

        @functools.wraps(func)
        def sync_wrapper(self, *args, **kwargs):
            tracer = get_tracer()
            name = adapter_name or getattr(self, "name", "unknown")
            span_name = f"adapter.{name}.{operation}"

            with tracer.start_as_current_span(span_name) as span:
                span.set_attribute("adapter.name", name)
                span.set_attribute("adapter.operation", operation)

                start_time = time.monotonic()
                try:
                    result = func(self, *args, **kwargs)
                    duration = time.monotonic() - start_time
                    span.set_attribute("adapter.duration_seconds", duration)
                    return result
                except Exception as e:
                    span.record_exception(e)
                    _set_error_status(span)
                    raise

        # Return appropriate wrapper based on function type
        if _is_coroutine_function(func):
            return async_wrapper  # type: ignore
        return sync_wrapper  # type: ignore

    return decorator


def trace_phase(phase_name: str) -> Callable[[F], F]:
    """Decorator to trace workflow phases.

    Args:
        phase_name: Name of the phase (planning, execution, review).

    Returns:
        Decorated function with tracing.
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(self, *args, **kwargs):
            tracer = get_tracer()
            span_name = f"phase.{phase_name}"

            with tracer.start_as_current_span(span_name) as span:
                span.set_attribute("phase.name", phase_name)

                # Add task info if available
                if args:
                    task = str(args[0])[:200]
                    span.set_attribute("phase.task_preview", task)

                # Add agent info
                if hasattr(self, "agents"):
                    span.set_attribute("phase.agents", ",".join(self.agents))

                start_time = time.monotonic()
                try:
                    result = await func(self, *args, **kwargs)

                    duration = time.monotonic() - start_time
                    span.set_attribute("phase.duration_seconds", duration)

                    # Record result metrics based on phase
                    _record_phase_metrics(span, phase_name, result)

                    return result

                except Exception as e:
                    span.record_exception(e)
                    _set_error_status(span)
                    raise

        return async_wrapper  # type: ignore

    return decorator


def trace_workflow(workflow_name: str = "jury") -> Callable[[F], F]:
    """Decorator to trace the complete workflow.

    Args:
        workflow_name: Name of the workflow.

    Returns:
        Decorated function with tracing.
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(self, task: str, *args, **kwargs):
            tracer = get_tracer()
            span_name = f"workflow.{workflow_name}"

            with tracer.start_as_current_span(span_name) as span:
                span.set_attribute("workflow.name", workflow_name)
                span.set_attribute("workflow.task", task[:500])

                # Add config info
                if hasattr(self, "config"):
                    cfg = self.config
                    span.set_attribute(
                        "workflow.planning_enabled",
                        cfg.workflow.planning.enabled,
                    )
                    span.set_attribute(
                        "workflow.execution_enabled",
                        cfg.workflow.execution.enabled,
                    )
                    span.set_attribute(
                        "workflow.review_enabled",
                        cfg.workflow.review.enabled,
                    )

                start_time = time.monotonic()
                try:
                    result = await func(self, task, *args, **kwargs)

                    duration = time.monotonic() - start_time
                    span.set_attribute("workflow.duration_seconds", duration)

                    # Record final result metrics
                    if hasattr(result, "success"):
                        span.set_attribute("workflow.success", result.success)
                    if hasattr(result, "total_token_usage"):
                        span.set_attribute("workflow.total_tokens", result.total_token_usage)
                    if hasattr(result, "total_cost_usd"):
                        span.set_attribute("workflow.total_cost_usd", result.total_cost_usd)

                    return result

                except Exception as e:
                    span.record_exception(e)
                    _set_error_status(span)
                    raise

        return async_wrapper  # type: ignore

    return decorator


def _is_coroutine_function(func: Callable) -> bool:
    """Check if a function is a coroutine function."""
    import asyncio

    return asyncio.iscoroutinefunction(func)


def _set_error_status(span) -> None:
    """Set error status on a span."""
    try:
        from opentelemetry.trace import StatusCode  # type: ignore[import-not-found]

        span.set_status(StatusCode.ERROR)
    except ImportError:
        pass


def _record_phase_metrics(span, phase_name: str, result: Any) -> None:
    """Record phase-specific metrics on a span."""
    if phase_name == "planning":
        if result is not None:
            span.set_attribute("phase.plan_selected", True)
            if hasattr(result, "agent"):
                span.set_attribute("phase.plan_agent", result.agent)
        else:
            span.set_attribute("phase.plan_selected", False)

    elif phase_name == "execution":
        if isinstance(result, list):
            span.set_attribute("phase.execution_count", len(result))
            successful = sum(1 for r in result if getattr(r, "success", False))
            span.set_attribute("phase.execution_successful", successful)

    elif phase_name == "review":
        if isinstance(result, tuple) and len(result) == 2:
            reviews, vote_result = result
            span.set_attribute("phase.review_count", len(reviews) if reviews else 0)
            if vote_result:
                span.set_attribute("phase.winner_id", vote_result.winner_id)
                span.set_attribute("phase.confidence", vote_result.confidence)
