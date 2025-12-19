"""
quick-publish - Shipped a standard `publish` workflow with one click for Python packages.

A Python port of the popular npm package quick-publish, providing automated
semantic versioning, changelog generation, git tagging, and package publishing.
"""

__version__ = "0.1.2"
__author__ = "quick-publish contributors"
__email__ = "contributors@quick-publish.dev"

from .changelog import ChangelogGenerator
from .core import Publisher
from .version import VersionManager

__all__ = ["Publisher", "VersionManager", "ChangelogGenerator"]
