"""Template management for FWAuto SDK templates."""

import shutil
import tomllib
from pathlib import Path
from typing import Any


class TemplateManager:
    """管理 SDK templates 的選擇、複製與 metadata 讀取"""

    def __init__(self):
        # 內建 templates 路徑
        import fwauto

        package_dir = Path(fwauto.__file__).parent
        self.builtin_templates_dir = package_dir / "templates"

        # User templates 路徑 (可選)
        self.user_templates_dir = Path.home() / ".fwauto" / "templates"

    def list_available_templates(self) -> list[dict[str, Any]]:
        """列出所有可用的 templates (內建 + 使用者自訂)"""
        templates = []

        # 掃描內建 templates
        if self.builtin_templates_dir.exists():
            for sdk_dir in self.builtin_templates_dir.iterdir():
                if sdk_dir.is_dir() and (sdk_dir / "metadata.toml").exists():
                    metadata = self._load_metadata(sdk_dir)
                    # 使用 metadata 中的 sdk.id 作為 sdk_type
                    sdk_id = metadata.get("sdk", {}).get("id", sdk_dir.name.replace("sdk_", ""))
                    templates.append(
                        {
                            "sdk_type": sdk_id,
                            "path": sdk_dir,
                            "metadata": metadata,
                            "source": "builtin",
                        }
                    )

        # 掃描使用者自訂 templates
        if self.user_templates_dir.exists():
            for sdk_dir in self.user_templates_dir.iterdir():
                if sdk_dir.is_dir() and (sdk_dir / "metadata.toml").exists():
                    metadata = self._load_metadata(sdk_dir)
                    # 使用 metadata 中的 sdk.id 作為 sdk_type
                    sdk_id = metadata.get("sdk", {}).get("id", sdk_dir.name.replace("sdk_", ""))
                    templates.append(
                        {
                            "sdk_type": sdk_id,
                            "path": sdk_dir,
                            "metadata": metadata,
                            "source": "user",
                        }
                    )

        return templates

    def get_template(self, sdk_type: str) -> Path | None:
        """根據 SDK type 取得 template 路徑"""
        templates = self.list_available_templates()
        for template in templates:
            if template["sdk_type"] == sdk_type:
                return template["path"]
        return None

    def copy_template_to_project(self, sdk_type: str, project_root: Path, overwrite: bool = False) -> bool:
        """複製 template 至專案的 .fwauto/ 目錄"""
        template_dir = self.get_template(sdk_type)
        if not template_dir:
            return False

        target_dir = project_root / ".fwauto"
        target_dir.mkdir(parents=True, exist_ok=True)

        # 複製 build/ 和 deploy/ 目錄
        for subdir in ["build", "deploy"]:
            src = template_dir / subdir
            dst = target_dir / subdir

            # 檢查來源目錄是否存在且不是空的
            if not src.exists():
                continue

            # 檢查來源目錄是否有檔案
            if not any(src.iterdir()):
                # 空目錄，只建立目標目錄
                dst.mkdir(exist_ok=True)
                continue

            if dst.exists() and not overwrite:
                print(f"⚠️  {dst} 已存在，使用 --overwrite 覆寫")
                continue

            if dst.exists():
                shutil.rmtree(dst)

            shutil.copytree(src, dst)
            print(f"✓ 已複製 {subdir}/ templates")

        return True

    def _load_metadata(self, template_dir: Path) -> dict[str, Any]:
        """載入 template 的 metadata.toml"""
        metadata_path = template_dir / "metadata.toml"
        with open(metadata_path, "rb") as f:
            return tomllib.load(f)
