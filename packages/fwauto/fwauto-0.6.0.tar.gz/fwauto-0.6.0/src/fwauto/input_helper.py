"""Input helper module for handling terminal input with CJK character support.

This module provides a wrapper around prompt_toolkit to handle terminal input
correctly for CJK (Chinese, Japanese, Korean) characters, which Rich's console.input()
doesn't handle properly for backspace operations.
"""

from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style


def get_input(prompt_text: str, style_tag: str = "cyan") -> str:
    """
    Get user input with proper CJK character support.

    This function uses prompt_toolkit instead of Rich's console.input()
    to correctly handle backspace operations with CJK characters.

    Args:
        prompt_text: The prompt text to display (e.g., "fwauto>", "You>")
        style_tag: HTML style tag for coloring (default: "cyan")

    Returns:
        User input string (stripped of leading/trailing whitespace)

    Examples:
        >>> user_input = get_input("fwauto>")
        >>> user_input = get_input("You>", style_tag="green")
    """
    # Create HTML-formatted prompt with styling
    formatted_prompt = HTML(f"<{style_tag}><b>{prompt_text}</b></{style_tag}> ")

    # Define custom style (minimal, just colors)
    custom_style = Style.from_dict(
        {
            "cyan": "#00ffff bold",
            "green": "#00ff00 bold",
            "yellow": "#ffff00 bold",
            "red": "#ff0000 bold",
        }
    )

    # Get input using prompt_toolkit
    try:
        user_input = prompt(formatted_prompt, style=custom_style)
        return user_input.strip()
    except (EOFError, KeyboardInterrupt):
        # Re-raise to let caller handle gracefully
        raise
