"""OpenTelemetry tracing setup and configuration."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

# Lazy imports to avoid requiring tracing deps for basic usage
_tracer = None
_tracer_provider = None

if TYPE_CHECKING:
    from opentelemetry.trace import Tracer  # type: ignore[import-not-found]


def init_tracing(
    service_name: str = "deliberate",
    otlp_endpoint: str | None = None,
    otlp_protocol: str | None = None,
    console_export: bool = False,
) -> None:
    """Initialize OpenTelemetry tracing.

    Args:
        service_name: Name of the service for tracing.
        otlp_endpoint: OTLP collector endpoint (e.g., "http://localhost:4317" for gRPC,
                      "http://localhost:4318" for HTTP). If not provided, the
                      OpenTelemetry defaults apply.
        otlp_protocol: Force protocol ("grpc" or "http/protobuf"). If None,
                       OpenTelemetry defaults apply (gRPC by default).
        console_export: If True, also export traces to console for debugging.

    Raises:
        ImportError: If opentelemetry packages are not installed.

    Note:
        Exporter imports are done inline because they are optional dependencies.
        Users can run deliberate without installing opentelemetry-exporter-otlp.
    """
    global _tracer, _tracer_provider

    # Core OpenTelemetry imports (required if tracing is enabled)
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.resources import SERVICE_NAME, Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
    except ImportError as e:
        raise ImportError("OpenTelemetry packages not installed. Install with: pip install deliberate[tracing]") from e

    # Create resource with service name
    resource = Resource.create({SERVICE_NAME: service_name})

    # Create tracer provider
    _tracer_provider = TracerProvider(resource=resource)

    # Add OTLP exporter; lean on exporter defaults/env when values aren't provided
    otlp_exporter = None
    if otlp_endpoint or otlp_protocol:
        protocol = (otlp_protocol or "").lower()

        # If no protocol specified, try gRPC first (more common), then HTTP
        if protocol in ("grpc", ""):
            try:
                from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
                    OTLPSpanExporter,
                )

                endpoint = otlp_endpoint or os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
                otlp_exporter = OTLPSpanExporter(endpoint=endpoint)
            except ImportError:
                # If gRPC not available and no protocol specified, try HTTP
                if not protocol:
                    try:
                        from opentelemetry.exporter.otlp.proto.http.trace_exporter import (  # type: ignore[import-not-found]
                            OTLPSpanExporter as HTTPOTLPSpanExporter,
                        )

                        endpoint = otlp_endpoint or os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
                        if endpoint and not endpoint.rstrip("/").endswith("/v1/traces"):
                            endpoint = endpoint.rstrip("/") + "/v1/traces"
                        otlp_exporter = HTTPOTLPSpanExporter(endpoint=endpoint)
                    except ImportError:
                        otlp_exporter = None
                else:
                    otlp_exporter = None
        elif protocol in ("http", "http/protobuf"):
            try:
                from opentelemetry.exporter.otlp.proto.http.trace_exporter import (  # type: ignore[import-not-found]
                    OTLPSpanExporter as HTTPOTLPSpanExporter,
                )

                endpoint = otlp_endpoint or os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
                if endpoint and not endpoint.rstrip("/").endswith("/v1/traces"):
                    endpoint = endpoint.rstrip("/") + "/v1/traces"
                otlp_exporter = HTTPOTLPSpanExporter(endpoint=endpoint)
            except ImportError:
                otlp_exporter = None

    if otlp_exporter:
        _tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

    # Add console exporter for debugging
    if console_export:
        from opentelemetry.sdk.trace.export import ConsoleSpanExporter  # type: ignore[import-not-found]

        _tracer_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    # Set the tracer provider
    trace.set_tracer_provider(_tracer_provider)
    _tracer = trace.get_tracer(__name__)


def get_tracer() -> "Tracer":
    """Get the configured tracer.

    Returns:
        The OpenTelemetry tracer, or a no-op tracer if not initialized.
    """
    global _tracer

    if _tracer is not None:
        return _tracer

    # Return no-op tracer if not initialized
    try:
        from opentelemetry import trace  # type: ignore[import-not-found]

        return trace.get_tracer(__name__)
    except ImportError:
        # Return a minimal no-op tracer
        return _NoOpTracer()


def shutdown_tracing() -> None:
    """Shutdown tracing and flush any pending spans."""
    global _tracer_provider

    if _tracer_provider is not None:
        _tracer_provider.shutdown()
        _tracer_provider = None


class _NoOpSpan:
    """No-op span for when tracing is not available."""

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def set_attribute(self, key, value):
        pass

    def set_status(self, status):
        pass

    def record_exception(self, exception):
        pass

    def add_event(self, name, attributes=None):
        pass


class _NoOpTracer:
    """No-op tracer for when OpenTelemetry is not installed."""

    def start_as_current_span(self, name, **kwargs):
        return _NoOpSpan()

    def start_span(self, name, **kwargs):
        return _NoOpSpan()
