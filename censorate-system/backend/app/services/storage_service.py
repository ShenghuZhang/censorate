"""Storage Service - handles file storage operations for skills."""

import os
import hashlib
import re
import zipfile
from io import BytesIO
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
from app.core.config import Settings
from app.core.minio_client import minio_client


settings = Settings.get()
STORAGE_BACKEND = getattr(settings, 'STORAGE_BACKEND', 'local')


class StorageService:
    """Service for managing skill file storage - supports both local and MinIO backends."""

    def __init__(self):
        """Initialize storage service."""
        from app.core.minio_client import minio_client
        self.settings = Settings.get()
        self.base_dir = Path(self.settings.SKILL_STORAGE_DIR)
        self._ensure_base_dir()
        self.storage_backend = getattr(self.settings, 'STORAGE_BACKEND', 'local')
        self.minio = minio_client
        self.bucket = getattr(self.settings, 'MINIO_SKILLS_BUCKET_NAME', 'censorate-skills')
        print(f"📦 Storage backend: {self.storage_backend}")

    def _ensure_base_dir(self) -> None:
        """Ensure base storage directory exists."""
        self.base_dir.mkdir(parents=True, exist_ok=True)

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
        """Save skill files to storage.

        Args:
            skill_slug: Skill slug
            version: Version string
            files: List of {path, content} dicts

        Returns:
            List of {path, storage_path, sha256_hash, file_size, content_type} dicts
        """
        if self.storage_backend == 'minio':
            return self._save_to_minio(skill_slug, version, files)
        else:
            return self._save_to_local(skill_slug, version, files)

    def _save_to_minio(
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

            # Clean path
            clean_path = Path(path).as_posix()

            # Determine content type
            content_type = self._get_content_type(clean_path)

            # Upload to MinIO
            object_name, _ = minio_client.upload_skill_file(
                skill_slug=skill_slug,
                version=version,
                file_path=clean_path,
                file_data=BytesIO(content),
                content_type=content_type,
                file_size=len(content)
            )

            # Compute hash
            sha256_hash = self.compute_sha256(content)

            # Store with minio:// prefix
            saved_files.append({
                "path": clean_path,
                "storage_path": f"minio://{object_name}",
                "sha256_hash": sha256_hash,
                "file_size": len(content),
                "content_type": content_type
            })

        print(f"💾 Saved {len(saved_files)} files to MinIO for skill {skill_slug}")
        return saved_files

    def _save_to_local(
        self,
        skill_slug: str,
        version: str,
        files: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Save skill files to local filesystem."""
        # Create version directory
        version_dir = self.base_dir / skill_slug / f"v{version}"
        version_dir.mkdir(parents=True, exist_ok=True)

        saved_files = []

        for file in files:
            path = file.get("path", "")
            content = file.get("content", b"")
            clean_path = Path(path).as_posix()

            # Create safe file path
            file_path = version_dir / Path(clean_path).name
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            file_path.write_bytes(content)

            # Compute hash
            sha256_hash = self.compute_sha256(content)

            # Store relative path
            storage_path = str(file_path.relative_to(self.base_dir.parent))
            saved_files.append({
                "path": clean_path,
                "storage_path": storage_path,
                "sha256_hash": sha256_hash,
                "file_size": len(content),
                "content_type": self._get_content_type(clean_path)
            })

        print(f"💾 Saved {len(saved_files)} files to local storage for skill {skill_slug}")
        return saved_files

    def get_file_path(self, storage_path: str) -> Path:
        """Get full path to a stored file (local only)."""
        return Path(self.base_dir.parent) / storage_path

    def read_file_content(self, storage_path: str) -> Optional[bytes]:
        """Read content of a stored file."""
        # Check if it's a MinIO path
        if storage_path.startswith("minio://"):
            object_name = storage_path[len("minio://"):]
            return minio_client.get_skill_file(object_name)

        # Fall back to local storage
        try:
            # Normalize path: replace backslashes
            normalized_path = storage_path.replace("\\", "/")

            file_path = self.get_file_path(normalized_path)
            if file_path.exists():
                with open(file_path, "rb") as f:
                    return f.read()
            else:
                print(f"File not found at: {file_path}")
        except Exception as e:
            print(f"Error reading file: {e}")
        return None

    def delete_file(self, storage_path: str) -> bool:
        """Delete a file from storage."""
        if storage_path.startswith("minio://"):
            object_name = storage_path[len("minio://"):]
            return minio_client.delete_skill_file(object_name)

        try:
            file_path = self.get_file_path(storage_path)
            if file_path.exists():
                file_path.unlink()
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False

    def delete_skill_files(self, skill_slug: str) -> None:
        """Delete all files for a skill."""
        if self.storage_backend == 'minio':
            minio_client.delete_all_skill_files(skill_slug)
        else:
            import shutil
            skill_dir = self.base_dir / skill_slug
            if skill_dir.exists():
                shutil.rmtree(skill_dir)

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
            ".js": "text/javascript",
            ".ts": "text/typescript",
            ".tsx": "text/typescript",
            ".jsx": "text/javascript",
            ".sh": "text/x-shellscript",
            ".bash": "text/x-shellscript",
            ".zsh": "text/x-shellscript",
            ".css": "text/css",
            ".html": "text/html",
            ".xml": "text/xml",
            ".csv": "text/csv",
            ".ini": "text/plain",
            ".cfg": "text/plain",
            ".conf": "text/plain",
            ".toml": "text/toml",
            ".env": "text/plain",
            ".env.example": "text/plain",
            ".gitignore": "text/plain",
            ".dockerignore": "text/plain",
            ".go": "text/x-go",
            ".rs": "text/rust",
            ".java": "text/x-java",
            ".kt": "text/x-kotlin",
            ".kts": "text/x-kotlin",
            ".scala": "text/x-scala",
            ".php": "text/x-php",
            ".rb": "text/x-ruby",
            ".cpp": "text/x-c++",
            ".c": "text/x-c",
            ".h": "text/x-c",
            ".hpp": "text/x-c++",
            ".cs": "text/x-csharp",
            ".fs": "text/x-fsharp",
            ".fsx": "text/x-fsharp",
            ".sql": "text/x-sql",
            ".graphql": "text/graphql",
            ".gql": "text/graphql",
            ".prisma": "text/plain",
            ".lua": "text/x-lua",
            ".pl": "text/x-perl",
            ".pm": "text/x-perl",
            ".r": "text/x-r",
            ".dart": "text/x-dart",
            ".swift": "text/x-swift",
            ".m": "text/x-objective-c",
            ".mm": "text/x-objective-c++",
            ".asm": "text/x-assembly",
            ".s": "text/x-assembly",
            ".wasm": "application/wasm",
            ".wat": "text/webassembly",
            ".wast": "text/webassembly",
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
