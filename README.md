# S3 Toolkit

A robust Python package for AWS S3 data integration with support for various file formats and advanced features.

## Features

- High-level interface for common S3 operations
- Support for various file formats (CSV, Parquet, JSON, Excel)
- Progress tracking for large file transfers
- Automatic retries and error handling
- Type hints and documentation
- Support for S3-compatible storage services

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from s3_toolkit import S3Client

# Initialize the client
s3 = S3Client(
    aws_access_key_id='your-access-key',
    aws_secret_access_key='your-secret-key',
    region_name='us-east-1'
)

# Upload a file
s3.upload_file('local/file.csv', 'my-bucket', 'path/to/remote/file.csv')

# Download a file
s3.download_file('my-bucket', 'path/to/remote/file.csv', 'local/downloaded.csv')

# Read a CSV file into a pandas DataFrame
df = s3.read_dataframe('my-bucket', 'path/to/data.csv', file_format='csv')

# Write a DataFrame to S3 as Parquet
s3.write_dataframe(df, 'my-bucket', 'path/to/output.parquet', file_format='parquet')
```

### Environment Variables

You can also configure the client using environment variables:

```bash
export AWS_ACCESS_KEY_ID='your-access-key'
export AWS_SECRET_ACCESS_KEY='your-secret-key'
export AWS_DEFAULT_REGION='us-east-1'
# Optional: For S3-compatible services
export S3_ENDPOINT_URL='https://s3.example.com'
```

Then initialize the client without parameters:

```python
from s3_toolkit import S3Client
s3 = S3Client()
```

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
