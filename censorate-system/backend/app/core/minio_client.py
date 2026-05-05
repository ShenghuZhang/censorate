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
        self.skills_bucket_name = getattr(settings, 'MINIO_SKILLS_BUCKET_NAME', 'censorate-skills')
        self._ensure_buckets_exist()

    def _ensure_buckets_exist(self):
        """Create buckets if they don't exist."""
        for bucket in [self.bucket_name, self.skills_bucket_name]:
            try:
                if not self.client.bucket_exists(bucket):
                    self.client.make_bucket(bucket)
                    print(f"Created bucket: {bucket}")
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

    # ===== Skills specific methods =====

    def _generate_skill_object_name(self, skill_slug: str, version: str, file_path: str) -> str:
        """Generate unique object name for skill files."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        clean_path = file_path.replace('../', '').replace('..\\', '').lstrip('/').lstrip('\\')
        return f"skill-{skill_slug}/v{version}/{unique_id}/{clean_path}"

    def upload_skill_file(
        self,
        skill_slug: str,
        version: str,
        file_path: str,
        file_data: BinaryIO,
        content_type: Optional[str] = None,
        file_size: Optional[int] = None
    ) -> tuple[str, str]:
        """
        Upload a skill file to MinIO.

        Returns: (object_name, public_url)
        """
        object_name = self._generate_skill_object_name(skill_slug, version, file_path)

        if file_size is None:
            data = file_data.read()
            file_size = len(data)
            file_data = io.BytesIO(data)

        try:
            self.client.put_object(
                bucket_name=self.skills_bucket_name,
                object_name=object_name,
                data=file_data,
                length=file_size,
                content_type=content_type
            )

            public_url = f"{settings.MINIO_PUBLIC_URL}/{self.skills_bucket_name}/{object_name}"
            return object_name, public_url
        except S3Error as e:
            print(f"Error uploading skill file: {e}")
            raise

    def get_skill_file(self, object_name: str) -> Optional[bytes]:
        """Get skill file content from MinIO."""
        try:
            response = self.client.get_object(self.skills_bucket_name, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            print(f"Error getting skill file: {e}")
            return None

    def delete_skill_file(self, object_name: str) -> bool:
        """Delete a skill file from MinIO."""
        try:
            self.client.remove_object(self.skills_bucket_name, object_name)
            return True
        except S3Error as e:
            print(f"Error deleting skill file: {e}")
            return False

    def delete_all_skill_files(self, skill_slug: str) -> bool:
        """Delete all files for a skill from MinIO."""
        try:
            prefix = f"skill-{skill_slug}/"
            objects = self.client.list_objects(self.skills_bucket_name, prefix=prefix, recursive=True)
            for obj in objects:
                if obj.object_name:
                    self.client.remove_object(self.skills_bucket_name, obj.object_name)
            return True
        except S3Error as e:
            print(f"Error deleting skill files: {e}")
            return False


# Singleton instance
minio_client = MinioClient()
