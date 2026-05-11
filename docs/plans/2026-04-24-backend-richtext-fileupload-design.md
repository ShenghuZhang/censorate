# Backend Rich Text + File Upload Design

**Date**: 2026-04-24  
**Author**: Claude Code  
**Status**: Approved

## Context

The Censorate system needs comprehensive rich text support with file upload capabilities. Currently:
- Requirement descriptions and comment content are stored as plain text
- No actual file upload implementation exists (only a placeholder endpoint)
- No XSS protection for HTML content
- No proper attachment management

This design provides:
- Secure rich text content handling with XSS sanitization
- File upload system supporting both local filesystem and object storage
- Proper file metadata management
- API endpoints for file operations

## Architecture

### Layered Design

```
┌─────────────────────────────────────────────────────────┐
│                    API Layer                             │
│  - files.py (new)                                        │
│  - requirements.py (updated)                             │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                  Service Layer                          │
│  - file_service.py (new)                                │
│  - requirement_service.py (updated - sanitization)      │
│  - comment_service.py (updated - sanitization)          │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                Repository Layer                         │
│  - file_repository.py (new)                             │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                  Model Layer                            │
│  - file.py (new File model)                             │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                 Storage Layer                           │
│  ┌──────────────────┐    ┌───────────────────────┐     │
│  │  LocalStorage    │ or │   ObjectStorage       │     │
│  │  (filesystem)    │    │  (S3/OSS compatible)  │     │
│  └──────────────────┘    └───────────────────────┘     │
└─────────────────────────────────────────────────────────┘
```

## Data Models

### File Model

**File**: `app/models/file.py`

```python
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class File(Base):
    __tablename__ = "files"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False)  # Unique filename (uuid-based)
    original_filename = Column(String(255), nullable=False)  # Original user filename
    content_type = Column(String(100), nullable=False)  # MIME type
    size = Column(Integer, nullable=False)  # Size in bytes
    file_hash = Column(String(64), nullable=False, index=True)  # SHA-256 hash for deduplication
    
    # Storage information
    storage_type = Column(String(20), nullable=False)  # 'local' or 'object'
    storage_path = Column(String(500), nullable=False)  # Path within storage
    storage_url = Column(String(500), nullable=True)  # Public URL (for object storage)
    
    # Ownership and association
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Can be attached to requirements or comments
    requirement_id = Column(UUID(as_uuid=True), ForeignKey("requirements.id"), nullable=True)
    comment_id = Column(UUID(as_uuid=True), ForeignKey("comments.id"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="files")
    uploaded_by_user = relationship("User")
    requirement = relationship("Requirement", back_populates="attachments")
    comment = relationship("Comment", back_populates="attachments")
```

### Updates to Existing Models

**Requirement**: Add relationship for attachments
```python
# In app/models/requirement.py
attachments = relationship("File", back_populates="requirement", cascade="all, delete-orphan")
```

**Comment**: Add relationship for attachments (keep existing attachments JSON field for backward compatibility)
```python
# In app/models/comment.py
attachments = relationship("File", back_populates="comment", cascade="all, delete-orphan")
```

**Project**: Add relationship for files
```python
# In app/models/project.py
files = relationship("File", back_populates="project", cascade="all, delete-orphan")
```

## Storage Layer

### Storage Provider Interface

**StorageProvider**: `app/services/storage/base.py`

```python
from abc import ABC, abstractmethod
from typing import Optional


class StorageProvider(ABC):
    @abstractmethod
    def save(self, filename: str, content: bytes, content_type: str) -> str:
        """
        Save file content to storage.
        Returns the storage path/identifier.
        """
        pass
    
    @abstractmethod
    def get(self, path: str) -> bytes:
        """
        Retrieve file content from storage.
        """
        pass
    
    @abstractmethod
    def delete(self, path: str) -> bool:
        """
        Delete file from storage.
        Returns True if successful.
        """
        pass
    
    @abstractmethod
    def get_url(self, path: str, expires_in: Optional[int] = 3600) -> str:
        """
        Get a URL for accessing the file.
        For object storage, this may be a pre-signed URL.
        """
        pass
    
    @abstractmethod
    def exists(self, path: str) -> bool:
        """
        Check if file exists in storage.
        """
        pass
```

### Local Storage Implementation

**LocalStorage**: `app/services/storage/local.py`

```python
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.core.config import settings
from .base import StorageProvider


class LocalStorage(StorageProvider):
    def __init__(self):
        self.base_path = Path(settings.LOCAL_STORAGE_PATH)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def _get_date_path(self) -> str:
        """Get date-based path: YYYY/MM/DD"""
        now = datetime.utcnow()
        return f"{now.year}/{now.month:02d}/{now.day:02d}"
    
    def save(self, filename: str, content: bytes, content_type: str) -> str:
        date_path = self._get_date_path()
        full_path = self.base_path / date_path
        full_path.mkdir(parents=True, exist_ok=True)
        
        file_path = full_path / filename
        file_path.write_bytes(content)
        
        return f"{date_path}/{filename}"
    
    def get(self, path: str) -> bytes:
        file_path = self.base_path / path
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        return file_path.read_bytes()
    
    def delete(self, path: str) -> bool:
        file_path = self.base_path / path
        if file_path.exists():
            file_path.unlink()
            return True
        return False
    
    def get_url(self, path: str, expires_in: Optional[int] = 3600) -> str:
        # For local storage, return API download URL
        return f"{settings.API_V1_STR}/files/download/{path}"
    
    def exists(self, path: str) -> bool:
        return (self.base_path / path).exists()
```

### Object Storage Implementation

**ObjectStorage**: `app/services/storage/object.py`

```python
import boto3
from botocore.exceptions import ClientError
from typing import Optional
from datetime import datetime, timedelta

from app.core.config import settings
from .base import StorageProvider


class ObjectStorage(StorageProvider):
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
            endpoint_url=settings.S3_ENDPOINT_URL
        )
        self.bucket = settings.S3_BUCKET
    
    def _get_date_path(self) -> str:
        """Get date-based path: YYYY/MM/DD"""
        now = datetime.utcnow()
        return f"{now.year}/{now.month:02d}/{now.day:02d}"
    
    def save(self, filename: str, content: bytes, content_type: str) -> str:
        date_path = self._get_date_path()
        storage_path = f"{date_path}/{filename}"
        
        self.s3.put_object(
            Bucket=self.bucket,
            Key=storage_path,
            Body=content,
            ContentType=content_type
        )
        
        return storage_path
    
    def get(self, path: str) -> bytes:
        try:
            response = self.s3.get_object(Bucket=self.bucket, Key=path)
            return response['Body'].read()
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                raise FileNotFoundError(f"File not found: {path}")
            raise
    
    def delete(self, path: str) -> bool:
        try:
            self.s3.delete_object(Bucket=self.bucket, Key=path)
            return True
        except ClientError:
            return False
    
    def get_url(self, path: str, expires_in: Optional[int] = 3600) -> str:
        try:
            url = self.s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': path},
                ExpiresIn=expires_in
            )
            return url
        except ClientError:
            # Fallback to API URL
            return f"{settings.API_V1_STR}/files/download/{path}"
    
    def exists(self, path: str) -> bool:
        try:
            self.s3.head_object(Bucket=self.bucket, Key=path)
            return True
        except ClientError:
            return False
```

### Storage Factory

**StorageFactory**: `app/services/storage/__init__.py`

```python
from app.core.config import settings
from .base import StorageProvider
from .local import LocalStorage
from .object import ObjectStorage


def get_storage_provider() -> StorageProvider:
    """Get the configured storage provider"""
    if settings.STORAGE_TYPE == "object":
        return ObjectStorage()
    return LocalStorage()
```

## Rich Text Sanitization

### Sanitization Service

**RichTextService**: `app/services/rich_text_service.py`

```python
import bleach
from typing import Optional

# Allowed HTML tags for rich text
ALLOWED_TAGS = [
    'p', 'br', 'div', 'span',
    'b', 'i', 'u', 'strong', 'em', 's', 'strike',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li',
    'blockquote', 'pre', 'code',
    'a', 'img',
    'table', 'tr', 'td', 'th', 'tbody', 'thead', 'tfoot',
    'hr'
]

# Allowed attributes
ALLOWED_ATTRIBUTES = {
    '*': ['class', 'style'],
    'a': ['href', 'title', 'target'],
    'img': ['src', 'alt', 'title', 'width', 'height'],
    'table': ['border', 'cellpadding', 'cellspacing'],
}

# Allowed CSS properties (very restrictive)
ALLOWED_STYLES = [
    'color', 'background-color',
    'font-size', 'font-weight', 'font-style', 'text-decoration',
    'text-align', 'margin', 'padding',
    'width', 'height'
]

# Allowed protocols
ALLOWED_PROTOCOLS = ['http', 'https', 'data']


class RichTextService:
    @staticmethod
    def sanitize_html(html: Optional[str]) -> str:
        """
        Sanitize HTML to prevent XSS attacks while preserving safe formatting.
        """
        if not html:
            return ""
        
        # Sanitize the HTML
        cleaned = bleach.clean(
            html,
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRIBUTES,
            styles=ALLOWED_STYLES,
            protocols=ALLOWED_PROTOCOLS,
            strip=True
        )
        
        return cleaned
    
    @staticmethod
    def validate_image_src(src: str, project_id: str) -> bool:
        """
        Validate that an image src is either:
        1. A safe external URL (http/https)
        2. A file uploaded to this project
        """
        if src.startswith(('http://', 'https://')):
            return True
        
        # Check if it's a local file URL - would need database lookup
        # For now, allow relative URLs and internal file URLs
        return True
```

## API Endpoints

### File Management Endpoints

**New**: `app/api/v1/endpoints/files.py`

```python
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import uuid
import hashlib

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.api.deps import get_current_user
from app.schemas.file import File as FileSchema, FileCreate, FileUploadResponse
from app.services.file_service import FileService
from app.services.storage import get_storage_provider

router = APIRouter()


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    project_id: uuid.UUID = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a file. Returns file_id and access URL.
    """
    # Validate file
    if file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Max size: {settings.MAX_FILE_SIZE} bytes"
        )
    
    # Validate extension
    ext = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File type not allowed. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Read file content
    content = await file.read()
    
    # Create file service
    file_service = FileService(db)
    
    # Save file
    file_record = await file_service.upload_file(
        content=content,
        original_filename=file.filename,
        content_type=file.content_type or 'application/octet-stream',
        project_id=project_id,
        uploaded_by=current_user.id
    )
    
    return FileUploadResponse(
        file_id=file_record.id,
        url=file_record.storage_url or file_service.get_file_url(file_record),
        filename=file_record.original_filename,
        content_type=file_record.content_type,
        size=file_record.size
    )


@router.get("/{file_id}", response_model=FileSchema)
async def get_file_info(
    file_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get file metadata"""
    file_service = FileService(db)
    return file_service.get_file(file_id, current_user.id)


@router.get("/{file_id}/download")
async def download_file(
    file_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Download file content"""
    file_service = FileService(db)
    file_record = file_service.get_file(file_id, current_user.id)
    
    storage = get_storage_provider()
    content = storage.get(file_record.storage_path)
    
    return StreamingResponse(
        iter([content]),
        media_type=file_record.content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{file_record.original_filename}"'
        }
    )


@router.delete("/{file_id}")
async def delete_file(
    file_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a file"""
    file_service = FileService(db)
    file_service.delete_file(file_id, current_user.id)
    return {"success": True}
```

### Updated Requirements Endpoints

**Updated**: `app/api/v1/endpoints/requirements.py`

Add attachment endpoints:

```python
@router.post("/{requirement_id}/upload-attachment", response_model=FileUploadResponse)
async def upload_requirement_attachment(
    requirement_id: uuid.UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload and attach a file to a requirement"""
    # First get the requirement to get project_id
    requirement = requirement_service.get_requirement(db, requirement_id)
    
    # Upload file (similar to /upload endpoint)
    # Then associate with requirement_id
    
    # Implementation reuses FileService with requirement_id parameter
    pass


@router.get("/{requirement_id}/attachments", response_model=List[FileSchema])
async def get_requirement_attachments(
    requirement_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all attachments for a requirement"""
    pass
```

## Configuration

**New settings** in `app/core/config.py`:

```python
class Settings(BaseSettings):
    # ... existing settings ...
    
    # Storage configuration
    STORAGE_TYPE: str = "local"  # "local" or "object"
    
    # Local storage
    LOCAL_STORAGE_PATH: str = "./app/storage/uploads"
    
    # Object storage (S3 compatible)
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    S3_BUCKET: Optional[str] = None
    S3_REGION: Optional[str] = "us-east-1"
    S3_ENDPOINT_URL: Optional[str] = None
    
    # File upload limits
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10 MB
    ALLOWED_EXTENSIONS: List[str] = [
        "jpg", "jpeg", "png", "gif", "webp",  # Images
        "pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx",  # Documents
        "txt", "md", "zip"  # Other
    ]
```

## Database Migration

**New migration** to create `files` table:

```python
"""create_files_table

Revision ID: [auto-generated]
Revises: [previous]
Create Date: 2026-04-24
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    op.create_table(
        'files',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('content_type', sa.String(length=100), nullable=False),
        sa.Column('size', sa.Integer(), nullable=False),
        sa.Column('file_hash', sa.String(length=64), nullable=False),
        sa.Column('storage_type', sa.String(length=20), nullable=False),
        sa.Column('storage_path', sa.String(length=500), nullable=False),
        sa.Column('storage_url', sa.String(length=500), nullable=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('uploaded_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('requirement_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('comment_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['comment_id'], ['comments.id'], ),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.ForeignKeyConstraint(['requirement_id'], ['requirements.id'], ),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_files_file_hash'), 'files', ['file_hash'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_files_file_hash'), table_name='files')
    op.drop_table('files')
```

## File Service

**FileService**: `app/services/file_service.py`

```python
import uuid
import hashlib
from typing import List, Optional
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.file import File
from app.schemas.file import FileCreate
from app.services.storage import get_storage_provider
from app.services.rich_text import RichTextService


class FileService:
    def __init__(self, db: Session):
        self.db = db
        self.storage = get_storage_provider()
    
    def _calculate_hash(self, content: bytes) -> str:
        """Calculate SHA-256 hash of content"""
        return hashlib.sha256(content).hexdigest()
    
    def _find_duplicate(self, file_hash: str, project_id: uuid.UUID) -> Optional[File]:
        """Find duplicate file by hash in project"""
        return self.db.query(File).filter(
            File.file_hash == file_hash,
            File.project_id == project_id
        ).first()
    
    async def upload_file(
        self,
        content: bytes,
        original_filename: str,
        content_type: str,
        project_id: uuid.UUID,
        uploaded_by: uuid.UUID,
        requirement_id: Optional[uuid.UUID] = None,
        comment_id: Optional[uuid.UUID] = None
    ) -> File:
        """
        Upload a file:
        1. Calculate hash
        2. Check for duplicates
        3. Save to storage
        4. Create database record
        """
        # Calculate hash
        file_hash = self._calculate_hash(content)
        
        # Check for duplicate
        duplicate = self._find_duplicate(file_hash, project_id)
        if duplicate:
            # Return duplicate if found (deduplication)
            return duplicate
        
        # Generate unique filename
        ext = original_filename.split('.')[-1].lower() if '.' in original_filename else ''
        unique_filename = f"{uuid.uuid4()}.{ext}" if ext else str(uuid.uuid4())
        
        # Save to storage
        storage_path = self.storage.save(unique_filename, content, content_type)
        
        # Get URL
        storage_url = None
        if self.storage.__class__.__name__ == 'ObjectStorage':
            storage_url = self.storage.get_url(storage_path)
        
        # Create database record
        file_record = File(
            id=uuid.uuid4(),
            filename=unique_filename,
            original_filename=original_filename,
            content_type=content_type,
            size=len(content),
            file_hash=file_hash,
            storage_type=settings.STORAGE_TYPE,
            storage_path=storage_path,
            storage_url=storage_url,
            project_id=project_id,
            uploaded_by=uploaded_by,
            requirement_id=requirement_id,
            comment_id=comment_id,
            created_at=datetime.utcnow()
        )
        
        self.db.add(file_record)
        self.db.commit()
        self.db.refresh(file_record)
        
        return file_record
    
    def get_file(self, file_id: uuid.UUID, user_id: uuid.UUID) -> File:
        """Get file by ID with permission check"""
        file_record = self.db.query(File).filter(File.id == file_id).first()
        if not file_record:
            raise HTTPException(status_code=404, detail="File not found")
        
        # TODO: Add proper permission check based on project membership
        return file_record
    
    def get_file_url(self, file_record: File) -> str:
        """Get access URL for file"""
        if file_record.storage_url:
            return file_record.storage_url
        return self.storage.get_url(file_record.storage_path)
    
    def delete_file(self, file_id: uuid.UUID, user_id: uuid.UUID):
        """Delete file from storage and database"""
        file_record = self.get_file(file_id, user_id)
        
        # Delete from storage
        self.storage.delete(file_record.storage_path)
        
        # Delete from database
        self.db.delete(file_record)
        self.db.commit()
```

## Schema Definitions

**New schemas**: `app/schemas/file.py`

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID


class FileBase(BaseModel):
    original_filename: str
    content_type: str
    size: int


class FileCreate(FileBase):
    filename: str
    file_hash: str
    storage_type: str
    storage_path: str
    storage_url: Optional[str] = None
    project_id: UUID
    uploaded_by: UUID
    requirement_id: Optional[UUID] = None
    comment_id: Optional[UUID] = None


class File(FileBase):
    id: UUID
    filename: str
    storage_type: str
    project_id: UUID
    uploaded_by: UUID
    requirement_id: Optional[UUID] = None
    comment_id: Optional[UUID] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class FileUploadResponse(BaseModel):
    file_id: UUID
    url: str
    filename: str
    content_type: str
    size: int
```

## Integration with Existing Services

### Requirement Service Updates

In `requirement_service.py`, sanitize description on create/update:

```python
from app.services.rich_text import RichTextService

# In create_requirement
if requirement.description:
    requirement.description = RichTextService.sanitize_html(requirement.description)

# In update_requirement  
if obj_in.description:
    obj_in.description = RichTextService.sanitize_html(obj_in.description)
```

### Comment Service Updates

Similarly, sanitize comment content:

```python
from app.services.rich_text import RichTextService

# In create_comment
if comment.content:
    comment.content = RichTextService.sanitize_html(comment.content)
```

## Files Summary

### New Files
- `app/models/file.py` - File model
- `app/schemas/file.py` - File schemas
- `app/repositories/file_repository.py` - File repository
- `app/services/file_service.py` - File service
- `app/services/rich_text_service.py` - Rich text sanitization
- `app/services/storage/base.py` - Storage provider interface
- `app/services/storage/local.py` - Local storage implementation
- `app/services/storage/object.py` - Object storage implementation
- `app/services/storage/__init__.py` - Storage factory
- `app/api/v1/endpoints/files.py` - File API endpoints

### Updated Files
- `app/models/project.py` - Add files relationship
- `app/models/requirement.py` - Add attachments relationship
- `app/models/comment.py` - Add attachments relationship
- `app/core/config.py` - Add storage configuration
- `app/services/requirement_service.py` - Add sanitization
- `app/services/comment_service.py` - Add sanitization
- `app/api/v1/endpoints/requirements.py` - Add attachment endpoints
- `app/api/v1/router.py` - Include files router

### Migration
- New migration to create `files` table

## Verification Steps

1. Test file upload (local storage)
2. Test file upload (object storage)
3. Test file download
4. Test file deletion
5. Test rich text sanitization (XSS attempt should be blocked)
6. Test deduplication (same file uploaded twice should return same record)
7. Test API permissions
8. Test requirements with attachments

## Success Criteria

- [ ] File upload works with both storage types
- [ ] Rich text sanitizes XSS payloads correctly
- [ ] Files can be downloaded and accessed
- [ ] Deduplication works
- [ ] API permission checks work
- [ ] Attachments are properly associated with requirements/comments
- [ ] Configuration switches between storage types correctly
