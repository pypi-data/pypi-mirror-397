"""Logging configuration for FWAuto project."""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Union

if TYPE_CHECKING:
    from fwauto.state import FirmwareState


class ConsoleFormatter(logging.Formatter):
    """Custom formatter for console output to maintain existing print style."""

    # Define colors for different log levels
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[0m",  # Default
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def __init__(self, use_colors: bool = True):
        super().__init__()
        self.use_colors = use_colors and sys.stdout.isatty()

    def format(self, record: logging.LogRecord) -> str:
        """Format log record for console output with emoji and color."""
        # Extract emoji and message from the record
        msg = record.getMessage()

        # Add file location info (filename:lineno)
        location = f"[{record.filename}:{record.lineno}]"

        # Add color if enabled
        if self.use_colors and record.levelname in self.COLORS:
            color = self.COLORS[record.levelname]
            msg = f"{color}{location} {msg}{self.RESET}"
        else:
            msg = f"{location} {msg}"

        return msg


class FileFormatter(logging.Formatter):
    """Detailed formatter for file output."""

    def __init__(self):
        super().__init__(
            fmt="[%(asctime)s] [%(name)s] [%(filename)s:%(lineno)d] %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )


def setup_logging(project_root: Path | None = None, log_level: str = "INFO") -> logging.Logger:
    """
    Setup logging configuration for FWAuto.

    Args:
        project_root: Project root directory for log files
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    # Convert log level string to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Get or create root logger for FWAuto
    logger = logging.getLogger("fwauto")
    logger.setLevel(numeric_level)

    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()

    # Console output is handled via print() statements in code
    # Logging is only for file-based debugging

    # Setup file handler with detailed formatting and unique filename
    if project_root is None:
        project_root = Path.cwd()

    # Store logs in .fwauto/logs directory
    log_dir = project_root / ".fwauto" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"fwauto_{timestamp}.log"

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)  # File logs everything
    file_handler.setFormatter(FileFormatter())
    logger.addHandler(file_handler)

    # Log the filename for user reference
    logger.info(f"📝 Logging to: {log_file}")

    # Prevent propagation to avoid duplicate logs
    logger.propagate = False

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a specific module."""
    # Ensure the logger is under the fwauto hierarchy
    if not name.startswith("fwauto"):
        name = f"fwauto.{name}"
    return logging.getLogger(name)


def log_workflow_start() -> None:
    """Log the start of the workflow."""
    logger = get_logger("config")
    logger.info("⚙️ Starting FWAuto workflow")


def log_node_start(node_name: str, mode: str = "") -> None:
    """Log the start of a node operation."""
    logger = get_logger(f"nodes.{node_name}")
    mode_indicator = f"[{mode.upper()}] " if mode else ""

    # Map node names to appropriate emojis
    emoji_map = {"build": "🔧", "flash": "🔌", "log_collect": "📊", "init": "🚀", "human_review": "👤"}

    emoji = emoji_map.get(node_name, "⚡")
    logger.info(f"{emoji} {mode_indicator}{node_name.replace('_', ' ').title()} starting...")


def log_node_success(node_name: str, message: str = "") -> None:
    """Log successful completion of a node operation."""
    logger = get_logger(f"nodes.{node_name}")
    base_msg = f"✅ {node_name.replace('_', ' ').title()} completed"
    full_msg = f"{base_msg}: {message}" if message else f"{base_msg} successfully"
    logger.info(full_msg)


def log_node_error(node_name: str, error: str) -> None:
    """Log error in a node operation."""
    logger = get_logger(f"nodes.{node_name}")
    logger.error(f"❌ {node_name.replace('_', ' ').title()} failed: {error}")


def log_node_warning(node_name: str, warning: str) -> None:
    """Log warning in a node operation."""
    logger = get_logger(f"nodes.{node_name}")
    logger.warning(f"⚠️ {node_name.replace('_', ' ').title()} warning: {warning}")


# Global logger instance - will be initialized when setup_logging is called
_main_logger: logging.Logger | None = None


def init_project_logging(project_root: Path | None = None) -> logging.Logger:
    """Initialize project-wide logging. Call this once at application startup."""
    global _main_logger

    # Setup logging
    _main_logger = setup_logging(project_root=project_root, log_level="DEBUG")

    # Log initialization
    _main_logger.info("🚀 FWAuto logging system initialized")

    return _main_logger


def log_node_input_state(node_name: str, state: Union["FirmwareState", dict[str, Any]]) -> None:
    """Log the input state of a node."""
    logger = get_logger(f"nodes.{node_name}")

    # Extract key state information without logging sensitive data
    key_fields = [
        "execution_mode",
        "command",
        "build_status",
        "flash_status",
        "project_initialized",
        "iteration",
        "max_retries",
    ]

    input_info = {}
    for field in key_fields:
        if field in state:
            input_info[field] = state[field]

    # Messages field has been removed from state

    logger.debug(f"📥 Input state: {input_info}")


def log_node_output_state(node_name: str, output_state: Union["FirmwareState", dict[str, Any]]) -> None:
    """Log the output state of a node."""
    logger = get_logger(f"nodes.{node_name}")

    # Extract key state changes/results
    key_fields = ["build_status", "flash_status", "project_initialized", "iteration", "execution_mode", "command"]

    output_info = {}
    for field in key_fields:
        if field in output_state:
            output_info[field] = output_state[field]

    # Add error information if exists
    if "build_errors" in output_state and output_state["build_errors"]:
        output_info["build_errors_count"] = len(output_state["build_errors"])
        output_info["build_errors_summary"] = output_state["build_errors"][0][:100] + "..."

    if "flash_errors" in output_state and output_state["flash_errors"]:
        output_info["flash_errors_count"] = len(output_state["flash_errors"])
        output_info["flash_errors_summary"] = output_state["flash_errors"][0][:100] + "..."

    # Add firmware path if generated
    if "firmware_path" in output_state:
        output_info["firmware_path"] = output_state["firmware_path"]

    # Messages field has been removed from state

    logger.debug(f"📤 Output state: {output_info}")


def get_main_logger() -> logging.Logger:
    """Get the main project logger."""
    if _main_logger is None:
        return init_project_logging()
    return _main_logger
