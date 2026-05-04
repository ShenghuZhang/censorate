"""
Test MinIO connection and provide fallback option.
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings


def test_minio():
    """Test MinIO connection."""
    print("Testing MinIO connection...")
    print(f"Endpoint: {settings.MINIO_ENDPOINT}")
    print(f"Bucket: {settings.MINIO_BUCKET_NAME}")

    try:
        from app.core.minio_client import minio_client

        # Check if bucket exists
        if minio_client.client.bucket_exists(settings.MINIO_BUCKET_NAME):
            print("✅ MinIO bucket exists!")
            return True
        else:
            print("⚠️ MinIO bucket does not exist, attempting to create...")
            minio_client.client.make_bucket(settings.MINIO_BUCKET_NAME)
            print("✅ MinIO bucket created successfully!")
            return True

    except Exception as e:
        print(f"❌ MinIO connection failed: {e}")
        print("\nFallback: Would you like to use local file storage instead?")
        print("If MinIO is not running, you can start it with:")
        print("  docker run -d -p 9000:9000 -p 9001:9001 --name censorate-minio minio/minio server /data --console-address ':9001'")
        return False


if __name__ == "__main__":
    success = test_minio()
    sys.exit(0 if success else 1)
