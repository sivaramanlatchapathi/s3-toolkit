"""
Basic usage example for S3 Toolkit.
"""
import os
import pandas as pd
from s3_toolkit import S3Client

def main():
    # Initialize the S3 client
    # Credentials can be provided directly or via environment variables
    s3 = S3Client(
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1'),
        endpoint_url=os.getenv('S3_ENDPOINT_URL')
    )
    
    # Example bucket and key
    bucket = 'your-bucket-name'
    key = 'example/data.csv'
    
    # Initialize variables for cleanup
    local_file = 'example_data.csv'
    downloaded_file = 'downloaded_data.csv'
    
    try:
        # Example 1: Upload a file
        print("Uploading file...")
        
        # Create a sample DataFrame and save it as CSV
        df = pd.DataFrame({
            'id': range(1, 6),
            'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
            'score': [85, 92, 78, 88, 95]
        })
        df.to_csv(local_file, index=False)
        
        # Upload the file
        s3_uri = s3.upload_file(local_file, bucket, key)
        print(f"File uploaded to: {s3_uri}")
        
        # Example 2: Download the file
        print("\nDownloading file...")
        s3.download_file(bucket, key, downloaded_file)
        print(f"File downloaded to: {downloaded_file}")
        
        # Example 3: Read directly into a DataFrame
        print("\nReading file directly into DataFrame...")
        df_read = s3.read_dataframe(bucket, key, file_format='csv')
        print("\nDataFrame contents:")
        print(df_read)
        
        # Example 4: Write DataFrame to S3 as Parquet
        print("\nWriting DataFrame to S3 as Parquet...")
        parquet_key = 'example/data.parquet'
        s3_uri = s3.write_dataframe(df, bucket, parquet_key, file_format='parquet')
        print(f"DataFrame written to: {s3_uri}")
        
        # Example 5: List objects in the bucket
        print("\nListing objects in bucket...")
        objects = s3.list_objects(bucket, prefix='example/')
        print("\nObjects in bucket:")
        for obj in objects:
            print(f"- {obj['Key']} ({obj['Size']} bytes)")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        # Cleanup
        for f in [local_file, downloaded_file]:
            if os.path.exists(f):
                os.remove(f)

if __name__ == "__main__":
    main()
