"""
Main Repo-Fetcher class.
"""
import asyncio
import logging
from typing import Optional, Dict, Any, Union
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from .models import DownloadConfig, DownloadResult
from .exceptions import (
    RepoFetcherError,
    DownloadError,
    PlatformNotSupportedError,
    InvalidConfigError
)
from .constants import Platform
from .platforms.github import GitHubFetcher
from .platforms.gitlab import GitLabFetcher
from .platforms.generic import GenericFetcher
class RepoFetcher:
    """
    Main class for downloading repositories from various platforms.
    Example:
        >>> from repo_fetcher import RepoFetcher, DownloadConfig
        >>> config = DownloadConfig(
        ...     url="https://github.com/owner/repo",
        ...     dest="./downloads",
        ...     branch="main"
        ... )
        >>> fetcher = RepoFetcher()
        >>> result = fetcher.download(config)
    """
    def __init__(self, default_config: Optional[Dict[str, Any]] = None):
        """
        Initialize RepoFetcher.
        Args:
            default_config: Default configuration to use for all downloads
        """
        self.default_config = default_config or {}
        self.logger = logging.getLogger(__name__)
        self._fetchers = {
            Platform.GITHUB: GitHubFetcher,
            Platform.GITLAB: GitLabFetcher,
            Platform.GIT: GenericFetcher,
            Platform.GENERIC: GenericFetcher,
            Platform.NPM: GenericFetcher,
            Platform.BITBUCKET: GenericFetcher,
        }
    def _get_fetcher_class(self, platform: Platform):
        """Get fetcher class for platform."""
        fetcher_class = self._fetchers.get(platform)
        if not fetcher_class:
            raise PlatformNotSupportedError(f"Platform not supported: {platform}")
        return fetcher_class
    def _merge_config(self, config: Union[Dict[str, Any], DownloadConfig]) -> DownloadConfig:
        """Merge user config with defaults."""
        if isinstance(config, dict):
            merged = {**self.default_config, **config}
            if 'platform' in merged and isinstance(merged['platform'], str):
                merged['platform'] = Platform(merged['platform'])
            config = DownloadConfig(**merged)
        elif isinstance(config, DownloadConfig):
            for key, value in self.default_config.items():
                if getattr(config, key, None) is None:
                    setattr(config, key, value)
        else:
            raise InvalidConfigError("Config must be dict or DownloadConfig")
        return config
    def download(self, config: Union[Dict[str, Any], DownloadConfig]) -> DownloadResult:
        """
        Download repository synchronously.
        Args:
            config: Download configuration
        Returns:
            DownloadResult object
        """
        config = self._merge_config(config)
        fetcher_class = self._get_fetcher_class(config.platform)
        fetcher = fetcher_class(config)
        if config.async_mode:
            return asyncio.run(fetcher.download_async())
        else:
            return fetcher.download_sync()
    async def download_async(self, config: Union[Dict[str, Any], DownloadConfig]) -> DownloadResult:
        """
        Download repository asynchronously.
        Args:
            config: Download configuration
        Returns:
            DownloadResult object
        """
        config = self._merge_config(config)
        fetcher_class = self._get_fetcher_class(config.platform)
        fetcher = fetcher_class(config)
        return await fetcher.download_async()
    def download_batch(
        self,
        configs: list,
        max_workers: int = 5,
        show_progress: bool = True
    ) -> list:
        """
        Download multiple repositories in parallel.
        Args:
            configs: List of download configurations
            max_workers: Maximum number of parallel downloads
            show_progress: Show progress bar for batch
        Returns:
            List of DownloadResult objects
        """
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for config in configs:
                future = executor.submit(self.download, config)
                futures.append(future)
            if show_progress:
                from tqdm import tqdm
                for future in tqdm(futures, desc="Downloading batch"):
                    results.append(future.result())
            else:
                for future in futures:
                    results.append(future.result())
        return results
    async def download_batch_async(
        self,
        configs: list,
        max_concurrent: int = 5,
        show_progress: bool = True
    ) -> list:
        """
        Download multiple repositories asynchronously.
        Args:
            configs: List of download configurations
            max_concurrent: Maximum number of concurrent downloads
            show_progress: Show progress bar for batch
        Returns:
            List of DownloadResult objects
        """
        import asyncio
        from tqdm.asyncio import tqdm_asyncio
        semaphore = asyncio.Semaphore(max_concurrent)
        async def download_with_semaphore(config):
            async with semaphore:
                return await self.download_async(config)
        tasks = [download_with_semaphore(config) for config in configs]
        if show_progress:
            results = []
            for task in tqdm_asyncio.as_completed(tasks, desc="Downloading batch"):
                result = await task
                results.append(result)
            return results
        else:
            return await asyncio.gather(*tasks)
    def register_fetcher(self, platform: Platform, fetcher_class):
        """
        Register a custom fetcher for a platform.
        Args:
            platform: Platform identifier
            fetcher_class: Fetcher class (must inherit from BaseFetcher)
        """
        from .platforms.base import BaseFetcher
        if not issubclass(fetcher_class, BaseFetcher):
            raise TypeError("Fetcher must inherit from BaseFetcher")
        self._fetchers[platform] = fetcher_class
        self.logger.info(f"Registered custom fetcher for platform: {platform}")
