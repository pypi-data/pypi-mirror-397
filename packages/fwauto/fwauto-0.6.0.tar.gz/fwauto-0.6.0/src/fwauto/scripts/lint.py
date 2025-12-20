#!/usr/bin/env python
"""程式碼檢查與自動修復工具"""

import subprocess
import sys


def main():
    """執行 ruff 檢查並自動修復"""
    print("🔧 Running Ruff with auto-fix...")
    print("=" * 60)

    # 執行檢查並自動修復
    result = subprocess.run(["ruff", "check", ".", "--fix"], capture_output=False)

    if result.returncode == 0:
        print("\n✅ All checks passed (or fixed)!")
    else:
        print("\n⚠️ Some issues remain that need manual fixing")
        print("💡 Run 'uv run check' to see detailed diagnostics")

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
