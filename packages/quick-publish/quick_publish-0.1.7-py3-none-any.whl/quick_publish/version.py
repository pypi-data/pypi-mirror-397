"""Version management utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import questionary
from packaging.version import InvalidVersion, Version

from .exceptions import VersionError


class VersionManager:
    """Manages semantic versioning for the project."""

    def __init__(self, working_dir: Path) -> None:
        self.working_dir = working_dir
        self.pyproject_path = working_dir / "pyproject.toml"

    def get_current_version(self) -> Version:
        """Get current version from pyproject.toml."""
        try:
            import toml

            pyproject_data = toml.load(self.pyproject_path)
            version_str = pyproject_data["project"]["version"]
            return Version(version_str)
        except (KeyError, FileNotFoundError, toml.TomlDecodeError) as e:
            raise VersionError(f"Failed to read current version: {e}") from e
        except InvalidVersion as e:
            raise VersionError(f"Invalid version format: {e}") from e

    def suggest_next_versions(self, current: Version) -> list[Version]:
        """Suggest possible next versions based on current version."""
        # Parse version components
        major = current.major
        minor = current.minor
        patch = current.micro

        suggestions = [
            Version(f"{major}.{minor}.{patch + 1}"),  # patch
            Version(f"{major}.{minor + 1}.0"),  # minor
            Version(f"{major + 1}.0.0"),  # major
        ]

        return suggestions

    def select_version(
        self, current: Version, version_override: str | None = None
    ) -> Version:
        """Interactively select next version or use override."""
        if version_override:
            try:
                return Version(version_override)
            except InvalidVersion as e:
                raise VersionError(f"Invalid version override: {e}") from e

        suggestions = self.suggest_next_versions(current)

        # Create choices for questionary
        choices = [
            (
                questionary.Choice(f"{v} (patch)", value=v)
                if v.micro > current.micro
                else (
                    questionary.Choice(f"{v} (minor)", value=v)
                    if v.minor > current.minor
                    else questionary.Choice(f"{v} (major)", value=v)
                )
            )
            for v in suggestions
        ]
        choices.append(questionary.Choice("Custom version", value="custom"))

        choice: Any = questionary.select(
            f"Current version: {current}\nSelect next version:",
            choices=choices,
        ).ask()

        if choice == "custom":
            custom_version: Any = questionary.text("Enter version:").ask()
            if not custom_version:
                raise VersionError("Version cannot be empty")
            try:
                return Version(custom_version)
            except InvalidVersion as e:
                raise VersionError(f"Invalid version format: {e}") from e

        # Type assertion - mypy doesn't know choice is Version
        assert isinstance(choice, Version)
        return choice

    def update_version(self, new_version: Version) -> None:
        """Update version in pyproject.toml."""
        try:
            import toml

            pyproject_data = toml.load(self.pyproject_path)
            pyproject_data["project"]["version"] = str(new_version)

            with open(self.pyproject_path, "w") as f:
                toml.dump(pyproject_data, f)
        except (KeyError, FileNotFoundError, toml.TomlDecodeError) as e:
            raise VersionError(f"Failed to update version: {e}") from e

    def validate_version(self, version: str) -> bool:
        """Validate if version string is a valid semantic version."""
        try:
            Version(version)
            return True
        except InvalidVersion:
            return False
