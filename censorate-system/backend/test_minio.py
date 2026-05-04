"""Test MinIO connection and basic operations."""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.minio_client import minio_client


def test_minio():
    """Test MinIO connection."""
    print("Testing MinIO connection...")

    try:
        # List buckets to verify connection
        buckets = minio_client.client.list_buckets()
        print(f"Successfully connected to MinIO!")
        print(f"Available buckets: {[b.name for b in buckets]}")

        # Verify our bucket exists
        bucket_names = [b.name for b in buckets]
        if minio_client.bucket_name in bucket_names:
            print(f"Bucket '{minio_client.bucket_name}' exists!")
        else:
            print(f"Bucket '{minio_client.bucket_name}' not found (should be auto-created)")

        print("\nMinIO configuration:")
        print(f"  Endpoint: {minio_client.client._base_url._url}")
        print(f"  Bucket: {minio_client.bucket_name}")

        return True

    except Exception as e:
        print(f"Error connecting to MinIO: {e}")
        print("\nPlease make sure MinIO is running locally with:")
        print("  docker run -d -p 9000:9000 -p 9001:9001 minio/minio server /data --console-address ':9001'")
        print("\nAnd check your .env file has correct MinIO configuration.")
        return False


if __name__ == "__main__":
    success = test_minio()
    sys.exit(0 if success else 1)
