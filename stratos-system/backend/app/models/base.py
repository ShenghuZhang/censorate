from datetime import datetime
from typing import Any
import json
import uuid
from sqlalchemy import Column, DateTime, String, Boolean, CHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import TypeDecorator, TEXT
from app.core.database import Base


class UUIDType(TypeDecorator):
    """UUID type that works with all databases."""
    impl = CHAR(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, str):
            return value
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        try:
            return uuid.UUID(value)
        except Exception:
            return value


class JsonType(TypeDecorator):
    """Generic JSON type that works with all databases."""
    impl = TEXT
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        try:
            return json.loads(value)
        except Exception:
            return value


class BaseModel(Base):
    """Base model for all database entities with common fields."""
    __abstract__ = True

    id = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    archived_at = Column(DateTime, nullable=True)

    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

    def update(self, **kwargs) -> "BaseModel":
        """Update model fields."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self
