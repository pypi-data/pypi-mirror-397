"""
GitHub platform fetcher.
"""
import asyncio
import re
import shutil
import tarfile
import zipfile
from pathlib import Path
from time import time
from typing import Dict, Any, Union
import requests
try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    aiohttp = None
try:
    from tqdm.asyncio import tqdm as async_tqdm
    TQDM_ASYNC_AVAILABLE = True
except ImportError:
    TQDM_ASYNC_AVAILABLE = False
    async_tqdm = None
from tqdm import tqdm
from .base import BaseFetcher
from ..models import DownloadResult, DownloadConfig
from ..exceptions import DownloadError
from ..constants import Platform
class GitHubFetcher(BaseFetcher):
    """GitHub repository fetcher."""
    def __init__(self, config: DownloadConfig):
        if isinstance(config.dest, (str, Path)):
            super().__init__(DownloadConfig(
                url=config.url,
                dest=Path(config.dest) if isinstance(config.dest, str) else config.dest,
                commit=config.commit,
                tag=config.tag,
                branch=config.branch,
                timeout=config.timeout,
                verify_ssl=config.verify_ssl,
                proxy=config.proxy,
                archive_format=config.archive_format,
                keep_archive=config.keep_archive,
                overwrite=config.overwrite,
                show_progress=config.show_progress,
                chunk_size=config.chunk_size,
                raise_on_error=config.raise_on_error,
                pre_download_hook=config.pre_download_hook,
                post_extract_hook=config.post_extract_hook
            ))
        else:
            super().__init__(config)
        self._parse_github_url()
    def _parse_github_url(self):
        """Parse GitHub URL to extract owner and repo."""
        pattern = r'https?://(?:www\.)?github\.com/([^/]+)/([^/?#]+)'
        match = re.match(pattern, self.config.url or "")
        if match:
            self.owner = match.group(1)
            self.repo = match.group(2).replace('.git', '')
        else:
            raise ValueError("Invalid GitHub URL")
    def get_download_url(self) -> str:
        """Get GitHub archive download URL."""
        ref = self.config.commit or self.config.tag or self.config.branch or "main"
        return f"https://api.github.com/repos/{self.owner}/{self.repo}/tarball/{ref}"
    def download_sync(self) -> DownloadResult:
        """Download repository synchronously."""
        start_time = time()
        destination = Path(self.config.dest) if isinstance(self.config.dest, str) else self.config.dest
        result = DownloadResult(
            success=False,
            platform=Platform.GITHUB,
            url=self.config.url or "",
            destination=destination
        )
        try:
            if self.config.pre_download_hook:
                self.config.pre_download_hook({"config": self.config})
            download_url = self.get_download_url()
            headers = self.get_headers()
            self.logger.info(f"Downloading from GitHub: {download_url}")
            response = requests.get(
                download_url,
                headers=headers,
                stream=True,
                timeout=self.config.timeout,
                verify=self.config.verify_ssl,
                proxies=self.config.proxy
            )
            response.raise_for_status()
            archive_path = self._save_archive(response)
            result.archive_path = archive_path
            result.size_bytes = archive_path.stat().st_size
            if not self.config.keep_archive:
                extracted_path = self._extract_archive(archive_path)
                result.extracted_path = extracted_path
            if self.config.post_extract_hook:
                self.config.post_extract_hook({
                    "config": self.config,
                    "result": result
                })
            result.success = True
            result.duration_seconds = time() - start_time
            self.logger.info(f"Successfully downloaded: {result.url}")
        except Exception as e:
            result.error = str(e)
            result.duration_seconds = time() - start_time
            if self.config.raise_on_error:
                raise DownloadError(f"Failed to download from GitHub: {e}") from e
            else:
                self.logger.error(f"Download failed: {e}")
        return result
    async def download_async(self) -> DownloadResult:
        """Download repository asynchronously."""
        if not AIOHTTP_AVAILABLE or aiohttp is None:
            raise ImportError(
                "aiohttp is required for async downloads. "
                "Install with: pip install aiohttp"
            )
        start_time = time()
        destination = Path(self.config.dest) if isinstance(self.config.dest, str) else self.config.dest
        result = DownloadResult(
            success=False,
            platform=Platform.GITHUB,
            url=self.config.url or "",
            destination=destination
        )
        try:
            if self.config.pre_download_hook:
                self.config.pre_download_hook({"config": self.config})
            download_url = self.get_download_url()
            headers = self.get_headers()
            self.logger.info(f"Downloading from GitHub (async): {download_url}")
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    download_url,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout)
                ) as response:
                    response.raise_for_status()
                    archive_path = await self._save_archive_async(response)
                    result.archive_path = archive_path
                    result.size_bytes = archive_path.stat().st_size
            if not self.config.keep_archive:
                extracted_path = self._extract_archive(archive_path)
                result.extracted_path = extracted_path
            if self.config.post_extract_hook:
                self.config.post_extract_hook({
                    "config": self.config,
                    "result": result
                })
            result.success = True
            result.duration_seconds = time() - start_time
            self.logger.info(f"Successfully downloaded (async): {result.url}")
        except Exception as e:
            result.error = str(e)
            result.duration_seconds = time() - start_time
            if self.config.raise_on_error:
                raise DownloadError(f"Failed to download from GitHub: {e}") from e
            else:
                self.logger.error(f"Download failed: {e}")
        return result
    def _save_archive(self, response: requests.Response) -> Path:
        """Save downloaded archive to file."""
        dest = Path(self.config.dest) if isinstance(self.config.dest, str) else self.config.dest
        dest.mkdir(parents=True, exist_ok=True)
        ref = self.config.commit or self.config.tag or self.config.branch or "main"
        filename = f"{self.owner}_{self.repo}_{ref}.{self.config.archive_format.value}"
        filepath = dest / filename
        if filepath.exists() and not self.config.overwrite:
            raise FileExistsError(f"File already exists: {filepath}")
        total_size = int(response.headers.get('content-length', 0))
        with open(filepath, 'wb') as f:
            if self.config.show_progress and total_size > 0:
                with tqdm(
                    total=total_size,
                    unit='B',
                    unit_scale=True,
                    desc=f"Downloading {filename}"
                ) as pbar:
                    for chunk in response.iter_content(chunk_size=self.config.chunk_size):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
            else:
                for chunk in response.iter_content(chunk_size=self.config.chunk_size):
                    if chunk:
                        f.write(chunk)
        return filepath
    async def _save_archive_async(self, response) -> Path:
        """Save downloaded archive to file asynchronously."""
        dest = Path(self.config.dest) if isinstance(self.config.dest, str) else self.config.dest
        dest.mkdir(parents=True, exist_ok=True)
        ref = self.config.commit or self.config.tag or self.config.branch or "main"
        filename = f"{self.owner}_{self.repo}_{ref}.{self.config.archive_format.value}"
        filepath = dest / filename
        if filepath.exists() and not self.config.overwrite:
            raise FileExistsError(f"File already exists: {filepath}")
        total_size = int(response.headers.get('content-length', 0))
        with open(filepath, 'wb') as f:
            if self.config.show_progress and total_size > 0:
                async for chunk in response.content.iter_chunked(self.config.chunk_size):
                    f.write(chunk)
            else:
                async for chunk in response.content.iter_chunked(self.config.chunk_size):
                    f.write(chunk)
        return filepath
    def _extract_archive(self, archive_path: Path) -> Path:
        """Extract downloaded archive."""
        dest = Path(self.config.dest) if isinstance(self.config.dest, str) else self.config.dest
        extract_dir = dest / f"{self.owner}_{self.repo}"
        if extract_dir.exists():
            if self.config.overwrite:
                shutil.rmtree(extract_dir)
            else:
                raise FileExistsError(f"Directory already exists: {extract_dir}")
        extract_dir.mkdir(parents=True, exist_ok=True)
        if archive_path.suffix in ['.gz', '.bz2', '.xz'] or '.tar.' in archive_path.suffixes:
            with tarfile.open(archive_path, 'r:*') as tar:
                tar.extractall(extract_dir)
        elif archive_path.suffix == '.zip':
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
        if not self.config.keep_archive:
            archive_path.unlink()
        return extract_dir
