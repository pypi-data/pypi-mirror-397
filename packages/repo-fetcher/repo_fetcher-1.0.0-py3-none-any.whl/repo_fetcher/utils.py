"""
Utility functions for Repo-Fetcher.
"""
import asyncio
import hashlib
import re
import shutil
import tempfile
import time
from functools import wraps
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """
    Decorator to retry a function on failure.
    Args:
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception: Optional[Exception] = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        time.sleep(delay * (2**attempt))
            if last_exception is not None:
                raise last_exception
            else:
                raise RuntimeError("Retry failed but no exception was caught")
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception: Optional[Exception] = None
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        await asyncio.sleep(delay * (2**attempt))
            if last_exception is not None:
                raise last_exception
            else:
                raise RuntimeError("Retry failed but no exception was caught")
        return async_wrapper if asyncio.iscoroutinefunction(func) else wrapper
    return decorator
def validate_url(url: str) -> bool:
    """
    Validate URL format.
    Args:
        url: URL to validate
    Returns:
        True if URL is valid
    """
    pattern = re.compile(
        r"^(https?://|git@|ssh://)"
        r"([a-zA-Z0-9.-]+)"
        r"(\.[a-zA-Z]{2,})?"
        r"(:[0-9]+)?"
        r"(/.*)?$"
    )
    return bool(pattern.match(url))
def calculate_file_hash(file_path: Union[str, Path], algorithm: str = "sha256") -> str:
    """
    Calculate hash of a file.
    Args:
        file_path: Path to file
        algorithm: Hash algorithm (md5, sha1, sha256)
    Returns:
        Hex digest of file hash
    """
    file_path = Path(file_path)
    hash_func = getattr(hashlib, algorithm, None)
    if not hash_func:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")
    hash_obj = hash_func()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()
def safe_delete(path: Union[str, Path]) -> bool:
    """
    Safely delete a file or directory.
    Args:
        path: Path to delete
    Returns:
        True if deletion was successful
    """
    try:
        path = Path(path)
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            shutil.rmtree(path)
        return True
    except Exception:
        return False
def create_temp_dir(prefix: str = "repo_fetcher_") -> Path:
    """
    Create a temporary directory.
    Args:
        prefix: Directory name prefix
    Returns:
        Path to created directory
    """
    temp_dir = tempfile.mkdtemp(prefix=prefix)
    return Path(temp_dir)
def filter_files(
    directory: Path,
    include_patterns: Optional[List[str]] = None,
    exclude_patterns: Optional[List[str]] = None,
) -> List[Path]:
    """
    Filter files based on patterns.
    Args:
        directory: Directory to search
        include_patterns: Patterns to include (glob patterns)
        exclude_patterns: Patterns to exclude (glob patterns)
    Returns:
        List of filtered file paths
    """
    import fnmatch
    files = []
    for file_path in directory.rglob("*"):
        if file_path.is_file():
            relative_path = file_path.relative_to(directory)
            include = True
            if include_patterns:
                include = any(
                    fnmatch.fnmatch(str(relative_path), pattern)
                    for pattern in include_patterns
                )
            if exclude_patterns and include:
                include = not any(
                    fnmatch.fnmatch(str(relative_path), pattern)
                    for pattern in exclude_patterns
                )
            if include:
                files.append(file_path)
    return files
def format_size(size_bytes: int) -> str:
    """
    Format file size in human readable format.
    Args:
        size_bytes: Size in bytes
    Returns:
        Formatted size string
    """
    size_in_units = float(size_bytes)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_in_units < 1024.0:
            return f"{size_in_units:.2f} {unit}"
        size_in_units /= 1024.0
    return f"{size_in_units:.2f} PB"
