"""Skill models - database models for AI agent skills system."""

from sqlalchemy import Column, String, Text, Boolean, ForeignKey, Integer, DateTime
from sqlalchemy.orm import relationship
from .base import UUIDType, BaseModel, JsonType


class Skill(BaseModel):
    """Skill model - represents an AI agent skill."""
    __tablename__ = "skills"

    slug = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False, index=True)
    owner_id = Column(UUIDType, nullable=True, index=True)
    latest_version_id = Column(UUIDType, ForeignKey("skill_versions.id"), nullable=True)
    tags = Column(JsonType, default=list)
    stats = Column(JsonType, default=dict)
    is_published = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    moderation_status = Column(String(50), default="pending")  # pending, approved, rejected, flagged

    # Relationships
    versions = relationship("SkillVersion", back_populates="skill", foreign_keys="SkillVersion.skill_id", order_by="SkillVersion.created_at.desc()")
    latest_version = relationship("SkillVersion", foreign_keys=[latest_version_id], post_update=True)
    downloads = relationship("SkillDownload", back_populates="skill", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Skill {self.slug} ({self.name})>"


class SkillVersion(BaseModel):
    """Skill version model - represents a specific version of a skill."""
    __tablename__ = "skill_versions"

    skill_id = Column(UUIDType, ForeignKey("skills.id"), nullable=False, index=True)
    version = Column(String(50), nullable=False)  # Semantic version: "1.0.0"
    changelog = Column(Text, nullable=True)
    manifest = Column(JsonType, default=dict)
    is_latest = Column(Boolean, default=False)
    is_deprecated = Column(Boolean, default=False)

    # Relationships
    skill = relationship("Skill", back_populates="versions", foreign_keys=[skill_id])
    files = relationship("SkillFile", back_populates="version", cascade="all, delete-orphan", order_by="SkillFile.path")

    __table_args__ = (
        {"extend_existing": True},
    )

    def __repr__(self):
        return f"<SkillVersion {self.skill_id} v{self.version}>"


class SkillFile(BaseModel):
    """Skill file model - represents a file within a skill version."""
    __tablename__ = "skill_files"

    version_id = Column(UUIDType, ForeignKey("skill_versions.id"), nullable=False, index=True)
    path = Column(String(500), nullable=False)  # File path like "SKILL.md", "utils/helper.py"
    content_type = Column(String(100), nullable=False, default="text/plain")
    file_size = Column(Integer, nullable=False, default=0)
    sha256_hash = Column(String(64), nullable=True)
    storage_path = Column(String(500), nullable=False)

    # Relationships
    version = relationship("SkillVersion", back_populates="files")

    __table_args__ = (
        {"extend_existing": True},
    )

    def __repr__(self):
        return f"<SkillFile {self.path}>"


class SkillDownload(BaseModel):
    """Skill download record - tracks downloads for statistics and deduplication."""
    __tablename__ = "skill_downloads"

    skill_id = Column(UUIDType, ForeignKey("skills.id"), nullable=False, index=True)
    version_id = Column(UUIDType, ForeignKey("skill_versions.id"), nullable=False, index=True)
    identity_hash = Column(String(64), nullable=False, index=True)  # Hashed user ID or IP
    downloaded_at = Column(DateTime, nullable=False)
    hour_start = Column(DateTime, nullable=False, index=True)  # For hourly deduplication

    # Relationships
    skill = relationship("Skill", back_populates="downloads")

    __table_args__ = (
        {"extend_existing": True},
    )

    def __repr__(self):
        return f"<SkillDownload {self.skill_id} at {self.downloaded_at}>"
