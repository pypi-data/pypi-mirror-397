"""
Custom exceptions for Repo-Fetcher.
"""
class RepoFetcherError(Exception):
    """Base exception for all Repo-Fetcher errors."""
    pass
class DownloadError(RepoFetcherError):
    """Raised when download fails."""
    pass
class AuthenticationError(RepoFetcherError):
    """Raised when authentication fails."""
    pass
class InvalidConfigError(RepoFetcherError):
    """Raised when configuration is invalid."""
    pass
class PlatformNotSupportedError(RepoFetcherError):
    """Raised when platform is not supported."""
    pass
class ArchiveError(RepoFetcherError):
    """Raised when archive operations fail."""
    pass
class NetworkError(RepoFetcherError):
    """Raised when network operations fail."""
    pass
class HookError(RepoFetcherError):
    """Raised when hook execution fails."""
    pass
