#!/usr/bin/env python
"""診斷檢查工具 - 執行 ruff 和 pyright 檢查"""

import subprocess
import sys


def run_command(cmd: list[str], description: str) -> int:
    """執行命令並回傳 return code"""
    print(f"\n{description}")
    print(f"{'=' * 60}")
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode


def run_ruff_check() -> int:
    """執行 ruff 語法檢查"""
    print("\n🔍 Running Ruff Linting Check...")
    print("-" * 60)

    # 執行檢查並顯示統計
    result = subprocess.run(["ruff", "check", ".", "--statistics"], capture_output=False)

    if result.returncode != 0:
        print("\n💡 Tip: Run 'uv run ruff check . --fix' to auto-fix issues")
        print("         Run 'uv run ruff check . --diff' to see suggested fixes")

    return result.returncode


def run_ruff_format_check() -> int:
    """檢查程式碼格式"""
    print("\n📐 Running Ruff Format Check...")
    print("-" * 60)

    result = subprocess.run(["ruff", "format", ".", "--check", "--diff"], capture_output=False)

    if result.returncode != 0:
        print("\n💡 Tip: Run 'uv run ruff format .' to auto-format code")

    return result.returncode


def run_pyright() -> int:
    """執行 pyright 類型檢查"""
    print("\n📊 Running Pyright Type Check...")
    print("-" * 60)

    result = subprocess.run(["pyright", "."], capture_output=False)

    return result.returncode


def main():
    """執行所有診斷檢查"""
    print("=" * 60)
    print("🚀 FWAuto Code Quality Check")
    print("=" * 60)

    # 收集所有檢查結果
    errors = []

    # Ruff linting
    if run_ruff_check() != 0:
        errors.append("Ruff linting")

    # Ruff formatting
    if run_ruff_format_check() != 0:
        errors.append("Ruff formatting")

    # Pyright type checking
    if run_pyright() != 0:
        errors.append("Pyright type checking")

    # 總結報告
    print("\n" + "=" * 60)
    if not errors:
        print("✅ All checks passed! Your code is clean! 🎉")
        return 0
    else:
        print(f"❌ Failed checks: {', '.join(errors)}")
        print("\n📝 Quick fixes:")
        print("  • Auto-fix linting: uv run ruff check . --fix")
        print("  • Auto-format code: uv run ruff format .")
        print("  • Show all issues:  uv run check")
        return 1


if __name__ == "__main__":
    sys.exit(main())
