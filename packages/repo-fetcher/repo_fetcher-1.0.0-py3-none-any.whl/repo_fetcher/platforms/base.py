"""
Base platform fetcher interface.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, BinaryIO
from pathlib import Path
import logging
from enum import Enum
from ..models import DownloadConfig, DownloadResult
from ..exceptions import PlatformNotSupportedError, DownloadError
class Platform(Enum):
    GITHUB = "github"
    GITLAB = "gitlab"
    NPM = "npm"
    BITBUCKET = "bitbucket"
class BaseFetcher(ABC):
    """Abstract base class for all platform fetchers."""
    def __init__(self, config: DownloadConfig):
        self.config = config
        self.logger = config.logger or logging.getLogger(__name__)
        self._setup_logging()
    def _setup_logging(self):
        """Setup logging configuration."""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(self.config.log_level.value)
    @abstractmethod
    def get_download_url(self) -> str:
        """Get the download URL for the repository."""
        pass
    @abstractmethod
    async def download_async(self) -> DownloadResult:
        """Download repository asynchronously."""
        pass
    @abstractmethod
    def download_sync(self) -> DownloadResult:
        """Download repository synchronously."""
        pass
    def validate_config(self) -> None:
        """Validate configuration before download."""
        if not self.config.url:
            raise ValueError("URL is required")
    def get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for the request."""
        headers = {
            "User-Agent": "Repo-Fetcher/1.0.0",
            "Accept": "application/vnd.github.v3+json"
        }
        if self.config.token:
            if self.config.platform == Platform.GITHUB:
                headers["Authorization"] = f"token {self.config.token}"
            elif self.config.platform == Platform.GITLAB:
                headers["Authorization"] = f"Bearer {self.config.token}"
            elif self.config.platform == Platform.NPM:
                headers["Authorization"] = f"Bearer {self.config.token}"
        return headers
    def _calculate_checksum(self, file_path: Path, algorithm: str) -> str:
        """Calculate checksum of a file."""
        import hashlib
        hash_func = getattr(hashlib, algorithm, None)
        if not hash_func:
            raise ValueError(f"Unsupported checksum algorithm: {algorithm}")
        hash_obj = hash_func()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
