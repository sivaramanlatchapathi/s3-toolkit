"""Utility functions for S3 Toolkit."""
import os
import logging
from pathlib import Path
from typing import Optional, Union, BinaryIO, Dict, Any
from functools import wraps
import boto3
from botocore.exceptions import ClientError
from tqdm import tqdm

from .exceptions import (
    S3ConnectionError,
    S3ObjectNotFoundError,
    S3PermissionError,
    S3UploadError,
    S3DownloadError
)

def setup_logging(level: int = logging.INFO) -> None:
    """Configure logging for the application."""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
        ]
    )

def get_s3_client(region_name: Optional[str] = None, **kwargs) -> boto3.client:
    """Create and return a boto3 S3 client with proper configuration."""
    try:
        return boto3.client('s3', region_name=region_name, **kwargs)
    except Exception as e:
        raise S3ConnectionError(f"Failed to create S3 client: {str(e)}")

class ProgressPercentage:
    """Display upload/download progress using tqdm."""
    def __init__(self, file_size: int, desc: str = "Transferring"):
        self.pbar = tqdm(
            total=file_size,
            unit='B',
            unit_scale=True,
            desc=desc,
            leave=False
        )
        self._seen_so_far = 0

    def __call__(self, bytes_amount: int) -> None:
        self._seen_so_far += bytes_amount
        self.pbar.update(bytes_amount)

    def close(self) -> None:
        self.pbar.close()

def handle_s3_errors(func):
    """Decorator to handle common S3 errors."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code')
            if error_code == '404':
                raise S3ObjectNotFoundError("The requested object was not found") from e
            elif error_code in ('403', 'AccessDenied'):
                raise S3PermissionError("Permission denied when accessing S3") from e
            elif error_code == 'NoSuchBucket':
                raise S3ObjectNotFoundError("The specified bucket does not exist") from e
            else:
                raise S3ConnectionError(f"S3 operation failed: {str(e)}") from e
        except Exception as e:
            if isinstance(e, S3ToolkitError):
                raise
            raise S3ConnectionError(f"An unexpected error occurred: {str(e)}") from e
    return wrapper
