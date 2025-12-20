"""Build node - executes Makefile-based build."""

import subprocess
from pathlib import Path
from typing import Any

from ..config import ConfigError, load_project_config
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


def build_node(state: FirmwareState) -> dict[str, Any]:
    """
    Build firmware using Makefile.

    Process:
    1. Validate project initialization
    2. Load project configuration
    3. Execute make build
    4. Update state with results
    """
    log_node_input_state("build", state)
    log_node_start("build", "build")

    # 1. Validate project initialization
    if not state.get("project_initialized"):
        error_msg = "Project not initialized. Run init first."
        log_node_error("build", error_msg)
        return {
            **state,
            "build_status": "error",
            "build_errors": [error_msg],
            "build_log": f"❌ {error_msg}",
        }

    project_root = state.get("project_root")
    if not project_root:
        error_msg = "Project root not set"
        log_node_error("build", error_msg)
        return {
            **state,
            "build_status": "error",
            "build_errors": [error_msg],
            "build_log": f"❌ {error_msg}",
        }

    # 2. Load project configuration
    try:
        project_root_path = Path(project_root)
        config = load_project_config(project_root_path)
        logger.info("🔨 Building project...")
    except ConfigError as e:
        error_msg = f"Config error: {str(e)}"
        log_node_error("build", error_msg)
        return {
            **state,
            "build_status": "error",
            "build_errors": [error_msg],
            "build_log": f"❌ {error_msg}",
        }

    # 3. Execute make build
    try:
        makefile_path = project_root_path / config.build_makefile
        target = config.build_target

        # 使用共用工具函數執行 make（包含跨平台處理和 timeout 保護）
        from ..utils import execute_make_command

        returncode, full_output = execute_make_command(
            makefile_path=makefile_path,
            target=target,
            project_root=project_root_path,
            timeout=60,  # 60 秒 timeout
        )

        # Check success
        if returncode == 0:
            success_msg = "Build succeeded"
            log_node_success("build", success_msg)

            result_state = {
                **state,
                "build_status": "success",
                "build_errors": [],
                "build_log": f"{full_output}\n✅ {success_msg}",
            }

            log_node_output_state("build", result_state)
            return result_state
        else:
            error_msg = f"Build failed with exit code {returncode}"
            log_node_error("build", error_msg)

            return {
                **state,
                "build_status": "error",
                "build_errors": [error_msg],
                "build_log": f"{full_output}\n❌ {error_msg}",
                "iteration": state.get("iteration", 0) + 1,
            }

    except subprocess.TimeoutExpired as e:
        error_msg = f"Build timeout after {e.timeout} seconds"
        log_node_error("build", error_msg)
        output = e.output if e.output else "No output captured"
        return {
            **state,
            "build_status": "error",
            "build_errors": [error_msg],
            "build_log": f"{output}\n❌ {error_msg}",
            "iteration": state.get("iteration", 0) + 1,
        }
    except Exception as e:
        error_msg = f"Build exception: {str(e)}"
        log_node_error("build", error_msg)
        return {
            **state,
            "build_status": "error",
            "build_errors": [error_msg],
            "build_log": f"❌ {error_msg}",
            "iteration": state.get("iteration", 0) + 1,
        }
