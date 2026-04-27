from datetime import datetime, timezone
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_serializer


class RequirementStatusHistoryResponse(BaseModel):
    """Response schema for status history."""
    id: UUID
    requirement_id: UUID
    from_status: Optional[str]
    to_status: str
    assigned_to: Optional[str]
    assigned_to_name: Optional[str]
    expected_completion_at: Optional[datetime]
    changed_by: Optional[str]
    changed_by_name: Optional[str]
    changed_at: datetime
    note: Optional[str]
    is_backward: bool
    created_at: datetime
    updated_at: datetime

    @field_serializer('created_at', 'updated_at', 'changed_at', 'expected_completion_at')
    def serialize_datetime(self, dt: Optional[datetime]) -> Optional[str]:
        """Ensure datetime has timezone info and serialize as ISO."""
        if dt is None:
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()

    class Config:
        from_attributes = True
