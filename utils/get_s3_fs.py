import s3fs

def get_s3_fs():
    return s3fs.S3FileSystem(
        key="test",
        secret="test",
        client_kwargs={"endpoint_url": "http://localhost:4566"},
        config_kwargs={"s3": {"addressing_style": "path"}},
    )
