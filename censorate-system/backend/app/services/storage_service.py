"""Storage Service - handles file storage operations for skills."""

import os
import hashlib
import re
import zipfile
from io import BytesIO
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
from app.core.config import Settings


class StorageService:
    """Service for managing skill file storage using MinIO."""

    def __init__(self):
        """Initialize storage service."""
        from app.core.minio_client import minio_client
        self.settings = Settings.get()
        self.minio = minio_client
        self.bucket = self.settings.MINIO_SKILLS_BUCKET_NAME

    def compute_sha256(self, content: bytes) -> str:
        """Compute SHA256 hash of content."""
        return hashlib.sha256(content).hexdigest()

    def validate_files(
        self,
        files: List[Dict[str, Any]]
    ) -> Tuple[bool, List[str]]:
        """Validate uploaded files."""
        errors = []
        total_size = 0

        # Check if SKILL.md is present
        has_skill_md = any(
            f.get("path", "").lower() == "skill.md"
            for f in files
        )
        if not has_skill_md:
            errors.append("Missing required SKILL.md file")

        for file in files:
            path = file.get("path", "")
            content = file.get("content", b"")

            if not path:
                errors.append("File path cannot be empty")
                continue

            if ".." in path or path.startswith("/") or path.startswith("\\"):
                errors.append(f"Invalid file path: {path}")
                continue

            ext = Path(path).suffix.lower()
            if ext not in self.settings.ALLOWED_EXTENSIONS:
                errors.append(f"Disallowed file type: {path}")
                continue

            file_size = len(content)
            if file_size > self.settings.MAX_FILE_SIZE:
                errors.append(
                    f"File too large: {path} ({file_size} bytes > {self.settings.MAX_FILE_SIZE} bytes)"
                )
                continue

            total_size += file_size

        if total_size > self.settings.MAX_TOTAL_SIZE:
            errors.append(
                f"Total file size too large: {total_size} bytes > {self.settings.MAX_TOTAL_SIZE} bytes"
            )

        return len(errors) == 0, errors

    def save_skill_files(
        self,
        skill_slug: str,
        version: str,
        files: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Save skill files to MinIO."""
        saved_files = []

        for file in files:
            path = file.get("path", "")
            content = file.get("content", b"")
            clean_path = Path(path).as_posix()
            
            # Object name: {skill_slug}/v{version}/{path}
            object_name = f"{skill_slug}/v{version}/{clean_path}"

            # Upload to MinIO
            self.minio.put_object(
                bucket_name=self.bucket,
                object_name=object_name,
                data=BytesIO(content),
                length=len(content),
                content_type=self._get_content_type(clean_path)
            )

            sha256_hash = self.compute_sha256(content)

            saved_files.append({
                "path": clean_path,
                "storage_path": object_name,
                "sha256_hash": sha256_hash,
                "file_size": len(content),
                "content_type": self._get_content_type(clean_path)
            })

        return saved_files

    def read_file_content(self, storage_path: str) -> Optional[bytes]:
        """Read content of a stored file from MinIO."""
        # Normalize path: replace backslashes and remove 'skills/' prefix if it exists
        normalized_path = storage_path.replace("\\", "/")
        if normalized_path.startswith("skills/"):
            normalized_path = normalized_path[len("skills/"):]
            
        try:
            response = self.minio.get_object(self.bucket, normalized_path)
            content = response.read()
            response.close()
            response.release_conn()
            return content
        except Exception as e:
            print(f"Error reading from MinIO ({normalized_path}): {e}")
            return None

    def delete_skill_files(self, skill_slug: str) -> None:
        """Delete all files for a skill from MinIO."""
        try:
            objects = self.minio.list_objects(self.bucket, prefix=f"{skill_slug}/", recursive=True)
            for obj in objects:
                self.minio.delete_file(obj.object_name, bucket_name=self.bucket)
        except Exception as e:
            print(f"Error deleting skill files from MinIO: {e}")

    def extract_zip(self, zip_content: bytes) -> List[Dict[str, Any]]:
        """Extract files from a ZIP archive."""
        files = []
        with zipfile.ZipFile(BytesIO(zip_content), 'r') as zf:
            for member in zf.infolist():
                if member.is_dir() or '/__MACOSX/' in member.filename or member.filename.startswith('__MACOSX/'):
                    continue
                if '.DS_Store' in member.filename:
                    continue

                path = member.filename
                content = zf.read(member)
                files.append({
                    "path": path,
                    "content": content,
                    "filename": Path(path).name
                })
        return files

    def _get_content_type(self, path: str) -> str:
        """Get MIME content type for a file path."""
        ext = Path(path).suffix.lower()
        content_types = {
            ".md": "text/markdown",
            ".json": "application/json",
            ".yaml": "application/x-yaml",
            ".yml": "application/x-yaml",
            ".txt": "text/plain",
            ".py": "text/x-python",
        }
        return content_types.get(ext, "application/octet-stream")


# Singleton instance
_storage_service = None


def get_storage_service() -> StorageService:
    """Get singleton storage service instance."""
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service
