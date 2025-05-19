"""Custom exceptions for the S3 Toolkit."""

class S3ToolkitError(Exception):
    """Base exception for all S3 Toolkit errors."""
    pass

class S3ConnectionError(S3ToolkitError):
    """Raised when there's an error connecting to S3."""
    pass

class S3ObjectNotFoundError(S3ToolkitError):
    """Raised when the specified S3 object is not found."""
    pass

class S3PermissionError(S3ToolkitError):
    """Raised when there are permission issues with S3."""
    pass

class S3UploadError(S3ToolkitError):
    """Raised when there's an error uploading to S3."""
    pass

class S3DownloadError(S3ToolkitError):
    """Raised when there's an error downloading from S3."""
    pass
