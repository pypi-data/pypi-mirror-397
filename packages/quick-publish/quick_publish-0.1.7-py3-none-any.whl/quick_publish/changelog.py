"""Changelog generation utilities."""

from __future__ import annotations

import re
from pathlib import Path

from .exceptions import ChangelogError


class ChangelogGenerator:
    """Generates and manages changelog files."""

    def __init__(self, working_dir: Path) -> None:
        self.working_dir = working_dir
        self.changelog_path = working_dir / "CHANGELOG.md"

    def get_git_commits_since_last_tag(self) -> list[str]:
        """Get commit messages since the last git tag."""
        try:
            import git

            repo = git.Repo(self.working_dir)

            # Get the latest tag
            try:
                latest_tag = repo.git.describe("--tags", "--abbrev=0")
            except git.exc.GitCommandError:
                # No tags found, get all commits
                latest_tag = None

            # Get commits since last tag
            if latest_tag:
                commits = repo.git.log(
                    f"{latest_tag}..HEAD", "--pretty=format:%s"
                ).split("\n")
            else:
                commits = repo.git.log("--pretty=format:%s").split("\n")

            return [c.strip() for c in commits if c.strip()]
        except Exception as e:
            raise ChangelogError(f"Failed to get git commits: {e}") from e

    def parse_conventional_commits(self, commits: list[str]) -> dict[str, list[str]]:
        """Parse conventional commits into categories."""
        categories: dict[str, list[str]] = {
            "feat": [],
            "fix": [],
            "docs": [],
            "style": [],
            "refactor": [],
            "perf": [],
            "test": [],
            "build": [],
            "ci": [],
            "chore": [],
            "other": [],
        }

        for commit in commits:
            # Parse conventional commit format: type(scope): description
            match = re.match(r"^(\w+)(\([^)]*\))?:\s*(.+)$", commit)
            if match:
                commit_type = match.group(1)
                description = match.group(3)

                if commit_type in categories:
                    categories[commit_type].append(description)
                else:
                    categories["other"].append(commit)
            else:
                categories["other"].append(commit)

        return categories

    def generate_changelog_entry(
        self, version: str, date: str, categories: dict[str, list[str]]
    ) -> str:
        """Generate a changelog entry for a specific version."""
        lines = [f"## [{version}] - {date}", ""]

        # Define category titles and order
        category_titles = {
            "feat": "### Features",
            "fix": "### Bug Fixes",
            "docs": "### Documentation",
            "style": "### Styles",
            "refactor": "### Code Refactoring",
            "perf": "### Performance Improvements",
            "test": "### Tests",
            "build": "### Build System",
            "ci": "### Continuous Integration",
            "chore": "### Chores",
            "other": "### Other Changes",
        }

        for category, title in category_titles.items():
            items = categories.get(category, [])
            if items:
                lines.append(title)
                for item in items:
                    lines.append(f"- {item}")
                lines.append("")

        return "\n".join(lines)

    def update_changelog(self, version: str, dry_run: bool = False) -> None:
        """Update CHANGELOG.md with new version entry."""
        from datetime import datetime

        commits = self.get_git_commits_since_last_tag()
        categories = self.parse_conventional_commits(commits)

        date = datetime.now().strftime("%Y-%m-%d")
        new_entry = self.generate_changelog_entry(version, date, categories)

        # Read existing changelog or create new one
        if self.changelog_path.exists():
            existing_content = self.changelog_path.read_text(encoding="utf-8")

            # Insert new entry after header
            lines = existing_content.split("\n")

            # Find where to insert (after title and any empty lines)
            insert_index = 1
            while insert_index < len(lines) and lines[insert_index].strip() == "":
                insert_index += 1

            lines.insert(insert_index, "")
            lines.insert(insert_index, new_entry)

            new_content = "\n".join(lines)
        else:
            # Create new changelog
            header = "# Changelog\n\nAll notable changes to this project will be documented in this file.\n\n"
            new_content = header + new_entry

        if not dry_run:
            self.changelog_path.write_text(new_content, encoding="utf-8")

    def ensure_changelog_exists(self) -> None:
        """Ensure CHANGELOG.md exists with proper header."""
        if not self.changelog_path.exists():
            header = "# Changelog\n\nAll notable changes to this project will be documented in this file.\n"
            self.changelog_path.write_text(header, encoding="utf-8")
