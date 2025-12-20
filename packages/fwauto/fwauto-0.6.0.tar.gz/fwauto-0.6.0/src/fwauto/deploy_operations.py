"""
Deploy operations module - Platform-agnostic deployment orchestration.

This module implements the platform abstraction pattern for firmware deployment:
- Supports multiple deploy types: Network Deployment (SSH) and Direct Flashing (JTAG/USB)
- Routes to platform-specific deploy scripts based on SDK type
- Platform-independent orchestration layer (no direct tool execution)

Supported platforms:
- Network Deployment: AM62X, Raspberry Pi, RISC-V SBC (via SSH/SCP)
- Direct Flashing: STM32, ESP32, nRF52 (future, via JTAG/USB) - not yet implemented

Architecture:
1. deploy_firmware() - Routes based on SDK type
2. _deploy_network() - SSH-based deployment with connectivity check
3. _deploy_direct_flashing() - JTAG/USB deployment (placeholder)
4. Platform-specific deploy.py - Actual deployment execution

Design principles:
- Platform-independent (no direct SSH/SCP/ST-LINK execution in Python)
- Tool-agnostic (doesn't know about SSH, ST-LINK, esptool, etc.)
- Easy to extend (add new platform = add new deploy.py template)
"""

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from .logging_config import get_logger

if TYPE_CHECKING:
    from .config import ProjectConfig

logger = get_logger(__name__)


# ============================================
# Deploy Type Mapping
# ============================================

SDK_DEPLOY_TYPE_MAP = {
    # Network Deployment (SSH-based, Linux SBC)
    "am62x": "network",
    "raspberry-pi": "network",
    "risc-v": "network",
    # Direct Flashing (MCU-based)
    "stm32": "direct_flashing",
    "esp32": "direct_flashing",
    "nrf52": "direct_flashing",
}


def _get_deploy_type(sdk_type: str | None) -> str:
    """
    Get deploy type from SDK type.

    Args:
        sdk_type: SDK type from ProjectConfig (e.g., "am62x", "stm32")

    Returns:
        Deploy type: "network" or "direct_flashing"

    Raises:
        ValueError: If sdk_type is None or unknown
    """
    if sdk_type is None:
        raise ValueError("sdk_type not set in config.toml")

    deploy_type = SDK_DEPLOY_TYPE_MAP.get(sdk_type)
    if deploy_type is None:
        raise ValueError(f"Unknown SDK type: {sdk_type}")

    return deploy_type


# ============================================
# Data Classes
# ============================================


@dataclass
class NetworkDeployConfig:
    """Configuration for SSH-based network deployment (AM62X, Raspberry Pi, RISC-V)."""

    board_ip: str
    board_user: str = "root"
    deploy_path: str = "/home/root"
    ssh_options: str = "-o StrictHostKeyChecking=no -o BatchMode=yes"
    binary_args: str = ""
    execution_mode: Literal["foreground", "background"] = "foreground"
    remote_log_enabled: bool = False
    remote_log_path: str = "/dev/null"


@dataclass
class DeployResult:
    """Result of deploy operation."""

    success: bool
    message: str
    binary_name: str = ""
    pid: int | None = None


# ============================================
# Binary Discovery
# ============================================


def find_binary(build_dir: Path) -> Path:
    """
    Find the first executable binary in build directory.

    Args:
        build_dir: Path to build directory

    Returns:
        Path to the binary file

    Raises:
        FileNotFoundError: If no executable binary found
    """
    if not build_dir.exists():
        raise FileNotFoundError(f"Build directory does not exist: {build_dir}")

    # Find executable files in build directory
    for file in build_dir.iterdir():
        if file.is_file() and _is_executable(file):
            logger.info(f"Found binary: {file.name}")
            return file

    raise FileNotFoundError(f"No executable binary found in {build_dir}")


def _is_executable(file: Path) -> bool:
    """Check if file is executable (cross-platform)."""
    import os
    import stat

    try:
        # On Unix, check execute permission
        return bool(file.stat().st_mode & stat.S_IXUSR)
    except Exception:
        # On Windows, assume files without extension or with common executable extensions are executable
        return file.suffix in ["", ".exe", ".out", ".elf"] or os.access(file, os.X_OK)


# ============================================
# Output Parsing Helpers
# ============================================


def _extract_binary_name_from_output(stderr: str) -> str:
    """
    Extract binary name from deploy.py stderr output.

    Args:
        stderr: stderr output from deploy.py

    Returns:
        Binary name if found, empty string otherwise
    """
    import re

    # deploy.py outputs: "ℹ️  Found binary: <name>"
    match = re.search(r"Found binary:\s+(\S+)", stderr)
    if match:
        return match.group(1)

    return ""


def _extract_pid_from_output(stderr: str) -> int | None:
    """Extract PID from SSH stderr output."""
    import re

    match = re.search(r"PID (\d+)", stderr)
    return int(match.group(1)) if match else None


def _extract_log_path_from_output(stderr: str) -> str:
    """
    Extract output log path from deploy.py stderr output.

    Args:
        stderr: stderr output from deploy.py

    Returns:
        Log path if found, empty string otherwise
    """
    import re

    # deploy.py outputs: "OUTPUT_LOG:/tmp/fwauto_led_2025-11-26.log"
    match = re.search(r"OUTPUT_LOG:(\S+)", stderr)
    return match.group(1) if match else ""


def _extract_deploy_error(stderr: str) -> str:
    """
    Extract meaningful error message from deploy script stderr.

    Filters out SSH warnings and extracts the actual error cause.
    Handles common errors like "Text file busy", "Permission denied", etc.

    Args:
        stderr: stderr output from deploy script

    Returns:
        Meaningful error message, or empty string if none found
    """
    if not stderr:
        return ""

    # Known error patterns to look for (in priority order)
    error_patterns = [
        "Text file busy",
        "Permission denied",
        "No such file or directory",
        "Connection refused",
        "Connection timed out",
        "Host is down",
        "Network is unreachable",
    ]

    # First, check for known error patterns
    stderr_lower = stderr.lower()
    for pattern in error_patterns:
        if pattern.lower() in stderr_lower:
            # Find the line containing this error
            for line in stderr.split("\n"):
                if pattern.lower() in line.lower():
                    # Clean up the line (remove scp: prefix, etc.)
                    clean_line = line.strip()
                    if clean_line.startswith("scp:"):
                        clean_line = clean_line[4:].strip()
                    return clean_line

    # Look for "❌ Execution failed:" pattern and extract full multi-line message
    if "❌ Execution failed:" in stderr:
        # Find the start of the error message
        start_idx = stderr.find("❌ Execution failed:")
        # Extract everything after "❌ Execution failed:" until next section or end
        error_section = stderr[start_idx:]
        # Find where the error message ends (at next ❌ or ============ or end)
        end_markers = ["\n❌", "\n===", "\n\n\n"]
        end_idx = len(error_section)
        for marker in end_markers:
            pos = error_section.find(marker, 1)  # Skip first char
            if pos != -1 and pos < end_idx:
                end_idx = pos
        return error_section[:end_idx].strip()

    # Fallback: find lines with error indicators (skip SSH warnings)
    for line in stderr.split("\n"):
        line = line.strip()
        # Skip empty lines and SSH warnings
        if not line or line.startswith("Warning:"):
            continue
        # Look for error indicators
        if any(indicator in line for indicator in ["❌", "ERROR", "failed", "Failed"]):
            return line

    # Last resort: return first non-warning line
    for line in stderr.split("\n"):
        line = line.strip()
        if line and not line.startswith("Warning:"):
            return line

    return ""


def _fetch_remote_output(
    board_ip: str,
    board_user: str,
    ssh_options: str,
    remote_log_path: str,
    max_lines: int = 20,
) -> str:
    """
    Fetch program output from remote log file via SSH.

    Args:
        board_ip: Board IP address
        board_user: SSH username
        ssh_options: SSH options string
        remote_log_path: Path to remote log file
        max_lines: Maximum lines to fetch (0 = all, N = first N lines)

    Returns:
        Program output string, or empty string if fetch fails
    """
    ssh_opts = ssh_options.split()

    # 構建讀取命令
    if max_lines > 0:
        read_cmd = f"head -n {max_lines} '{remote_log_path}' 2>/dev/null || echo ''"
    else:
        read_cmd = f"cat '{remote_log_path}' 2>/dev/null || echo ''"

    ssh_cmd = ["ssh"] + ssh_opts + [f"{board_user}@{board_ip}", read_cmd]

    try:
        result = subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True,
            timeout=10,
        )

        return result.stdout.strip() if result.returncode == 0 else ""
    except subprocess.TimeoutExpired:
        logger.debug(f"Timeout fetching remote output from {remote_log_path}")
        return ""
    except Exception as e:
        logger.debug(f"Failed to fetch remote output: {e}")
        return ""


# ============================================
# High-Level Deploy Operation
# ============================================


def deploy_firmware(build_dir: Path, config: "ProjectConfig", binary_args: str = "") -> DeployResult:
    """
    Deploy firmware by routing to appropriate deploy method based on SDK type.

    This function follows the platform abstraction pattern:
    - Determines deploy type from SDK type (network vs direct_flashing)
    - Routes to appropriate platform-specific deploy function
    - Platform-specific logic is delegated to deploy scripts

    Args:
        build_dir: Path to build directory containing the binary
        config: Project configuration (contains sdk_type and deployment settings)
        binary_args: Arguments to pass to the binary (optional)

    Returns:
        DeployResult indicating success/failure

    Raises:
        ValueError: If sdk_type is unknown or not set
    """
    # Log to file
    logger.info("=" * 60)
    logger.info("FWAuto Deploy: Platform-Agnostic Deployment")
    logger.info("=" * 60)

    # Determine deploy type from SDK type
    deploy_type = _get_deploy_type(config.sdk_type)
    logger.info(f"📦 SDK Type: {config.sdk_type}")
    logger.info(f"🚀 Deploy Type: {deploy_type}")
    logger.info("")

    # Route to appropriate deploy method
    if deploy_type == "network":
        return _deploy_network(build_dir, config, binary_args)
    elif deploy_type == "direct_flashing":
        return _deploy_direct_flashing(build_dir, config, binary_args)
    else:
        # Should never reach here due to _get_deploy_type validation
        raise ValueError(f"Unknown deploy type: {deploy_type}")


# ============================================
# Platform-Specific Deploy Methods
# ============================================


def _check_ssh_connection(
    board_ip: str, board_user: str, ssh_options: str, port: int = 22, timeout: int = 5
) -> None:
    """
    Check SSH connection including authentication.

    This performs a two-step check:
    1. TCP port check - verify SSH port is reachable
    2. SSH authentication check - verify credentials are valid

    Args:
        board_ip: Board IP address
        board_user: SSH username
        ssh_options: SSH options string
        port: SSH port (default: 22)
        timeout: Connection timeout in seconds (default: 5)

    Raises:
        ConnectionError: If SSH connection fails (port or auth)
    """
    import socket

    logger.debug(f"🔍 Checking SSH connection to {board_user}@{board_ip}:{port}")

    # Step 1: TCP port check
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((board_ip, port))
        sock.close()

        if result != 0:
            raise ConnectionError(
                _format_ssh_error(board_ip, board_user, "Port not reachable")
            )
        logger.debug(f"✅ SSH port {port} is reachable")
    except TimeoutError:
        raise ConnectionError(
            _format_ssh_error(board_ip, board_user, "Connection timeout")
        )
    except ConnectionError:
        raise
    except Exception as e:
        raise ConnectionError(
            _format_ssh_error(board_ip, board_user, str(e))
        )

    # Step 2: SSH authentication check
    logger.debug(f"🔍 Checking SSH authentication for {board_user}@{board_ip}")

    ssh_opts = ssh_options.split()
    ssh_cmd = ["ssh"] + ssh_opts + ["-o", "BatchMode=yes", f"{board_user}@{board_ip}", "exit"]

    try:
        result = subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        if result.returncode != 0:
            raise ConnectionError(
                _format_ssh_error(board_ip, board_user, "Authentication failed")
            )
        logger.debug("✅ SSH authentication successful")
    except subprocess.TimeoutExpired:
        raise ConnectionError(
            _format_ssh_error(board_ip, board_user, "Authentication timeout")
        )
    except ConnectionError:
        raise
    except Exception as e:
        raise ConnectionError(
            _format_ssh_error(board_ip, board_user, str(e))
        )


def _format_ssh_error(board_ip: str, board_user: str, reason: str) -> str:
    """Format unified SSH error message."""
    return (
        f"Cannot connect to {board_user}@{board_ip} ({reason})\n"
        f"\n"
        f"Please check:\n"
        f"  - Board is powered on and connected to network\n"
        f"  - SSH credentials are correct\n"
        f"\n"
        f"Config location: ~/.fwauto/config.toml\n"
        f"Test manually: ssh {board_user}@{board_ip}"
    )


def _kill_remote_process(
    binary_name: str,
    board_ip: str,
    board_user: str,
    ssh_options: str,
) -> None:
    """
    Kill remote process before deployment to avoid 'Text file busy' error.

    This function attempts to kill any running instance of the binary on the
    remote board before SCP deployment. If the process doesn't exist, the
    command silently succeeds.

    Args:
        binary_name: Name of the binary to kill (exact match)
        board_ip: Board IP address
        board_user: SSH username
        ssh_options: SSH options string
    """
    ssh_opts = ssh_options.split()

    # Use pkill -x for exact name match (safer than pattern match)
    # 2>/dev/null || true ensures command succeeds even if process doesn't exist
    kill_cmd = f"pkill -9 -x '{binary_name}' 2>/dev/null || true"

    ssh_cmd = ["ssh"] + ssh_opts + [f"{board_user}@{board_ip}", kill_cmd]

    logger.debug(f"🔪 Killing remote process: {binary_name}")

    try:
        subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True,
            timeout=10,
        )
        # Don't check return code - pkill returns non-zero if no process found
        logger.debug("✅ Kill command executed (process may or may not have existed)")
    except subprocess.TimeoutExpired:
        logger.debug("⚠️ Kill command timeout (continuing anyway)")
    except Exception as e:
        logger.debug(f"⚠️ Kill command failed: {e} (continuing anyway)")


def _deploy_network(build_dir: Path, config: "ProjectConfig", binary_args: str) -> DeployResult:
    """
    Deploy to Linux-based platforms via SSH/SCP (AM62X, Raspberry Pi, RISC-V).

    Process:
    1. Build NetworkDeployConfig from ProjectConfig
    2. Locate deploy.py script
    3. Build command with SSH-specific parameters
    4. Execute deploy.py via subprocess
    5. Parse result and return DeployResult

    Args:
        build_dir: Path to build directory
        config: Project configuration
        binary_args: Arguments to pass to the binary

    Returns:
        DeployResult indicating success/failure
    """
    # Console output
    print("📡 Network Deployment (SSH-based)")

    # Log to file
    logger.info("📡 Network Deployment (SSH-based)")

    # Read remote_log_path from config temporary attribute (set by deploy_node if enabled)
    remote_log_path = getattr(config, "_tmp_remote_log_path", "/dev/null")

    # Build NetworkDeployConfig from ProjectConfig
    deploy_config = NetworkDeployConfig(
        board_ip=config.board_ip,
        board_user=config.board_user,
        deploy_path=config.deploy_path,
        ssh_options=config.ssh_options,
        binary_args=binary_args,
        execution_mode="background",  # Default to background
        remote_log_enabled=config.remote_log_enabled,
        remote_log_path=remote_log_path,  # Use value from deploy_node
    )

    # Check SSH connection before deploying
    try:
        _check_ssh_connection(
            deploy_config.board_ip,
            deploy_config.board_user,
            deploy_config.ssh_options,
        )
    except ConnectionError as e:
        error_msg = str(e)
        # Console output
        print(f"❌ SSH connection failed: {error_msg}")
        # Log to file
        logger.error(f"❌ {error_msg}")
        return DeployResult(success=False, message=error_msg)

    # Find binary and kill any running instance before SCP
    # This prevents "Text file busy" error when overwriting running binary
    try:
        binary_path = find_binary(build_dir)
        binary_name = binary_path.name
        _kill_remote_process(
            binary_name,
            deploy_config.board_ip,
            deploy_config.board_user,
            deploy_config.ssh_options,
        )
    except FileNotFoundError as e:
        error_msg = str(e)
        print(f"❌ {error_msg}")
        logger.error(f"❌ {error_msg}")
        return DeployResult(success=False, message=error_msg)

    # Locate deploy.py script
    deploy_script = build_dir.parent / ".fwauto" / "deploy" / "deploy.py"

    if not deploy_script.exists():
        error_msg = f"Deploy script not found: {deploy_script}"
        # Console output
        print(f"❌ {error_msg}")
        # Log to file
        logger.error(f"❌ {error_msg}")
        return DeployResult(success=False, message=error_msg)

    # Build deploy.py command (SSH-specific parameters)
    # Note: ssh_options and execution_mode are now internal parameters,
    # controlled via environment variables only (not command-line args)
    cmd = [
        "python3",
        str(deploy_script),
        "--board-ip",
        deploy_config.board_ip,
        "--board-user",
        deploy_config.board_user,
        "--deploy-path",
        deploy_config.deploy_path,
    ]

    # Add optional parameters
    if deploy_config.binary_args:
        cmd.extend(["--binary-args", deploy_config.binary_args])

    if deploy_config.remote_log_enabled and deploy_config.remote_log_path != "/dev/null":
        cmd.extend(["--remote-log-path", deploy_config.remote_log_path])

    # Console output: simple progress message
    print(f"📤 Deploying to {deploy_config.board_ip}...")

    # Log to file: detailed command info
    logger.info("💡 Invoking deploy script:")
    logger.info(f"   Command: {' '.join(cmd)}")
    logger.info(f"   Working directory: {build_dir.parent}")

    # Prepare environment variables for internal parameters
    import os

    env = os.environ.copy()
    env["SSH_OPTIONS"] = deploy_config.ssh_options
    env["EXECUTION_MODE"] = deploy_config.execution_mode

    # Execute deploy.py
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,  # 2 minutes timeout
            cwd=str(build_dir.parent),
            env=env,  # Pass environment variables for internal parameters
        )

        # Parse result
        if result.returncode == 0:
            # Extract binary name from stderr output (deploy.py logs to stderr)
            binary_name = _extract_binary_name_from_output(result.stderr)

            # Extract PID if background mode
            pid = _extract_pid_from_output(result.stderr) if deploy_config.execution_mode == "background" else None

            # Extract and display program output
            log_path = _extract_log_path_from_output(result.stderr)
            program_output = ""
            if log_path:
                program_output = _fetch_remote_output(
                    deploy_config.board_ip,
                    deploy_config.board_user,
                    deploy_config.ssh_options,
                    remote_log_path=log_path,
                    max_lines=20,  # 顯示前 20 行
                )

            # Console output: success summary
            print("✅ Deploy completed successfully")
            if pid:
                print(f"🎯 Binary '{binary_name}' is running with PID {pid}")

            # Display program output if available
            if program_output:
                print("\n📋 Program Output:")
                print(program_output)
                # 檢查是否被截斷
                if program_output.count("\n") >= 19:
                    print(f"\n💡 (showing first 20 lines, full log at: {log_path})")

            # Log to file: detailed info
            logger.info("✅ Deploy completed successfully")
            if pid:
                logger.info(f"🎯 Binary '{binary_name}' is running with PID {pid}")
            if program_output:
                logger.info("")
                logger.info("--- Program Output ---")
                logger.info(program_output)
            if result.stderr:
                logger.info("")
                logger.info("--- Deploy Script Output ---")
                logger.info(result.stderr.strip())
            logger.info("")
            logger.info("=" * 60)

            return DeployResult(
                success=True,
                message=result.stderr.strip(),
                binary_name=binary_name,
                pid=pid,
            )
        else:
            # Failure - show summary on console, details in log file
            error_msg = f"Deploy script failed with exit code {result.returncode}"

            # Extract and display program output (even on failure)
            log_path = _extract_log_path_from_output(result.stderr)
            program_output = ""
            if log_path:
                program_output = _fetch_remote_output(
                    deploy_config.board_ip,
                    deploy_config.board_user,
                    deploy_config.ssh_options,
                    remote_log_path=log_path,
                    max_lines=20,
                )

            # Console output: error message with program output
            print(f"❌ {error_msg}")

            # Display program output (helps user understand what went wrong)
            if program_output:
                print("\n📋 Program Output (Error):")
                print(program_output)
            elif result.stderr:
                # Extract meaningful error from stderr (skip SSH warnings)
                actual_error = _extract_deploy_error(result.stderr)
                if actual_error:
                    print(f"💥 {actual_error}")

            # Log to file: detailed error information
            logger.error(f"❌ {error_msg}")
            logger.error("")
            logger.error("=" * 60)
            logger.error("Deploy Script Failure Details")
            logger.error("=" * 60)
            logger.error(f"Command: {' '.join(cmd)}")
            logger.error(f"Exit Code: {result.returncode}")
            logger.error("")

            if program_output:
                logger.error("--- Program Output ---")
                logger.error(program_output)
                logger.error("")

            if result.stdout:
                logger.error("--- STDOUT ---")
                logger.error(result.stdout)
                logger.error("")

            if result.stderr:
                logger.error("--- STDERR ---")
                logger.error(result.stderr)
                logger.error("")

            if not result.stdout and not result.stderr:
                logger.error("(No output from deploy script)")
                logger.error("")

            logger.error("=" * 60)

            return DeployResult(
                success=False,
                message=result.stderr.strip() if result.stderr else error_msg,
            )

    except subprocess.TimeoutExpired as e:
        error_msg = "Deploy script timeout (120s)"

        # Console output: simple timeout message
        print(f"❌ {error_msg}")

        # Log to file: detailed timeout information
        logger.error(f"❌ {error_msg}")
        logger.error("")
        logger.error("=" * 60)
        logger.error("Deploy Script Timeout Details")
        logger.error("=" * 60)
        logger.error(f"Command: {' '.join(cmd)}")
        logger.error("Timeout: 120 seconds")
        logger.error("")

        # Show partial output if available
        if e.stdout:
            logger.error("--- PARTIAL STDOUT ---")
            logger.error(e.stdout)
            logger.error("")

        if e.stderr:
            logger.error("--- PARTIAL STDERR ---")
            logger.error(e.stderr)
            logger.error("")

        logger.error("=" * 60)
        return DeployResult(success=False, message=error_msg)

    except Exception as e:
        error_msg = f"Failed to execute deploy script: {str(e)}"

        # Console output: simple error message
        print(f"❌ {error_msg}")

        # Log to file: detailed error information
        logger.error(f"❌ {error_msg}")
        logger.error("")
        logger.error("=" * 60)
        logger.error("Deploy Script Execution Error")
        logger.error("=" * 60)
        logger.error(f"Command: {' '.join(cmd)}")
        logger.error(f"Error Type: {type(e).__name__}")
        logger.error(f"Error Message: {str(e)}")
        logger.error("=" * 60)
        return DeployResult(success=False, message=error_msg)


def _deploy_direct_flashing(build_dir: Path, config: "ProjectConfig", binary_args: str) -> DeployResult:
    """
    Deploy to MCU platforms via direct flashing (STM32, ESP32, nRF52).

    This function is a placeholder for future MCU platform support.
    When implementing STM32 support, this function will:
    1. Locate platform-specific deploy.py (e.g., .fwauto/deploy/deploy_stm32.py)
    2. Build command with MCU-specific parameters (e.g., --hex-file, --stlink-cli)
    3. Execute deploy script via subprocess
    4. Parse result and return DeployResult

    Args:
        build_dir: Path to build directory
        config: Project configuration
        binary_args: Arguments to pass (may not be applicable for MCU)

    Returns:
        DeployResult indicating success/failure

    Raises:
        NotImplementedError: Direct flashing not yet implemented
    """
    logger.error("❌ Direct flashing support not yet implemented")
    logger.error(f"   SDK Type: {config.sdk_type}")
    logger.error("   Supported platforms: STM32, ESP32, nRF52 (future)")
    logger.error("")
    logger.error("To add STM32 support:")
    logger.error("1. Create .fwauto/deploy/deploy.py for STM32 platform")
    logger.error("2. Implement this function to call the deploy script")
    logger.error("3. Update tests")

    raise NotImplementedError(f"Direct flashing not yet implemented for SDK type: {config.sdk_type}")
