"""Chat node for interactive conversation with Claude Code SDK."""

import asyncio
import time
from pathlib import Path
from typing import Any

from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient
from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner

from ..ai_utils import print_ai_message
from ..auth import get_user_token, get_auth_server_url, is_direct_api_mode
from ..chat_logger import ChatLogger
from ..logging_config import get_logger
from ..prompt_manager import PromptManager
from ..state import FirmwareState

logger = get_logger(__name__)
console = Console()

# Global prompt manager
prompt_manager = PromptManager()


class ChatExitRequest(Exception):
    """Raised when user requests to exit chat via /exit command."""
    pass


def chat_node(state: FirmwareState) -> dict[str, Any]:
    """
    Interactive chat node using ClaudeSDKClient.

    This node:
    1. Loads the chat prompt template
    2. Configures Claude SDK with full permissions
    3. Enters interactive conversation loop
    4. Maintains conversation history in memory (via SDK)
    5. Exits on '/exit' or Ctrl+D

    Args:
        state: Current firmware state

    Returns:
        Updated state with chat_completed flag
    """
    logger.debug("💬 Chat: Starting interactive mode...")

    # Get project context from state
    project_root = state.get("project_root", "")

    # Load chat prompt template
    try:
        system_prompt = prompt_manager.get_prompt("chat", dict(state))
        logger.debug(f"💬 Chat: System prompt loaded ({len(system_prompt)} chars)")
    except Exception as e:
        logger.error(f"❌ Chat: Failed to load prompt: {e}")
        console.print(f"[red]❌ 無法載入 chat prompt: {e}[/red]")
        return {**state, "chat_completed": False}

    # Configure API mode (direct vs proxy)
    env = {}

    if is_direct_api_mode():
        # Direct 模式：使用本機 Claude Max 訂閱，不設定 env
        logger.debug("💬 Chat: Using direct API (Claude Max subscription)")
    else:
        # Proxy 模式：使用 FWAuto Server API proxy
        user_token = get_user_token()
        server_url = get_auth_server_url()

        if user_token and server_url:
            env = {
                "ANTHROPIC_BASE_URL": f"{server_url}/api/proxy",
                "ANTHROPIC_API_KEY": user_token,  # Will be sent as x-api-key header
            }
            logger.debug(f"💬 Chat: Using API proxy at {server_url}/api/proxy")
        else:
            logger.warning("💬 Chat: No auth token found, using direct API (requires ANTHROPIC_API_KEY)")

    # Configure Claude Agent SDK with full permissions
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Write", "Edit", "Glob", "Grep", "Bash"],
        permission_mode="bypassPermissions",
        add_dirs=[project_root] if project_root else [],
        cwd=project_root if project_root else None,
        system_prompt=system_prompt,
        env=env,
    )

    logger.info(f"💬 Chat: Project root = {project_root}")
    console.print("\n[cyan]💬 進入對話模式[/cyan]")
    if is_direct_api_mode():
        console.print("[green]  • API: Direct (Claude Max subscription)[/green]")
    console.print("[dim]  • 輸入 /exit 或 Ctrl+D 離開[/dim]")
    console.print("[dim]  • 行尾加 \\ 可換行輸入[/dim]\n")

    # Initialize loggers
    chat_logger = None
    cmd_logger = None
    if project_root:
        try:
            from ..command_logger import CommandLogger

            chat_logger = ChatLogger(Path(project_root), state)
            cmd_logger = CommandLogger(Path(project_root), state)
            logger.debug("💬 Chat: Loggers initialized")
        except Exception as e:
            logger.warning(f"⚠️ Chat: Failed to initialize loggers: {e}")

    # Execute async chat loop
    # Always use threading to avoid event loop conflicts
    # This is safer than trying to detect running loops, as some
    # libraries may create event loops unexpectedly
    import threading

    result_container = {"completed": False, "error": None}

    def run_in_thread():
        """Run chat loop in a separate thread with its own event loop."""
        try:
            # Create a new event loop for this thread
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                new_loop.run_until_complete(_run_chat_loop(options, chat_logger, cmd_logger, state))
                logger.debug("💬 Chat: _run_chat_loop completed normally")
                result_container["completed"] = True
            finally:
                new_loop.close()
        except ChatExitRequest:
            # Normal exit via /exit command
            logger.debug("💬 Chat: ChatExitRequest caught in run_in_thread")
            result_container["completed"] = True
        except Exception as e:
            logger.debug(f"💬 Chat: Exception in run_in_thread: {type(e).__name__}: {e}")
            result_container["error"] = e

    thread: threading.Thread | None = None
    try:
        logger.debug("💬 Chat: Starting chat loop in dedicated thread")
        thread = threading.Thread(target=run_in_thread, name="ChatLoopThread", daemon=False)
        thread.start()
        thread.join()

        if result_container["error"]:
            raise result_container["error"]

        logger.info("✅ Chat: Session ended normally")
        logger.debug(f"💬 Chat: result_container = {result_container}")
        return {**state, "chat_completed": result_container["completed"]}
    except KeyboardInterrupt:
        # 使用者按 Ctrl+C 終止對話，視為正常結束
        logger.info("💬 Chat: Session interrupted by user (Ctrl+C)")
        console.print("\n[yellow]👋 對話已中斷[/yellow]")
        # 等待線程完成清理（最多 3 秒）
        if thread is not None and thread.is_alive():
            thread.join(timeout=3)
        return {**state, "chat_completed": True}
    except Exception as e:
        logger.error(f"❌ Chat: Session failed: {e}")
        console.print(f"[red]❌ 對話發生錯誤: {e}[/red]")
        return {**state, "chat_completed": False}


async def _run_chat_loop(
    options: ClaudeAgentOptions,
    chat_logger: ChatLogger | None = None,
    cmd_logger: Any | None = None,
    state: FirmwareState | None = None,
) -> None:
    """
    Execute async interactive chat loop.

    Args:
        options: Claude Agent SDK options
        chat_logger: Optional chat logger for conversation recording
        cmd_logger: Optional command logger for slash command recording
        state: Current FirmwareState (needed for command execution)
    """
    # Create async prompt session for CJK support
    prompt_style = Style.from_dict({"cyan": "#00ffff bold"})
    session = PromptSession(
        message=HTML("<cyan><b>You></b></cyan> "),
        style=prompt_style,
    )

    async with ClaudeSDKClient(options=options) as client:
        connect_start = time.time()
        await client.connect()
        connect_elapsed = time.time() - connect_start
        logger.debug(f"💬 Chat: SDK connected, elapsed={connect_elapsed:.2f}s")

        try:
            while True:
                # 多行輸入累積
                input_lines = []

                while True:
                    try:
                        if input_lines:
                            # 續行提示
                            line = await session.prompt_async(HTML("<cyan><b>...></b></cyan> "))
                        else:
                            # 首行提示
                            line = await session.prompt_async()
                    except EOFError:
                        console.print("[yellow]👋 結束對話[/yellow]")
                        return  # 退出整個函數
                    except KeyboardInterrupt:
                        console.print()
                        input_lines = []  # 清空累積
                        break  # 跳出內層循環，重新開始

                    if line.endswith("\\"):
                        input_lines.append(line[:-1])  # 移除反斜線，繼續累積
                    else:
                        input_lines.append(line)
                        break  # 輸入完成

                if not input_lines:
                    continue  # Ctrl+C 清空後重新開始

                user_input = "\n".join(input_lines).strip()

                # Skip empty input
                if not user_input:
                    continue

                # Check for slash command
                from ..slash_commands import parse_slash_command

                slash_cmd = parse_slash_command(user_input)

                if slash_cmd:
                    # Execute slash command
                    try:
                        await _handle_slash_command(slash_cmd, state, client, cmd_logger, chat_logger)
                    except ChatExitRequest:
                        break  # Exit chat loop on /exit command
                    continue  # Skip normal AI query

                # Log user message (normal conversation)
                if chat_logger:
                    chat_logger.log_user_message(user_input)

                # Send message to Claude with spinner
                response_texts = []
                live = None
                query_start_time = time.time()

                try:
                    # 初始 spinner
                    spinner = Spinner("dots", text="[cyan]🤔 思考中...[/cyan]")
                    live = Live(spinner, console=console, transient=True)
                    live.start()

                    logger.debug(f"💬 Chat: Sending query ({len(user_input)} chars)")
                    await client.query(user_input)
                    query_sent_time = time.time()
                    logger.debug(f"💬 Chat: Query sent, elapsed={query_sent_time - query_start_time:.2f}s")

                    # Receive and display response
                    from claude_agent_sdk.types import AssistantMessage, TextBlock

                    first_response = True
                    async for msg in client.receive_response():
                        if isinstance(msg, AssistantMessage):
                            for block in msg.content:
                                if isinstance(block, TextBlock):
                                    if first_response:
                                        first_response_time = time.time()
                                        logger.debug(f"💬 Chat: First response received, elapsed={first_response_time - query_start_time:.2f}s")
                                        first_response = False
                                    # 停止當前 spinner
                                    live.stop()
                                    # 輸出文字
                                    console.print(f"💬 {block.text.strip()}")
                                    response_texts.append(block.text)
                                    # 重新啟動 spinner（為下一個訊息）
                                    spinner = Spinner("dots", text="[cyan]🤔 思考中...[/cyan]")
                                    live = Live(spinner, console=console, transient=True)
                                    live.start()

                    # 循環結束，停止最後的 spinner
                    live.stop()
                    response_end_time = time.time()
                    logger.debug(f"💬 Chat: Response complete, total_elapsed={response_end_time - query_start_time:.2f}s")

                except KeyboardInterrupt:
                    if live:
                        live.stop()
                    console.print("\n[yellow]⚠️ 回應已中斷[/yellow]")

                # Log assistant response
                if chat_logger and response_texts:
                    chat_logger.log_assistant_message("\n".join(response_texts))

                console.print()  # Add spacing between exchanges

        finally:
            # Finalize logs
            if chat_logger:
                chat_logger.finalize()
            if cmd_logger:
                cmd_logger.finalize()

            # Ensure proper cleanup
            await client.disconnect()
            logger.debug("💬 Chat: SDK disconnected")


async def _handle_slash_command(
    cmd: Any,
    state: FirmwareState,
    client: ClaudeSDKClient,
    cmd_logger: Any | None,
    chat_logger: Any | None,
) -> None:
    """Handle slash command execution.

    Steps:
    1. Parse command arguments
    2. Build appropriate FirmwareState
    3. Execute corresponding node (synchronously)
    4. Inject result into AI conversation (as system message)
    5. Log command execution
    6. If failed, ask user about AI repair

    Args:
        cmd: Parsed SlashCommand
        state: Current FirmwareState
        client: ClaudeSDKClient for AI conversation
        cmd_logger: Optional command logger
        chat_logger: Optional chat logger
    """
    from ..cli import _build_deploy_state, _build_log_state
    from ..slash_commands import parse_command_args

    try:
        # Parse arguments
        parsed_args = parse_command_args(cmd)
        cmd.parsed_args = parsed_args

        # Build state and execute based on command type
        if cmd.name == "build":
            from ..nodes.build import build_node

            exec_state = {
                **state,
                "execution_mode": "build",
                "command": "build",
                "command_args": {},
            }
            result = build_node(exec_state)
            status = result["build_status"]
            output = result["build_log"]

        elif cmd.name == "deploy":
            from ..nodes.deploy import deploy_node

            # Handle scenario loading if needed
            binary_args = parsed_args.get("binary_args", "")
            scenario = parsed_args.get("scenario", "")

            if not binary_args and scenario:
                # Load scenario
                try:
                    from ..config import find_project_root, load_project_config

                    project_root = find_project_root()
                    if project_root:
                        config = load_project_config(project_root)
                        scenario_manager = config.get_scenario_manager()
                        scenario_obj = scenario_manager.get_scenario(scenario)
                        if scenario_obj:
                            binary_args = scenario_obj.binary_args
                            console.print(f"[green]✓[/green] Using scenario: {scenario_obj.name}")
                except Exception as e:
                    logger.warning(f"Failed to load scenario: {e}")

            exec_state = _build_deploy_state(
                binary_args, state["project_root"], state.get("platform", "unknown")
            )
            result = deploy_node(exec_state)
            status = result["deploy_status"]
            output = result["deploy_log"]

        elif cmd.name == "log":
            from ..nodes.log import log_node

            log_path = parsed_args["log_path"]
            analysis_prompt = parsed_args["analysis_prompt"]
            exec_state = _build_log_state(
                log_path, analysis_prompt, state["project_root"], state.get("platform", "unknown")
            )
            result = log_node(exec_state)
            status = "success" if result.get("log_analysis_result") else "error"
            output = result.get("log_analysis_result", "分析失敗")

        elif cmd.name == "help":
            from ..cli import _get_help_info

            help_text = _get_help_info()
            console.print(help_text)

            # Log command execution
            if cmd_logger:
                cmd_logger.log_command_execution(
                    command="/help",
                    parameters={},
                    status="success",
                    output=help_text,
                )
            return  # help 不需要注入 AI 對話

        elif cmd.name == "exit":
            console.print("[yellow]👋 結束對話[/yellow]")
            # Log command execution
            if cmd_logger:
                cmd_logger.log_command_execution(
                    command="/exit",
                    parameters={},
                    status="success",
                    output="User requested exit",
                )
            raise ChatExitRequest  # Signal to exit the chat loop

        else:
            raise ValueError(f"Unknown command: {cmd.name}")

        # Log command execution
        if cmd_logger:
            cmd_logger.log_command_execution(
                command=f"/{cmd.name} {' '.join(cmd.raw_args)}",
                parameters=parsed_args,
                status=status,
                output=output,
            )

        # Inject result into AI conversation as system message
        system_msg = f"""[系統] 使用者執行了指令：/{cmd.name}
參數：{parsed_args}

執行結果：{status}

完整 Log：
{output}
"""

        await client.query(system_msg)

        # Display result to user
        console.print(f"\n[cyan]✅ 指令執行完成：/{cmd.name}[/cyan]")
        console.print(f"狀態：{status}\n")

        # If failed, ask user about AI repair
        if status == "error":
            console.print("[yellow]指令執行失敗，是否需要 AI 協助診斷與修復？(y/n)[/yellow]")

            # Get user confirmation
            from prompt_toolkit import PromptSession

            confirm_session = PromptSession()

            try:
                confirm = await confirm_session.prompt_async("AI 修復 (y/n): ")
                confirm = confirm.strip().lower()

                if confirm in ["y", "yes"]:
                    # Let AI analyze the error
                    repair_prompt = f"剛才執行 /{cmd.name} 失敗了，錯誤訊息如下：\n\n{output}\n\n請幫我診斷問題並修復。"

                    if chat_logger:
                        chat_logger.log_user_message(repair_prompt)

                    await client.query(repair_prompt)

                    # Receive AI response
                    from claude_agent_sdk.types import AssistantMessage, TextBlock

                    response_texts = []
                    async for msg in client.receive_response():
                        from ..ai_utils import print_ai_message

                        print_ai_message(msg, prefix="💬")
                        if isinstance(msg, AssistantMessage):
                            for block in msg.content:
                                if isinstance(block, TextBlock):
                                    response_texts.append(block.text)

                    if chat_logger and response_texts:
                        chat_logger.log_assistant_message("\n".join(response_texts))
                else:
                    console.print("[cyan]已略過 AI 修復[/cyan]")

            except (EOFError, KeyboardInterrupt):
                console.print("[cyan]已略過 AI 修復[/cyan]")

    except ChatExitRequest:
        raise  # Re-raise to signal exit to caller
    except Exception as e:
        console.print(f"[red]❌ 指令執行錯誤：{e}[/red]")
        logger.error(f"Slash command execution failed: {e}")

        if cmd_logger:
            cmd_logger.log_command_execution(
                command=f"/{cmd.name} {' '.join(cmd.raw_args)}",
                parameters=cmd.parsed_args,
                status="error",
                output=str(e),
            )
