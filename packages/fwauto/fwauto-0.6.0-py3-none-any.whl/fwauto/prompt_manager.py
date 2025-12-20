"""Prompt Template Manager for AI Brain."""

import os
import platform as platform_module  # 重命名避免與變數名稱衝突
from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from .logging_config import get_logger


class PromptManager:
    """Manages prompt templates for AI Brain tasks."""

    def __init__(self):
        """Initialize prompt manager with prompts directory."""
        # prompts/ directory inside the package (src/fwauto/prompts/)
        self.prompts_dir = Path(__file__).parent / "prompts"

        # Jinja2 environment with strict undefined variables
        self.env = Environment(
            loader=FileSystemLoader(self.prompts_dir),
            undefined=StrictUndefined,  # Variables not found will raise error
        )

        # Set up logger
        self.logger = get_logger("prompt_manager")

    def get_prompt(self, task_type: str, state: dict[str, Any]) -> str:
        """
        Get prompt template for specified task type.

        Args:
            task_type: Task type (e.g., 'fix_build_errors')
            state: FirmwareState dictionary

        Returns:
            Rendered prompt string

        Raises:
            TemplateNotFound: If prompt file doesn't exist
            UndefinedError: If template variable is missing
        """
        template_file = f"{task_type}.md"

        # Log prompt selection
        self.logger.debug(f"🧠 AI Brain: Task type: {task_type}")
        self.logger.debug(f"🧠 AI Brain: Prompt: prompts/{template_file}")
        self.logger.debug(f"🧠 AI Brain: Reason: {self._get_trigger_reason(task_type, state)}")

        # Prepare all available variables
        variables = self._build_variables(state)

        # Load and render template
        template = self.env.get_template(template_file)
        prompt = template.render(**variables)

        self.logger.debug(f"🧠 AI Brain: Prompt loaded successfully ({len(prompt)} chars)")
        return prompt

    def _build_variables(self, state: dict[str, Any]) -> dict[str, Any]:
        """Build variables dictionary for template rendering."""
        platform = state.get("platform", "stm32_keil")

        # Build base variables
        variables = {
            # System variables
            "cwd": os.getcwd(),
            "username": os.getenv("USERNAME", os.getenv("USER", "unknown")),
            "os_name": platform_module.system(),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "platform": platform,
            # State variables (direct pass-through)
            **state,
        }

        # Only load platform_config if needed (for AI brain prompts)
        # Check if template uses platform_config by looking at the template content
        # This avoids errors for platforms that don't have platform_config defined
        try:
            from .platforms import get_platform_config
            platform_config = get_platform_config(platform)
            variables["platform_config"] = platform_config
        except ValueError as e:
            # Platform not defined in platforms.py - only warn if this is an AI brain task
            # For chat/log modes, platform_config is not needed
            self.logger.debug(f"Platform config not found for {platform}: {e}")
            # Provide a minimal fallback to avoid template rendering errors
            variables["platform_config"] = {
                "name": platform,
                "forbidden_dirs": [],
                "allowed_dirs": [],
                "stop_conditions": [],
            }

        return variables

    def _get_trigger_reason(self, task_type: str, state: dict[str, Any]) -> str:
        """Get human-readable reason for task type selection."""
        if task_type == "fix_build_errors":
            error_count = len(state.get("build_errors", []))
            return f"Build failed with {error_count} errors"
        elif task_type == "implement_feature":
            prompt = state.get("user_prompt", "")
            return f"Feature request: {prompt[:50]}..." if len(prompt) > 50 else f"Feature request: {prompt}"
        elif task_type == "rag_query":
            command_args = state.get("command_args", {})
            query = command_args.get("query", "")
            return f"RAG query: {query[:50]}..." if len(query) > 50 else f"RAG query: {query}"
        elif task_type == "fix_bug":
            prompt = state.get("user_prompt", "")
            return f"Bug fix: {prompt[:50]}..." if len(prompt) > 50 else f"Bug fix: {prompt}"
        elif task_type == "natural_language":
            prompt = state.get("user_prompt", "")
            return f"Natural language: {prompt[:50]}..." if len(prompt) > 50 else f"Natural language: {prompt}"
        elif task_type == "general_codegen":
            return "General code generation task"
        else:
            return f"Unknown task type: {task_type}"
