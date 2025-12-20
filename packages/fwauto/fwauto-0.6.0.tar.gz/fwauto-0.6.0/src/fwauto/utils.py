"""Utility functions for FWAuto."""

# Python 3.11+ has tomllib built-in, earlier versions need tomli
import os
import subprocess
import tomllib
from pathlib import Path
from typing import Any


def load_toml(file_path: str | Path) -> dict[str, Any]:
    """
    Load and parse a TOML file.

    Args:
        file_path: Path to the TOML file

    Returns:
        Parsed TOML data as dictionary

    Raises:
        FileNotFoundError: If the TOML file does not exist
        tomllib.TOMLDecodeError: If the TOML file is malformed
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"TOML file not found: {file_path}")

    with open(path, "rb") as f:
        return tomllib.load(f)


def check_fwauto_config_exists(project_root: str | Path) -> bool:
    """
    Check if .fwauto/config.toml exists in the project root.

    This is used to determine whether to use Makefile-based build/flash
    or fallback to STM32-specific legacy implementation.

    Args:
        project_root: Path to the project root directory

    Returns:
        True if .fwauto/config.toml exists, False otherwise
    """
    config_path = Path(project_root) / ".fwauto" / "config.toml"
    return config_path.exists()


def get_fwauto_dir(project_root: str | Path) -> Path:
    """
    Get the .fwauto directory path for a project.

    Args:
        project_root: Path to the project root directory

    Returns:
        Path to the .fwauto directory
    """
    return Path(project_root) / ".fwauto"


def ensure_fwauto_dir(project_root: str | Path) -> Path:
    """
    Ensure the .fwauto directory exists, create if not.

    Args:
        project_root: Path to the project root directory

    Returns:
        Path to the .fwauto directory
    """
    fwauto_dir = get_fwauto_dir(project_root)
    fwauto_dir.mkdir(parents=True, exist_ok=True)
    return fwauto_dir


def execute_make_command(
    makefile_path: Path,
    target: str,
    project_root: Path,
    timeout: int = 60,
    env_vars: dict[str, str] | None = None,
) -> tuple[int, str]:
    """
    Execute make command with real-time output and cross-platform compatibility.

    Args:
        makefile_path: Path to Makefile
        target: Make target to execute (e.g., "build", "flash")
        project_root: Project root directory
        timeout: Command timeout in seconds (default: 60)
        env_vars: Additional environment variables to pass to the process

    Returns:
        Tuple of (returncode, full_output)

    Raises:
        subprocess.TimeoutExpired: If command exceeds timeout
    """
    from .logging_config import get_logger

    makefile_dir = makefile_path.parent
    cmd = ["make", target, f"PROJECT_ROOT={project_root}"]

    logger = get_logger(__name__)
    logger.info(f"Executing: {' '.join(cmd)} in {makefile_dir}")

    # 準備環境變數
    env = os.environ.copy()
    if env_vars:
        env.update(env_vars)
        logger.info(f"Additional env vars: {list(env_vars.keys())}")

    # 準備 Popen 參數
    popen_kwargs = {
        "stdout": subprocess.PIPE,
        "stderr": subprocess.STDOUT,  # 合併 stderr 到 stdout
        "text": True,
        "encoding": "utf-8",
        "errors": "replace",
        "cwd": str(makefile_dir),
        "bufsize": 1,  # Line buffered
        "env": env,  # 新增環境變數
    }

    # Windows 平台：不使用特殊 creationflags（經測試，問題在 Makefile 的 -j0 參數）
    # 現在 Makefile 已修正，可以正常捕獲輸出

    # 執行命令
    process = subprocess.Popen(cmd, **popen_kwargs)

    # 使用 communicate 配合 timeout（一次性獲取所有輸出）
    print("")  # 空行分隔
    try:
        stdout_data, _ = process.communicate(timeout=timeout)
        output_lines = stdout_data.splitlines(keepends=True) if stdout_data else []

        # 輸出到 console
        for line in output_lines:
            print(line, end="", flush=True)
    except subprocess.TimeoutExpired:
        process.kill()
        stdout_data, _ = process.communicate()  # 收集已有的輸出
        output_lines = stdout_data.splitlines(keepends=True) if stdout_data else []
        raise subprocess.TimeoutExpired(cmd=cmd, timeout=timeout, output="".join(output_lines))
    except Exception as e:
        process.kill()
        process.communicate()  # 清理
        raise RuntimeError(f"Error executing command: {e}") from e
    finally:
        print("")  # 空行分隔

    # 組合完整輸出
    full_output = f"Command: {' '.join(cmd)}\n"
    full_output += f"Working directory: {makefile_dir}\n"
    full_output += f"Exit code: {process.returncode}\n"
    full_output += "=" * 60 + "\n\n"
    full_output += "".join(output_lines)

    # Log the full output to file
    logger.info(f"Make output:\n{full_output}")

    return process.returncode, full_output
