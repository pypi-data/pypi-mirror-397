#!/usr/bin/env python
"""程式碼格式化工具 - 執行 ruff format"""

import subprocess
import sys


def main():
    """執行 ruff 格式化"""
    print("🎨 Formatting code with Ruff...")
    print("=" * 60)

    result = subprocess.run(["ruff", "format", "."], capture_output=False)

    if result.returncode == 0:
        print("\n✅ Code formatted successfully!")
    else:
        print("\n❌ Formatting failed")

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
