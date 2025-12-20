"""Chat conversation logger for FWAuto."""

from datetime import datetime
from pathlib import Path
from typing import Any

from .logging_config import get_logger

logger = get_logger("chat_logger")


class ChatLogger:
    """
    Chat conversation logger.

    Logs user inputs and Claude responses to a Markdown file
    in .fwauto/logs/ directory.
    """

    def __init__(self, project_root: Path, state: dict[str, Any]):
        """
        Initialize chat logger with session file.

        Args:
            project_root: Project root directory
            state: Current firmware state
        """
        # 使用與系統日誌相同的目錄
        self.log_dir = project_root / ".fwauto" / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # 生成檔案名：chat_YYYYMMDD_HHMMSS.txt
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"chat_{timestamp}.txt"

        # 會話資訊
        self.start_time = datetime.now()
        self.message_count = 0

        # 寫入會話標頭
        self._write_header(state)

        logger.info(f"💬 Chat log created: {self.log_file}")

    def _write_header(self, state: dict[str, Any]) -> None:
        """Write session header."""
        with open(self.log_file, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write(" " * 30 + "CHAT SESSION\n")
            f.write("=" * 80 + "\n")
            f.write(f"開始時間: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"專案路徑: {state.get('project_root', 'N/A')}\n")
            f.write(f"平台: {state.get('platform', 'N/A')}\n")
            f.write("=" * 80 + "\n\n")

    def log_user_message(self, message: str) -> None:
        """
        Log user input message.

        Args:
            message: User input text
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write("┌" + "─" * 77 + "\n")
                f.write(f"│ 👤 USER [{timestamp}]\n")
                f.write("├" + "─" * 77 + "\n")
                # 處理多行訊息，每行前加 "│ "
                for line in message.split("\n"):
                    f.write(f"│ {line}\n")
                f.write("└" + "─" * 77 + "\n\n")
            self.message_count += 1
        except Exception as e:
            logger.warning(f"⚠️ Failed to log user message: {e}")

    def log_assistant_message(self, message: str) -> None:
        """
        Log assistant response message.

        Args:
            message: Assistant response text
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        duration = (datetime.now() - self.start_time).total_seconds()
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write("┌" + "─" * 77 + "\n")
                f.write(f"│ 🤖 AI [{timestamp}] - 累計時間 {duration:.0f} 秒\n")
                f.write("├" + "─" * 77 + "\n")
                # 處理多行訊息，每行前加 "│ "
                for line in message.split("\n"):
                    f.write(f"│ {line}\n")
                f.write("└" + "─" * 77 + "\n\n")
            self.message_count += 1
        except Exception as e:
            logger.warning(f"⚠️ Failed to log assistant message: {e}")

    def finalize(self) -> None:
        """Write session footer and close."""
        end_time = datetime.now()
        duration = end_time - self.start_time

        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write("=" * 80 + "\n")
                f.write(f"結束時間: {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"對話輪數: {self.message_count // 2}\n")
                f.write(f"持續時間: {duration.total_seconds():.1f} 秒\n")
                f.write("=" * 80 + "\n")
            logger.info(f"✅ Chat log finalized: {self.log_file}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to finalize chat log: {e}")
