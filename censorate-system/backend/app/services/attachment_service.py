"""Attachment service for handling file uploads and management with MinIO."""
import uuid
from typing import List, Optional
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from app.models.attachment import Attachment
from app.models.requirement import Requirement
from app.repositories.attachment_repository import AttachmentRepository
from app.core.minio_client import minio_client
import io


class AttachmentService:
    """Service for managing attachments."""

    def __init__(self):
        self.repository = AttachmentRepository()

    async def upload_attachment(
        self,
        db: Session,
        requirement_id: str,
        file: UploadFile,
        uploaded_by: Optional[str] = None,
        uploaded_by_name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Attachment:
        """Upload a file attachment to MinIO and save metadata."""
        # Verify requirement exists
        requirement = db.query(Requirement).filter(
            Requirement.id == requirement_id,
            Requirement.archived_at.is_(None)
        ).first()
        if not requirement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Requirement not found"
            )

        original_filename = file.filename or "unknown"

        # Read file data
        content = await file.read()
        file_size = len(content)
        file_data = io.BytesIO(content)

        # Upload to MinIO
        object_name, public_url = minio_client.upload_file(
            requirement_id=str(requirement_id),
            filename=original_filename,
            file_data=file_data,
            content_type=file.content_type,
            file_size=file_size
        )

        # Generate storage filename
        storage_filename = object_name.split('/')[-1]

        # Create database record
        attachment_data = {
            "requirement_id": requirement_id,
            "filename": storage_filename,
            "original_filename": original_filename,
            "content_type": file.content_type,
            "file_size": file_size,
            "minio_object_name": object_name,
            "minio_url": public_url,
            "uploaded_by": uploaded_by,
            "uploaded_by_name": uploaded_by_name,
            "description": description
        }

        attachment = self.repository.create(db, attachment_data)
        return attachment

    def get_attachment(
        self,
        db: Session,
        attachment_id: str
    ) -> Optional[Attachment]:
        """Get an attachment by ID."""
        return self.repository.get(db, attachment_id)

    def get_attachment_by_filename(
        self,
        db: Session,
        requirement_id: str,
        filename: str
    ) -> Optional[Attachment]:
        """Get an attachment by filename."""
        return self.repository.get_by_filename(db, requirement_id, filename)

    def get_requirement_attachments(
        self,
        db: Session,
        requirement_id: str
    ) -> List[Attachment]:
        """Get all attachments for a requirement."""
        return self.repository.get_by_requirement(db, requirement_id)

    def delete_attachment(
        self,
        db: Session,
        attachment_id: str
    ) -> bool:
        """Delete an attachment from MinIO and database."""
        attachment = self.repository.get(db, attachment_id)
        if not attachment:
            return False

        # Delete from MinIO first
        if attachment.minio_object_name:
            minio_client.delete_file(attachment.minio_object_name)

        # Delete database record
        self.repository.delete(db, attachment_id)
        return True

    def get_attachment_with_url(
        self,
        db: Session,
        attachment: Attachment
    ) -> dict:
        """Get attachment data with public URL."""
        return {
            "id": attachment.id,
            "requirement_id": attachment.requirement_id,
            "filename": attachment.filename,
            "original_filename": attachment.original_filename,
            "content_type": attachment.content_type,
            "file_size": attachment.file_size,
            "minio_object_name": attachment.minio_object_name,
            "uploaded_by": attachment.uploaded_by,
            "uploaded_by_name": attachment.uploaded_by_name,
            "description": attachment.description,
            "created_at": attachment.created_at,
            "updated_at": attachment.updated_at,
            "url": attachment.minio_url  # Use MinIO URL directly
        }
