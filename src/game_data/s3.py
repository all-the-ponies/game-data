import os

import boto3
from botocore.config import Config


DEFAULT_BUCKET = 'all-the-ponies-assets'

__bucket_exists: dict[str, bool] = {}


def get_s3_client(
    bucket: str = DEFAULT_BUCKET,
    max_workers: int | None = 10,
):
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
    if bucket and not __bucket_exists.get(bucket):
        try:
            client.head_bucket(Bucket = bucket)
        except:
            client.create_bucket(Bucket = bucket)
        
        __bucket_exists[bucket] = True
    
    return client

def get_secret_s3_client(
    bucket: str | None = None,
    max_workers: int | None = 10,
):
    client = boto3.client(
        service_name = "s3",
        endpoint_url = os.environ.get('PRIVATE_S3_ENDPOINT'),
        aws_access_key_id = os.environ.get('PRIVATE_S3_ACCESS_KEY'),
        aws_secret_access_key = os.environ.get('PRIVATE_S3_SECRET_KEY'),
        region_name = os.environ.get('PRIVATE_S3_REGION'),
        config = Config(
            max_pool_connections = max_workers,
        )
    )

    global __bucket_exists
    if bucket and not __bucket_exists.get(bucket):
        try:
            client.head_bucket(Bucket = bucket)
        except:
            client.create_bucket(Bucket = bucket)
        
        __bucket_exists[bucket] = True
    
    return client
