"""AI utilities for Claude Code SDK integration.

Shared utilities used across all AI nodes (ai_brain, log, chat) to reduce
code duplication and ensure consistent behavior.
"""

from claude_agent_sdk.types import AssistantMessage, Message, TextBlock


def print_ai_message(message: Message, prefix: str = "🧠") -> None:
    """
    Print AI message to console with consistent formatting.

    Args:
        message: Message from Claude Agent SDK
        prefix: Emoji prefix for the message (default: "🧠")

    Examples:
        >>> print_ai_message(message, prefix="📊")  # For log analysis
        >>> print_ai_message(message, prefix="💬")  # For chat
    """
    if isinstance(message, AssistantMessage):
        for block in message.content:
            if isinstance(block, TextBlock):
                print(f"{prefix} {block.text.strip()}")


def format_ai_response(message: Message) -> str:
    """
    Extract text content from AI message for storage.

    Args:
        message: Message from Claude Agent SDK

    Returns:
        Formatted text content
    """
    if isinstance(message, AssistantMessage):
        texts = []
        for block in message.content:
            if isinstance(block, TextBlock):
                texts.append(block.text.strip())
        return "\n".join(texts)
    return str(message)
