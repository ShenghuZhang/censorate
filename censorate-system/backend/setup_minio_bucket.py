"""Setup MinIO bucket with public read access."""
from minio import Minio
from app.core.config import Settings


settings = Settings.get()


def setup_bucket():
    """Setup bucket with public read policy."""
    client = Minio(
        settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_SECURE
    )

    bucket_name = settings.MINIO_BUCKET_NAME

    # Create bucket if not exists
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)
        print(f"Created bucket: {bucket_name}")

    # Set public read policy
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"AWS": "*"},
                "Action": ["s3:GetObject"],
                "Resource": [f"arn:aws:s3:::{bucket_name}/*"]
            }
        ]
    }

    import json
    client.set_bucket_policy(bucket_name, json.dumps(policy))
    print(f"Set public read policy for bucket: {bucket_name}")


if __name__ == "__main__":
    setup_bucket()
