"""
Data models and configuration classes.
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Callable, Union
from pathlib import Path
from enum import Enum
import logging
from .constants import Platform, ArchiveFormat, LogLevel
@dataclass
class DownloadConfig:
    """Configuration for repository download."""
    platform: Platform = Platform.GITHUB
    url: Optional[str] = None
    token: Optional[str] = None
    ssh_key_path: Optional[Union[str, Path]] = None
    branch: Optional[str] = None
    tag: Optional[str] = None
    commit: Optional[str] = None
    dest: Union[str, Path] = "."
    keep_archive: bool = False
    overwrite: bool = False
    mkdirs: bool = True
    path: Optional[str] = None
    files: Optional[List[str]] = None
    exclude: Optional[List[str]] = None
    flatten: bool = False
    archive_format: ArchiveFormat = ArchiveFormat.TAR_GZ
    compression_level: int = 6
    timeout: int = 30
    retries: int = 3
    retry_delay: float = 1.0
    verify_ssl: bool = True
    proxy: Optional[Dict[str, str]] = None
    async_mode: bool = False
    chunk_size: int = 8192
    max_connections: int = 10
    show_progress: bool = True
    logger: Optional[logging.Logger] = None
    log_level: LogLevel = LogLevel.INFO
    pre_download_hook: Optional[Callable[[Dict[str, Any]], Any]] = None
    post_download_hook: Optional[Callable[[Dict[str, Any]], Any]] = None
    post_extract_hook: Optional[Callable[[Dict[str, Any]], Any]] = None
    checksum_verify: Optional[str] = None
    ignore_errors: bool = False
    raise_on_error: bool = True
    retry_on_fail: bool = True
    custom_fetcher: Optional[Callable] = None
    custom_extractor: Optional[Callable] = None
    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.url and self.platform != Platform.GIT:
            raise ValueError("URL is required for non-Git platforms")
        if self.dest:
            self.dest = Path(self.dest)
        if self.ssh_key_path:
            self.ssh_key_path = Path(self.ssh_key_path)
            if not self.ssh_key_path.exists():
                raise FileNotFoundError(f"SSH key not found: {self.ssh_key_path}")
@dataclass
class DownloadResult:
    """Result of a download operation."""
    success: bool
    platform: Platform
    url: str
    destination: Path
    archive_path: Optional[Path] = None
    extracted_path: Optional[Path] = None
    size_bytes: int = 0
    duration_seconds: float = 0.0
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
