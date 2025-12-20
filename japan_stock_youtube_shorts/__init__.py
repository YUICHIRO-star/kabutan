"""
Utility package for orchestrating a YouTube Shorts pipeline focused on
Japanese stock market updates.
"""

from importlib import metadata


def get_version() -> str:
    """Return the package version if installed, otherwise an empty string."""
    try:
        return metadata.version(__name__)
    except metadata.PackageNotFoundError:
        return ""
