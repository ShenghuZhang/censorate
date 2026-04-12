from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate
from app.repositories.base_repository import BaseRepository
from app.core.logger import get_logger
from app.exceptions import TaskNotFoundError

logger = get_logger(__name__)


class TaskService:
    """Task management service."""

    def __init__(self):
        """Initialize task service."""
        self.repository = BaseRepository(Task)

    def create_task(self, db: Session, task_data: TaskCreate) -> Task:
        """Create a new task."""
        logger.info(f"Creating task: {task_data.title}")

        task = self.repository.create(db, task_data.dict())
        logger.info(f"Task created successfully: {task.id}")
        return task

    def update_task(self, db: Session, task_id: int, task_data: TaskUpdate) -> Task:
        """Update an existing task."""
        logger.info(f"Updating task: {task_id}")

        task = self.repository.get(db, task_id)
        if not task:
            raise TaskNotFoundError(f"Task {task_id} not found")

        updated_task = self.repository.update(db, task, task_data.dict(exclude_unset=True))
        logger.info(f"Task updated successfully: {task_id}")
        return updated_task

    def get_task(self, db: Session, task_id: int) -> Optional[Task]:
        """Get task by ID."""
        return self.repository.get(db, task_id)

    def get_tasks(self, db: Session, skip: int = 0, limit: int = 100) -> List[Task]:
        """Get all tasks with pagination."""
        return self.repository.get_multi(db, skip, limit)

    def get_tasks_by_requirement(self, db: Session, requirement_id: int) -> List[Task]:
        """Get all tasks for a specific requirement."""
        logger.info(f"Getting tasks for requirement: {requirement_id}")
        return db.query(Task).filter(Task.requirement_id == requirement_id).all()

    def delete_task(self, db: Session, task_id: int) -> None:
        """Delete a task."""
        logger.info(f"Deleting task: {task_id}")

        task = self.repository.get(db, task_id)
        if not task:
            raise TaskNotFoundError(f"Task {task_id} not found")

        self.repository.delete(db, task_id)
        logger.info(f"Task deleted successfully: {task_id}")
