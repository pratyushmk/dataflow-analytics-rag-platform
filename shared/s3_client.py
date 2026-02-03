import boto3
import os

def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url="http://localhost:4566",
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )