"""Slash command parsing for unified chat interface."""

import shlex
from dataclasses import dataclass
from typing import Any


@dataclass
class SlashCommand:
    """Parsed slash command representation."""

    name: str  # "build", "deploy", "log"
    raw_args: list[str]  # 原始參數列表
    parsed_args: dict[str, Any]  # 解析後的參數 dict


def parse_slash_command(user_input: str) -> SlashCommand | None:
    """Parse user input as slash command.

    Examples:
        "/build" -> SlashCommand(name="build", raw_args=[], parsed_args={})
        "/deploy --binary-args test.hex" -> SlashCommand(...)
        "/log analyze.txt '有任何 error 嗎?'" -> SlashCommand(...)
        "請幫我分析這個錯誤" -> None

    Args:
        user_input: User input string

    Returns:
        SlashCommand if input is valid slash command, None otherwise
    """
    if not user_input.strip().startswith("/"):
        return None

    try:
        parts = shlex.split(user_input)
    except ValueError:
        # Invalid quote syntax
        return None

    if not parts:
        return None

    command_name = parts[0][1:]  # Remove leading /

    if command_name not in ["build", "deploy", "log", "help", "exit"]:
        return None

    return SlashCommand(
        name=command_name,
        raw_args=parts[1:],
        parsed_args={},  # Will be filled by parse_command_args
    )


def parse_command_args(cmd: SlashCommand) -> dict[str, Any]:
    """Parse slash command arguments into command_args dict.

    Handles:
    - /build -> {}
    - /deploy --binary-args test.hex -> {"binary_args": "test.hex"}
    - /deploy --scenario quick -> {"binary_args": scenario.binary_args}
    - /log path.txt "prompt" -> {"log_path": "path.txt", "analysis_prompt": "prompt"}

    Args:
        cmd: SlashCommand to parse

    Returns:
        Dictionary of parsed arguments

    Raises:
        ValueError: If required arguments are missing
    """
    if cmd.name == "build":
        return _parse_build_args(cmd.raw_args)
    elif cmd.name == "deploy":
        return _parse_deploy_args(cmd.raw_args)
    elif cmd.name == "log":
        return _parse_log_args(cmd.raw_args)
    elif cmd.name == "help":
        return {}  # help 不需要參數
    elif cmd.name == "exit":
        return {}  # exit 不需要參數
    else:
        raise ValueError(f"Unknown command: {cmd.name}")


def _parse_build_args(args: list[str]) -> dict[str, Any]:
    """Parse build command arguments.

    Build command has no arguments currently.

    Args:
        args: Raw argument list

    Returns:
        Empty dict
    """
    return {}


def _parse_deploy_args(args: list[str]) -> dict[str, Any]:
    """Parse deploy command arguments.

    Priority: --binary-args > --scenario

    Args:
        args: Raw argument list

    Returns:
        Dictionary with "binary_args" key

    Examples:
        ["--binary-args", "test.hex"] -> {"binary_args": "test.hex"}
        ["--scenario", "quick"] -> {"binary_args": <from scenario>}
        ["-ba", "on"] -> {"binary_args": "on"}
    """
    binary_args = ""
    scenario = ""

    i = 0
    while i < len(args):
        if args[i] in ["--binary-args", "-ba"]:
            if i + 1 < len(args):
                binary_args = args[i + 1]
                i += 2
            else:
                raise ValueError("--binary-args requires a value")
        elif args[i] in ["--scenario", "-s"]:
            if i + 1 < len(args):
                scenario = args[i + 1]
                i += 2
            else:
                raise ValueError("--scenario requires a value")
        else:
            i += 1

    # Apply priority rule
    final_binary_args = binary_args
    if not final_binary_args and scenario:
        # Load scenario (will be done in handler)
        # For now, just pass the scenario name
        return {"binary_args": "", "scenario": scenario}

    return {"binary_args": final_binary_args}


def _parse_log_args(args: list[str]) -> dict[str, Any]:
    """Parse log command arguments.

    Format: /log [log_path] [analysis_prompt]

    Args:
        args: Raw argument list

    Returns:
        Dictionary with "log_path" and "analysis_prompt" keys
        - log_path: None if not provided (system will use last_log_file_path from config)
        - analysis_prompt: User prompt or default "分析這份 log"

    Examples:
        [] -> {"log_path": None, "analysis_prompt": "分析這份 log"}
        ["有 error 嗎?"] -> {"log_path": None, "analysis_prompt": "有 error 嗎?"}
        ["uart.log"] -> {"log_path": "uart.log", "analysis_prompt": "分析這份 log"}
        ["uart.log", "有 error 嗎?"] -> {"log_path": "uart.log", "analysis_prompt": "有 error 嗎?"}
    """
    if not args:
        # No arguments: use default prompt and auto-detect log path from config
        return {"log_path": None, "analysis_prompt": "分析這份 log"}

    # Detect if first arg is a file path or a prompt
    # Heuristic: if first arg contains path-like patterns or file extensions, treat as path
    first_arg = args[0]
    is_path = (
        "/" in first_arg  # Contains path separator
        or "\\" in first_arg  # Windows path
        or first_arg.endswith((".log", ".txt"))  # Has log file extension
        or "@" in first_arg  # Remote path (user@host:path)
    )

    if is_path:
        # First arg is log_path
        log_path = first_arg
        analysis_prompt = " ".join(args[1:]) if len(args) > 1 else "分析這份 log"
    else:
        # First arg is analysis_prompt (no log_path provided)
        log_path = None
        analysis_prompt = " ".join(args)

    return {"log_path": log_path, "analysis_prompt": analysis_prompt}
