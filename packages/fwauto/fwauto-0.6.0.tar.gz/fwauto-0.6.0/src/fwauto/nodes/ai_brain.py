"""AI Brain - Unified intelligent decision maker with prompt templates."""

import asyncio
from typing import Any

from claude_agent_sdk import ClaudeAgentOptions, query

from ..ai_utils import print_ai_message
from ..auth import get_user_token, get_auth_server_url, is_direct_api_mode
from ..logging_config import (
    get_logger,
    log_node_error,
    log_node_input_state,
    log_node_output_state,
    log_node_start,
    log_node_success,
)
from ..prompt_manager import PromptManager
from ..state import FirmwareState

# Global prompt manager
prompt_manager = PromptManager()


def ai_brain_node(state: FirmwareState) -> dict[str, Any]:
    """
    AI Brain - Unified intelligent processor using prompt templates.

    This node serves as the central AI coordinator that handles all AI-driven tasks
    by loading appropriate prompt templates and executing them through Claude Code SDK.
    """
    logger = get_logger("nodes.ai_brain")

    log_node_input_state("ai_brain", state)
    log_node_start("ai_brain")

    async def run_ai_brain():
        """Execute AI brain processing with prompt templates."""
        try:
            # 1. Analyze and determine task type
            task_type = analyze_task_type(state)

            # 2. Generate prompt from template (prompts/{task_type}.md)
            prompt = prompt_manager.get_prompt(task_type, dict(state))

            # 3. Configure AI options with STM32 project access
            options = get_ai_options(state)

            # 4. Execute AI query
            # Note: Usage is now tracked by the API proxy on the server side,
            # so we don't need to capture ResultMessage for client-side reporting
            responses = []

            async for message in query(prompt=prompt, options=options):
                logger.debug(f"🧠 AI Brain: {message}")
                print_ai_message(message, prefix="🧠")
                responses.append(str(message))

            return {"success": True, "responses": responses, "task_type": task_type}

        except Exception as e:
            logger.debug(f"AI Brain exception: {str(e)}")
            return {"success": False, "error": str(e)}

    # Execute AI brain processing
    result = asyncio.run(run_ai_brain())

    # Update state based on result
    output_state = update_state_from_result(state, result)

    if result["success"]:
        log_node_success("ai_brain", f"Task completed: {result.get('task_type', 'unknown')}")
    else:
        log_node_error("ai_brain", result["error"])

    log_node_output_state("ai_brain", output_state)
    return output_state


def analyze_task_type(state: FirmwareState) -> str:
    """
    Analyze current state to determine task type for prompt selection.

    Returns task type that directly corresponds to prompt filename.

    Supported task types:
    - fix_build_errors: Auto-fix compilation errors (triggered by build failures)
    - implement_feature: Implement new features (triggered by 'fwauto feat')
    - rag_query: RAG document query (triggered by 'fwauto rag')
    """
    logger = get_logger("nodes.ai_brain")
    logger.debug("🧠 AI Brain: Analyzing task type...")

    if state.get("build_errors") and state.get("build_status") == "error":
        logger.debug("  ✓ Build errors detected → fix_build_errors")
        return "fix_build_errors"
    elif state.get("execution_mode") == "feat":
        logger.debug("  ✓ Feature mode detected → implement_feature")
        return "implement_feature"
    elif state.get("execution_mode") == "rag":
        logger.debug("  ✓ RAG mode detected → rag_query")
        return "rag_query"
    else:
        # This should never happen - all valid paths are handled above
        logger.error(f"  ✗ Unexpected state: execution_mode={state.get('execution_mode')}")
        raise ValueError(
            f"Invalid execution_mode for AI Brain: {state.get('execution_mode')}. "
            "AI Brain only supports 'feat', 'rag' mode or build error auto-fix."
        )


def get_ai_options(state: FirmwareState) -> ClaudeAgentOptions:
    """
    Configure AI options with STM32 project directory access.

    Uses Claude Agent SDK's add_dirs and cwd parameters to enable
    AI access to STM32 project files.

    Also configures API proxy settings:
    - ANTHROPIC_BASE_URL: Points to FWAuto Server proxy
    - ANTHROPIC_API_KEY: Set to user_token for authentication
    """
    logger = get_logger("nodes.ai_brain")
    project_root = state.get("project_root")

    # Base configuration
    options = {
        "allowed_tools": ["Read", "Write", "Edit", "MultiEdit", "Glob", "Grep", "Bash"],
        "permission_mode": "bypassPermissions",  # 等同於 --dangerously-skip-permissions
    }

    # Add STM32 project directory access if available
    if project_root:
        options["add_dirs"] = [project_root]
        options["cwd"] = project_root
        logger.debug(f"🧠 AI Brain: Working in project: {project_root}")
    else:
        logger.debug("🧠 AI Brain: No project path found, using default directory")

    # Configure API mode (direct vs proxy)
    if is_direct_api_mode():
        # Direct 模式：使用本機 Claude Max 訂閱，不設定 env
        logger.debug("🧠 AI Brain: Using direct API (Claude Max subscription)")
    else:
        # Proxy 模式：使用 FWAuto Server API proxy
        user_token = get_user_token()
        server_url = get_auth_server_url()

        if user_token and server_url:
            options["env"] = {
                "ANTHROPIC_BASE_URL": f"{server_url}/api/proxy",
                "ANTHROPIC_API_KEY": user_token,  # Will be sent as x-api-key header
            }
            logger.debug(f"🧠 AI Brain: Using API proxy at {server_url}/api/proxy")
        else:
            logger.warning("🧠 AI Brain: No auth token found, using direct API (requires ANTHROPIC_API_KEY)")

    return ClaudeAgentOptions(**options)


def update_state_from_result(state: FirmwareState, result: dict[str, Any]) -> dict[str, Any]:
    """
    Update firmware state based on AI processing result.

    Simple success/failure state management without complex logic.
    """
    logger = get_logger("nodes.ai_brain")

    if result["success"]:
        logger.debug(f"AI Brain result: Success - {result.get('task_type', 'unknown')}")
        return {
            **state,
            "build_status": "success",
            "build_errors": [],
            "build_log": f"🧠 AI Brain completed: {result.get('task_type', 'unknown')}",
        }
    else:
        logger.debug(f"AI Brain result: Failed - {result['error']}")
        return {
            **state,
            "build_status": "error",
            "build_errors": [result["error"]],
            "build_log": f"🧠 AI Brain failed: {result['error']}",
            "iteration": state.get("iteration", 0) + 1,
        }
