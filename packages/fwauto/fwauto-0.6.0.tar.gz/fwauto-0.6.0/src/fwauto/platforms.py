"""Platform configuration for multi-platform firmware development."""

from typing import TypedDict


class PlatformConfig(TypedDict):
    """Configuration for a specific firmware development platform."""

    name: str  # 顯示名稱，例如 "STM32 + Keil"
    forbidden_dirs: list[str]  # 禁止修改的目錄
    allowed_dirs: list[str]  # 允許修改的目錄
    stop_conditions: list[str]  # AI 停止修復的條件描述


# 平台配置字典
PLATFORMS: dict[str, PlatformConfig] = {
    "stm32_keil": {
        "name": "STM32 + Keil",
        "forbidden_dirs": ["SYSTEM", "CORE", "HALLIB", "HARDWARE"],
        "allowed_dirs": ["USER"],
        "stop_conditions": [
            "錯誤來源於 SYSTEM/、CORE/、HALLIB/、HARDWARE/ 目錄",
            "缺少標頭檔案（如 *.h not found）",
            "需要下載或安裝任何依賴",
            "需要修改系統配置或編譯器設定",
            "涉及 HAL 庫、BSP 檔案或 SDK 檔案的問題",
        ],
    },
    "am62x": {
        "name": "TI AM62x",
        "forbidden_dirs": [],  # AM62x 通常沒有禁止修改的目錄限制
        "allowed_dirs": [],  # 允許所有目錄
        "stop_conditions": [
            "缺少標頭檔案（如 *.h not found）",
            "需要下載或安裝任何依賴",
            "需要修改系統配置或編譯器設定",
        ],
    },
    "raspberry-pi": {
        "name": "Raspberry Pi",
        "forbidden_dirs": [],
        "allowed_dirs": [],
        "stop_conditions": [
            "缺少標頭檔案（如 *.h not found）",
            "需要下載或安裝任何依賴",
            "需要修改系統配置或編譯器設定",
        ],
    },
    "risc-v": {
        "name": "RISC-V",
        "forbidden_dirs": [],
        "allowed_dirs": [],
        "stop_conditions": [
            "缺少標頭檔案（如 *.h not found）",
            "需要下載或安裝任何依賴",
            "需要修改系統配置或編譯器設定",
        ],
    },
    # 保留擴展空間（未來 MCU 平台）
    # "esp32_idf": {...},
    # "nordic_nrf": {...},
}


def get_platform_config(platform: str) -> PlatformConfig:
    """
    Get platform configuration by platform identifier.

    Args:
        platform: Platform identifier (e.g., 'stm32_keil')

    Returns:
        PlatformConfig dictionary

    Raises:
        ValueError: If platform is not supported
    """
    if platform not in PLATFORMS:
        raise ValueError(f"Unsupported platform: {platform}. Supported platforms: {', '.join(PLATFORMS.keys())}")
    return PLATFORMS[platform]


def list_platforms() -> list[str]:
    """List all supported platform identifiers."""
    return list(PLATFORMS.keys())
