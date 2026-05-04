"""
Simple MinIO client fallback that stores files locally.
Used for debugging when MinIO is not available.
"""
import os
import uuid
from pathlib import Path
from app.core.config import Settings


settings = Settings.get()


class SimpleMinioClient:
    """Fallback implementation - stores files locally."""

    def __init__(self):
        self.upload_dir = Path("uploads/attachments")
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.bucket_name = "local-storage"
        print(f"📁 Using local file storage at: {self.upload_dir}")

    def _ensure_bucket_exists(self):
        pass

    def _generate_object_name(self, requirement_id: str, original_filename: str) -> str:
        """Generate unique object name."""
        ext = original_filename[original_filename.rfind('.'):] if '.' in original_filename else ''
        unique_id = str(uuid.uuid4())[:8]
        return f"requirement-{requirement_id}/{unique_id}{ext}"

    def upload_file(
        self,
        requirement_id: str,
        filename: str,
        file_data,
        content_type: str = None,
        file_size: int = None
    ) -> tuple[str, str]:
        """Upload file to local storage."""
        object_name = self._generate_object_name(requirement_id, filename)

        # Create directories
        file_path = self.upload_dir / object_name.replace('/', os.sep)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        if hasattr(file_data, 'read'):
            content = file_data.read()
        else:
            content = file_data

        with open(file_path, 'wb') as f:
            f.write(content)

        # Generate URL - use the storage filename (not full path)
        storage_filename = object_name.split('/')[-1]
        backend_host = getattr(settings, 'BACKEND_HOST', 'http://localhost:8216')
        public_url = f"{backend_host}{settings.API_PREFIX}/requirements/{requirement_id}/attachments/file/{storage_filename}"

        return object_name, public_url

    def delete_file(self, object_name: str) -> bool:
        """Delete file from local storage."""
        try:
            file_path = self.upload_dir / object_name.replace('/', os.sep)
            if file_path.exists():
                file_path.unlink()
            return True
        except:
            return False

    def get_file_url(self, object_name: str) -> str:
        """Get URL - not used in fallback mode."""
        return ""


# Singleton instance
minio_client = SimpleMinioClient()
