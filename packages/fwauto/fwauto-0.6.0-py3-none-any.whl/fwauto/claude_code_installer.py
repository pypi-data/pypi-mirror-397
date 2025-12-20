# -*- coding: utf-8 -*-
"""
AI Engine Installer

自動檢測並安裝 FWAuto AI 引擎：
- Windows: 需要 Git Bash
- Linux/macOS: 直接支援
"""

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

from .logging_config import get_logger

logger = get_logger("ai_engine_installer")


def is_git_installed() -> bool:
    """檢查 Git 是否已安裝"""
    return shutil.which("git") is not None


def is_winget_available() -> bool:
    """檢查 winget 是否可用 (Windows 10/11 內建)"""
    if platform.system().lower() != "windows":
        return False

    try:
        result = subprocess.run(
            ["winget", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def install_git_windows(silent: bool = False) -> bool:
    """
    使用 winget 在 Windows 上自動安裝 Git

    Args:
        silent: 是否靜默安裝

    Returns:
        bool: 是否安裝成功
    """
    if not is_winget_available():
        if not silent:
            print("   ❌ winget 不可用，無法自動安裝 Git")
        return False

    if not silent:
        print("   正在使用 winget 安裝 Git...")
        print("   (這可能需要幾分鐘，請稍候)")
        print()

    try:
        # 使用 winget 安裝 Git
        result = subprocess.run(
            ["winget", "install", "--id", "Git.Git", "-e", "--accept-source-agreements", "--accept-package-agreements"],
            capture_output=not silent,
            text=True,
            timeout=600  # 10 分鐘超時
        )

        if result.returncode == 0:
            if not silent:
                print("   ✅ Git 安裝成功！")

            # 刷新環境變數（需要重開終端機才會完全生效）
            # 嘗試將 Git 加入目前 session 的 PATH
            git_paths = [
                Path("C:/Program Files/Git/cmd"),
                Path("C:/Program Files/Git/bin"),
                Path("C:/Program Files (x86)/Git/cmd"),
                Path("C:/Program Files (x86)/Git/bin"),
            ]
            for git_path in git_paths:
                if git_path.exists():
                    os.environ["PATH"] = f"{git_path};{os.environ.get('PATH', '')}"
                    break

            return True
        else:
            if not silent:
                print(f"   ❌ Git 安裝失敗 (exit code: {result.returncode})")
            logger.error(f"Git installation failed: {result.stderr if result.stderr else 'unknown error'}")
            return False

    except subprocess.TimeoutExpired:
        if not silent:
            print("   ❌ Git 安裝超時")
        logger.error("Git installation timed out")
        return False
    except Exception as e:
        if not silent:
            print(f"   ❌ Git 安裝錯誤: {e}")
        logger.error(f"Git installation error: {e}")
        return False


def get_ai_engine_paths() -> list[Path]:
    """
    取得 AI 引擎可能的安裝路徑

    Returns:
        list[Path]: 可能的安裝路徑列表
    """
    system = platform.system().lower()
    home = Path.home()
    paths = []

    if system == "windows":
        # Windows 常見安裝位置
        paths = [
            home / ".claude" / "local" / "bin",
            home / "AppData" / "Local" / "Claude" / "bin",
            home / "AppData" / "Roaming" / "Claude" / "bin",
            home / "AppData" / "Local" / "Programs" / "Claude" / "bin",
            home / ".local" / "bin",
            Path("C:/Program Files/Claude"),
            Path("C:/Program Files (x86)/Claude"),
        ]
    else:
        # Linux/macOS 常見安裝位置
        paths = [
            home / ".claude" / "local" / "bin",
            home / ".claude" / "bin",
            home / ".local" / "bin",
            Path("/usr/local/bin"),
            Path("/opt/claude/bin"),
        ]

    return paths


def find_ai_engine_executable() -> Path | None:
    """
    尋找 AI 引擎執行檔

    Returns:
        Path | None: 執行檔路徑，找不到則回傳 None
    """
    system = platform.system().lower()
    exe_name = "claude.exe" if system == "windows" else "claude"

    # 先檢查 PATH
    which_result = shutil.which("claude")
    if which_result:
        return Path(which_result)

    # 檢查常見安裝位置
    for path in get_ai_engine_paths():
        exe_path = path / exe_name
        if exe_path.exists():
            return exe_path

    return None


def is_ai_engine_installed() -> bool:
    """檢查 AI 引擎是否已安裝"""
    return find_ai_engine_executable() is not None


# Backward compatibility aliases
get_claude_code_paths = get_ai_engine_paths
find_claude_executable = find_ai_engine_executable
is_claude_code_installed = is_ai_engine_installed


def get_install_command() -> tuple[str, list[str]]:
    """
    根據作業系統返回安裝指令

    Returns:
        tuple: (shell, command_args)
    """
    system = platform.system().lower()

    if system == "windows":
        # PowerShell command
        return ("powershell", [
            "-ExecutionPolicy", "Bypass",
            "-Command",
            "irm https://claude.ai/install.ps1 | iex"
        ])
    else:
        # Linux / macOS - use bash
        return ("bash", [
            "-c",
            "curl -fsSL https://claude.ai/install.sh | bash"
        ])


def install_ai_engine(silent: bool = False) -> bool:
    """
    安裝 AI 引擎

    Args:
        silent: 是否靜默安裝（不顯示輸出）

    Returns:
        bool: 是否安裝成功
    """
    if not silent:
        print()
        print("=" * 60)
        print("🔧 安裝 FWAuto AI 引擎")
        print("=" * 60)
        print()
        print(f"   作業系統: {platform.system()}")
        print()

    shell, args = get_install_command()

    try:
        if not silent:
            print("   正在下載並安裝...")
            print()

        # 執行安裝指令
        result = subprocess.run(
            [shell] + args,
            capture_output=silent,
            text=True,
            timeout=300  # 5 分鐘超時
        )

        if result.returncode == 0:
            # 驗證安裝
            if is_ai_engine_installed():
                if not silent:
                    print()
                    print("=" * 60)
                    print("✅ AI 引擎安裝成功！")
                    print("=" * 60)
                    print()
                logger.info("AI engine installed successfully")
                return True
            else:
                if not silent:
                    print()
                    print("⚠️  安裝完成，請重新開啟終端機後再試")
                    print()
                logger.warning("AI engine installed but not found in PATH")
                # 回傳 True 因為安裝指令成功了，只是需要重開終端機
                return True
        else:
            if not silent:
                print()
                print(f"❌ 安裝失敗 (exit code: {result.returncode})")
                print()
            logger.error(f"AI engine installation failed: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        if not silent:
            print()
            print("❌ 安裝超時")
            print()
        logger.error("AI engine installation timed out")
        return False
    except FileNotFoundError as e:
        if not silent:
            print()
            print(f"❌ 找不到 {shell}: {e}")
            print()
        logger.error(f"Shell not found: {e}")
        return False
    except Exception as e:
        if not silent:
            print()
            print(f"❌ 安裝過程發生錯誤: {e}")
            print()
        logger.error(f"AI engine installation error: {e}")
        return False


# Backward compatibility alias
install_claude_code = install_ai_engine


def ensure_ai_engine_installed(auto_install: bool = True) -> bool:
    """
    確保 AI 引擎已安裝

    Args:
        auto_install: 是否自動安裝（否則只提示）

    Returns:
        bool: AI 引擎是否可用
    """
    if is_ai_engine_installed():
        logger.debug("AI engine is already installed")
        return True

    print()
    print("⚠️  FWAuto 需要安裝 AI 引擎才能使用 AI 功能")
    print()

    # Windows 需要先檢查 Git
    if platform.system().lower() == "windows" and not is_git_installed():
        print("⚠️  需要安裝 Git")
        print()

        # 嘗試使用 winget 自動安裝
        if is_winget_available():
            print("   偵測到 winget，嘗試自動安裝 Git...")
            print()
            if install_git_windows(silent=False):
                print()
                print("   ✅ Git 已安裝，繼續安裝 AI 引擎...")
                print()
            else:
                print("   ❌ 自動安裝 Git 失敗")
                print()
                print("   請手動下載安裝: https://git-scm.com/downloads/win")
                print()
                print("   安裝 Git 時請勾選:")
                print("   ✅ Git Bash Here")
                print("   ✅ Add Git to PATH")
                print()
                print("   安裝完成後請重新執行 fwauto setup")
                print()
                return False
        else:
            print("   FWAuto AI 引擎在 Windows 上需要 Git")
            print("   請下載安裝: https://git-scm.com/downloads/win")
            print()
            print("   安裝 Git 時請勾選:")
            print("   ✅ Git Bash Here")
            print("   ✅ Add Git to PATH")
            print()
            print("   安裝完成後請重新執行 fwauto setup")
            print()
            return False

    if auto_install:
        try:
            # 詢問用戶是否要安裝
            response = input("   是否現在安裝 AI 引擎？ [Y/n]: ").strip().lower()

            if response in ("", "y", "yes"):
                return install_ai_engine(silent=False)
            else:
                print()
                print("   請執行 'fwauto setup' 來安裝 AI 引擎")
                print()
                return False
        except (KeyboardInterrupt, EOFError):
            print("\n   已取消")
            return False
    else:
        print("   請執行 'fwauto setup' 來安裝 AI 引擎")
        print()
        return False


# Backward compatibility alias
ensure_claude_code_installed = ensure_ai_engine_installed


def get_uv_tool_bin_dir() -> Path:
    """
    取得 uv tool 安裝的 bin 目錄

    Returns:
        Path: bin 目錄路徑
    """
    system = platform.system().lower()

    if system == "windows":
        # Windows: %USERPROFILE%\.local\bin
        return Path.home() / ".local" / "bin"
    else:
        # Linux/macOS: ~/.local/bin
        return Path.home() / ".local" / "bin"


def is_path_configured() -> bool:
    """
    檢查 uv tool bin 目錄是否已在 PATH 中

    Returns:
        bool: 是否已設定
    """
    bin_dir = get_uv_tool_bin_dir()
    current_path = os.environ.get("PATH", "")

    return str(bin_dir) in current_path


def setup_path_windows() -> bool:
    """
    Windows: 將 uv tool bin 目錄加入使用者 PATH

    Returns:
        bool: 是否成功
    """
    bin_dir = get_uv_tool_bin_dir()

    try:
        # 使用 PowerShell 設定使用者環境變數
        # 先取得目前的使用者 PATH
        result = subprocess.run(
            ["powershell", "-Command",
             "[Environment]::GetEnvironmentVariable('Path', 'User')"],
            capture_output=True,
            text=True
        )

        current_user_path = result.stdout.strip() if result.returncode == 0 else ""

        # 檢查是否已存在
        if str(bin_dir) in current_user_path:
            return True

        # 新增到 PATH
        new_path = f"{current_user_path};{bin_dir}" if current_user_path else str(bin_dir)

        result = subprocess.run(
            ["powershell", "-Command",
             f"[Environment]::SetEnvironmentVariable('Path', '{new_path}', 'User')"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            # 同時更新目前 session 的 PATH
            os.environ["PATH"] = f"{os.environ.get('PATH', '')};{bin_dir}"
            return True
        else:
            logger.error(f"Failed to set PATH: {result.stderr}")
            return False

    except Exception as e:
        logger.error(f"Failed to setup PATH on Windows: {e}")
        return False


def setup_path_unix() -> bool:
    """
    Linux/macOS: 將 uv tool bin 目錄加入 shell 設定檔

    Returns:
        bool: 是否成功
    """
    bin_dir = get_uv_tool_bin_dir()
    home = Path.home()

    # 決定要修改的 shell 設定檔
    shell = os.environ.get("SHELL", "/bin/bash")
    if "zsh" in shell:
        rc_file = home / ".zshrc"
    else:
        rc_file = home / ".bashrc"

    export_line = f'export PATH="$HOME/.local/bin:$PATH"'

    try:
        # 檢查是否已存在
        if rc_file.exists():
            content = rc_file.read_text()
            if ".local/bin" in content:
                return True

        # 附加到設定檔
        with open(rc_file, "a") as f:
            f.write(f"\n# Added by fwauto setup\n")
            f.write(f"{export_line}\n")

        # 更新目前 session 的 PATH
        os.environ["PATH"] = f"{bin_dir}:{os.environ.get('PATH', '')}"

        return True

    except Exception as e:
        logger.error(f"Failed to setup PATH on Unix: {e}")
        return False


def setup_path() -> bool:
    """
    自動設定 PATH 環境變數

    Returns:
        bool: 是否成功
    """
    system = platform.system().lower()

    if system == "windows":
        return setup_path_windows()
    else:
        return setup_path_unix()


def add_ai_engine_to_path() -> bool:
    """
    將 AI 引擎的安裝路徑加入 PATH

    Returns:
        bool: 是否成功
    """
    ai_exe = find_ai_engine_executable()
    if not ai_exe:
        return False

    ai_bin_dir = ai_exe.parent
    system = platform.system().lower()

    # 檢查是否已在 PATH
    current_path = os.environ.get("PATH", "")
    if str(ai_bin_dir) in current_path:
        return True

    try:
        if system == "windows":
            # Windows: 加入使用者 PATH
            result = subprocess.run(
                ["powershell", "-Command",
                 "[Environment]::GetEnvironmentVariable('Path', 'User')"],
                capture_output=True,
                text=True
            )
            current_user_path = result.stdout.strip() if result.returncode == 0 else ""

            if str(ai_bin_dir) not in current_user_path:
                new_path = f"{current_user_path};{ai_bin_dir}" if current_user_path else str(ai_bin_dir)
                subprocess.run(
                    ["powershell", "-Command",
                     f"[Environment]::SetEnvironmentVariable('Path', '{new_path}', 'User')"],
                    capture_output=True,
                    text=True
                )

            # 更新目前 session
            os.environ["PATH"] = f"{os.environ.get('PATH', '')};{ai_bin_dir}"

        else:
            # Linux/macOS: 加入 shell 設定檔
            home = Path.home()
            shell = os.environ.get("SHELL", "/bin/bash")
            rc_file = home / ".zshrc" if "zsh" in shell else home / ".bashrc"

            export_line = f'export PATH="{ai_bin_dir}:$PATH"'

            if rc_file.exists():
                content = rc_file.read_text()
                if str(ai_bin_dir) not in content:
                    with open(rc_file, "a") as f:
                        f.write(f"\n# FWAuto AI engine PATH (added by fwauto setup)\n")
                        f.write(f"{export_line}\n")

            # 更新目前 session
            os.environ["PATH"] = f"{ai_bin_dir}:{os.environ.get('PATH', '')}"

        return True

    except Exception as e:
        logger.error(f"Failed to add AI engine to PATH: {e}")
        return False


# Backward compatibility alias
add_claude_to_path = add_ai_engine_to_path


def run_full_setup(silent: bool = False) -> bool:
    """
    執行完整的 FWAuto 環境設定

    包含：
    1. 檢查 Git (Windows)
    2. 檢查並設定 fwauto PATH
    3. 安裝 AI 引擎
    4. 設定 AI 引擎 PATH

    Args:
        silent: 是否靜默執行

    Returns:
        bool: 是否全部成功
    """
    system = platform.system()
    is_windows = system.lower() == "windows"
    all_success = True
    need_restart = False

    if not silent:
        print()
        print("=" * 60)
        print("🚀 FWAuto 環境設定")
        print("=" * 60)
        print()
        print(f"   作業系統: {system}")
        print()

    # Step 0 (Windows only): 檢查 Git
    if is_windows:
        if not silent:
            print("[1/4] 檢查 Git...")

        if is_git_installed():
            if not silent:
                print("   ✅ Git 已安裝")
        else:
            if not silent:
                print("   ⚠️  找不到 Git")
                print()

            # 嘗試使用 winget 自動安裝
            if is_winget_available():
                if not silent:
                    print("   偵測到 winget，嘗試自動安裝 Git...")
                    print()

                if install_git_windows(silent=silent):
                    # 再次檢查 Git
                    if is_git_installed():
                        if not silent:
                            print("   ✅ Git 安裝成功並可用")
                        need_restart = True
                    else:
                        if not silent:
                            print("   ⚠️  Git 已安裝，但需要重新開啟終端機才能使用")
                        need_restart = True
                else:
                    # winget 安裝失敗，提示手動安裝
                    if not silent:
                        print("   ❌ 自動安裝 Git 失敗")
                        print()
                        print("   請手動下載安裝: https://git-scm.com/downloads/win")
                        print()
                        print("   安裝 Git 時請勾選:")
                        print("   ✅ Git Bash Here")
                        print("   ✅ Add Git to PATH")
                        print()
                        print("   安裝完成後請重新執行 fwauto setup")
                        print()
                    return False
            else:
                # winget 不可用，提示手動安裝
                if not silent:
                    print("   FWAuto AI 功能在 Windows 上需要 Git")
                    print()
                    print("   請下載安裝: https://git-scm.com/downloads/win")
                    print()
                    print("   安裝 Git 時請勾選:")
                    print("   ✅ Git Bash Here")
                    print("   ✅ Add Git to PATH")
                    print()
                    print("   安裝完成後請重新執行 fwauto setup")
                    print()
                return False

        step_offset = 1
        total_steps = 4
    else:
        step_offset = 0
        total_steps = 3

    # Step 1: 設定 fwauto PATH
    if not silent:
        print()
        print(f"[{1 + step_offset}/{total_steps}] 檢查 fwauto 環境變數...")

    bin_dir = get_uv_tool_bin_dir()

    if is_path_configured():
        if not silent:
            print(f"   ✅ PATH 已包含 {bin_dir}")
    else:
        if not silent:
            print(f"   正在設定 PATH: {bin_dir}")

        if setup_path():
            if not silent:
                print(f"   ✅ PATH 設定成功")
            need_restart = True
        else:
            if not silent:
                print(f"   ❌ PATH 設定失敗")
                print(f"   請手動將 {bin_dir} 加入 PATH")
            all_success = False

    # Step 2: 安裝 AI 引擎
    if not silent:
        print()
        print(f"[{2 + step_offset}/{total_steps}] 檢查 AI 引擎...")

    ai_exe = find_ai_engine_executable()

    if ai_exe:
        if not silent:
            print(f"   ✅ AI 引擎已安裝")
    else:
        if not silent:
            print("   正在安裝 AI 引擎（這可能需要幾分鐘）...")
            print()

        # 不使用 silent 模式，讓使用者看到安裝進度
        install_success = install_ai_engine(silent=False)

        # 重新檢查
        ai_exe = find_ai_engine_executable()

        if ai_exe:
            if not silent:
                print(f"   ✅ AI 引擎安裝成功")
        elif install_success:
            # 安裝指令成功但找不到執行檔，可能需要重開終端機
            if not silent:
                print("   ⚠️  安裝成功，但需要重新開啟終端機才能使用")
            need_restart = True
        else:
            # 安裝失敗
            if not silent:
                print("   ❌ AI 引擎安裝失敗")
                print()
                print("   可能的原因：")
                print("   - 網路連線問題")
                print("   - 防火牆阻擋")
                if is_windows:
                    print("   - Git 未正確安裝")
                print()
                print("   請檢查後重新執行 fwauto setup")
            all_success = False

    # Step 3: 設定 AI 引擎 PATH
    if not silent:
        print()
        print(f"[{3 + step_offset}/{total_steps}] 設定 AI 引擎環境變數...")

    if ai_exe:
        ai_bin_dir = ai_exe.parent
        current_path = os.environ.get("PATH", "")

        if str(ai_bin_dir) in current_path or shutil.which("claude"):
            if not silent:
                print(f"   ✅ AI 引擎 PATH 已設定")
        else:
            if add_ai_engine_to_path():
                if not silent:
                    print(f"   ✅ AI 引擎 PATH 設定成功")
                need_restart = True
            else:
                if not silent:
                    print(f"   ⚠️  無法自動設定 PATH")
                    print(f"   請手動將以下路徑加入 PATH: {ai_bin_dir}")
    else:
        if not silent:
            print("   ⏭️  跳過（AI 引擎尚未安裝）")

    # 完成
    if not silent:
        print()
        print("=" * 60)
        if all_success:
            print("✅ 設定完成！")
        else:
            print("⚠️  設定完成，但有部分項目需要手動處理")
        print("=" * 60)
        print()

        if need_restart:
            print("⚠️  請重新開啟終端機，讓環境變數生效！")
            print()

        print("然後執行以下指令確認安裝成功：")
        print("   fwauto --help")
        print()

    return all_success
