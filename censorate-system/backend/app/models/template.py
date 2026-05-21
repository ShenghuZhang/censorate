from sqlalchemy import Column, String, Text, Boolean
from .base import BaseModel, JsonType


class Template(BaseModel):
    """Predefined tech stack template for code generation."""
    __tablename__ = "templates"

    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    tech_stack = Column(JsonType, default=dict)
    is_monorepo = Column(Boolean, default=True)
    config = Column(JsonType, default=dict)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Template {self.name} ({self.slug})>"
