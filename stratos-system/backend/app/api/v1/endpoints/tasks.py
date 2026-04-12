from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.task import Task
from app.models.requirement import Requirement
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse

router = APIRouter()


def get_next_task_number(requirement_id: str, db: Session) -> int:
    """Get the next task number for a requirement."""
    max_task = db.query(Task).filter(
        Task.requirement_id == requirement_id
    ).order_by(Task.task_number.desc()).first()
    return (max_task.task_number + 1) if max_task else 1


@router.get("/requirements/{requirement_id}/tasks", response_model=List[TaskResponse])
def list_tasks(requirement_id: str, db: Session = Depends(get_db)):
    """List all tasks for a requirement."""
    requirement = db.query(Requirement).filter(
        Requirement.id == requirement_id
    ).first()
    if not requirement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requirement not found"
        )
    tasks = db.query(Task).filter(
        Task.requirement_id == requirement_id,
        Task.archived_at.is_(None)
    ).order_by(Task.task_number).all()
    return tasks


@router.post("/requirements/{requirement_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    requirement_id: str,
    task_in: TaskCreate,
    db: Session = Depends(get_db)
):
    """Create a new task."""
    requirement = db.query(Requirement).filter(
        Requirement.id == requirement_id
    ).first()
    if not requirement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requirement not found"
        )

    task_number = get_next_task_number(requirement_id, db)

    task = Task(
        requirement_id=requirement_id,
        task_number=task_number,
        title=task_in.title,
        description=task_in.description,
        status="pending",
        estimate_hours=task_in.estimate_hours,
        assigned_to=task_in.assigned_to,
        created_by="default-user"
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: str, db: Session = Depends(get_db)):
    """Get a task by ID."""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.archived_at.is_(None)
    ).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task


@router.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: str,
    task_in: TaskUpdate,
    db: Session = Depends(get_db)
):
    """Update a task."""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.archived_at.is_(None)
    ).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    update_data = task_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str, db: Session = Depends(get_db)):
    """Delete (archive) a task."""
    from datetime import datetime
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    task.archived_at = datetime.utcnow()
    db.commit()
    return None


@router.post("/tasks/{task_id}/generate-tests")
def generate_tests(task_id: str, db: Session = Depends(get_db)):
    """Generate test cases for a task."""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.archived_at.is_(None)
    ).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # TODO: Implement test generation
    return {"message": "Test generation triggered", "task_id": task_id}
