"""Command-line interface for S3 Toolkit."""
import os
import sys
import logging
import argparse
from typing import Optional, List
from pathlib import Path

from .client import S3Client
from .utils import setup_logging

def create_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""
    parser = argparse.ArgumentParser(prog='s3toolkit', description='S3 Toolkit CLI')
    
    # Global arguments
    parser.add_argument('--access-key', help='AWS access key ID', default=os.getenv('AWS_ACCESS_KEY_ID'))
    parser.add_argument('--secret-key', help='AWS secret access key', default=os.getenv('AWS_SECRET_ACCESS_KEY'))
    parser.add_argument('--region', help='AWS region', default=os.getenv('AWS_DEFAULT_REGION', 'us-east-1'))
    parser.add_argument('--endpoint-url', help='S3 endpoint URL', default=os.getenv('S3_ENDPOINT_URL'))
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', required=True, help='Command to execute')
    
    # Upload command
    upload_parser = subparsers.add_parser('upload', help='Upload a file to S3')
    upload_parser.add_argument('file_path', help='Path to the local file to upload')
    upload_parser.add_argument('bucket', help='S3 bucket name')
    upload_parser.add_argument('key', help='S3 object key')
    
    # Download command
    download_parser = subparsers.add_parser('download', help='Download a file from S3')
    download_parser.add_argument('bucket', help='S3 bucket name')
    download_parser.add_argument('key', help='S3 object key')
    download_parser.add_argument('local_path', help='Local path to save the file')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List objects in an S3 bucket')
    list_parser.add_argument('bucket', help='S3 bucket name')
    list_parser.add_argument('--prefix', default='', help='Prefix to filter objects')
    list_parser.add_argument('--max-keys', type=int, default=1000, help='Maximum number of objects to return')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete an object from S3')
    delete_parser.add_argument('bucket', help='S3 bucket name')
    delete_parser.add_argument('key', help='S3 object key')
    
    return parser

def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI."""
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    
    # Configure logging
    log_level = logging.DEBUG if parsed_args.debug else logging.INFO
    setup_logging(log_level)
    
    # Initialize the S3 client
    s3 = S3Client(
        aws_access_key_id=parsed_args.access_key,
        aws_secret_access_key=parsed_args.secret_key,
        region_name=parsed_args.region,
        endpoint_url=parsed_args.endpoint_url
    )
    
    try:
        if parsed_args.command == 'upload':
            # Upload file
            print(f"Uploading {parsed_args.file_path} to s3://{parsed_args.bucket}/{parsed_args.key}")
            s3_uri = s3.upload_file(
                parsed_args.file_path,
                parsed_args.bucket,
                parsed_args.key
            )
            print(f"Successfully uploaded to {s3_uri}")
            
        elif parsed_args.command == 'download':
            # Download file
            print(f"Downloading s3://{parsed_args.bucket}/{parsed_args.key} to {parsed_args.local_path}")
            local_path = s3.download_file(
                parsed_args.bucket,
                parsed_args.key,
                parsed_args.local_path
            )
            print(f"Successfully downloaded to {local_path}")
            
        elif parsed_args.command == 'list':
            # List objects
            print(f"Objects in s3://{parsed_args.bucket}/{parsed_args.prefix}:")
            objects = s3.list_objects(
                parsed_args.bucket,
                prefix=parsed_args.prefix,
                max_keys=parsed_args.max_keys
            )
            for obj in objects:
                print(f"{obj['Key']} ({obj['Size']} bytes)")
                
        elif parsed_args.command == 'delete':
            # Delete object
            print(f"Deleting s3://{parsed_args.bucket}/{parsed_args.key}")
            success = s3.delete_object(parsed_args.bucket, parsed_args.key)
            if success:
                print("Successfully deleted object")
                
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
