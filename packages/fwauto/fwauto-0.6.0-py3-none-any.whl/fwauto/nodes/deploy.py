"""Deploy node - Pure Python deploy operations."""

from pathlib import Path
from typing import Any

from ..config import ConfigError, load_project_config
from ..deploy_operations import deploy_firmware
from ..logging_config import (
    get_logger,
    log_node_error,
    log_node_input_state,
    log_node_output_state,
    log_node_start,
    log_node_success,
)
from ..state import FirmwareState

logger = get_logger(__name__)


def _render_remote_log_path(config, binary_name: str) -> str:
    """
    使用 Jinja2 模板渲染遠端日誌檔案路徑。

    Args:
        config: 專案配置
        binary_name: 可執行檔名（例如 "led"）

    Returns:
        渲染後的遠端日誌路徑（例如 "/home/root/.fwauto/logs/led_2025-11-13.log"）

    Template variables:
        - deploy_path: 日誌目錄路徑（預設：{{ config.deploy_path }}/.fwauto/logs）
        - app_name: 應用程式名稱（預設：binary_name 或 "app"）
        - date: 日期（格式：YYYY-MM-DD）
    """
    from datetime import datetime

    from jinja2 import Template

    template_str = config.remote_log_pattern
    template = Template(template_str)

    context = {
        "deploy_path": f"{config.deploy_path}/.fwauto/logs",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "binary_name": binary_name,
        "app_name": binary_name if binary_name else "app",
    }

    return template.render(context)


def deploy_node(state: FirmwareState) -> dict[str, Any]:
    """
    Deploy firmware using pure Python operations.

    Process:
    1. Validate project initialization
    2. Load project configuration
    3. Execute deploy operation via deploy_operations module
    4. Update state with results
    """
    log_node_input_state("deploy", state)
    log_node_start("deploy", "deploy")

    # 1. Validate project initialization
    if not state.get("project_initialized"):
        error_msg = "Project not initialized. Run init first."
        log_node_error("deploy", error_msg)
        return {
            **state,
            "deploy_status": "error",
            "deploy_errors": [error_msg],
            "deploy_log": f"❌ {error_msg}",
        }

    project_root = state.get("project_root")
    if not project_root:
        error_msg = "Project root not set"
        log_node_error("deploy", error_msg)
        return {
            **state,
            "deploy_status": "error",
            "deploy_errors": [error_msg],
            "deploy_log": f"❌ {error_msg}",
        }

    # 2. Load project configuration
    try:
        project_root_path = Path(project_root)
        config = load_project_config(project_root_path)
        logger.info("📥 Deploying firmware...")
    except ConfigError as e:
        error_msg = f"Config error: {str(e)}"
        log_node_error("deploy", error_msg)
        return {
            **state,
            "deploy_status": "error",
            "deploy_errors": [error_msg],
            "deploy_log": f"❌ {error_msg}",
        }

    # 3. Execute Python-based flash operation
    try:
        # Extract binary arguments
        command_args = state.get("command_args") or {}
        binary_args = command_args.get("binary_args", "")

        # Basic argument validation (prevent shell injection)
        if binary_args:
            dangerous_chars = [";", "|", "&", "$", "`", "\n", "\r"]
            if any(c in binary_args for c in dangerous_chars):
                error_msg = "Binary args contain dangerous shell metacharacters - rejected"
                logger.error(error_msg)
                return {
                    **state,
                    "deploy_status": "error",
                    "deploy_errors": [error_msg],
                    "deploy_log": f"❌ {error_msg}",
                }
            logger.info(f"📦 Binary arguments: {binary_args}")

        # Handle remote log configuration
        remote_log_path_local = None
        remote_log_path_full = None
        if config.remote_log_enabled:
            try:
                # Import here to avoid circular dependency
                from ..deploy_operations import find_binary as find_binary_op

                binary_path = find_binary_op(project_root_path / "build")
                binary_name = binary_path.name
                remote_log_path_local = _render_remote_log_path(config, binary_name)
                remote_log_path_full = f"{config.board_user}@{config.board_ip}:{remote_log_path_local}"

                logger.info(f"📊 Remote log will be saved to: {remote_log_path_full}")

                # Store remote_log_path as a temporary attribute on config object
                # This avoids modifying config.data which would shadow user config settings
                config._tmp_remote_log_path = remote_log_path_local
            except Exception as e:
                logger.warning(f"Failed to setup remote log: {e}")
                remote_log_path_local = "/dev/null"
                remote_log_path_full = None

        # Execute deploy operation (new API: pass ProjectConfig directly)
        result = deploy_firmware(
            build_dir=project_root_path / "build",
            config=config,
            binary_args=binary_args,
        )

        if result.success:
            success_msg = "✅ 燒錄成功!"
            log_node_success("deploy", success_msg)

            # Persist log path to config.toml (cross-execution support)
            if remote_log_path_full:
                try:
                    config.update_last_log_path(remote_log_path_full)
                    logger.info(f"📊 Auto-populated log_file_path = {remote_log_path_full}")
                except Exception as e:
                    logger.warning(f"Failed to save log path to config: {e}")

            result_state = {
                **state,
                "deploy_status": "success",
                "deploy_errors": [],
                "deploy_log": f"{result.message}\n{success_msg}",
                "log_file_path": remote_log_path_full,
            }

            log_node_output_state("deploy", result_state)
            return result_state
        else:
            error_msg = f"Deploy failed: {result.message}"
            log_node_error("deploy", error_msg)
            return {
                **state,
                "deploy_status": "error",
                "deploy_errors": [result.message],
                "deploy_log": f"❌ {error_msg}",
            }

    except Exception as e:
        error_msg = f"Deploy exception: {str(e)}"
        log_node_error("deploy", error_msg)
        return {
            **state,
            "deploy_status": "error",
            "deploy_errors": [str(e)],
            "deploy_log": f"❌ {error_msg}",
        }
