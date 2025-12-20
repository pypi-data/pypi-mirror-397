"""Configuration management for FWAuto."""

import platform
import sys
import tomllib
from pathlib import Path
from typing import Any

import tomli_w

from .scenario import Scenario, ScenarioManager
from .user_config import UserConfig


def detect_platform() -> str:
    """Detect the current platform."""
    system = platform.system().lower()

    # Check for WSL (Windows Subsystem for Linux)
    if system == "linux" and "microsoft" in platform.release().lower():
        # WSL is treated as Linux for our purposes
        return "linux"

    return system


def print_config_info():
    """Print current configuration information for debugging."""
    platform_info = detect_platform()

    print("🔧 FWAuto Configuration:")
    print(f"  Platform: {platform_info}")
    print(f"  Python: {sys.version}")
    print(f"  OS Info: {platform.platform()}")


class ConfigError(Exception):
    """Configuration related errors."""

    pass


class ProjectConfig:
    """Project configuration from .fwauto/config.toml."""

    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.user_config = UserConfig()
        self.data = self._load()
        self._validate()

    def _load(self) -> dict[str, Any]:
        """Load TOML configuration."""
        try:
            with open(self.config_path, "rb") as f:
                return tomllib.load(f)
        except FileNotFoundError:
            raise ConfigError(f"Config file not found: {self.config_path}")
        except Exception as e:
            raise ConfigError(f"Failed to load config: {e}")

    def _validate(self) -> None:
        """Validate configuration schema."""
        # Config 所有欄位都是可選的，使用預設值
        pass

    @property
    def build_makefile(self) -> str:
        """Build Makefile 路徑，預設為 .fwauto/build/Makefile"""
        return self.data.get("build", {}).get("makefile", ".fwauto/build/Makefile")

    @property
    def build_target(self) -> str:
        """Build target 名稱，預設為 build"""
        return self.data.get("build", {}).get("target", "build")

    @property
    def sdk_type(self) -> str | None:
        """SDK type (e.g., stm32f4, am62x)"""
        return self.data.get("sdk", {}).get("type")

    @property
    def sdk_path(self) -> str | None:
        """SDK 路徑優先從 Project Config 讀取，否則從 User Config 繼承"""
        sdk_type = self.sdk_type
        if not sdk_type:
            return None

        # 1. 優先使用 Project Scope (罕見，用於特殊情況)
        project_sdk_path = self.data.get("sdk", {}).get("path")
        if project_sdk_path:
            return project_sdk_path

        # 2. 從 User Scope 繼承
        user_sdk = self.user_config.get_sdk_config(sdk_type)
        return user_sdk.get("path") if user_sdk else None

    @property
    def device_family(self) -> str:
        """取得裝置系列 (e.g., stm32f4)"""
        return self.data.get("device", {}).get("family", "")

    @property
    def device_model(self) -> str:
        """取得裝置型號 (e.g., STM32F407VGT6)"""
        return self.data.get("device", {}).get("model", "")

    @property
    def deployment_config(self) -> dict[str, Any]:
        """
        Deployment 配置：User Config 為基礎，Project Config 覆蓋特定欄位

        Returns:
            包含 board_ip, board_user, deploy_path, ssh_options 的字典
            若無配置則返回空字典
        """
        sdk_type = self.sdk_type
        if not sdk_type:
            return {}

        # 1. 從 User Scope 載入基礎配置
        user_deployment = self.user_config.get_deployment_config(sdk_type) or {}

        # 2. Project Scope 覆蓋特定欄位（合併，而非完全取代）
        project_deployment = self.data.get("deployment", {}).get(sdk_type, {})

        # 合併：User config 為底，Project config 覆蓋
        merged = {**user_deployment, **project_deployment}
        return merged

    @property
    def board_ip(self) -> str:
        """開發板 IP 地址"""
        ip = self.deployment_config.get("board_ip")
        if not ip:
            raise ConfigError(
                f"board_ip not configured for SDK type '{self.sdk_type}'.\n"
                f"\n"
                f"Please configure in one of:\n"
                f"  1. Project config: {self.config_path}\n"
                f"     [deployment.{self.sdk_type}]\n"
                f"     board_ip = \"192.168.x.x\"\n"
                f"\n"
                f"  2. User config: ~/.fwauto/config.toml\n"
                f"     [deployment.{self.sdk_type}]\n"
                f"     board_ip = \"192.168.x.x\"\n"
            )
        return ip

    @property
    def board_user(self) -> str:
        """SSH 登入使用者"""
        return self.deployment_config.get("board_user", "root")

    @property
    def deploy_path(self) -> str:
        """遠端部署目錄"""
        return self.deployment_config.get("deploy_path", "/home/root")

    @property
    def ssh_options(self) -> str:
        """SSH 選項"""
        default_opts = "-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5"
        return self.deployment_config.get("ssh_options", default_opts)

    @property
    def remote_log_enabled(self) -> bool:
        """是否啟用遠端日誌檔案"""
        return self.deployment_config.get("remote_log_enabled", True)

    @property
    def remote_log_pattern(self) -> str:
        """遠端日誌檔案命名模板 (Jinja2 格式)"""
        default_pattern = "{{ deploy_path }}/{{ app_name }}_{{ date }}.log"
        return self.deployment_config.get("remote_log_pattern", default_pattern)

    @property
    def last_log_file_path(self) -> str | None:
        """上次 flash 產生的日誌路徑（程式自動寫入）"""
        return self.deployment_config.get("last_log_file_path")

    def update_last_log_path(self, log_path: str) -> None:
        """
        更新 last_log_file_path 到 config.toml

        Args:
            log_path: 遠端日誌路徑（例如 root@192.168.50.170:/home/root/uart.log）
        """
        from .logging_config import get_logger

        logger = get_logger(__name__)

        # 讀取現有 config
        if self.config_path.exists():
            with open(self.config_path, "rb") as f:
                config_data = tomllib.load(f)
        else:
            config_data = {}

        # 確保結構存在
        sdk_type = self.sdk_type
        if sdk_type:
            if "deployment" not in config_data:
                config_data["deployment"] = {}
            if sdk_type not in config_data["deployment"]:
                config_data["deployment"][sdk_type] = {}

            # 更新路徑
            config_data["deployment"][sdk_type]["last_log_file_path"] = log_path

        # 寫回檔案
        with open(self.config_path, "wb") as f:
            tomli_w.dump(config_data, f)

        logger.debug(f"💾 Updated last_log_file_path in config: {log_path}")

    def get_scenarios(self) -> list[Scenario]:
        """
        載入 Project Config 中的所有 scenarios.

        Returns:
            List of Scenario objects from config
        """
        scenarios_data = self.data.get("scenarios", [])
        return [Scenario.from_dict(s) for s in scenarios_data]

    def get_scenario_manager(self) -> ScenarioManager:
        """
        建立 ScenarioManager.

        Returns:
            ScenarioManager instance with project scenarios
        """
        project_scenarios = self.get_scenarios()
        return ScenarioManager(project_scenarios)


def find_project_root(start_path: Path | None = None) -> Path | None:
    """
    向上搜尋 .fwauto/ 目錄,找到專案根目錄.

    Args:
        start_path: 搜尋起點,預設為當前目錄

    Returns:
        專案根目錄 Path,若未找到則返回 None
    """
    if start_path is None:
        start_path = Path.cwd()

    current = start_path.resolve()

    # 向上搜尋,最多到根目錄
    while True:
        fwauto_dir = current / ".fwauto"
        if fwauto_dir.is_dir():
            return current

        # 到達根目錄
        if current.parent == current:
            return None

        current = current.parent


def load_project_config(project_root: Path) -> ProjectConfig:
    """Load project configuration."""
    config_path = project_root / ".fwauto" / "config.toml"
    return ProjectConfig(config_path)


def create_default_config(project_root: Path) -> None:
    """Create default .fwauto/config.toml.

    空白配置，所有設定使用預設值。
    build 和 flash 路徑由 ProjectConfig 屬性提供。
    """
    config_dir = project_root / ".fwauto"
    config_dir.mkdir(exist_ok=True)

    # 空白配置 - 所有設定使用預設值
    config_data = {}

    config_path = config_dir / "config.toml"
    with open(config_path, "wb") as f:
        tomli_w.dump(config_data, f)


if __name__ == "__main__":
    """Test configuration detection."""
    print_config_info()
