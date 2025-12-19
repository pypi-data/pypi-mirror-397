"""
Generic Git and HTTP fetcher.
"""
import subprocess
import tempfile
import shutil
import requests
from typing import Dict, Any, Optional
from pathlib import Path
from time import time
from .base import BaseFetcher
from ..models import DownloadResult, DownloadConfig
from ..exceptions import DownloadError
from ..constants import Platform
class GenericFetcher(BaseFetcher):
    """Generic Git and HTTP fetcher."""
    def __init__(self, config: DownloadConfig):
        super().__init__(config)
    def get_download_url(self) -> str:
        """Get download URL for generic fetcher."""
        return self.config.url or ""
    def download_sync(self) -> DownloadResult:
        """Download repository using generic methods."""
        start_time = time()
        destination = Path(self.config.dest) if isinstance(self.config.dest, str) else self.config.dest
        url = self.config.url or ""
        result = DownloadResult(
            success=False,
            platform=Platform.GENERIC,
            url=url,
            destination=destination
        )
        try:
            self.logger.info(f"Downloading generic repository: {url}")
            if url and (url.startswith('git@') or url.endswith('.git')):
                result = self._clone_git_repo()
            else:
                result = self._download_direct_file()
            result.duration_seconds = time() - start_time
        except Exception as e:
            result.error = str(e)
            result.duration_seconds = time() - start_time
            if self.config.raise_on_error:
                raise DownloadError(f"Failed to download generic repository: {e}") from e
        return result
    def _clone_git_repo(self) -> DownloadResult:
        """Clone Git repository."""
        destination = Path(self.config.dest) if isinstance(self.config.dest, str) else self.config.dest
        url = self.config.url or ""
        result = DownloadResult(
            success=False,
            platform=Platform.GIT,
            url=url,
            destination=destination
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            cmd: list[str] = ['git', 'clone']
            if self.config.ssh_key_path:
                cmd.extend(['-c', f'core.sshCommand=ssh -i {self.config.ssh_key_path}'])
            ref = self.config.commit or self.config.tag or self.config.branch
            if ref:
                cmd.extend(['--branch', ref, '--single-branch'])
            cmd.extend([url, tmpdir])
            try:
                subprocess.run(cmd, check=True, capture_output=True, text=True)
                if destination.exists() and not self.config.overwrite:
                    raise FileExistsError(f"Destination exists: {destination}")
                shutil.move(tmpdir, str(destination))
                result.success = True
                result.extracted_path = destination
            except subprocess.CalledProcessError as e:
                result.error = f"Git clone failed: {e.stderr}"
        return result
    def _download_direct_file(self) -> DownloadResult:
        """Download direct file from URL."""
        destination = Path(self.config.dest) if isinstance(self.config.dest, str) else self.config.dest
        url = self.config.url or ""
        result = DownloadResult(
            success=False,
            platform=Platform.GENERIC,
            url=url,
            destination=destination
        )
        if not url:
            result.error = "URL is required for direct file download"
            return result
        response = requests.get(
            url,
            stream=True,
            timeout=self.config.timeout,
            verify=self.config.verify_ssl,
            proxies=self.config.proxy if self.config.proxy else None
        )
        response.raise_for_status()
        filename = Path(url).name or "downloaded_file"
        filepath = destination / filename
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=self.config.chunk_size):
                if chunk:
                    f.write(chunk)
        result.success = True
        result.archive_path = filepath
        result.size_bytes = filepath.stat().st_size
        return result
    async def download_async(self) -> DownloadResult:
        """Download repository asynchronously."""
        return self.download_sync()
