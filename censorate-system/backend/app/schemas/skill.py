"""Skill schemas - Pydantic models for skill API requests and responses."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID


# ============== Skill Schemas ==============

class SkillCreate(BaseModel):
    """Schema for creating a new skill."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: str = Field(..., min_length=1, max_length=100)
    tags: List[str] = Field(default_factory=list)


class SkillUpdate(BaseModel):
    """Schema for updating a skill."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    tags: Optional[List[str]] = None
    is_published: Optional[bool] = None


class SkillFileResponse(BaseModel):
    """Schema for skill file response."""
    id: UUID
    path: str
    content_type: str
    file_size: int
    sha256_hash: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SkillVersionResponse(BaseModel):
    """Schema for skill version response."""
    id: UUID
    version: str
    changelog: Optional[str] = None
    manifest: Dict[str, Any] = Field(default_factory=dict)
    is_latest: bool
    is_deprecated: bool
    created_at: datetime
    files: List[SkillFileResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class SkillResponse(BaseModel):
    """Schema for skill response."""
    id: UUID
    slug: str
    name: str
    description: Optional[str] = None
    category: str
    owner_id: Optional[UUID] = None
    latest_version_id: Optional[UUID] = None
    tags: List[str] = Field(default_factory=list)
    stats: Dict[str, Any] = Field(default_factory=dict)
    is_published: bool
    is_archived: bool
    moderation_status: str
    created_at: datetime
    updated_at: datetime
    archived_at: Optional[datetime] = None

    # Optional nested data
    latest_version: Optional[SkillVersionResponse] = None
    versions: Optional[List[SkillVersionResponse]] = None

    class Config:
        from_attributes = True


class SkillListResponse(BaseModel):
    """Schema for paginated skill list response."""
    count: int
    skip: int
    limit: int
    skills: List[SkillResponse]


# ============== Skill Version Schemas ==============

class SkillVersionCreate(BaseModel):
    """Schema for creating a new skill version."""
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")
    changelog: Optional[str] = None


class SkillVersionUpdate(BaseModel):
    """Schema for updating a skill version."""
    changelog: Optional[str] = None
    is_deprecated: Optional[bool] = None


# ============== Search Schemas ==============

class SkillSearchQuery(BaseModel):
    """Schema for skill search query."""
    query: str = Field(..., min_length=1, max_length=200)
    category: Optional[str] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)


class SkillSearchResult(BaseModel):
    """Schema for skill search result."""
    skill: SkillResponse
    relevance_score: float


class SkillSearchResponse(BaseModel):
    """Schema for skill search response."""
    count: int
    results: List[SkillSearchResult]


# ============== Upload Schemas ==============

class SkillUploadMetadata(BaseModel):
    """Schema for skill upload metadata."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: str = Field(..., min_length=1, max_length=100)
    tags: List[str] = Field(default_factory=list)
    version: str = Field(default="1.0.0", pattern=r"^\d+\.\d+\.\d+$")
    changelog: Optional[str] = None


class SkillUploadResponse(BaseModel):
    """Schema for skill upload response."""
    status: str
    message: str
    skill: SkillResponse


# ============== Download Schemas ==============

class SkillDownloadRecord(BaseModel):
    """Schema for skill download record."""
    id: UUID
    skill_id: UUID
    version_id: UUID
    downloaded_at: datetime

    class Config:
        from_attributes = True


# ============== Category Schemas ==============

class CategoryListResponse(BaseModel):
    """Schema for category list response."""
    categories: List[str]
    counts: Dict[str, int]


# ============== Statistics Schemas ==============

class SkillStatsResponse(BaseModel):
    """Schema for skill statistics response."""
    total_skills: int
    total_downloads: int
    total_views: int
    categories: Dict[str, int]
    popular_skills: List[SkillResponse]
