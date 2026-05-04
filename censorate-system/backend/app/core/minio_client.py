"""MinIO client for object storage."""
from minio import Minio
from minio.error import S3Error
from typing import Optional, BinaryIO
from app.core.config import Settings
import io
import uuid


settings = Settings.get()


class MinioClient:
    """MinIO client wrapper for Censorate attachments."""

    def __init__(self):
        """Initialize MinIO client."""
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """Create bucket if it doesn't exist."""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                print(f"Created bucket: {self.bucket_name}")
        except S3Error as e:
            print(f"Error ensuring bucket exists: {e}")

    def _generate_object_name(self, requirement_id: str, original_filename: str) -> str:
        """Generate unique object name."""
        ext = original_filename[original_filename.rfind('.'):] if '.' in original_filename else ''
        unique_id = str(uuid.uuid4())[:8]
        return f"requirement-{requirement_id}/{unique_id}{ext}"

    def upload_file(
        self,
        requirement_id: str,
        filename: str,
        file_data: BinaryIO,
        content_type: Optional[str] = None,
        file_size: Optional[int] = None
    ) -> tuple[str, str]:
        """
        Upload file to MinIO.

        Returns: (object_name, public_url)
        """
        object_name = self._generate_object_name(requirement_id, filename)

        # If file_size is not provided, read all data
        if file_size is None:
            data = file_data.read()
            file_size = len(data)
            file_data = io.BytesIO(data)

        try:
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=file_data,
                length=file_size,
                content_type=content_type
            )

            public_url = f"{settings.MINIO_PUBLIC_URL}/{self.bucket_name}/{object_name}"
            return object_name, public_url

        except S3Error as e:
            print(f"Error uploading file: {e}")
            raise

    def delete_file(self, object_name: str) -> bool:
        """Delete file from MinIO."""
        try:
            self.client.remove_object(self.bucket_name, object_name)
            return True
        except S3Error as e:
            print(f"Error deleting file: {e}")
            return False

    def get_file_url(self, object_name: str) -> str:
        """Get public URL for a file."""
        return f"{settings.MINIO_PUBLIC_URL}/{self.bucket_name}/{object_name}"


# Singleton instance
minio_client = MinioClient()
