import os

import boto3
from botocore.config import Config


BUCKET = 'all-the-ponies-assets'

__bucket_exists = False


def get_s3_client(max_workers: int | None = 10):
    client = boto3.client(
        service_name = "s3",
        endpoint_url = os.environ.get('S3_ENDPOINT'),
        aws_access_key_id = os.environ.get('S3_ACCESS_KEY'),
        aws_secret_access_key = os.environ.get('S3_SECRET_KEY'),
        region_name = os.environ.get('S3_REGION', 'auto'),
        config = Config(
            max_pool_connections = max_workers,
        )
    )

    global __bucket_exists
    if not __bucket_exists:
        try:
            client.head_bucket(Bucket = BUCKET)
        except:
            client.create_bucket(Bucket = BUCKET)
        
        __bucket_exists = True
    
    return client
