"""Initialize project node to find project root."""

from typing import Any

from ..config import ConfigError, find_project_root, load_project_config
from ..logging_config import init_project_logging
from ..state import FirmwareState


def init_project_node(state: FirmwareState) -> dict[str, Any]:
    """
    Initialize project paths using .fwauto/ anchor.

    Searches for .fwauto/ directory from current working directory upwards,
    loads configuration, and initializes logging.
    """
    # Search for .fwauto/ anchor
    project_root = find_project_root()

    if not project_root:
        # No .fwauto/ found
        return {
            **state,
            "project_root": "",
            "project_initialized": False,
            "build_status": "error",
            "build_errors": ["No .fwauto/ directory found. Please run 'fwauto init' first."],
        }

    # Found .fwauto/ directory
    try:
        # Initialize logging with project directory
        init_project_logging(project_root)

        # Load project configuration
        load_project_config(project_root)
        print(f"✅ Found project root: {project_root}")
        print(f"📦 Project: {project_root.name}")

        return {
            **state,
            "project_root": str(project_root),
            "project_initialized": True,
        }

    except ConfigError as e:
        print(f"❌ Config error: {e}")
        return {
            **state,
            "project_root": "",
            "project_initialized": False,
            "build_status": "error",
            "build_errors": [f"Configuration error: {str(e)}"],
        }
