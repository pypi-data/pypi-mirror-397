"""Git operations utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import git

from .exceptions import GitError


class GitManager:
    """Manages git operations for publishing."""

    def __init__(self, working_dir: Path) -> None:
        self.working_dir = working_dir
        self._repo: git.Repo | None = None

    @property
    def repo(self) -> git.Repo:
        """Lazy load git repository."""
        if self._repo is None:
            try:
                import git

                self._repo = git.Repo(self.working_dir)
            except git.exc.InvalidGitRepositoryError as e:
                raise GitError("Not a git repository") from e
            except Exception as e:
                raise GitError(f"Failed to initialize git repository: {e}") from e
        return self._repo

    def ensure_clean_working_tree(self) -> None:
        """Ensure working tree is clean."""
        if self.repo.is_dirty(untracked_files=True):
            raise GitError(
                "Working tree is not clean. Please commit or stash changes first."
            )

    def get_current_branch(self) -> str:
        """Get current git branch."""
        try:
            return str(self.repo.active_branch.name)
        except Exception as e:
            raise GitError(f"Failed to get current branch: {e}") from e

    def create_tag(self, tag_name: str, message: str) -> None:
        """Create a git tag."""
        try:
            self.repo.create_tag(tag_name, message=message)
        except Exception as e:
            raise GitError(f"Failed to create tag {tag_name}: {e}") from e

    def push_to_remote(self, remote: str = "origin", push_tags: bool = True) -> None:
        """Push commits and tags to remote."""
        try:
            # Push commits
            self.repo.remotes[remote].push()

            # Push tags if requested
            if push_tags:
                self.repo.remotes[remote].push(tags=True)
        except Exception as e:
            raise GitError(f"Failed to push to remote {remote}: {e}") from e

    def add_and_commit(self, files: list[str], message: str) -> None:
        """Add files and create commit."""
        try:
            # Add files
            for file_path in files:
                self.repo.index.add([file_path])

            # Commit
            self.repo.index.commit(message)
        except Exception as e:
            raise GitError(f"Failed to add and commit: {e}") from e

    def get_latest_tag(self) -> str | None:
        """Get the latest tag."""
        try:
            result: Any = self.repo.git.describe("--tags", "--abbrev=0")
            return str(result)
        except Exception:
            return None

    def tag_exists(self, tag_name: str) -> bool:
        """Check if tag exists."""
        try:
            self.repo.tags[tag_name]
            return True
        except Exception:
            return False

    def get_remote_url(self, remote: str = "origin") -> str:
        """Get remote repository URL."""
        try:
            url: Any = self.repo.remotes[remote].url
            return str(url)
        except Exception as e:
            raise GitError(f"Failed to get remote URL: {e}") from e
