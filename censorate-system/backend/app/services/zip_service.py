"""ZIP Service - creates deterministic ZIP files for skill downloads."""

import zipfile
import io
import time
from datetime import datetime
from typing import List, Dict, Any


class ZipService:
    """Service for creating ZIP files for skills."""

    # Fixed timestamp for deterministic ZIP (2020-01-01 00:00:00 UTC)
    FIXED_TIMESTAMP = (2020, 1, 1, 0, 0, 0)

    def create_deterministic_zip(
        self,
        files: List[Dict[str, Any]],
        metadata: Dict[str, Any]
    ) -> bytes:
        """Create a deterministic ZIP file.

        The same content will always produce the same ZIP file hash.

        Args:
            files: List of {path, content} dicts
            metadata: Metadata dict {owner, slug, version, published_at}

        Returns:
            ZIP file content as bytes
        """
        zip_buffer = io.BytesIO()

        # Create ZIP with ZIP_DEFLATED compression
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            # Sort files by path for determinism
            sorted_files = sorted(files, key=lambda f: f["path"])

            for file in sorted_files:
                path = file["path"]
                content = file["content"]

                # Create ZipInfo with fixed timestamp
                zip_info = zipfile.ZipInfo(path, self.FIXED_TIMESTAMP)

                # Set consistent permissions (rw-r--r--)
                zip_info.external_attr = 0o644 << 16

                # Set compression flags
                zip_info.compress_type = zipfile.ZIP_DEFLATED

                # Add file to ZIP
                zf.writestr(zip_info, content)

            # Add manifest.json with metadata
            manifest_content = self._create_manifest(metadata, files)
            manifest_info = zipfile.ZipInfo("manifest.json", self.FIXED_TIMESTAMP)
            manifest_info.external_attr = 0o644 << 16
            manifest_info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(manifest_info, manifest_content)

        return zip_buffer.getvalue()

    def _create_manifest(
        self,
        metadata: Dict[str, Any],
        files: List[Dict[str, Any]]
    ) -> str:
        """Create manifest.json content."""
        import json

        manifest = {
            "owner": metadata.get("owner", ""),
            "slug": metadata.get("slug", ""),
            "version": metadata.get("version", ""),
            "published_at": metadata.get("published_at", ""),
            "files": [
                {
                    "path": f["path"],
                    "sha256": f.get("sha256_hash", ""),
                    "size": f.get("file_size", 0)
                }
                for f in sorted(files, key=lambda f: f["path"])
            ]
        }

        return json.dumps(manifest, indent=2, sort_keys=True)

    def create_zip_from_storage(
        self,
        files: List[Dict[str, Any]],
        metadata: Dict[str, Any],
        storage_service
    ) -> bytes:
        """Create ZIP from stored files.

        Args:
            files: List of {path, storage_path, sha256_hash, file_size} dicts
            metadata: Metadata dict
            storage_service: StorageService instance

        Returns:
            ZIP file content as bytes
        """
        # Read file contents
        files_with_content = []
        for file in files:
            content = storage_service.read_file_content(file["storage_path"])
            if content is not None:
                files_with_content.append({
                    **file,
                    "content": content
                })

        return self.create_deterministic_zip(files_with_content, metadata)


# Singleton instance
_zip_service = None


def get_zip_service() -> ZipService:
    """Get singleton ZIP service instance."""
    global _zip_service
    if _zip_service is None:
        _zip_service = ZipService()
    return _zip_service
