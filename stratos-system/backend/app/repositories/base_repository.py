"""Base repository class - provides common database operations."""

from abc import ABC, abstractmethod
from typing import Any, List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from ..models import BaseModel


class BaseRepository(ABC):
    """Abstract base repository class."""

    @abstractmethod
    def get(self, db: Session, id: UUID) -> Optional[BaseModel]:
        """Get a single entity by ID."""
        pass

    @abstractmethod
    def get_all(self, db: Session) -> List[BaseModel]:
        """Get all entities."""
        pass

    @abstractmethod
    def create(self, db: Session, entity: BaseModel) -> BaseModel:
        """Create a new entity."""
        pass

    @abstractmethod
    def update(self, db: Session, entity: BaseModel) -> BaseModel:
        """Update an existing entity."""
        pass

    @abstractmethod
    def delete(self, db: Session, id: UUID) -> None:
        """Delete an entity by ID."""
        pass
