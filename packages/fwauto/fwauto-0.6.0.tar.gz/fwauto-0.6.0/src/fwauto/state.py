"""State definitions for firmware development workflow."""

from typing import Annotated, Any, Literal, TypedDict


class FirmwareState(TypedDict):
    """
    State container for the firmware development workflow.

    This TypedDict defines the complete state structure used throughout the
    LangGraph workflow for STM32 firmware development automation.

    Attributes:
        user_prompt: User input or command description
        project_root: Absolute path to the project root directory
        project_initialized: Flag indicating if project paths are validated

        build_status: Current build operation status
        build_errors: List of compilation error messages
        build_log: Complete build output and logs

        deploy_status: Current deploy operation status
        deploy_errors: List of deployment error messages
        deploy_log: Complete deploy output and logs

        iteration: Current retry attempt number (for AI fix loops)
        max_retries: Maximum allowed retry attempts

        execution_mode: Workflow execution mode set by Typer CLI
        command: Command name from Typer CLI (e.g., "build", "quick")
        command_args: Dictionary of parsed command arguments
        mode_metadata: Additional metadata for execution mode context
        command_error: Error message from command parsing failures
    """

    user_prompt: Annotated[str, "User input or command description"]
    project_root: Annotated[str, "Absolute path to the project root directory"]
    project_initialized: Annotated[bool, "Flag indicating if project paths are validated"]

    build_status: Annotated[Literal["success", "error", "pending"], "Current build operation status"]
    build_errors: Annotated[list[str], "List of compilation error messages"]
    build_log: Annotated[str, "Complete build output and logs"]

    deploy_status: Annotated[Literal["success", "error", "pending"], "Current deploy operation status"]
    deploy_errors: Annotated[list[str], "List of deployment error messages"]
    deploy_log: Annotated[str, "Complete deploy output and logs"]

    # Retry mechanism fields
    iteration: Annotated[int, "Current retry attempt number (for AI fix loops)"]
    max_retries: Annotated[int, "Maximum allowed retry attempts"]

    # Command fields (set by Typer CLI)
    execution_mode: Annotated[
        Literal["build", "deploy", "run", "log", "feat", "chat"] | None,
        "Workflow execution mode set by Typer CLI",
    ]
    command: Annotated[str | None, "Command name from Typer CLI (e.g., 'build', 'quick')"]
    command_args: Annotated[dict[str, Any] | None, "Dictionary of parsed command arguments"]
    mode_metadata: Annotated[dict[str, Any] | None, "Additional metadata for execution mode context"]
    command_error: Annotated[str | None, "Error message from command parsing failures"]

    # Log analysis fields
    log_file_path: Annotated[str | None, "Path to UART log file for analysis"]
    log_analysis_result: Annotated[str | None, "AI analysis result text"]

    # Firmware build output fields
    firmware_path: Annotated[
        str | None,
        "Generated firmware hex file path (populated by build_node on success)",
    ]

    # Platform configuration field
    platform: Annotated[
        str,
        "Platform identifier (e.g., 'stm32_keil', 'esp32_idf', 'nordic_nrf')",
    ]

    # Chat mode fields
    chat_completed: Annotated[
        bool | None,
        "Flag indicating if chat session ended normally (True) or abnormally (False/None)",
    ]
