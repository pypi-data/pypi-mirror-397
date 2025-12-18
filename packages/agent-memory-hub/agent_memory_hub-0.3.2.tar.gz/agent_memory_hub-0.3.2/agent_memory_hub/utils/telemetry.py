"""
Telemetry utilities for Agent Memory Hub.
"""
from opentelemetry import trace

TRACER_NAME = "agent-memory-hub"

def get_tracer():
    """Get the library-specific tracer."""
    return trace.get_tracer(TRACER_NAME)
