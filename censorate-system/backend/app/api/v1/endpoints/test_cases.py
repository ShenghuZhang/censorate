"""Test case endpoints for Stratos API."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.test_case import TestCase
from app.models.requirement import Requirement
from app.schemas.test_case import TestCaseCreate, TestCaseUpdate, TestCaseResponse

router = APIRouter()


def get_next_test_number(requirement_id: str, db: Session) -> int:
    """Get the next test case number for a requirement."""
    max_test = db.query(TestCase).filter(
        TestCase.requirement_id == requirement_id
    ).order_by(TestCase.test_number.desc()).first()
    return (max_test.test_number + 1) if max_test else 1


@router.get("/requirements/{requirement_id}/test-cases", response_model=List[TestCaseResponse])
def list_test_cases(requirement_id: str, db: Session = Depends(get_db)):
    """List all test cases for a requirement."""
    requirement = db.query(Requirement).filter(
        Requirement.id == requirement_id
    ).first()
    if not requirement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requirement not found"
        )
    test_cases = db.query(TestCase).filter(
        TestCase.requirement_id == requirement_id,
        TestCase.archived_at.is_(None)
    ).order_by(TestCase.test_number).all()
    return test_cases


@router.post("/requirements/{requirement_id}/test-cases", response_model=TestCaseResponse, status_code=status.HTTP_201_CREATED)
def create_test_case(
    requirement_id: str,
    test_case_in: TestCaseCreate,
    db: Session = Depends(get_db)
):
    """Create a new test case."""
    requirement = db.query(Requirement).filter(
        Requirement.id == requirement_id
    ).first()
    if not requirement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requirement not found"
        )

    test_number = get_next_test_number(requirement_id, db)

    test_case = TestCase(
        requirement_id=requirement_id,
        test_number=test_number,
        title=test_case_in.title,
        description=test_case_in.description,
        type=test_case_in.type,
        status=test_case_in.status,
        github_run_url=test_case_in.github_run_url,
        created_by="default-user"
    )
    db.add(test_case)
    db.commit()
    db.refresh(test_case)
    return test_case


@router.get("/test-cases/{test_case_id}", response_model=TestCaseResponse)
def get_test_case(test_case_id: str, db: Session = Depends(get_db)):
    """Get a test case by ID."""
    test_case = db.query(TestCase).filter(
        TestCase.id == test_case_id,
        TestCase.archived_at.is_(None)
    ).first()
    if not test_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test case not found"
        )
    return test_case


@router.put("/test-cases/{test_case_id}", response_model=TestCaseResponse)
def update_test_case(
    test_case_id: str,
    test_case_in: TestCaseUpdate,
    db: Session = Depends(get_db)
):
    """Update a test case."""
    test_case = db.query(TestCase).filter(
        TestCase.id == test_case_id,
        TestCase.archived_at.is_(None)
    ).first()
    if not test_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test case not found"
        )

    update_data = test_case_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(test_case, field, value)

    db.commit()
    db.refresh(test_case)
    return test_case


@router.delete("/test-cases/{test_case_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_test_case(test_case_id: str, db: Session = Depends(get_db)):
    """Delete (archive) a test case."""
    from datetime import datetime
    test_case = db.query(TestCase).filter(TestCase.id == test_case_id).first()
    if not test_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test case not found"
        )
    test_case.archived_at = datetime.utcnow()
    db.commit()
    return None
