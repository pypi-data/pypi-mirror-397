"""Interactive initialization wizard for FWAuto projects."""

import platform
from pathlib import Path

import tomli_w
from rich.console import Console
from rich.prompt import Confirm, IntPrompt, Prompt

from ..template_manager import TemplateManager
from ..user_config import UserConfig

console = Console()


def _get_current_os() -> str:
    """檢測當前操作系統並返回標準化名稱"""
    system = platform.system().lower()
    if system == "linux":
        # 檢查是否為 WSL
        try:
            with open("/proc/version") as f:
                if "microsoft" in f.read().lower():
                    return "wsl"
        except FileNotFoundError:
            pass
        return "linux"
    elif system == "darwin":
        return "macos"
    elif system == "windows":
        return "windows"
    return "unknown"


def _filter_sdks_by_os(configured_sdks: dict, template_manager: TemplateManager) -> dict:
    """根據當前操作系統過濾可用的 SDK"""
    current_os = _get_current_os()
    compatible_sdks = {}

    for sdk_type, sdk_info in configured_sdks.items():
        # 檢查是否有對應的 template
        template_path = template_manager.get_template(sdk_type)
        if not template_path:
            continue

        # 讀取 template metadata
        templates = template_manager.list_available_templates()
        template_data = next((t for t in templates if t["sdk_type"] == sdk_type), None)
        if not template_data:
            continue

        # 檢查 OS 兼容性
        supported_os = template_data["metadata"].get("compatibility", {}).get("os", [])
        if not supported_os or current_os in supported_os:
            compatible_sdks[sdk_type] = sdk_info

    return compatible_sdks


def run_init_wizard(project_root: Path | None = None, overwrite: bool = False) -> bool:
    """
    互動式初始化專案

    Returns:
        True if initialization succeeded, False otherwise
    """
    if project_root is None:
        project_root = Path.cwd()

    fwauto_dir = project_root / ".fwauto"

    # 檢查是否已初始化
    if fwauto_dir.exists() and not overwrite:
        console.print("[yellow]⚠️  專案已初始化，使用 'fwauto init --overwrite' 重新設定[/yellow]")
        return False

    console.print("\n[cyan]=== FWAuto 專案初始化 ===[/cyan]\n")

    # Step 1: 檢查 User Config 是否已有 SDK 設定
    user_config = UserConfig()
    configured_sdks = user_config.data.get("sdk", {})
    sdk_type = ""
    sdk_path = ""
    device_family = ""
    device_model = ""
    use_existing_config = False

    if configured_sdks:
        # 根據當前操作系統過濾可用的 SDK
        template_manager = TemplateManager()
        compatible_sdks = _filter_sdks_by_os(configured_sdks, template_manager)

        if not compatible_sdks:
            console.print("[yellow]⚠️  找不到與當前操作系統兼容的 SDK 設定[/yellow]")
            console.print("[yellow]   將進入手動選擇模式[/yellow]")
        else:
            # 建立選項列表：已配置的 + 未配置的
            all_templates = template_manager.list_available_templates()
            configured_sdk_ids = set(compatible_sdks.keys())

            options = []  # 格式: [(sdk_type, is_configured, sdk_info_or_template), ...]

            # 已配置的 SDK
            if compatible_sdks:
                console.print("[bold]已配置的 SDK:[/bold]")
                for sdk_id, sdk_info in compatible_sdks.items():
                    device_info = user_config.get_device_config(sdk_id)
                    device_str = "未設定"
                    if device_info:
                        device_str = f"{device_info.get('family', 'N/A')} / {device_info.get('model', 'N/A')}"
                    idx = len(options) + 1
                    console.print(f"  {idx}. {sdk_id} ({sdk_info.get('path', 'N/A')}) - 裝置: {device_str}")
                    options.append((sdk_id, True, sdk_info))

            # 可用但未配置的 SDK (需過濾 OS)
            unconfigured_templates = [t for t in all_templates if t["sdk_type"] not in configured_sdk_ids]

            # 過濾 OS 兼容性
            current_os = _get_current_os()
            compatible_unconfigured = []
            for template in unconfigured_templates:
                supported_os = template["metadata"].get("compatibility", {}).get("os", [])
                if not supported_os or current_os in supported_os:
                    compatible_unconfigured.append(template)

            if compatible_unconfigured:
                console.print("\n[bold]可用但未配置的 SDK:[/bold]")
                for template in compatible_unconfigured:
                    idx = len(options) + 1
                    meta = template["metadata"]["template"]
                    console.print(f"  {idx}. {meta['name']}")
                    options.append((template["sdk_type"], False, template))

            # 讓用戶選擇
            choice = IntPrompt.ask("\n請選擇", choices=[str(i) for i in range(1, len(options) + 1)])

            selected_sdk_type, is_configured, data = options[choice - 1]

            if is_configured:
                # 用戶選擇已配置的 SDK
                sdk_type = selected_sdk_type
                sdk_path = data.get("path", "")
                device_info = user_config.get_device_config(sdk_type)
                if device_info:
                    device_family = device_info.get("family", "")
                    device_model = device_info.get("model", "")
                use_existing_config = True
                console.print(f"\n[green]✓ 已選擇: {sdk_type}[/green]")
            else:
                # 用戶選擇未配置的 SDK
                sdk_type = selected_sdk_type
                console.print(f"\n[green]✓ 已選擇: {data['metadata']['template']['name']}[/green]")
                # sdk_type 已設定，但 sdk_path 為空，後續會要求輸入

    # Step 2: 如果沒有 SDK 配置，進入完整選擇流程
    if not sdk_type:
        # User config 沒有 SDK 設定，或選擇的 SDK 沒有對應 template
        # 進入傳統流程：列出可用 templates
        template_manager = TemplateManager()
        templates = template_manager.list_available_templates()

        if not templates:
            console.print("[red]❌ 未找到可用的 SDK templates[/red]")
            return False

        console.print("[bold]可用的 SDK Templates:[/bold]")
        for i, template in enumerate(templates, 1):
            meta = template["metadata"]["template"]
            console.print(f"  {i}. {meta['name']} - {meta['description']}")

        while True:
            choice = IntPrompt.ask("\n請選擇 SDK template", choices=[str(i) for i in range(1, len(templates) + 1)])
            choice_idx = choice - 1
            if 0 <= choice_idx < len(templates):
                break

        sdk_type = templates[choice_idx]["sdk_type"]
        console.print(f"\n[green]✓ 已選擇: {templates[choice_idx]['metadata']['template']['name']}[/green]")

    # Step 2.5: 如果選擇了未配置的 SDK，要求輸入路徑
    if sdk_type and not sdk_path:
        sdk_path = Prompt.ask(f"\n請輸入 {sdk_type} SDK 安裝路徑", default="/home/alientek/ATK-AM62x-SDK")

        # 驗證路徑存在
        if not Path(sdk_path).exists():
            console.print(f"[yellow]⚠️  警告: 路徑 {sdk_path} 不存在[/yellow]")
            confirm = Confirm.ask("仍要繼續？", default=False)
            if not confirm:
                return False

        # 儲存至 User Config
        sdk_version = Prompt.ask("SDK 版本 (可選，直接 Enter 跳過)", default="unknown")
        user_config.set_sdk_config(
            sdk_type,
            {"type": sdk_type, "path": sdk_path, "version": sdk_version},
        )
        console.print("[green]✓ SDK 資訊已儲存至 ~/.fwauto/config.toml[/green]")

    # Step 3: 輸入裝置資訊（如果沒有使用現有配置）
    if not use_existing_config:
        console.print("\n[bold]=== 裝置設定 ===[/bold]")
        device_family = Prompt.ask("裝置系列 (e.g., stm32f4, am62x)", default="am62x")
        device_model = Prompt.ask("裝置型號 (e.g., STM32F407VGT6)", default="ATK-DLAM62xB")

        # 儲存裝置設定至 User Config
        user_config.set_device_config(
            sdk_type,
            {"family": device_family, "model": device_model},
        )
        console.print("[green]✓ 裝置資訊已儲存至 ~/.fwauto/config.toml[/green]")

    # Step 3.5: Deployment 配置（僅限 AM62X）
    if not use_existing_config and "am62x" in sdk_type.lower():
        console.print("\n[bold]=== Deployment 設定 ===[/bold]")
        board_ip = Prompt.ask("開發板 IP 地址", default="192.168.50.169")
        board_user = Prompt.ask("SSH 登入使用者", default="root")
        deploy_path = Prompt.ask("遠端部署目錄", default="/home/root")

        # 使用預設 SSH options
        ssh_options = "-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5"

        # 儲存至 User Config
        user_config.set_deployment_config(
            sdk_type,
            {
                "board_ip": board_ip,
                "board_user": board_user,
                "deploy_path": deploy_path,
                "ssh_options": ssh_options,
            },
        )
        console.print("[green]✓ Deployment 資訊已儲存至 ~/.fwauto/config.toml[/green]")

    # Step 4: 複製 template
    console.print("\n[bold]=== 複製 Templates ===[/bold]")
    success = template_manager.copy_template_to_project(sdk_type, project_root, overwrite=overwrite)

    if not success:
        console.print("[red]❌ Template 複製失敗[/red]")
        return False

    # Step 5: 建立 Project Config
    config_path = fwauto_dir / "config.toml"
    project_config_data = {
        "sdk": {
            "type": sdk_type,
            # path 不儲存，從 User Config 繼承
        },
        "device": {"family": device_family, "model": device_model},
        "build": {"target": "build", "makefile": ".fwauto/build/Makefile"},
    }

    with open(config_path, "wb") as f:
        tomli_w.dump(project_config_data, f)

    console.print(f"\n[green]✓ Project config 已建立: {config_path}[/green]")

    # Step 6: 建立 logs 目錄
    (fwauto_dir / "logs").mkdir(exist_ok=True)

    console.print("\n[bold green]✅ 初始化完成！[/bold green]")
    console.print("\n[bold]專案結構:[/bold]")
    console.print("  .fwauto/")
    console.print("    ├── config.toml")
    console.print("    ├── build/")
    console.print("    ├── deploy/")
    console.print("    └── logs/")

    return True
