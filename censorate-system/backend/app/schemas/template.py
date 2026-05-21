from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class TemplateBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    tech_stack: Dict[str, Any] = {}
    is_monorepo: bool = True
    config: Dict[str, Any] = {}


class TemplateCreate(TemplateBase):
    pass


class TemplateResponse(TemplateBase):
    id: UUID
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
