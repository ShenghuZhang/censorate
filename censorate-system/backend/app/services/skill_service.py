"""Skill Service - manages AI Agent skills with full version control and storage."""

import re
import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from sqlalchemy.orm import Session
from slugify import slugify

from app.models import Skill, SkillVersion, SkillFile, SkillDownload
from app.schemas import (
    SkillCreate, SkillUpdate, SkillUploadMetadata
)
from app.repositories import (
    SkillRepository, SkillVersionRepository,
    SkillFileRepository, SkillDownloadRepository
)
from app.services.storage_service import get_storage_service
from app.services.zip_service import get_zip_service
from app.core.exceptions import (
    NotFoundException, ValidationException, ConflictException
)


class SkillService:
    """Service for managing AI Agent skills."""

    def __init__(self):
        """Initialize skill service with repositories and services."""
        self.skill_repo = SkillRepository()
        self.version_repo = SkillVersionRepository()
        self.file_repo = SkillFileRepository()
        self.download_repo = SkillDownloadRepository()
        self.storage_service = get_storage_service()
        self.zip_service = get_zip_service()

    # ===== Skill CRUD Operations =====

    def create_skill(
        self,
        db: Session,
        data: SkillCreate,
        files: List[Dict[str, Any]],
        owner_id: Optional[uuid.UUID] = None
    ) -> Skill:
        """Create a new skill with initial version.

        Args:
            db: Database session
            data: Skill creation data
            files: List of {path, content} dicts
            owner_id: Optional owner ID

        Returns:
            Created Skill instance
        """
        # Generate slug
        base_slug = slugify(data.name)
        slug = base_slug
        counter = 1

        # Ensure slug is unique
        while self.skill_repo.get_by_slug(db, slug):
            slug = f"{base_slug}-{counter}"
            counter += 1

        # Create skill
        skill = Skill(
            id=uuid.uuid4(),
            slug=slug,
            name=data.name,
            description=data.description,
            category=data.category,
            owner_id=owner_id,
            tags=data.tags or [],
            stats={"downloads": 0, "views": 0},
            is_published=False,
            is_archived=False,
            moderation_status="pending"
        )
        skill = self.skill_repo.create(db, skill)

        # Create initial version
        try:
            version = self.create_version(
                db,
                skill.id,
                files,
                "1.0.0",
                "Initial version"
            )
            # Set latest version
            skill.latest_version_id = version.id
            self.skill_repo.update(db, skill)
        except Exception as e:
            # Clean up if version creation fails
            self.skill_repo.delete(db, skill.id)
            raise e

        return skill

    def update_skill(
        self,
        db: Session,
        skill_id: uuid.UUID,
        data: SkillUpdate
    ) -> Skill:
        """Update a skill's metadata.

        Args:
            db: Database session
            skill_id: Skill ID
            data: Update data

        Returns:
            Updated Skill instance
        """
        skill = self.skill_repo.get(db, skill_id)
        if not skill:
            raise NotFoundException(f"Skill with id {skill_id} not found")

        update_data = data.model_dump(exclude_unset=True)
        skill.update(**update_data)
        return self.skill_repo.update(db, skill)

    def get_skill(self, db: Session, slug: str, increment_views: bool = False) -> Skill:
        """Get a skill by slug.

        Args:
            db: Database session
            slug: Skill slug
            increment_views: Whether to increment view count

        Returns:
            Skill instance
        """
        skill = self.skill_repo.get_by_slug(db, slug)
        if not skill or skill.is_archived:
            raise NotFoundException(f"Skill with slug '{slug}' not found")

        if increment_views:
            self.skill_repo.increment_views(db, skill.id)

        return skill

    def get_skill_by_id(self, db: Session, skill_id: uuid.UUID) -> Skill:
        """Get a skill by ID.

        Args:
            db: Database session
            skill_id: Skill ID

        Returns:
            Skill instance
        """
        skill = self.skill_repo.get(db, skill_id)
        if not skill or skill.is_archived:
            raise NotFoundException(f"Skill with id {skill_id} not found")
        return skill

    def list_skills(
        self,
        db: Session,
        category: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Skill], int]:
        """List skills with optional category filter.

        Args:
            db: Database session
            category: Optional category filter
            skip: Pagination skip
            limit: Pagination limit

        Returns:
            Tuple of (skills list, total count)
        """
        if category:
            skills = self.skill_repo.get_by_category(db, category, skip, limit)
            # TODO: Get total count properly
            total = len(skills)
        else:
            skills = self.skill_repo.get_all_published(db, skip, limit)
            # TODO: Get total count properly
            total = len(skills)

        return skills, total

    def search_skills(
        self,
        db: Session,
        query: str,
        category: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Skill], int]:
        """Search skills.

        Args:
            db: Database session
            query: Search query
            category: Optional category filter
            skip: Pagination skip
            limit: Pagination limit

        Returns:
            Tuple of (skills list, total count)
        """
        skills = self.skill_repo.search(db, query, category, skip, limit)
        # TODO: Get total count properly
        total = len(skills)
        return skills, total

    def archive_skill(self, db: Session, skill_id: uuid.UUID) -> Skill:
        """Archive (soft delete) a skill.

        Args:
            db: Database session
            skill_id: Skill ID

        Returns:
            Archived Skill instance
        """
        skill = self.get_skill_by_id(db, skill_id)
        skill.is_archived = True
        return self.skill_repo.update(db, skill)

    # ===== Version Management =====

    def create_version(
        self,
        db: Session,
        skill_id: uuid.UUID,
        files: List[Dict[str, Any]],
        version_str: str,
        changelog: Optional[str] = None
    ) -> SkillVersion:
        """Create a new version of a skill.

        Args:
            db: Database session
            skill_id: Skill ID
            files: List of {path, content} dicts
            version_str: Semantic version string
            changelog: Optional changelog

        Returns:
            Created SkillVersion instance
        """
        # Validate version format
        if not re.match(r"^\d+\.\d+\.\d+$", version_str):
            raise ValidationException("Version must be in format MAJOR.MINOR.PATCH")

        # Check if version already exists
        existing = self.version_repo.get_by_skill_and_version(db, skill_id, version_str)
        if existing:
            raise ConflictException(f"Version {version_str} already exists")

        # Validate files
        is_valid, errors = self.storage_service.validate_files(files)
        if not is_valid:
            raise ValidationException("; ".join(errors))

        # Get skill
        skill = self.get_skill_by_id(db, skill_id)

        # Save files to storage
        saved_files = self.storage_service.save_skill_files(
            skill.slug,
            version_str,
            files
        )

        # Parse SKILL.md for manifest
        manifest = self._parse_skill_manifest(files)

        # Create version
        version = SkillVersion(
            id=uuid.uuid4(),
            skill_id=skill_id,
            version=version_str,
            changelog=changelog,
            manifest=manifest,
            is_latest=False,
            is_deprecated=False
        )
        version = self.version_repo.create(db, version)

        # Create file records
        for file_data in saved_files:
            skill_file = SkillFile(
                id=uuid.uuid4(),
                version_id=version.id,
                path=file_data["path"],
                content_type=file_data["content_type"],
                file_size=file_data["file_size"],
                sha256_hash=file_data["sha256_hash"],
                storage_path=file_data["storage_path"]
            )
            self.file_repo.create(db, skill_file)

        return version

    def get_version(
        self,
        db: Session,
        skill_id: uuid.UUID,
        version_str: str
    ) -> SkillVersion:
        """Get a specific version of a skill.

        Args:
            db: Database session
            skill_id: Skill ID
            version_str: Version string

        Returns:
            SkillVersion instance
        """
        version = self.version_repo.get_by_skill_and_version(db, skill_id, version_str)
        if not version:
            raise NotFoundException(f"Version {version_str} not found")
        return version

    def list_versions(self, db: Session, skill_id: uuid.UUID) -> List[SkillVersion]:
        """List all versions of a skill.

        Args:
            db: Database session
            skill_id: Skill ID

        Returns:
            List of SkillVersion instances
        """
        return self.version_repo.get_all_for_skill(db, skill_id)

    def set_latest_version(
        self,
        db: Session,
        skill_id: uuid.UUID,
        version_id: uuid.UUID
    ) -> Skill:
        """Set a version as latest for a skill.

        Args:
            db: Database session
            skill_id: Skill ID
            version_id: Version ID to set as latest

        Returns:
            Updated Skill instance
        """
        skill = self.get_skill_by_id(db, skill_id)
        version = self.version_repo.get(db, version_id)

        if not version or version.skill_id != skill_id:
            raise NotFoundException("Version not found")

        self.version_repo.set_latest(db, version_id)
        skill.latest_version_id = version_id
        return self.skill_repo.update(db, skill)

    # ===== File Operations =====

    def get_files_for_version(
        self,
        db: Session,
        version_id: uuid.UUID
    ) -> List[SkillFile]:
        """Get all files for a version.

        Args:
            db: Database session
            version_id: Version ID

        Returns:
            List of SkillFile instances
        """
        return self.file_repo.get_by_version(db, version_id)

    def get_file_content(
        self,
        db: Session,
        version_id: uuid.UUID,
        file_path: str
    ) -> Optional[bytes]:
        """Get content of a specific file.

        Args:
            db: Database session
            version_id: Version ID
            file_path: File path

        Returns:
            File content as bytes or None
        """
        file = self.file_repo.get_by_version_and_path(db, version_id, file_path)
        if not file:
            raise NotFoundException(f"File {file_path} not found")

        return self.storage_service.read_file_content(file.storage_path)

    # ===== Download Operations =====

    def record_download(
        self,
        db: Session,
        skill_id: uuid.UUID,
        version_id: uuid.UUID,
        identity: str
    ) -> Optional[SkillDownload]:
        """Record a skill download (with hourly deduplication).

        Args:
            db: Database session
            skill_id: Skill ID
            version_id: Version ID
            identity: Identity string (user ID or IP)

        Returns:
            SkillDownload instance if new, None if deduplicated
        """
        # Hash identity for privacy
        identity_hash = hashlib.sha256(identity.encode()).hexdigest()

        # Compute hour start
        now = datetime.utcnow()
        hour_start = datetime(now.year, now.month, now.day, now.hour)

        # Check for existing download in this hour
        existing = self.download_repo.get_by_skill_and_hour(
            db, skill_id, identity_hash, hour_start
        )
        if existing:
            return None  # Deduplicated

        # Create download record
        download = SkillDownload(
            id=uuid.uuid4(),
            skill_id=skill_id,
            version_id=version_id,
            identity_hash=identity_hash,
            downloaded_at=now,
            hour_start=hour_start
        )
        download = self.download_repo.create(db, download)

        # Increment download count
        self.skill_repo.increment_downloads(db, skill_id)

        return download

    def generate_zip(
        self,
        db: Session,
        skill_id: uuid.UUID,
        version_id: Optional[uuid.UUID] = None
    ) -> bytes:
        """Generate ZIP file for a skill version.

        Args:
            db: Database session
            skill_id: Skill ID
            version_id: Optional version ID (uses latest if not provided)

        Returns:
            ZIP file content as bytes
        """
        skill = self.get_skill_by_id(db, skill_id)

        # Get version
        if version_id:
            version = self.version_repo.get(db, version_id)
            if not version or version.skill_id != skill_id:
                raise NotFoundException("Version not found")
        else:
            version = self.version_repo.get_latest_for_skill(db, skill_id)
            if not version:
                raise NotFoundException("No version available")

        # Get files
        files = self.file_repo.get_by_version(db, version.id)

        # Prepare metadata
        metadata = {
            "owner": str(skill.owner_id) if skill.owner_id else "",
            "slug": skill.slug,
            "version": version.version,
            "published_at": version.created_at.isoformat() if version.created_at else ""
        }

        # Create ZIP
        return self.zip_service.create_zip_from_storage(
            [f.to_dict() for f in files],
            metadata,
            self.storage_service
        )

    # ===== Category Operations =====

    def get_categories(self, db: Session) -> Tuple[List[str], Dict[str, int]]:
        """Get all categories and their counts.

        Args:
            db: Database session

        Returns:
            Tuple of (categories list, counts dict)
        """
        categories = self.skill_repo.get_categories(db)
        counts = self.skill_repo.get_category_counts(db)
        return categories, counts

    # ===== Helper Methods =====

    def _parse_skill_manifest(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse SKILL.md to extract manifest data.

        Args:
            files: List of {path, content} dicts

        Returns:
            Manifest dict
        """
        import frontmatter

        # Find SKILL.md
        skill_md = next(
            (f for f in files if f.get("path", "").lower() == "skill.md"),
            None
        )

        if not skill_md:
            return {}

        try:
            content = skill_md.get("content", b"").decode("utf-8")
            post = frontmatter.loads(content)
            return dict(post.metadata)
        except Exception:
            return {}


# Singleton instance
_skill_service = None


def get_skill_service() -> SkillService:
    """Get singleton skill service instance."""
    global _skill_service
    if _skill_service is None:
        _skill_service = SkillService()
    return _skill_service
