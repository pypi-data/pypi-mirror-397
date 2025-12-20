"""User-level configuration management for FWAuto."""

import tomllib
from pathlib import Path
from typing import Any

import tomli_w


class UserConfig:
    """管理 ~/.fwauto/config.toml 的全域設定"""

    def __init__(self):
        self.config_path = Path.home() / ".fwauto" / "config.toml"
        self.data = self._load()

    def _load(self) -> dict[str, Any]:
        """載入 User Scope config，不存在則返回空 dict"""
        if not self.config_path.exists():
            return {}

        try:
            with open(self.config_path, "rb") as f:
                return tomllib.load(f)
        except Exception:
            # 如果載入失敗，返回空 dict
            return {}

    def get_sdk_config(self, sdk_type: str) -> dict[str, Any] | None:
        """取得特定 SDK 的設定"""
        return self.data.get("sdk", {}).get(sdk_type)

    def set_sdk_config(self, sdk_type: str, sdk_data: dict[str, Any]) -> None:
        """設定 SDK 資訊並儲存"""
        if "sdk" not in self.data:
            self.data["sdk"] = {}
        self.data["sdk"][sdk_type] = sdk_data
        self._save()

    def get_device_config(self, sdk_type: str) -> dict[str, Any] | None:
        """取得特定 SDK 的裝置設定"""
        return self.data.get("device", {}).get(sdk_type)

    def set_device_config(self, sdk_type: str, device_data: dict[str, Any]) -> None:
        """設定裝置資訊並儲存"""
        if "device" not in self.data:
            self.data["device"] = {}
        self.data["device"][sdk_type] = device_data
        self._save()

    def get_deployment_config(self, sdk_type: str) -> dict[str, Any] | None:
        """取得特定 SDK 的 deployment 設定"""
        return self.data.get("deployment", {}).get(sdk_type)

    def set_deployment_config(self, sdk_type: str, deployment_data: dict[str, Any]) -> None:
        """設定 deployment 資訊並儲存"""
        if "deployment" not in self.data:
            self.data["deployment"] = {}
        self.data["deployment"][sdk_type] = deployment_data
        self._save()

    def _save(self) -> None:
        """儲存至 ~/.fwauto/config.toml"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "wb") as f:
            tomli_w.dump(self.data, f)
