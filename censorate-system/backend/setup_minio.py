"""
Setup MinIO: create bucket and configure CORS.
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.minio_client import minio_client, settings
from minio.commonconfig import ENABLED
from minio.cors import CORSRule


def setup_minio():
    """Setup MinIO bucket and CORS."""
    print(f"Setting up MinIO at {settings.MINIO_ENDPOINT}")
    print(f"Bucket: {settings.MINIO_BUCKET_NAME}")

    # Ensure bucket exists
    if not minio_client.client.bucket_exists(settings.MINIO_BUCKET_NAME):
        minio_client.client.make_bucket(settings.MINIO_BUCKET_NAME)
        print(f"Created bucket: {settings.MINIO_BUCKET_NAME}")
    else:
        print(f"Bucket already exists: {settings.MINIO_BUCKET_NAME}")

    # Configure CORS
    print("\nConfiguring CORS...")
    cors_config = [
        CORSRule(
            allowed_origins=["*"],
            allowed_methods=["GET", "POST", "PUT"],
            allowed_headers=["*"],
            expose_headers=["ETag"],
            max_age_seconds=3000,
        )
    ]

    try:
        minio_client.client.set_bucket_cors(settings.MINIO_BUCKET_NAME, cors_config)
        print("CORS configured successfully")
    except Exception as e:
        print(f"Failed to configure CORS: {e}")
        print("Continuing anyway...")

    print("\n✅ MinIO setup complete!")
    print(f"Public URL pattern: {settings.MINIO_PUBLIC_URL}/{settings.MINIO_BUCKET_NAME}/<object-name>")


if __name__ == "__main__":
    setup_minio()
