from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, field_serializer
from uuid import UUID


class RequirementCreate(BaseModel):
    """Schema for creating a new requirement."""
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    priority: str = Field(default="medium", pattern=r"^(low|medium|high)$")
    source: Optional[str] = None
    source_metadata: Optional[dict] = None
    lark_doc_token: Optional[str] = None
    lark_doc_url: Optional[str] = None
    lark_editable: bool = Field(default=False)


class RequirementUpdate(BaseModel):
    """Schema for updating a requirement."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = Field(None, pattern=r"^(low|medium|high)$")
    assigned_to: Optional[str] = None
    expected_completion_at: Optional[datetime] = None
    ai_confidence: Optional[float] = None
    ai_suggestions: Optional[dict] = None
    current_agent: Optional[str] = None
    current_thread_id: Optional[str] = None


class RequirementTransition(BaseModel):
    """Schema for requirement status transition."""
    to_status: str
    ai_approved: bool = False


class RequirementTransitionWithData(BaseModel):
    """Schema for requirement status transition with additional data."""
    to_status: str
    assigned_to: Optional[str] = None
    assigned_to_name: Optional[str] = None
    expected_completion_at: Optional[datetime] = None
    note: Optional[str] = None
    changed_by: Optional[str] = None
    changed_by_name: Optional[str] = None
    ai_approved: bool = False


class RequirementResponse(BaseModel):
    """Schema for requirement response."""
    id: UUID
    project_id: UUID
    req_number: int
    title: str
    description: Optional[str]
    status: str
    priority: str
    source: Optional[str]
    source_metadata: Optional[dict]
    lark_doc_token: Optional[str]
    lark_doc_url: Optional[str]
    lark_editable: bool
    ai_confidence: Optional[float]
    ai_suggestions: Optional[dict]
    current_agent: Optional[str]
    current_thread_id: Optional[str]
    created_by: str
    assigned_to: Optional[str]
    assigned_to_name: Optional[str]
    expected_completion_at: Optional[datetime]
    return_count: int
    last_returned_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    @field_serializer('created_at', 'updated_at', 'expected_completion_at', 'last_returned_at', 'completed_at')
    def serialize_datetime(self, dt: Optional[datetime]) -> Optional[str]:
        """Ensure datetime has timezone info and serialize as ISO."""
        if dt is None:
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()

    class Config:
        from_attributes = True
