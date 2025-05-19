"""Data models for S3 Toolkit."""
from typing import Optional
from pydantic import BaseModel, validator, HttpUrl

class S3Location(BaseModel):
    """Represents an S3 location with bucket and key."""
    bucket: str
    key: str
    region: Optional[str] = None
    endpoint_url: Optional[HttpUrl] = None

    @validator('bucket')
    def validate_bucket_name(cls, v):
        if not v:
            raise ValueError("Bucket name cannot be empty")
        if ' ' in v:
            raise ValueError("Bucket name cannot contain spaces")
        return v

    @property
    def s3_uri(self) -> str:
        """Return the S3 URI for this location."""
        return f"s3://{self.bucket}/{self.key}"

    @classmethod
    def from_uri(cls, s3_uri: str) -> 'S3Location':
        """Create an S3Location from an S3 URI."""
        if not s3_uri.startswith('s3://'):
            raise ValueError("Invalid S3 URI. Must start with 's3://'")
        
        parts = s3_uri[5:].split('/', 1)
        if len(parts) == 1:
            return cls(bucket=parts[0], key="")
        return cls(bucket=parts[0], key=parts[1] if len(parts) > 1 else "")
