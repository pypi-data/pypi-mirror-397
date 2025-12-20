"""Modern CLI using Typer framework."""

import sys
from pathlib import Path

import typer
from rich.console import Console

from fwauto.cli_commands.init import run_init_wizard
from fwauto.graph import create_firmware_graph
from fwauto.logging_config import init_project_logging
from fwauto.state import FirmwareState

# Create Typer app
app = typer.Typer(
    name="fwauto",
    help="🚀 STM32 Firmware Automation Tool with AI",
    add_completion=False,
    pretty_exceptions_enable=False,
)

# Auth sub-commands
auth_app = typer.Typer(help="🔐 Authentication commands")
app.add_typer(auth_app, name="auth")

console = Console()


# ============================================================
# Auth Commands
# ============================================================

@auth_app.command(name="login")
def auth_login(
    dev: bool = typer.Option(False, "--dev", help="Use development mode (skip Google OAuth)"),
):
    """
    🔐 Login to FWAuto usage tracking server.

    Examples:
        fwauto auth login          # Google OAuth login
        fwauto auth login --dev    # Development mode (no OAuth)
    """
    from .auth import get_auth_manager

    auth = get_auth_manager()
    success = auth.ensure_authenticated(use_dev_login=dev)

    if success:
        console.print("[green]✅ 登入成功[/green]")
    else:
        console.print("[red]❌ 登入失敗[/red]")
        raise typer.Exit(1)


@auth_app.command(name="logout")
def auth_logout():
    """
    🚪 Logout from FWAuto usage tracking server.

    Example:
        fwauto auth logout
    """
    from .auth import get_auth_manager

    auth = get_auth_manager()
    auth.logout()


@auth_app.command(name="status")
def auth_status():
    """
    📋 Show current authentication status.

    Example:
        fwauto auth status
    """
    from .auth import cli_status

    cli_status()


@app.command(name="dashboard")
def dashboard_cmd(
    open_browser: bool = typer.Option(False, "--open", "-o", help="Open dashboard in browser"),
):
    """
    🌐 Show or open FWAuto Dashboard.

    Examples:
        fwauto dashboard          # Show dashboard URL
        fwauto dashboard --open   # Open in browser
    """
    import webbrowser
    from .auth import FWAUTO_SERVER_URL

    dashboard_url = f"{FWAUTO_SERVER_URL}/dashboard"

    console.print()
    console.print("🌐 FWAuto Dashboard")
    console.print("=" * 50)
    console.print(f"   URL: {dashboard_url}")
    console.print()

    if open_browser:
        console.print("[dim]正在開啟瀏覽器...[/dim]")
        webbrowser.open(dashboard_url)
    else:
        console.print("[dim]提示：使用 --open 或 -o 可直接開啟瀏覽器[/dim]")
    console.print()


def _ensure_ai_engine_installed() -> bool:
    """
    確保 AI 引擎已安裝。

    Returns True if installed, False otherwise.
    """
    from .claude_code_installer import is_ai_engine_installed, ensure_ai_engine_installed

    if is_ai_engine_installed():
        return True

    # 需要安裝
    return ensure_ai_engine_installed(auto_install=True)


def _ensure_authenticated() -> bool:
    """
    Ensure user is authenticated before running AI commands.

    Returns True if authenticated, False otherwise.
    """
    from .auth import get_auth_manager

    auth = get_auth_manager()

    # 嘗試載入已有的 token
    if auth._load_config() and auth._verify_token():
        return True

    # 需要登入
    console.print("[yellow]⚠️  尚未登入，需要先登入才能使用 AI 功能[/yellow]")
    console.print()

    # 詢問是否要登入
    try:
        do_login = typer.confirm("是否現在登入？", default=True)
        if do_login:
            return auth.ensure_authenticated(use_dev_login=False)
        else:
            console.print("[dim]提示：執行 'fwauto auth login' 進行登入[/dim]")
            return False
    except (KeyboardInterrupt, EOFError):
        console.print("\n[yellow]已取消[/yellow]")
        return False


def _ensure_ai_ready() -> bool:
    """
    確保 AI 功能所需的所有前置條件。

    檢查：
    1. AI 引擎已安裝
    2. 用戶已登入（Direct 模式跳過此檢查）

    Returns True if ready, False otherwise.
    """
    from .auth import is_direct_api_mode

    # 1. 檢查 AI 引擎
    if not _ensure_ai_engine_installed():
        return False

    # 2. Direct 模式跳過登入檢查（使用本機 Claude Max 訂閱）
    if is_direct_api_mode():
        return True

    # 3. Proxy 模式檢查登入狀態
    if not _ensure_authenticated():
        return False

    return True


def _get_auth_status() -> str:
    """Get authentication status for display."""
    from .auth import get_user_token, AUTH_CONFIG_FILE
    import json

    token = get_user_token()
    if not token:
        return "❌ 未登入"

    # Try to get email from config
    try:
        if AUTH_CONFIG_FILE.exists():
            with open(AUTH_CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                email = config.get('email', '')
                if email:
                    return f"✅ {email}"
    except Exception:
        pass

    return "✅ 已登入"


def _get_help_info() -> str:
    """Generate help information string.

    Returns formatted help text including:
    - Version
    - Available commands
    - Environment info (Python, platform, project path)
    - Auth status
    """
    import platform
    from importlib.metadata import version

    from .config import find_project_root
    from .auth import FWAUTO_SERVER_URL

    # Get version
    try:
        ver = version("fwauto")
    except Exception:
        ver = "unknown"

    # Get project root
    project_root = find_project_root()
    project_path = str(project_root) if project_root else "不在專案目錄中"

    # Get auth status
    auth_status = _get_auth_status()

    # Build help text
    help_text = f"""🚀 FWAuto v{ver}

📋 支援的指令：
  build       🔨 Build firmware project
  deploy      📥 Deploy firmware to device
  run         ⚡ Run build and deploy
  log         📊 Analyze UART log files
  feat        🚀 AI-assisted feature implementation
  chat        💬 Chat with AI
  init        🚀 Initialize new project
  setup       🔧 Setup environment (PATH + AI engine)
  dashboard   🌐 Show Dashboard URL
  help        ❓ Show this help message

📚 RAG 命令（專案級別）：
  rag project create <name>     建立 RAG 專案
  rag project list              列出所有專案
  rag project info <id|slug>    查看專案詳情
  rag project delete <id|slug>  刪除專案
  rag upload <path> -p <proj>   上傳文件到專案
  rag list -p <project>         列出專案文件
  rag search <query> -p <proj>  搜尋專案文件
  rag delete -p <proj> --file   刪除文件

🔐 認證指令：
  auth login     登入
  auth logout    登出
  auth status    查看登入狀態

💡 直接執行 fwauto（無參數）進入互動模式

🔧 環境資訊：
  Python:    {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}
  Platform:  {platform.system().lower()}
  Project:   {project_path}

🔐 登入狀態： {auth_status}
🌐 Dashboard: {FWAUTO_SERVER_URL}/dashboard"""

    return help_text


def _build_deploy_state(
    binary_args: str,
    project_root: str,
    platform: str,
) -> FirmwareState:
    """Build FirmwareState for deploy command.

    Used by both CLI deploy command and /deploy slash command.

    Args:
        binary_args: Binary arguments string
        project_root: Project root path
        platform: Platform identifier

    Returns:
        FirmwareState configured for deploy
    """
    return {
        "user_prompt": "部署韌體到裝置",
        "project_root": project_root,
        "project_initialized": True,
        "platform": platform,
        "execution_mode": "deploy",
        "command": "deploy",
        "command_args": {"binary_args": binary_args},
        "mode_metadata": {},
        "command_error": None,
        "build_status": "pending",
        "build_errors": [],
        "build_log": "",
        "deploy_status": "pending",
        "deploy_errors": [],
        "deploy_log": "",
        "iteration": 0,
        "max_retries": 3,
        "log_file_path": None,
        "log_analysis_result": None,
        "firmware_path": None,
    }


def _build_log_state(
    log_path: str | None,
    analysis_prompt: str,
    project_root: str,
    platform: str,
) -> FirmwareState:
    """Build FirmwareState for log command.

    Used by both CLI log command and /log slash command.
    Maintains double storage pattern for log_file_path.

    Args:
        log_path: Path to log file (None to auto-detect from config)
        analysis_prompt: Analysis prompt text
        project_root: Project root path
        platform: Platform identifier

    Returns:
        FirmwareState configured for log analysis
    """
    return {
        "user_prompt": analysis_prompt,
        "project_root": project_root,
        "project_initialized": True,
        "platform": platform,
        "execution_mode": "log",
        "command": "log",
        "command_args": {
            "log_path": log_path,
            "analysis_prompt": analysis_prompt,
        },
        "mode_metadata": {},
        "command_error": None,
        "build_status": "pending",
        "build_errors": [],
        "build_log": "",
        "deploy_status": "pending",
        "deploy_errors": [],
        "deploy_log": "",
        "iteration": 0,
        "max_retries": 3,
        "log_file_path": log_path,  # Double storage (None is OK, log_node will handle)
        "log_analysis_result": None,
        "firmware_path": None,
    }


def run_workflow(state: FirmwareState) -> None:
    """Execute the firmware workflow with given state."""
    workflow = create_firmware_graph()

    try:
        # Stream workflow execution
        for event in workflow.stream(state):
            for node, result in event.items():
                # Display progress
                if node == "build":
                    status = result.get("build_status")
                    if status == "success":
                        console.print("[green]✓ Build succeeded[/green]")
                    elif status == "error":
                        iteration = result.get("iteration", 0)
                        max_retries = result.get("max_retries", 3)
                        console.print(f"[red]❌ Build failed (attempt {iteration}/{max_retries})[/red]")

                elif node == "deploy":
                    status = result.get("deploy_status")
                    if status == "success":
                        console.print("[green]✓ Deploy succeeded[/green]")

                        # Show remote log path if available
                        log_file_path = result.get("log_file_path")
                        if log_file_path:
                            console.print(f"[cyan]📊 Remote log: {log_file_path}[/cyan]")

                    elif status == "error":
                        console.print("[red]❌ Deploy failed[/red]")

                        # Show brief error summary
                        errors = result.get("deploy_errors", [])
                        if errors:
                            # Show first line of error
                            error_summary = errors[0].split("\n")[0] if errors[0] else ""
                            if error_summary and error_summary != "Deploy failed: ":
                                console.print(f"[red]   {error_summary}[/red]")

                        # Hint to check detailed logs
                        console.print("[dim]📝 See detailed logs in .fwauto/logs/[/dim]")

                elif node == "log":
                    # Log analysis output is handled by the node itself
                    pass

    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Operation cancelled by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"[red]❌ Workflow error: {e}[/red]")
        sys.exit(1)


@app.command()
def build():
    """
    🔨 Build STM32 firmware project.

    Requires .fwauto/ configuration in current directory or parent directories.

    Example:
        fwauto build
    """
    console.print("[cyan]🔨 Building project (using .fwauto/ config)...[/cyan]")

    state: FirmwareState = {
        "user_prompt": "build",
        "project_root": "",
        "project_initialized": False,
        "build_status": "pending",
        "build_errors": [],
        "build_log": "",
        "deploy_status": "pending",
        "deploy_errors": [],
        "deploy_log": "",
        "iteration": 0,
        "max_retries": 3,
        "execution_mode": "build",
        "command": "build",
        "command_args": {},
        "mode_metadata": None,
        "command_error": None,
        "log_file_path": None,
        "log_analysis_result": None,
        "firmware_path": None,
    }

    run_workflow(state)


@app.command()
def deploy(
    binary_args: str = typer.Option(
        "",
        "--binary-args",
        "-ba",
        help="Arguments to pass to the binary (e.g., 'on' or '--mode test')",
    ),
    scenario: str = typer.Option(
        "",
        "--scenario",
        "-s",
        help="Use a predefined scenario (overridden by --binary-args)",
    ),
):
    """
    📥 Deploy firmware to device.

    Supports passing arguments to the binary after deployment.

    \b
    Examples:
        fwauto deploy                             # Deploy without arguments
        fwauto deploy --binary-args "on"          # Pass single argument
        fwauto deploy -ba "arg1 arg2"             # Pass multiple arguments
        fwauto deploy --scenario led-on           # Use predefined scenario
        fwauto deploy -s test-mode                # Use scenario (short option)
    """
    console.print("[cyan]📥 Deploying firmware (using .fwauto/ config)...[/cyan]")

    # 優先級：--binary-args > --scenario
    final_binary_args = binary_args

    if not final_binary_args and scenario:
        # 載入 scenario
        try:
            from .config import find_project_root, load_project_config

            project_root = find_project_root()
            if not project_root:
                console.print("[red]❌ Not in a FWAuto project (no .fwauto/ found)[/red]")
                raise typer.Exit(1)

            config = load_project_config(project_root)
            scenario_manager = config.get_scenario_manager()

            scenario_obj = scenario_manager.get_scenario(scenario)
            if not scenario_obj:
                console.print(f"[red]❌ Scenario '{scenario}' not found[/red]")
                console.print("[yellow]💡 Check scenarios in .fwauto/config.toml[/yellow]")
                raise typer.Exit(1)

            final_binary_args = scenario_obj.binary_args
            console.print(f"[green]✓[/green] Using scenario: {scenario_obj.name}")
            console.print(f"[dim]  Description: {scenario_obj.description}[/dim]")
            console.print(f"[dim]  Args: {scenario_obj.binary_args}[/dim]")

        except typer.Exit:
            raise
        except Exception as e:
            console.print(f"[red]❌ Failed to load scenario: {e}[/red]")
            raise typer.Exit(1)

    if final_binary_args:
        console.print(f"[cyan]📦 Binary args: {final_binary_args}[/cyan]")

    # Get project config for helper function
    from .config import find_project_root, load_project_config

    project_root_path = find_project_root()
    if not project_root_path:
        console.print("[red]❌ Not in a FWAuto project (no .fwauto/ found)[/red]")
        raise typer.Exit(1)

    config = load_project_config(project_root_path)
    sdk_type = config.sdk_type or "unknown"

    # Use helper function to build state
    state = _build_deploy_state(final_binary_args, str(project_root_path), sdk_type)

    run_workflow(state)


@app.command()
def run(
    binary_args: str = typer.Option(
        "",
        "--binary-args",
        "-ba",
        help="Arguments to pass to the binary (e.g., 'on' or '--mode test')",
    ),
    scenario: str = typer.Option(
        "",
        "--scenario",
        "-s",
        help="Use a predefined scenario (overridden by --binary-args)",
    ),
):
    """
    ⚡ Run build and deploy.

    Builds the project and deploys to device with optional binary arguments.

    \b
    Examples:
        fwauto run                                # Build and deploy
        fwauto run --binary-args "on"             # Build, deploy with argument
        fwauto run -ba "arg1 arg2"                # Build, deploy with multiple args
        fwauto run --scenario led-on              # Build, deploy with scenario
        fwauto run -s test-mode                   # Build, deploy with scenario (short)
    """
    console.print("[cyan]⚡ Run build and deploy (using .fwauto/ config)...[/cyan]")

    # 優先級：--binary-args > --scenario
    final_binary_args = binary_args

    if not final_binary_args and scenario:
        # 載入 scenario
        try:
            from .config import find_project_root, load_project_config

            project_root = find_project_root()
            if not project_root:
                console.print("[red]❌ Not in a FWAuto project (no .fwauto/ found)[/red]")
                raise typer.Exit(1)

            config = load_project_config(project_root)
            scenario_manager = config.get_scenario_manager()

            scenario_obj = scenario_manager.get_scenario(scenario)
            if not scenario_obj:
                console.print(f"[red]❌ Scenario '{scenario}' not found[/red]")
                console.print("[yellow]💡 Check scenarios in .fwauto/config.toml[/yellow]")
                raise typer.Exit(1)

            final_binary_args = scenario_obj.binary_args
            console.print(f"[green]✓[/green] Using scenario: {scenario_obj.name}")
            console.print(f"[dim]  Description: {scenario_obj.description}[/dim]")
            console.print(f"[dim]  Args: {scenario_obj.binary_args}[/dim]")

        except typer.Exit:
            raise
        except Exception as e:
            console.print(f"[red]❌ Failed to load scenario: {e}[/red]")
            raise typer.Exit(1)

    if final_binary_args:
        console.print(f"[cyan]📦 Binary args: {final_binary_args}[/cyan]")

    state: FirmwareState = {
        "user_prompt": "run",
        "project_root": "",
        "project_initialized": False,
        "build_status": "pending",
        "build_errors": [],
        "build_log": "",
        "deploy_status": "pending",
        "deploy_errors": [],
        "deploy_log": "",
        "iteration": 0,
        "max_retries": 3,
        "execution_mode": "run",
        "command": "run",
        "command_args": {"binary_args": final_binary_args},
        "mode_metadata": {"deploy_after_build": True},
        "command_error": None,
        "log_file_path": None,
        "log_analysis_result": None,
        "firmware_path": None,
    }

    run_workflow(state)


@app.command(name="log")
def log_command(
    prompt: str = typer.Argument(..., help="Analysis question or query"),
    log_path: str | None = typer.Option(
        None,
        "--log-path",
        "-l",
        help="Path to UART log file (local or remote: user@host:/path). If not provided, uses last log from config.",
    ),
):
    """
    📊 Analyze UART log files using AI.

    Supports both local and remote log files via SSH/SCP.

    Examples:
        fwauto log "有任何 error 嗎?"
        fwauto log "LED的閃爍頻率為何?" --log-path logs/uart.log
        fwauto log "開機訊息" --log-path user@192.168.1.100:/var/log/uart.log
    """
    # 檢查 AI 功能是否可用
    if not _ensure_ai_ready():
        raise typer.Exit(1)

    if log_path:
        console.print(f"[cyan]📊 Analyzing log: {log_path}[/cyan]")
    else:
        console.print("[cyan]📊 Using log path from last deployment...[/cyan]")
    console.print(f"[cyan]❓ Question: {prompt}[/cyan]")

    # Get project config for helper function
    from .config import find_project_root, load_project_config

    project_root_path = find_project_root()
    if not project_root_path:
        console.print("[red]❌ Not in a FWAuto project (no .fwauto/ found)[/red]")
        raise typer.Exit(1)

    config = load_project_config(project_root_path)
    sdk_type = config.sdk_type or "unknown"

    # Use helper function to build state (pass None if not provided)
    state = _build_log_state(log_path, prompt, str(project_root_path), sdk_type)

    run_workflow(state)


@app.command()
def feat(
    prompt: str = typer.Argument(..., help="Feature description in natural language"),
):
    """
    🚀 AI-assisted firmware feature implementation.

    Automatically implements new firmware features with AI assistance,
    including code generation, compilation, auto-fix, and deployment.

    Examples:
        fwauto feat "實作摩斯密碼編碼，支援字符 A-Z"
        fwauto feat "加入蜂鳴器控制，發出 100ms 短音和 300ms 長音"
    """
    # 檢查 AI 功能是否可用
    if not _ensure_ai_ready():
        raise typer.Exit(1)

    console.print("[cyan]🚀 AI Feature Implementation[/cyan]")
    console.print(f"[yellow]Feature: {prompt}[/yellow]\n")

    state: FirmwareState = {
        "user_prompt": prompt,
        "project_root": "",
        "project_initialized": False,
        "build_status": "pending",
        "build_errors": [],
        "build_log": "",
        "deploy_status": "pending",
        "deploy_errors": [],
        "deploy_log": "",
        "iteration": 0,
        "max_retries": 3,
        "execution_mode": "feat",
        "command": "feat",
        "command_args": {"feature_prompt": prompt},
        "mode_metadata": {"deploy_after_build": True},
        "command_error": None,
        "log_file_path": None,
        "log_analysis_result": None,
        "firmware_path": None,
        "platform": "stm32_keil",
    }

    run_workflow(state)


# ============================================================
# RAG Sub-commands (Project-level RAG)
# ============================================================

rag_app = typer.Typer(help="📚 RAG document management (project-level)")
app.add_typer(rag_app, name="rag")

# RAG Project sub-commands
rag_project_app = typer.Typer(help="📁 Project management")
rag_app.add_typer(rag_project_app, name="project")


def _get_rag_api_client():
    """取得 RAG API client 所需的資訊"""
    from .auth import get_user_token, get_auth_server_url
    import requests

    token = get_user_token()
    if not token:
        return None, None, None

    server_url = get_auth_server_url()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    return requests, server_url, headers


def _format_file_size(size_bytes: int) -> str:
    """格式化檔案大小"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


@rag_project_app.command(name="create")
def rag_project_create(
    name: str = typer.Argument(..., help="Project name"),
    description: str = typer.Option("", "--desc", "-d", help="Project description"),
):
    """
    📁 Create a new RAG project.

    Examples:
        fwauto rag project create "My Firmware Docs"
        fwauto rag project create "STM32 Manual" --desc "Official STM32 documentation"
    """
    if not _ensure_authenticated():
        raise typer.Exit(1)

    requests, server_url, headers = _get_rag_api_client()

    console.print(f"[cyan]📁 Creating project: {name}[/cyan]")

    try:
        response = requests.post(
            f"{server_url}/api/projects",
            headers=headers,
            json={"name": name, "description": description},
            timeout=30
        )

        if response.status_code == 201:
            data = response.json()
            project = data.get("project", {})
            console.print(f"[green]✅ Project created successfully![/green]")
            console.print(f"   ID: {project.get('id')}")
            console.print(f"   Name: {project.get('name')}")
            console.print(f"   Slug: {project.get('slug')}")
        elif response.status_code == 409:
            console.print(f"[red]❌ Project '{name}' already exists[/red]")
            raise typer.Exit(1)
        else:
            console.print(f"[red]❌ Failed to create project: {response.text}[/red]")
            raise typer.Exit(1)

    except requests.exceptions.RequestException as e:
        console.print(f"[red]❌ Connection error: {e}[/red]")
        raise typer.Exit(1)


@rag_project_app.command(name="list")
def rag_project_list():
    """
    📋 List all RAG projects.

    Example:
        fwauto rag project list
    """
    if not _ensure_authenticated():
        raise typer.Exit(1)

    requests, server_url, headers = _get_rag_api_client()

    try:
        response = requests.get(
            f"{server_url}/api/projects",
            headers=headers,
            timeout=30
        )

        if response.status_code != 200:
            console.print(f"[red]❌ Failed to list projects: {response.text}[/red]")
            raise typer.Exit(1)

        data = response.json()
        projects = data.get("projects", [])

        if not projects:
            console.print("[yellow]No projects found.[/yellow]")
            console.print("[dim]Use 'fwauto rag project create <name>' to create one.[/dim]")
            return

        console.print(f"[cyan]📋 Your RAG Projects ({len(projects)})[/cyan]")
        console.print("=" * 60)

        for p in projects:
            doc_count = p.get("document_count", 0)
            total_size = p.get("total_size_bytes", 0)
            size_str = _format_file_size(total_size) if total_size else "0 B"

            console.print(f"\n[bold]{p.get('name')}[/bold] [dim](ID: {p.get('id')})[/dim]")
            console.print(f"   Slug: {p.get('slug')}")
            if p.get("description"):
                console.print(f"   Description: {p.get('description')}")
            console.print(f"   Documents: {doc_count} ({size_str})")

        console.print()

    except requests.exceptions.RequestException as e:
        console.print(f"[red]❌ Connection error: {e}[/red]")
        raise typer.Exit(1)


@rag_project_app.command(name="info")
def rag_project_info(
    project: str = typer.Argument(..., help="Project ID or slug"),
):
    """
    📊 Show project details.

    Examples:
        fwauto rag project info 1
        fwauto rag project info my-firmware-docs
    """
    if not _ensure_authenticated():
        raise typer.Exit(1)

    requests, server_url, headers = _get_rag_api_client()

    try:
        response = requests.get(
            f"{server_url}/api/projects/{project}",
            headers=headers,
            timeout=30
        )

        if response.status_code == 404:
            console.print(f"[red]❌ Project '{project}' not found[/red]")
            raise typer.Exit(1)

        if response.status_code != 200:
            console.print(f"[red]❌ Failed to get project info: {response.text}[/red]")
            raise typer.Exit(1)

        data = response.json()
        p = data.get("project", {})

        console.print(f"\n[cyan]📊 Project: {p.get('name')}[/cyan]")
        console.print("=" * 50)
        console.print(f"   ID: {p.get('id')}")
        console.print(f"   Slug: {p.get('slug')}")
        console.print(f"   Description: {p.get('description') or '(none)'}")
        console.print(f"   Documents: {p.get('document_count', 0)}")
        console.print(f"   Total Size: {_format_file_size(p.get('total_size_bytes', 0))}")
        console.print(f"   Created: {p.get('created_at')}")
        console.print()

    except requests.exceptions.RequestException as e:
        console.print(f"[red]❌ Connection error: {e}[/red]")
        raise typer.Exit(1)


@rag_project_app.command(name="delete")
def rag_project_delete(
    project: str = typer.Argument(..., help="Project ID or slug"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    """
    🗑️ Delete a RAG project and all its documents.

    Examples:
        fwauto rag project delete 1
        fwauto rag project delete my-firmware-docs --force
    """
    if not _ensure_authenticated():
        raise typer.Exit(1)

    requests, server_url, headers = _get_rag_api_client()

    # 先取得專案資訊
    try:
        response = requests.get(
            f"{server_url}/api/projects/{project}",
            headers=headers,
            timeout=30
        )

        if response.status_code == 404:
            console.print(f"[red]❌ Project '{project}' not found[/red]")
            raise typer.Exit(1)

        if response.status_code != 200:
            console.print(f"[red]❌ Failed to get project: {response.text}[/red]")
            raise typer.Exit(1)

        data = response.json()
        p = data.get("project", {})
        project_name = p.get("name")
        doc_count = p.get("document_count", 0)

    except requests.exceptions.RequestException as e:
        console.print(f"[red]❌ Connection error: {e}[/red]")
        raise typer.Exit(1)

    # 確認刪除
    if not force:
        console.print(f"[yellow]⚠️  Warning: This will delete project '{project_name}' and {doc_count} document(s).[/yellow]")
        try:
            confirm = typer.confirm("Are you sure?", default=False)
            if not confirm:
                console.print("[dim]Cancelled[/dim]")
                raise typer.Exit(0)
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Cancelled[/dim]")
            raise typer.Exit(0)

    # 執行刪除
    try:
        response = requests.delete(
            f"{server_url}/api/projects/{project}",
            headers=headers,
            timeout=30
        )

        if response.status_code == 200:
            console.print(f"[green]✅ Project '{project_name}' deleted successfully![/green]")
        else:
            console.print(f"[red]❌ Failed to delete project: {response.text}[/red]")
            raise typer.Exit(1)

    except requests.exceptions.RequestException as e:
        console.print(f"[red]❌ Connection error: {e}[/red]")
        raise typer.Exit(1)


@rag_app.command(name="upload")
def rag_upload(
    path: Path = typer.Argument(..., help="File or folder path to upload"),
    project: str = typer.Option(..., "--project", "-p", help="Project ID or slug"),
    recursive: bool = typer.Option(False, "--recursive", "-r", help="Upload folders recursively"),
):
    """
    📤 Upload files to a RAG project.

    Supports single file, multiple files, or entire folders.
    Shows upload progress with a progress bar.

    Examples:
        fwauto rag upload ./doc.pdf -p my-project
        fwauto rag upload ./docs/ -p my-project
        fwauto rag upload ./docs/ -p my-project --recursive
    """
    if not _ensure_authenticated():
        raise typer.Exit(1)

    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    import requests as req_lib
    from .auth import get_user_token, get_auth_server_url

    token = get_user_token()
    server_url = get_auth_server_url()

    # 驗證路徑
    if not path.exists():
        console.print(f"[red]❌ Path not found: {path}[/red]")
        raise typer.Exit(1)

    # 收集要上傳的檔案
    supported_extensions = {'.txt', '.md', '.pdf', '.docx'}
    files_to_upload = []

    if path.is_file():
        if path.suffix.lower() in supported_extensions:
            files_to_upload.append(path)
        else:
            console.print(f"[red]❌ Unsupported file type: {path.suffix}[/red]")
            console.print(f"[dim]Supported types: {', '.join(supported_extensions)}[/dim]")
            raise typer.Exit(1)
    else:
        # 目錄
        if recursive:
            for ext in supported_extensions:
                files_to_upload.extend(path.rglob(f"*{ext}"))
        else:
            for ext in supported_extensions:
                files_to_upload.extend(path.glob(f"*{ext}"))

    if not files_to_upload:
        console.print(f"[yellow]No supported files found in {path}[/yellow]")
        console.print(f"[dim]Supported types: {', '.join(supported_extensions)}[/dim]")
        raise typer.Exit(0)

    console.print(f"[cyan]📤 Uploading {len(files_to_upload)} file(s) to project '{project}'[/cyan]")

    # 上傳檔案
    success_count = 0
    failed_files = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Uploading...", total=len(files_to_upload))

        for file_path in files_to_upload:
            progress.update(task, description=f"Uploading {file_path.name}...")

            try:
                with open(file_path, 'rb') as f:
                    files = {'files': (file_path.name, f)}
                    response = req_lib.post(
                        f"{server_url}/api/projects/{project}/documents/upload",
                        headers={"Authorization": f"Bearer {token}"},
                        files=files,
                        timeout=120
                    )

                if response.status_code in (200, 201):
                    success_count += 1
                else:
                    failed_files.append((file_path.name, response.text))

            except Exception as e:
                failed_files.append((file_path.name, str(e)))

            progress.advance(task)

    # 顯示結果
    console.print()
    if success_count > 0:
        console.print(f"[green]✅ Successfully uploaded {success_count} file(s)[/green]")

    if failed_files:
        console.print(f"[red]❌ Failed to upload {len(failed_files)} file(s):[/red]")
        for name, error in failed_files:
            console.print(f"   - {name}: {error[:50]}...")


@rag_app.command(name="list")
def rag_list(
    project: str = typer.Option(..., "--project", "-p", help="Project ID or slug"),
):
    """
    📋 List documents in a RAG project.

    Example:
        fwauto rag list -p my-project
    """
    if not _ensure_authenticated():
        raise typer.Exit(1)

    requests, server_url, headers = _get_rag_api_client()

    try:
        response = requests.get(
            f"{server_url}/api/projects/{project}/documents",
            headers=headers,
            timeout=30
        )

        if response.status_code == 404:
            console.print(f"[red]❌ Project '{project}' not found[/red]")
            raise typer.Exit(1)

        if response.status_code != 200:
            console.print(f"[red]❌ Failed to list documents: {response.text}[/red]")
            raise typer.Exit(1)

        data = response.json()
        documents = data.get("documents", [])

        if not documents:
            console.print(f"[yellow]No documents in project '{project}'[/yellow]")
            console.print("[dim]Use 'fwauto rag upload <path> -p <project>' to upload files.[/dim]")
            return

        console.print(f"[cyan]📋 Documents in '{project}' ({len(documents)})[/cyan]")
        console.print("=" * 60)

        for doc in documents:
            size_str = _format_file_size(doc.get("file_size_bytes", 0))
            file_type = doc.get("file_type", "?").upper()

            console.print(f"\n[bold]{doc.get('original_filename')}[/bold] [dim](ID: {doc.get('id')})[/dim]")
            console.print(f"   Type: {file_type} | Size: {size_str}")
            console.print(f"   Uploaded: {doc.get('created_at')}")

        console.print()

    except requests.exceptions.RequestException as e:
        console.print(f"[red]❌ Connection error: {e}[/red]")
        raise typer.Exit(1)


@rag_app.command(name="delete")
def rag_delete(
    project: str = typer.Option(..., "--project", "-p", help="Project ID or slug"),
    file_id: int = typer.Option(None, "--file", "-f", help="Document ID to delete"),
    all_files: bool = typer.Option(False, "--all", help="Delete all documents in project"),
    force: bool = typer.Option(False, "--force", help="Skip confirmation"),
):
    """
    🗑️ Delete documents from a RAG project.

    Examples:
        fwauto rag delete -p my-project --file 1
        fwauto rag delete -p my-project --all --force
    """
    if not _ensure_authenticated():
        raise typer.Exit(1)

    if file_id is None and not all_files:
        console.print("[red]❌ Please specify --file <id> or --all[/red]")
        raise typer.Exit(1)

    requests, server_url, headers = _get_rag_api_client()

    if all_files:
        # 刪除所有文件
        if not force:
            console.print(f"[yellow]⚠️  This will delete ALL documents in project '{project}'[/yellow]")
            try:
                confirm = typer.confirm("Are you sure?", default=False)
                if not confirm:
                    console.print("[dim]Cancelled[/dim]")
                    raise typer.Exit(0)
            except (KeyboardInterrupt, EOFError):
                console.print("\n[dim]Cancelled[/dim]")
                raise typer.Exit(0)

        try:
            # 先取得所有文件 ID
            response = requests.get(
                f"{server_url}/api/projects/{project}/documents",
                headers=headers,
                timeout=30
            )

            if response.status_code != 200:
                console.print(f"[red]❌ Failed to get documents: {response.text}[/red]")
                raise typer.Exit(1)

            documents = response.json().get("documents", [])
            doc_ids = [d["id"] for d in documents]

            if not doc_ids:
                console.print("[yellow]No documents to delete[/yellow]")
                return

            # 批次刪除
            response = requests.delete(
                f"{server_url}/api/projects/{project}/documents",
                headers=headers,
                json={"document_ids": doc_ids},
                timeout=60
            )

            if response.status_code == 200:
                console.print(f"[green]✅ Deleted {len(doc_ids)} document(s)[/green]")
            else:
                console.print(f"[red]❌ Failed to delete documents: {response.text}[/red]")
                raise typer.Exit(1)

        except requests.exceptions.RequestException as e:
            console.print(f"[red]❌ Connection error: {e}[/red]")
            raise typer.Exit(1)

    else:
        # 刪除單一文件
        try:
            response = requests.delete(
                f"{server_url}/api/projects/{project}/documents/{file_id}",
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                console.print(f"[green]✅ Document {file_id} deleted[/green]")
            elif response.status_code == 404:
                console.print(f"[red]❌ Document {file_id} not found[/red]")
                raise typer.Exit(1)
            else:
                console.print(f"[red]❌ Failed to delete document: {response.text}[/red]")
                raise typer.Exit(1)

        except requests.exceptions.RequestException as e:
            console.print(f"[red]❌ Connection error: {e}[/red]")
            raise typer.Exit(1)


@rag_app.command(name="search")
def rag_search(
    query: str = typer.Argument(..., help="Search query"),
    project: str = typer.Option(..., "--project", "-p", help="Project ID or slug"),
    top_k: int = typer.Option(5, "--top-k", "-k", help="Number of results to return"),
    auto_select: bool = typer.Option(False, "--auto", "-a", help="Automatically select all results for AI"),
):
    """
    🔍 Search documents in a RAG project.

    Search your uploaded documents and optionally use results with AI.

    Examples:
        fwauto rag search "GPIO configuration" -p my-project
        fwauto rag search "error handling" -p my-project --top-k 10
        fwauto rag search "LED control" -p my-project --auto
    """
    if not _ensure_authenticated():
        raise typer.Exit(1)

    requests, server_url, headers = _get_rag_api_client()

    console.print(f"[cyan]🔍 Searching in project '{project}'[/cyan]")
    console.print(f"[yellow]Query: {query}[/yellow]\n")

    try:
        response = requests.post(
            f"{server_url}/api/projects/{project}/search",
            headers=headers,
            json={"query": query, "top_k": top_k},
            timeout=60
        )

        if response.status_code == 404:
            console.print(f"[red]❌ Project '{project}' not found[/red]")
            raise typer.Exit(1)

        if response.status_code != 200:
            console.print(f"[red]❌ Search failed: {response.text}[/red]")
            raise typer.Exit(1)

        data = response.json()
        results = data.get("results", [])

    except requests.exceptions.RequestException as e:
        console.print(f"[red]❌ Connection error: {e}[/red]")
        raise typer.Exit(1)

    if not results:
        console.print("[yellow]No matching documents found[/yellow]")
        raise typer.Exit(0)

    console.print(f"[green]Found {len(results)} result(s):[/green]\n")

    for i, result in enumerate(results, 1):
        score = result.get("score", 0)
        doc = result.get("document_name", "unknown")
        text = result.get("text", "")

        preview = text[:150] + "..." if len(text) > 150 else text
        preview = preview.replace("\n", " ")

        score_color = "green" if score > 0.7 else "yellow" if score > 0.4 else "red"
        console.print(f"[bold][{i}][/bold] [{score_color}]{score:.0%}[/{score_color}] 📄 {doc}")
        console.print(f"    [dim]{preview}[/dim]")
        console.print()

    # 讓用戶選擇要使用的片段
    if auto_select:
        selected_indices = list(range(len(results)))
        console.print("[cyan]--auto mode: selecting all results[/cyan]\n")
    else:
        console.print("[cyan]Select results for AI context (comma-separated numbers, 'all', or 'q' to quit):[/cyan]")
        try:
            selection = typer.prompt("Selection", default="q")

            if selection.lower() == 'q':
                console.print("[dim]Done[/dim]")
                raise typer.Exit(0)
            elif selection.lower() == 'all':
                selected_indices = list(range(len(results)))
            else:
                selected_indices = []
                for part in selection.split(","):
                    part = part.strip()
                    if part.isdigit():
                        idx = int(part) - 1
                        if 0 <= idx < len(results):
                            selected_indices.append(idx)

        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Cancelled[/dim]")
            raise typer.Exit(0)

    if not selected_indices:
        console.print("[dim]No results selected[/dim]")
        raise typer.Exit(0)

    # 組合 context
    selected_chunks = [results[i] for i in selected_indices]
    context_text = "\n\n---\n\n".join([
        f"[Source: {c.get('document_name', 'unknown')}]\n{c.get('text', '')}"
        for c in selected_chunks
    ])

    console.print(f"[green]Selected {len(selected_chunks)} result(s) as context[/green]\n")

    # 詢問問題
    console.print("[cyan]Enter your question (AI will answer based on selected content):[/cyan]")
    try:
        user_question = typer.prompt("Question")
    except (KeyboardInterrupt, EOFError):
        console.print("\n[dim]Cancelled[/dim]")
        raise typer.Exit(0)

    # 建構 prompt 並執行 AI
    full_prompt = f"""Based on the following reference materials, answer the question.

## Reference Materials

{context_text}

## Question

{user_question}

## Answer

Please answer based on the reference materials above. If the information is not available, please say so."""

    console.print("\n[cyan]AI is processing...[/cyan]\n")

    state: FirmwareState = {
        "user_prompt": full_prompt,
        "project_root": "",
        "project_initialized": False,
        "build_status": "pending",
        "build_errors": [],
        "build_log": "",
        "deploy_status": "pending",
        "deploy_errors": [],
        "deploy_log": "",
        "iteration": 0,
        "max_retries": 3,
        "execution_mode": "rag",
        "command": "rag",
        "command_args": {
            "query": query,
            "question": user_question,
            "context": context_text,
            "project": project,
        },
        "mode_metadata": {"rag_context": context_text},
        "command_error": None,
        "log_file_path": None,
        "log_analysis_result": None,
        "firmware_path": None,
        "platform": "generic",
    }

    run_workflow(state)


@app.command()
def chat():
    """
    💬 Interactive chat with AI.

    Start an interactive conversation session to:
    - Ask questions about your STM32 project
    - Request code modifications or new features
    - Get help with debugging and analysis
    - Explore codebase structure

    Requires .fwauto/ configuration in current directory or parent directories.

    Examples:
        fwauto chat
    """
    # 檢查 AI 功能是否可用
    if not _ensure_ai_ready():
        raise typer.Exit(1)

    console.print("[cyan]💬 Starting interactive chat session...[/cyan]")

    state: FirmwareState = {
        "user_prompt": "chat",
        "project_root": "",
        "project_initialized": False,
        "build_status": "pending",
        "build_errors": [],
        "build_log": "",
        "deploy_status": "pending",
        "deploy_errors": [],
        "deploy_log": "",
        "iteration": 0,
        "max_retries": 3,
        "execution_mode": "chat",
        "command": "chat",
        "command_args": {},
        "mode_metadata": None,
        "command_error": None,
        "log_file_path": None,
        "log_analysis_result": None,
        "firmware_path": None,
        "platform": "stm32_keil",
    }

    run_workflow(state)


@app.command()
def init(
    path: Path | None = typer.Argument(None, help="Project root path (default: current directory)"),
):
    """
    🚀 Initialize new FWAuto project with .fwauto/ configuration.

    Creates .fwauto/ directory structure and configuration files.

    Examples:
        fwauto init              # Initialize in current directory
        fwauto init ./my-project # Initialize in specified directory
    """
    project_root = path if path else Path.cwd()
    console.print(f"[cyan]🚀 Initializing FWAuto project in {project_root}[/cyan]\n")

    success = run_init_wizard(project_root)
    sys.exit(0 if success else 1)


@app.command(name="help")
def help_command():
    """
    ❓ Show help information.

    Displays available commands, version, environment info, and API key status.

    Example:
        fwauto help
    """
    console.print(_get_help_info())


@app.command(name="setup")
def setup_command():
    """
    🔧 Setup FWAuto environment.

    Automatically configures:
    - PATH environment variable for fwauto command
    - AI engine installation

    Run this after installing fwauto via 'uv tool install fwauto'.

    Examples:
        fwauto setup
    """
    from .claude_code_installer import run_full_setup

    success = run_full_setup(silent=False)
    raise typer.Exit(0 if success else 1)


def _enter_unified_chat_mode() -> None:
    """Enter unified chat interface mode.

    This replaces the old _interactive_mode() function.
    Uses chat_node for interactive conversation with slash command support.
    """
    from .config import find_project_root, load_project_config
    from .logging_config import get_logger

    logger = get_logger(__name__)

    try:
        # Load project config (with anchor-based discovery)
        project_root = find_project_root()
        if not project_root:
            console.print("[red]❌ Not in a FWAuto project (no .fwauto/ found)[/red]")
            console.print(
                "[yellow]提示：請在 FWAuto 專案目錄（包含 .fwauto/）中執行此指令，或使用 'fwauto init' 初始化專案[/yellow]"
            )
            sys.exit(1)

        config = load_project_config(project_root)
        sdk_type = config.sdk_type or "unknown"

        console.print(f"[cyan]📁 專案路徑: {project_root}[/cyan]")
        console.print(f"[cyan]🔧 SDK: {sdk_type}[/cyan]")
        console.print("[cyan]💬 進入對話模式（輸入 /exit 或按 Ctrl+D 離開）[/cyan]")
        console.print("[dim]提示：使用 /build, /deploy, /log 執行指令[/dim]\n")

        # Build initial state for chat mode
        state: FirmwareState = {
            "user_prompt": "",
            "project_root": str(project_root),
            "project_initialized": True,
            "platform": sdk_type,
            "execution_mode": "chat",
            "command": "chat",
            "command_args": {},
            "mode_metadata": {},
            "command_error": None,
            "build_status": "pending",
            "build_errors": [],
            "build_log": "",
            "deploy_status": "pending",
            "deploy_errors": [],
            "deploy_log": "",
            "iteration": 0,
            "max_retries": 3,
            "log_file_path": None,
            "log_analysis_result": None,
            "firmware_path": None,
            "chat_completed": None,
        }

        # Create and execute graph (which will route to chat_node)
        app_graph = create_firmware_graph()
        result = app_graph.invoke(state)

        logger.debug(f"💬 Chat: Graph result chat_completed = {result.get('chat_completed')}")
        if result.get("chat_completed"):
            console.print("\n[green]✅ 對話結束[/green]")
        else:
            console.print("\n[yellow]⚠️ 對話異常結束[/yellow]")

    except KeyboardInterrupt:
        # 使用者按 Ctrl+C 終止，視為正常結束
        console.print("\n[green]✅ 對話結束[/green]")

    except FileNotFoundError as e:
        console.print(f"[red]❌ 找不到專案：{e}[/red]")
        console.print("[yellow]提示：請在 FWAuto 專案目錄（包含 .fwauto/）中執行此指令[/yellow]")
        sys.exit(1)

    except Exception as e:
        logger.error(f"Chat mode failed: {e}", exc_info=True)
        console.print(f"[red]❌ 對話模式啟動失敗：{e}[/red]")
        sys.exit(1)


def main():
    """Entry point for the CLI."""
    # Initialize logging first (ensures debug logs for all commands)
    init_project_logging()

    # Check if running in unified chat mode (no arguments)
    if len(sys.argv) == 1:
        _enter_unified_chat_mode()
    else:
        app()


if __name__ == "__main__":
    main()
