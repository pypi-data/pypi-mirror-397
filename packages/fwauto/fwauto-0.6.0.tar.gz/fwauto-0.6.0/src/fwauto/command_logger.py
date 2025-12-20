"""Command execution logger for slash commands."""

from datetime import datetime
from pathlib import Path
from typing import Any


class CommandLogger:
    """Records slash command executions and their results.

    Log format (plain text):
        ========================================
        Command Execution Log
        Session: 2025-11-20 14:30:00
        Project: /path/to/project
        ========================================

        [14:30:15] Command: /deploy --binary-args test.hex
        Parameters:
          - binary_args: test.hex

        Status: success

        Output:
        ✅ 韌體部署成功
        Deploy log: ...

        ----------------------------------------

        [14:31:20] Command: /build
        Parameters: (none)

        Status: error

        Output:
        ❌ 編譯失敗
        Build errors: ...

        ========================================
        Session ended: 2025-11-20 14:35:00
        Total commands: 2
        ========================================
    """

    def __init__(self, project_root: Path, state: dict[str, Any]):
        """Initialize command logger.

        Args:
            project_root: Project root directory
            state: Initial FirmwareState
        """
        self.project_root = project_root
        self.log_dir = project_root / ".fwauto" / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"commands_{timestamp}.txt"

        self.command_count = 0
        self.session_start = datetime.now()

        # Write header
        self._write_header(state)

    def _write_header(self, state: dict[str, Any]) -> None:
        """Write log file header."""
        with open(self.log_file, "w", encoding="utf-8") as f:
            f.write("=" * 50 + "\n")
            f.write("Command Execution Log\n")
            f.write(f"Session: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Project: {self.project_root}\n")
            f.write(f"Platform: {state.get('platform', 'unknown')}\n")
            f.write("=" * 50 + "\n\n")

    def log_command_execution(
        self, command: str, parameters: dict[str, Any], status: str, output: str
    ) -> None:
        """Log a command execution.

        Args:
            command: Slash command name (e.g., "/deploy")
            parameters: Parsed command parameters
            status: Execution status ("success" or "error")
            output: Command output text
        """
        self.command_count += 1
        timestamp = datetime.now().strftime("%H:%M:%S")

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] Command: {command}\n")

            if parameters:
                f.write("Parameters:\n")
                for key, value in parameters.items():
                    f.write(f"  - {key}: {value}\n")
            else:
                f.write("Parameters: (none)\n")

            f.write(f"\nStatus: {status}\n\n")
            f.write("Output:\n")
            f.write(output + "\n")
            f.write("-" * 50 + "\n\n")

    def finalize(self) -> None:
        """Write session summary and close log."""
        session_end = datetime.now()
        duration = (session_end - self.session_start).total_seconds()

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write("=" * 50 + "\n")
            f.write(f"Session ended: {session_end.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Duration: {duration:.1f} seconds\n")
            f.write(f"Total commands: {self.command_count}\n")
            f.write("=" * 50 + "\n")
