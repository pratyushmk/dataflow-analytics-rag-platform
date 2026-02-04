import os
import s3fs

def get_s3_fs():
    endpoint_url = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
    return s3fs.S3FileSystem(
        key="test",
        secret="test",
        client_kwargs={"endpoint_url": endpoint_url},
        config_kwargs={"s3": {"addressing_style": "path"}},
    )
