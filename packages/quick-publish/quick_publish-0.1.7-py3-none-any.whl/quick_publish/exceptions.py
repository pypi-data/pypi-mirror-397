"""Custom exceptions for quick-publish."""


class QuickPublishError(Exception):
    """Base exception for quick-publish errors."""

    pass


class GitError(QuickPublishError):
    """Raised when git operations fail."""

    pass


class VersionError(QuickPublishError):
    """Raised when version operations fail."""

    pass


class ChangelogError(QuickPublishError):
    """Raised when changelog operations fail."""

    pass


class ConfigError(QuickPublishError):
    """Raised when configuration is invalid."""

    pass


class PublishError(QuickPublishError):
    """Raised when publishing operations fail."""

    pass
