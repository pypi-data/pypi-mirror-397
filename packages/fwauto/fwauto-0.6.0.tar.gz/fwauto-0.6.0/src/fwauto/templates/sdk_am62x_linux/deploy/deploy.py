#!/usr/bin/env python3
"""
Standalone deploy script for AM62X Linux deployment.

This script is completely self-contained and has NO external dependencies.
It uses only Python built-in libraries.

Usage:
    python3 deploy.py
    python3 deploy.py --board-ip 192.168.50.169 --binary-args "on"
    python3 deploy.py --help

Environment Variables (User Configurable):
    BOARD_IP          - Board IP address (default: 192.168.50.169)
    BOARD_USER        - SSH user (default: root)
    DEPLOY_PATH       - Remote deployment path (default: /home/root)
    BINARY_ARGS       - Arguments to pass to binary (default: "")
    REMOTE_LOG_PATH   - Remote log file path (default: .fwauto/logs/app.log)

Environment Variables (Internal - Not for user modification):
    SSH_OPTIONS       - SSH options (default: -o StrictHostKeyChecking=no ...)
    EXECUTION_MODE    - foreground or background (default: foreground)
"""

import argparse
import os
import socket
import subprocess
import sys
from pathlib import Path

# ============================================
# Configuration
# ============================================


def get_config():
    """Parse command line arguments and environment variables."""
    parser = argparse.ArgumentParser(
        description="AM62X Deploy: Deploy and execute binary via SSH",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--board-ip",
        default=os.getenv("BOARD_IP", "192.168.50.169"),
        help="Board IP address (default: %(default)s or $BOARD_IP)",
    )

    parser.add_argument(
        "--board-user",
        default=os.getenv("BOARD_USER", "root"),
        help="SSH user (default: %(default)s or $BOARD_USER)",
    )

    parser.add_argument(
        "--deploy-path",
        default=os.getenv("DEPLOY_PATH", "/home/root"),
        help="Remote deployment path (default: %(default)s or $DEPLOY_PATH)",
    )

    parser.add_argument(
        "--binary-args",
        default=os.getenv("BINARY_ARGS", ""),
        help="Arguments to pass to binary (default: '' or $BINARY_ARGS)",
    )

    parser.add_argument(
        "--build-dir",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "build",
        help="Build directory containing binary (default: ../../build)",
    )

    parser.add_argument(
        "--remote-log-path",
        default=os.getenv("REMOTE_LOG_PATH", ".fwauto/logs/app.log"),
        help="Remote log file path for background execution (default: .fwauto/logs/app.log or $REMOTE_LOG_PATH)",
    )

    args = parser.parse_args()

    # Internal parameters (not exposed as command-line arguments)
    args.ssh_options = os.getenv(
        "SSH_OPTIONS", "-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5"
    )
    args.execution_mode = os.getenv("EXECUTION_MODE", "foreground")

    return args


# ============================================
# Logging
# ============================================


def log_section(msg):
    """Print section header."""
    print("=" * 60, file=sys.stderr)
    print(msg, file=sys.stderr)
    print("=" * 60, file=sys.stderr)


def log_info(msg):
    """Print info message."""
    print(f"ℹ️  {msg}", file=sys.stderr)


def log_success(msg):
    """Print success message."""
    print(f"✅ {msg}", file=sys.stderr)


def log_error(msg):
    """Print error message."""
    print(f"❌ {msg}", file=sys.stderr)


# ============================================
# Network Connectivity
# ============================================


def check_network_connectivity(board_ip):
    """
    Check if the board is reachable via network.

    Args:
        board_ip: IP address of the target board

    Raises:
        SystemExit: If board is not reachable or SSH port is closed
    """
    log_info(f"Checking network connectivity to {board_ip}...")

    # Check if host is reachable via ping
    ping_cmd = ["ping", "-c", "1", "-W", "2", board_ip]
    try:
        result = subprocess.run(ping_cmd, capture_output=True, timeout=5)
        if result.returncode != 0:
            log_error(f"Cannot reach board at {board_ip}")
            print("\nPossible causes:", file=sys.stderr)
            print("  1. Board is powered off", file=sys.stderr)
            print("  2. Network cable is disconnected", file=sys.stderr)
            print("  3. Board IP address has changed", file=sys.stderr)
            print("  4. Wrong network configuration", file=sys.stderr)
            print("\nTroubleshooting steps:", file=sys.stderr)
            print("  • Check board power and network connection", file=sys.stderr)
            print("  • Verify IP address with: ip addr (on board console)", file=sys.stderr)
            print("  • Override IP with: export BOARD_IP=<your_board_ip>", file=sys.stderr)
            sys.exit(1)
    except subprocess.TimeoutExpired:
        log_error(f"Ping timeout to {board_ip}")
        sys.exit(1)

    # Check if SSH port is accessible
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((board_ip, 22))
        sock.close()

        if result != 0:
            log_error(f"SSH port (22) is not accessible on {board_ip}")
            print("\nPossible causes:", file=sys.stderr)
            print("  1. SSH service is not running on the board", file=sys.stderr)
            print("  2. Firewall is blocking port 22", file=sys.stderr)
            print("  3. Board is still booting", file=sys.stderr)
            print("\nTroubleshooting steps:", file=sys.stderr)
            print("  • Wait for board to fully boot (~30 seconds)", file=sys.stderr)
            print("  • Check SSH service: systemctl status sshd (on board)", file=sys.stderr)
            print(f"  • Try manual SSH: ssh root@{board_ip}", file=sys.stderr)
            sys.exit(1)
    except OSError as e:
        log_error(f"Socket error while checking SSH port: {e}")
        sys.exit(1)

    log_success("Network connectivity OK")


# ============================================
# Binary Discovery
# ============================================


def find_binary(build_dir):
    """
    Find the first executable binary in build directory.

    Args:
        build_dir: Path to build directory

    Returns:
        Path to the binary file

    Raises:
        SystemExit: If no executable binary found
    """
    if not build_dir.exists():
        log_error(f"Build directory does not exist: {build_dir}")
        sys.exit(1)

    # Find executable files in build directory
    for file in build_dir.iterdir():
        if file.is_file() and is_executable(file):
            log_info(f"Found binary: {file.name}")
            return file

    log_error(f"No executable binary found in {build_dir}")
    sys.exit(1)


def is_executable(file):
    """Check if file is executable (cross-platform)."""
    import stat

    try:
        # On Unix, check execute permission
        return bool(file.stat().st_mode & stat.S_IXUSR)
    except Exception:
        # On Windows, assume files without extension or with common executable extensions are executable
        return file.suffix in ["", ".exe", ".out", ".elf"] or os.access(file, os.X_OK)


# ============================================
# SSH Deployment
# ============================================


def deploy_binary(binary_path, board_ip, board_user, deploy_path, ssh_options):
    """
    Deploy binary to remote board via SCP.

    Args:
        binary_path: Path to the binary file to deploy
        board_ip: Board IP address
        board_user: SSH user
        deploy_path: Remote deployment path
        ssh_options: SSH options string

    Returns:
        Name of the deployed binary

    Raises:
        SystemExit: If deployment fails
    """
    binary_name = binary_path.name
    remote_path = f"{deploy_path}/{binary_name}"

    log_info(f"Deploying {binary_name} to {board_user}@{board_ip}:{remote_path}")

    # Build SCP command
    ssh_opts = ssh_options.split()
    scp_cmd = ["scp"] + ssh_opts + [str(binary_path), f"{board_user}@{board_ip}:{remote_path}"]

    try:
        result = subprocess.run(scp_cmd, capture_output=True, timeout=30, text=True)

        if result.returncode != 0:
            log_error(f"Deploy failed: {result.stderr}")
            sys.exit(1)

        log_success("Deploy successful")
        return binary_name

    except subprocess.TimeoutExpired:
        log_error("SCP timeout (30s)")
        sys.exit(1)


# ============================================
# Remote Execution
# ============================================


def execute_on_board(
    binary_name, board_ip, board_user, deploy_path, ssh_options, binary_args, execution_mode, remote_log_path=""
):
    """
    Execute binary on remote board via SSH.

    Args:
        binary_name: Name of the binary to execute
        board_ip: Board IP address
        board_user: SSH user
        deploy_path: Remote deployment path
        ssh_options: SSH options string
        binary_args: Arguments to pass to binary
        execution_mode: foreground or background
        remote_log_path: Remote log file path (optional)

    Raises:
        SystemExit: If execution fails
    """
    mode_desc = "foreground" if execution_mode == "foreground" else "background"
    log_info(f"Executing {binary_name} on board ({mode_desc} mode)...")

    # Display full execution command
    full_command = f"./{binary_name}"
    if binary_args:
        full_command += f" {binary_args}"

    log_info(f"Full command: {full_command}")
    log_info(f"Execution path: {deploy_path}")
    log_info(f"Target: {board_user}@{board_ip}")

    print("", file=sys.stderr)

    # Build remote execution script
    remote_script = build_remote_script(binary_name, deploy_path, binary_args, execution_mode, remote_log_path)

    # Execute via SSH
    ssh_opts = ssh_options.split()
    ssh_cmd = ["ssh"] + ssh_opts + [f"{board_user}@{board_ip}", "bash"]

    try:
        result = subprocess.run(ssh_cmd, input=remote_script, capture_output=True, timeout=10, text=True)

        if result.returncode != 0:
            # Extract program output from between markers (background mode)
            stdout = result.stdout or ""
            if "PROGRAM_OUTPUT_START" in stdout and "PROGRAM_OUTPUT_END" in stdout:
                start = stdout.find("PROGRAM_OUTPUT_START") + len("PROGRAM_OUTPUT_START")
                end = stdout.find("PROGRAM_OUTPUT_END")
                program_output = stdout[start:end].strip()
                if program_output:
                    log_error(f"Execution failed: {program_output}")
                    sys.exit(1)

            # Fallback: extract error from stdout and stderr (ignore SSH warnings)
            combined_output = stdout + "\n" + (result.stderr or "")
            error_lines = [
                line
                for line in combined_output.strip().split("\n")
                if line
                and not line.startswith("Warning:")
                and not line.startswith("**")  # Ignore post-quantum SSH warnings
                and not line.startswith("Executing ./")  # Ignore our own echo
                and "PROGRAM_OUTPUT" not in line  # Ignore markers
            ]
            error_msg = error_lines[-1] if error_lines else "Unknown error"
            log_error(f"Execution failed: {error_msg}")
            sys.exit(1)

        if execution_mode == "foreground":
            log_success("Binary executed successfully")
        else:
            log_success("Firmware started successfully (background mode)")

    except subprocess.TimeoutExpired:
        log_error("SSH execution timeout (10s)")
        sys.exit(1)


def build_remote_script(binary_name, deploy_path, binary_args, execution_mode, remote_log_path=""):
    """Build the bash script to execute on remote board."""
    # Escape single quotes in arguments to prevent injection
    binary_args_escaped = binary_args.replace("'", "'\\''")

    if execution_mode == "foreground":
        return f"""
set -eo pipefail
cd '{deploy_path}' || {{ echo "ERROR: Cannot cd to {deploy_path}" >&2; exit 1; }}
pkill -9 '{binary_name}' 2>/dev/null || true
chmod +x './{binary_name}' || {{ echo "ERROR: Cannot chmod {binary_name}" >&2; exit 1; }}
echo "Executing ./{binary_name} {binary_args_escaped}..." >&2
'./{binary_name}' {binary_args_escaped}
EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
    echo "SUCCESS: Binary executed successfully" >&2
    exit 0
else
    echo "ERROR: Binary exited with code $EXIT_CODE" >&2
    exit 1
fi
"""
    else:
        # Background mode with configurable logging
        log_path_escaped = remote_log_path.replace("'", "'\\''") if remote_log_path else ""

        if log_path_escaped:
            # 有指定日誌路徑：寫入日誌
            import time

            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            log_setup = f"""
mkdir -p "$(dirname '{log_path_escaped}')"
cat >> '{log_path_escaped}' <<'LOG_HEADER'

==========================================
Firmware Execution: {timestamp}
Binary: {binary_name}
Arguments: {binary_args_escaped}
==========================================

LOG_HEADER
LOG_TARGET='{log_path_escaped}'
"""
        else:
            # 無指定日誌路徑：使用 /dev/null
            log_setup = "LOG_TARGET='/dev/null'"

        return f"""
set -e
cd '{deploy_path}' || {{ echo "ERROR: Cannot cd to {deploy_path}" >&2; exit 1; }}
pkill -9 '{binary_name}' 2>/dev/null || true
chmod +x './{binary_name}' || {{ echo "ERROR: Cannot chmod {binary_name}" >&2; exit 1; }}
{log_setup}
# Capture output to temp file first (for error reporting)
TEMP_OUTPUT=$(mktemp)
'./{binary_name}' {binary_args_escaped} > "$TEMP_OUTPUT" 2>&1 &
FIRMWARE_PID=$!
sleep 0.5

# Check if process is still running (daemon) or completed successfully (short-lived)
if kill -0 $FIRMWARE_PID 2>/dev/null; then
    # Process still running - it's a daemon, append output to log and continue
    cat "$TEMP_OUTPUT" >> "$LOG_TARGET" 2>/dev/null
    rm -f "$TEMP_OUTPUT"
    echo "SUCCESS: Firmware started with PID $FIRMWARE_PID (running)" >&2
    exit 0
else
    # Process already exited, check if it was successful
    # Note: capture exit code before set -e can terminate the script
    EXIT_CODE=0
    wait $FIRMWARE_PID 2>/dev/null || EXIT_CODE=$?
    if [ $EXIT_CODE -eq 0 ]; then
        cat "$TEMP_OUTPUT" >> "$LOG_TARGET" 2>/dev/null
        rm -f "$TEMP_OUTPUT"
        echo "SUCCESS: Firmware completed successfully" >&2
        exit 0
    else
        # Show program output on failure (this goes to stdout for Python to capture)
        echo "PROGRAM_OUTPUT_START"
        cat "$TEMP_OUTPUT" 2>/dev/null
        echo "PROGRAM_OUTPUT_END"
        cat "$TEMP_OUTPUT" >> "$LOG_TARGET" 2>/dev/null
        rm -f "$TEMP_OUTPUT"
        echo "ERROR: Firmware failed with exit code $EXIT_CODE" >&2
        exit 1
    fi
fi
"""


# ============================================
# Main
# ============================================


def main():
    """Main entry point."""
    config = get_config()

    log_section("AM62X Deploy: Deploy and Execute")

    # Step 1: Check network connectivity
    check_network_connectivity(config.board_ip)

    # Step 2: Find binary
    binary_path = find_binary(config.build_dir)

    # Step 3: Deploy binary
    binary_name = deploy_binary(binary_path, config.board_ip, config.board_user, config.deploy_path, config.ssh_options)

    # Step 4: Execute on board
    execute_on_board(
        binary_name,
        config.board_ip,
        config.board_user,
        config.deploy_path,
        config.ssh_options,
        config.binary_args,
        config.execution_mode,
        config.remote_log_path,
    )

    print("", file=sys.stderr)
    log_section("✅ Deploy completed successfully")

    return 0


if __name__ == "__main__":
    sys.exit(main())
