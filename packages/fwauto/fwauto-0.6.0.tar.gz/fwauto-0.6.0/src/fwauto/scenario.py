"""Scenario management for FWAuto.

Scenarios are predefined parameter combinations that can be used with flash/run commands.
Example:
    [[scenarios]]
    name = "led-on"
    description = "Turn on LED"
    binary_args = "on"
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class Scenario:
    """Represents a predefined execution scenario."""

    name: str
    description: str
    binary_args: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Scenario":
        """
        Create Scenario from TOML dict.

        Args:
            data: Dictionary containing scenario configuration

        Returns:
            Scenario instance

        Raises:
            KeyError: If required fields are missing
        """
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            binary_args=data.get("binary_args", ""),
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Convert to dict for TOML serialization.

        Returns:
            Dictionary representation of the scenario
        """
        return {
            "name": self.name,
            "description": self.description,
            "binary_args": self.binary_args,
        }


class ScenarioManager:
    """Manage scenarios from Project config."""

    def __init__(self, project_scenarios: list[Scenario]):
        """
        Initialize scenario manager.

        Args:
            project_scenarios: Scenarios from Project Config
        """
        self.scenarios = {s.name: s for s in project_scenarios}

    def get_scenario(self, name: str) -> Scenario | None:
        """
        Get scenario by name.

        Args:
            name: Scenario name to lookup

        Returns:
            Scenario object or None if not found
        """
        return self.scenarios.get(name)

    def list_scenarios(self) -> list[Scenario]:
        """
        List all scenarios.

        Returns:
            List of all available scenarios
        """
        return list(self.scenarios.values())
