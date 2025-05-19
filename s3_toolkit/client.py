"""Main S3 client for the S3 Toolkit."""
import os
import io
import logging
from typing import Union, Optional, Dict, Any, BinaryIO, List
from pathlib import Path

import boto3
import pandas as pd
from smart_open import open as smart_open

from .models import S3Location
from .exceptions import (
    S3ToolkitError,
    S3UploadError,
    S3DownloadError,
    S3ObjectNotFoundError
)
from .utils import (
    get_s3_client,
    ProgressPercentage,
    handle_s3_errors
)

logger = logging.getLogger(__name__)

class S3Client:
    """A high-level client for interacting with AWS S3."""
    
    def __init__(
        self,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        region_name: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        **kwargs
    ):
        """Initialize the S3 client.
        
        Args:
            aws_access_key_id: AWS access key ID
            aws_secret_access_key: AWS secret access key
            region_name: AWS region name
            endpoint_url: Custom endpoint URL (for S3-compatible services)
            **kwargs: Additional arguments to pass to boto3.client
        """
        self.aws_access_key_id = aws_access_key_id or os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = aws_secret_access_key or os.getenv('AWS_SECRET_ACCESS_KEY')
        self.region_name = region_name or os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        self.endpoint_url = endpoint_url or os.getenv('S3_ENDPOINT_URL')
        
        self._s3_client = None
        self._extra_args = kwargs
    
    @property
    def client(self) -> boto3.client:
        """Lazy-loaded S3 client."""
        if self._s3_client is None:
            self._s3_client = get_s3_client(
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.region_name,
                endpoint_url=self.endpoint_url,
                **self._extra_args
            )
        return self._s3_client
    
    @handle_s3_errors
    def upload_file(
        self,
        file_path: Union[str, Path, BinaryIO],
        bucket: str,
        key: str,
        extra_args: Optional[Dict[str, Any]] = None,
        show_progress: bool = True
    ) -> str:
        """Upload a file to S3.
        
        Args:
            file_path: Path to the file or file-like object
            bucket: S3 bucket name
            key: S3 object key
            extra_args: Extra arguments to pass to the S3 upload
            show_progress: Whether to show upload progress
            
        Returns:
            str: The S3 URI of the uploaded file
        """
        if isinstance(file_path, (str, Path)):
            file_path = str(file_path)
            file_size = os.path.getsize(file_path)
            mode = 'rb'
        else:
            file_size = file_path.seek(0, 2)
            file_path.seek(0)
            mode = 'rb+'
        
        callback = None
        if show_progress:
            callback = ProgressPercentage(file_size, desc=f"Uploading {key}")
        
        try:
            self.client.upload_fileobj(
                file_path,
                bucket,
                key,
                ExtraArgs=extra_args or {},
                Callback=callback
            )
            return f"s3://{bucket}/{key}"
        except Exception as e:
            raise S3UploadError(f"Failed to upload file to s3://{bucket}/{key}: {str(e)}")
        finally:
            if callback:
                callback.close()
    
    @handle_s3_errors
    def download_file(
        self,
        bucket: str,
        key: str,
        local_path: Union[str, Path],
        show_progress: bool = True
    ) -> str:
        """Download a file from S3.
        
        Args:
            bucket: S3 bucket name
            key: S3 object key
            local_path: Local path to save the file
            show_progress: Whether to show download progress
            
        Returns:
            str: Path to the downloaded file
        """
        local_path = Path(local_path)
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Get file size for progress bar
            response = self.client.head_object(Bucket=bucket, Key=key)
            file_size = response['ContentLength']
            
            callback = None
            if show_progress:
                callback = ProgressPercentage(file_size, desc=f"Downloading {key}")
            
            self.client.download_file(
                bucket,
                key,
                str(local_path),
                Callback=callback
            )
            return str(local_path.absolute())
        except Exception as e:
            raise S3DownloadError(f"Failed to download s3://{bucket}/{key}: {str(e)}")
        finally:
            if callback:
                callback.close()
    
    @handle_s3_errors
    def read_dataframe(
        self,
        bucket: str,
        key: str,
        file_format: str = None,
        **kwargs
    ) -> pd.DataFrame:
        """Read a file from S3 into a pandas DataFrame.
        
        Args:
            bucket: S3 bucket name
            key: S3 object key
            file_format: File format (csv, parquet, json, etc.)
                       If not provided, inferred from file extension
            **kwargs: Additional arguments to pass to pandas read function
            
        Returns:
            pd.DataFrame: The loaded DataFrame
        """
        if file_format is None:
            file_format = key.split('.')[-1].lower()
        
        s3_uri = f"s3://{bucket}/{key}"
        
        try:
            with smart_open(s3_uri, 'rb') as f:
                if file_format == 'csv':
                    return pd.read_csv(f, **kwargs)
                elif file_format in ('parquet', 'pq'):
                    return pd.read_parquet(f, **kwargs)
                elif file_format == 'json':
                    return pd.read_json(f, **kwargs)
                elif file_format in ('xls', 'xlsx'):
                    return pd.read_excel(f, **kwargs)
                else:
                    raise ValueError(f"Unsupported file format: {file_format}")
        except Exception as e:
            raise S3DownloadError(f"Failed to read DataFrame from {s3_uri}: {str(e)}")
    
    @handle_s3_errors
    def write_dataframe(
        self,
        df: pd.DataFrame,
        bucket: str,
        key: str,
        file_format: str = 'parquet',
        **kwargs
    ) -> str:
        """Write a pandas DataFrame to S3.
        
        Args:
            df: DataFrame to write
            bucket: S3 bucket name
            key: S3 object key
            file_format: Output file format (csv, parquet, json, etc.)
            **kwargs: Additional arguments to pass to pandas write function
            
        Returns:
            str: S3 URI of the written file
        """
        s3_uri = f"s3://{bucket}/{key}"
        
        try:
            with smart_open(s3_uri, 'wb') as f:
                if file_format == 'csv':
                    df.to_csv(f, index=False, **kwargs)
                elif file_format == 'parquet':
                    df.to_parquet(f, index=False, **kwargs)
                elif file_format == 'json':
                    df.to_json(f, orient='records', lines=True, **kwargs)
                elif file_format in ('xls', 'xlsx'):
                    with pd.ExcelWriter(f, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False, **kwargs)
                else:
                    raise ValueError(f"Unsupported file format: {file_format}")
            return s3_uri
        except Exception as e:
            raise S3UploadError(f"Failed to write DataFrame to {s3_uri}: {str(e)}")
    
    @handle_s3_errors
    def list_objects(
        self,
        bucket: str,
        prefix: str = '',
        max_keys: int = 1000
    ) -> List[Dict[str, Any]]:
        """List objects in an S3 bucket.
        
        Args:
            bucket: S3 bucket name
            prefix: Prefix to filter objects
            max_keys: Maximum number of objects to return
            
        Returns:
            List of object metadata dictionaries
        """
        try:
            response = self.client.list_objects_v2(
                Bucket=bucket,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            return response.get('Contents', [])
        except Exception as e:
            raise S3ToolkitError(f"Failed to list objects in s3://{bucket}/{prefix}: {str(e)}")
    
    @handle_s3_errors
    def delete_object(self, bucket: str, key: str) -> bool:
        """Delete an object from S3.
        
        Args:
            bucket: S3 bucket name
            key: S3 object key
            
        Returns:
            bool: True if deletion was successful
        """
        try:
            self.client.delete_object(Bucket=bucket, Key=key)
            return True
        except Exception as e:
            raise S3ToolkitError(f"Failed to delete s3://{bucket}/{key}: {str(e)}")
    
    @handle_s3_errors
    def object_exists(self, bucket: str, key: str) -> bool:
        """Check if an object exists in S3.
        
        Args:
            bucket: S3 bucket name
            key: S3 object key
            
        Returns:
            bool: True if the object exists, False otherwise
        """
        try:
            self.client.head_object(Bucket=bucket, Key=key)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise
        except Exception as e:
            raise S3ToolkitError(f"Error checking if s3://{bucket}/{key} exists: {str(e)}")
