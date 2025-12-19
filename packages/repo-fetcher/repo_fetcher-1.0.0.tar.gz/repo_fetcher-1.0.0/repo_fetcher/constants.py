"""
Constants and enumerations for Repo-Fetcher.
"""

from enum import Enum
from typing import Dict, Any

class Platform(Enum):
    """Supported platforms."""
    GITHUB = "github"
    GITLAB = "gitlab"
    NPM = "npm"
    BITBUCKET = "bitbucket"
    GIT = "git"
    GENERIC = "generic"

class ArchiveFormat(Enum):
    """Supported archive formats."""
    TAR_GZ = "tar.gz"
    TAR_BZ2 = "tar.bz2"
    TAR_XZ = "tar.xz"
    ZIP = "zip"

class LogLevel(Enum):
    """Logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

# Default configuration
DEFAULT_CONFIG: Dict[str, Any] = {
    "platform": Platform.GITHUB,
    "dest": ".",
    "branch": "main",
    "tag": None,
    "commit": None,
    "archive_format": ArchiveFormat.TAR_GZ,
    "compression_level": 6,
    "keep_archive": False,
    "overwrite": False,
    "mkdirs": True,
    "timeout": 30,
    "retries": 3,
    "retry_delay": 1.0,
    "verify_ssl": True,
    "async_mode": False,
    "chunk_size": 8192,
    "show_progress": True,
    "log_level": LogLevel.INFO,
    "ignore_errors": False,
    "raise_on_error": True,
    "retry_on_fail": True,
    "flatten": False,
}
