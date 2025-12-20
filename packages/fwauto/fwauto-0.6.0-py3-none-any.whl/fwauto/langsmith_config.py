"""LangSmith configuration and utilities for tracing."""

import logging
import os
from typing import Any

from langsmith import Client


def init_langsmith() -> Client | None:
    """
    Initialize LangSmith client with API key from environment.
    Returns None if API key is not configured.
    """
    api_key = os.getenv("LANGSMITH_API_KEY")
    if not api_key:
        # LangSmith is optional - silently skip if not configured
        return None

    # Set required environment variables for LangChain tracing
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    # Force project name to be "fwauto" regardless of environment variable
    os.environ["LANGCHAIN_PROJECT"] = "fwauto"
    os.environ["LANGSMITH_PROJECT"] = "fwauto"

    client = Client(api_key=api_key)

    # Use logging if available, fallback to print
    try:
        logger = logging.getLogger("fwauto.langsmith")
        logger.info(f"✅ LangSmith initialized with project: {os.environ['LANGCHAIN_PROJECT']}")
    except Exception:
        print(f"✅ LangSmith initialized with project: {os.environ['LANGCHAIN_PROJECT']}")

    return client


def log_to_langsmith(client: Client, event_type: str, data: dict[str, Any], tags: list | None = None) -> None:
    """
    Log an event to LangSmith for tracing.

    Args:
        client: LangSmith client instance
        event_type: Type of event (build_start, build_error, flash_success, etc.)
        data: Event data to log
        tags: Optional tags for categorization
    """
    if not client:
        return

    try:
        # Create a run for logging custom events
        # This is a simplified implementation - you may need to adjust based on your LangSmith usage
        run_metadata = {
            "event_type": event_type,
            "timestamp": data.get("timestamp"),
            "node": data.get("node_name"),
            "mode": data.get("mode"),
            "tags": tags or [],
        }

        # Log the event (implementation depends on how you want to structure LangSmith logs)
        # For now, we'll use the logger to record that we would send to LangSmith
        logger = logging.getLogger("fwauto.langsmith")
        logger.debug(f"Would log to LangSmith: {event_type} - {data} - {run_metadata}")

    except Exception as e:
        # Silently fail to avoid disrupting main workflow
        logger = logging.getLogger("fwauto.langsmith")
        logger.debug(f"Failed to log to LangSmith: {e}")


def get_trace_url(run_id: str) -> str:
    """Generate LangSmith trace URL for a specific run."""
    return f"https://smith.langchain.com/public/{run_id}/r"
