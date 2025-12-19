"""
Repo-Fetcher: A production-ready library for downloading repositories
from various platforms with maximum flexibility.
"""

__version__ = "1.0.0"
__author__ = "Repo-Fetcher Team"

from .fetcher import RepoFetcher, DownloadConfig, DownloadResult
from .exceptions import (
    RepoFetcherError,
    DownloadError,
    AuthenticationError,
    InvalidConfigError,
    PlatformNotSupportedError,
)

__all__ = [
    "RepoFetcher",
    "DownloadConfig",
    "DownloadResult",
    "RepoFetcherError",
    "DownloadError",
    "AuthenticationError",
    "InvalidConfigError",
    "PlatformNotSupportedError",
]
