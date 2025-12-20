"""Log analysis node for UART log analysis using Claude Agent SDK."""

import asyncio
import os
import subprocess
from pathlib import Path
from typing import Any

from claude_agent_sdk import ClaudeAgentOptions, query

from ..ai_utils import print_ai_message
from ..auth import get_user_token, get_auth_server_url
from ..logging_config import get_logger
from ..prompt_manager import PromptManager
from ..state import FirmwareState

logger = get_logger(__name__)

# Global prompt manager
prompt_manager = PromptManager()


def log_node(state: FirmwareState) -> dict[str, Any]:
    """
    Analyze UART log files using Claude Code SDK.

    This node:
    1. Loads the log analysis prompt template
    2. Configures Claude Agent SDK with Read/Grep tools
    3. Executes AI-powered log analysis
    4. Returns analysis results in state

    Args:
        state: Current firmware state containing log_file_path and user_prompt

    Returns:
        Updated state with log_analysis_result
    """
    logger.debug("📊 Log Analysis: Starting analysis...")

    # Get analysis parameters from state
    user_prompt = state.get("user_prompt", "")
    log_file_path = state.get("log_file_path")

    # Fallback: 從 config 讀取（跨執行持久化）
    if not log_file_path:
        try:
            from ..config import find_project_root, load_project_config

            # 嘗試找到專案根目錄
            project_root = state.get("project_root")
            if not project_root:
                found_root = find_project_root()
                if found_root:
                    project_root = str(found_root)

            if project_root:
                config = load_project_config(Path(project_root))
                log_file_path = config.last_log_file_path

                if log_file_path:
                    logger.info(f"📂 Using log path from config (last deploy): {log_file_path}")
        except Exception as e:
            logger.debug(f"Failed to load last log path from config: {e}")

    # Validate log_file_path is provided
    if not log_file_path:
        logger.error("❌ Log Analysis: No log file path provided")
        return {
            **state,
            "log_analysis_result": (
                "Error: No log file path provided.\nPlease use --log-path option or run 'fwauto deploy' first."
            ),
        }

    # 路徑解析：支援本地和遠端
    try:
        if _is_remote_path(log_file_path):
            # 遠端路徑：下載到暫存目錄
            logger.info(f"📡 Detected remote path: {log_file_path}")

            project_root = state.get("project_root", os.getcwd())
            temp_dir = _get_temp_log_dir(project_root)

            # Phase 1: 暫不支援 ssh_options（Phase 2 才從配置讀取）
            log_file_path = _fetch_remote_log(log_file_path, temp_dir, ssh_options=None)

        else:
            # 本地路徑：現有邏輯
            if not os.path.isabs(log_file_path):
                log_file_path = os.path.join(os.getcwd(), log_file_path)
                logger.info(f"📊 Converted to absolute path: {log_file_path}")

            if not os.path.exists(log_file_path):
                logger.error(f"❌ Log Analysis: Log file not found: {log_file_path}")
                return {
                    **state,
                    "log_analysis_result": f"Error: Log file not found: {log_file_path}",
                }

    except RuntimeError as e:
        # 遠端下載錯誤
        logger.error(f"❌ Remote log download failed: {e}")
        return {
            **state,
            "log_analysis_result": f"Error: {e}",
        }

    # Validate user_prompt
    if not user_prompt:
        logger.error("❌ Log Analysis: No analysis prompt provided")
        return {
            **state,
            "log_analysis_result": "Error: No analysis prompt provided",
        }

    logger.info(f"📊 Log Analysis: Analyzing {log_file_path}")
    logger.info(f"📊 Analysis Target: {user_prompt}")

    # Load prompt template
    try:
        # 建立更新的 state，包含正確的 log_file_path（下載後的本地路徑）
        updated_state = {
            **state,
            "log_file_path": log_file_path,  # 使用處理後的本地路徑
        }
        prompt = prompt_manager.get_prompt("log", updated_state)
        logger.debug(f"📊 Log Analysis: Prompt loaded ({len(prompt)} chars)")
    except Exception as e:
        logger.error(f"❌ Log Analysis: Failed to load prompt: {e}")
        return {
            **state,
            "log_analysis_result": f"Error: Failed to load prompt template: {e}",
        }

    # Configure Claude Agent SDK
    allowed_tools = ["Read", "Grep"]

    log_full_path = os.path.abspath(log_file_path)
    log_dir = os.path.dirname(log_full_path)
    logger.info(f"📊 Log Analysis: log_file={log_full_path}")
    print(f"📊 Log Analysis: log_file={log_full_path}")
    logger.info(f"📊 Log Analysis: log_dir={log_dir}")

    # Add system prompt to enforce strict execution without consulting behavior
    system_override = (
        "CRITICAL: You are executing a specific automated task via SDK. "
        "This is NOT an interactive consultation. "
        "Execute the user's prompt instructions IMMEDIATELY and EXACTLY. "
        "DO NOT ask clarifying questions. DO NOT provide help menus. "
        "DO NOT explain what you can do. JUST DO THE TASK."
    )

    # Configure API proxy (use FWAuto Server instead of direct Anthropic API)
    user_token = get_user_token()
    server_url = get_auth_server_url()
    env = {}

    if user_token and server_url:
        env = {
            "ANTHROPIC_BASE_URL": f"{server_url}/api/proxy",
            "ANTHROPIC_API_KEY": user_token,  # Will be sent as x-api-key header
        }
        logger.debug(f"📊 Log Analysis: Using API proxy at {server_url}/api/proxy")
    else:
        logger.warning("📊 Log Analysis: No auth token found, using direct API (requires ANTHROPIC_API_KEY)")

    options = ClaudeAgentOptions(
        allowed_tools=allowed_tools,
        permission_mode="bypassPermissions",
        add_dirs=[log_dir],
        system_prompt=system_override,
        env=env,
    )

    logger.debug(f"📊 Log Analysis: SDK configured - Tools={allowed_tools}")

    # Execute async analysis
    try:
        # Check if we're already in an event loop (e.g., called from chat_node)
        try:
            loop = asyncio.get_running_loop()
            # We're in an async context, run in the same loop
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, _run_analysis(prompt, options))
                result = future.result()
        except RuntimeError:
            # No running loop, safe to use asyncio.run()
            result = asyncio.run(_run_analysis(prompt, options))

        logger.info("✅ Log Analysis: Completed successfully")
        return {
            **state,
            "log_analysis_result": result,
        }
    except Exception as e:
        logger.error(f"❌ Log Analysis: Analysis failed: {e}")
        return {
            **state,
            "log_analysis_result": f"Error: Analysis failed: {e}",
        }


async def _run_analysis(prompt: str, options: ClaudeAgentOptions) -> str:
    """
    Execute async log analysis using Claude Agent SDK.

    Args:
        prompt: Rendered prompt template
        options: Claude Agent SDK options

    Returns:
        Complete analysis result text
    """
    responses = []

    async for message in query(prompt=prompt, options=options):
        logger.debug(f"🧠 Log Analysis: {message}")
        print_ai_message(message, prefix="📊")
        responses.append(str(message))

    return "\n".join(responses)


def _is_remote_path(path: str) -> bool:
    """
    檢查路徑是否為遠端格式 (user@host:path)

    Args:
        path: 日誌檔案路徑

    Returns:
        True if remote path, False otherwise

    Examples:
        >>> _is_remote_path("kent@192.168.50.1:/home/kent/uart.log")
        True
        >>> _is_remote_path("logs/uart.log")
        False
        >>> _is_remote_path("/absolute/path/uart.log")
        False
    """
    import re

    # 匹配格式: user@host:path
    pattern = r"^[^@]+@[^:]+:.+"
    return bool(re.match(pattern, path))


def _parse_remote_path(remote_path: str) -> tuple[str, str, str]:
    """
    解析遠端路徑格式

    Args:
        remote_path: user@host:path 格式

    Returns:
        Tuple of (user, host, path)

    Raises:
        ValueError: 如果格式不正確

    Examples:
        >>> _parse_remote_path("kent@192.168.50.1:/home/kent/uart.log")
        ('kent', '192.168.50.1', '/home/kent/uart.log')
    """
    import re

    # 匹配並提取: user@host:path
    match = re.match(r"^([^@]+)@([^:]+):(.+)$", remote_path)
    if not match:
        raise ValueError(f"Invalid remote path format: {remote_path}")

    user, host, path = match.groups()
    return user, host, path


def _fetch_remote_log(remote_path: str, temp_dir: Path, ssh_options: str | None = None) -> str:
    """
    使用 SCP 下載遠端日誌到暫存目錄

    Args:
        remote_path: user@host:path 格式
        temp_dir: 暫存目錄路徑
        ssh_options: SSH 選項字串（可選）

    Returns:
        本地暫存檔案路徑

    Raises:
        RuntimeError: SCP 下載失敗
    """
    try:
        user, host, path = _parse_remote_path(remote_path)
    except ValueError as e:
        raise RuntimeError(f"Failed to parse remote path: {e}")

    # 預設 SSH 選項（與 deploy 一致）
    default_ssh_opts = [
        "-o",
        "StrictHostKeyChecking=no",
        "-o",
        "UserKnownHostsFile=/dev/null",
        "-o",
        "ConnectTimeout=5",
    ]

    # 如果有自訂選項，解析並覆蓋
    if ssh_options:
        # 簡單解析：用空格分割（未來可改進）
        custom_opts = ssh_options.split()
        ssh_opts = custom_opts
    else:
        ssh_opts = default_ssh_opts

    # 建立暫存檔案路徑 - 使用遠端原始檔名
    import os

    # 從遠端路徑提取檔名
    filename = os.path.basename(path)
    local_path = temp_dir / filename

    # 執行 SCP 命令
    scp_cmd = ["scp"] + ssh_opts + [f"{user}@{host}:{path}", str(local_path)]

    logger.info(f"📥 Downloading remote log: {remote_path}")
    logger.debug(f"SCP command: {' '.join(scp_cmd)}")

    try:
        subprocess.run(
            scp_cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=30,  # 30 秒超時
        )
        logger.info(f"✅ Download successful: {local_path}")
        return str(local_path)

    except subprocess.TimeoutExpired:
        raise RuntimeError(f"SCP timeout: Remote host {host} did not respond within 30 seconds")
    except subprocess.CalledProcessError as e:
        # 詳細錯誤分析
        stderr = e.stderr.lower()

        if "connection refused" in stderr or "no route to host" in stderr:
            raise RuntimeError(
                f"Cannot connect to remote host {host}. Check network connectivity and firewall settings."
            )
        elif "permission denied" in stderr or "publickey" in stderr:
            raise RuntimeError(f"SSH authentication failed for {user}@{host}. Check SSH keys and permissions.")
        elif "no such file" in stderr or "not found" in stderr:
            raise RuntimeError(f"Remote log file not found: {path} on {host}")
        else:
            raise RuntimeError(f"SCP download failed: {e.stderr}")
    except FileNotFoundError:
        raise RuntimeError("SCP command not found. Please install OpenSSH client.")


def _get_temp_log_dir(project_root: str) -> Path:
    """
    取得或建立暫存日誌目錄

    Args:
        project_root: 專案根目錄

    Returns:
        暫存目錄路徑 (.fwauto/logs/)
    """
    temp_dir = Path(project_root) / ".fwauto" / "logs"
    temp_dir.mkdir(parents=True, exist_ok=True)
    return temp_dir


# Test support
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m src.fwauto.nodes.log_analysis <prompt> [log_path]")
        print('Example: python -m src.fwauto.nodes.log_analysis "分析LED閃爍頻率" logs/uart.log')
        sys.exit(1)

    analysis_prompt = sys.argv[1]
    log_path = sys.argv[2] if len(sys.argv) > 2 else "logs/uart.log"

    # Create test state
    test_state: FirmwareState = {
        "user_prompt": analysis_prompt,
        "project_root": os.getcwd(),
        "project_initialized": True,
        "build_status": "pending",
        "build_errors": [],
        "build_log": "",
        "deploy_status": "pending",
        "deploy_errors": [],
        "deploy_log": "",
        "iteration": 0,
        "max_retries": 3,
        "execution_mode": "log",
        "command": "log-analysis",
        "command_args": {"analysis_prompt": analysis_prompt, "log_path": log_path},
        "mode_metadata": None,
        "command_error": None,
        "log_file_path": log_path,
        "log_analysis_result": None,
        "firmware_path": None,
        "platform": "test",
    }

    print(f"\n{'=' * 60}")
    print("Testing log_node")
    print(f"{'=' * 60}")
    print(f"Prompt: {analysis_prompt}")
    print(f"Log Path: {log_path}")
    print(f"{'=' * 60}\n")

    result = log_node(test_state)

    print(f"\n{'=' * 60}")
    print("Analysis Result:")
    print(f"{'=' * 60}")
    print(result.get("log_analysis_result", "No result"))
    print(f"{'=' * 60}")
