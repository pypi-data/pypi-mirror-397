from pathlib import Path
from .base import BaseFetcher, Platform
from ..models import DownloadResult, DownloadConfig
from ..exceptions import DownloadError
import re
import requests
from time import time
from typing import Dict
class GitLabFetcher(BaseFetcher):
    """GitLab repository fetcher."""
    def __init__(self, config: DownloadConfig):
        super().__init__(config)
        self._parse_gitlab_url()
    def _parse_gitlab_url(self):
        pattern = r'https?://(?:www\.)?gitlab\.com/([^/?#]+)'
        match = re.match(pattern, self.config.url or "")
        if match:
            self.project_path = match.group(1).replace('.git', '')
        else:
            raise ValueError("Invalid GitLab URL")
    def get_download_url(self) -> str:
        ref = self.config.commit or self.config.tag or self.config.branch or "main"
        encoded_project = self.project_path.replace('/', '%2F')
        return f"https://gitlab.com/api/v4/projects/{encoded_project}/repository/archive.tar.gz?sha={ref}"
    def download_sync(self) -> DownloadResult:
        start_time = time()
        result = DownloadResult(
            success=False,
            platform=Platform.GITLAB, # pyright: ignore[reportArgumentType]
            url=self.config.url or "",
            destination=Path(self.config.dest)
        )
        try:
            download_url = self.get_download_url()
            headers = self.get_headers()
            self.logger.info(f"Downloading from GitLab: {download_url}")
            response = requests.get(
                download_url,
                headers=headers,
                stream=True,
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            )
            response.raise_for_status()
            # Save & extract logic here
            result.success = True
            result.duration_seconds = time() - start_time
        except Exception as e:
            result.error = str(e)
            result.duration_seconds = time() - start_time
            if self.config.raise_on_error:
                raise DownloadError(f"Failed to download from GitLab: {e}") from e
        return result
    async def download_async(self) -> DownloadResult:
        """Temporary async wrapper"""
        return self.download_sync()
