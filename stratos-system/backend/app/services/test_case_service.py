from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.test_case import TestCase
from app.schemas.test_case import TestCaseCreate, TestCaseUpdate
from app.repositories.base_repository import BaseRepository
from app.core.logger import get_logger
from app.exceptions import TestCaseNotFoundError

logger = get_logger(__name__)


class TestCaseService:
    """Test case management service."""

    def __init__(self):
        """Initialize test case service."""
        self.repository = BaseRepository(TestCase)

    def create_test_case(self, db: Session, test_case_data: TestCaseCreate) -> TestCase:
        """Create a new test case."""
        logger.info(f"Creating test case: {test_case_data.title}")

        test_case = self.repository.create(db, test_case_data.dict())
        logger.info(f"Test case created successfully: {test_case.id}")
        return test_case

    def update_test_case(self, db: Session, test_case_id: int, test_case_data: TestCaseUpdate) -> TestCase:
        """Update an existing test case."""
        logger.info(f"Updating test case: {test_case_id}")

        test_case = self.repository.get(db, test_case_id)
        if not test_case:
            raise TestCaseNotFoundError(f"Test case {test_case_id} not found")

        updated_test_case = self.repository.update(db, test_case, test_case_data.dict(exclude_unset=True))
        logger.info(f"Test case updated successfully: {test_case_id}")
        return updated_test_case

    def get_test_case(self, db: Session, test_case_id: int) -> Optional[TestCase]:
        """Get test case by ID."""
        return self.repository.get(db, test_case_id)

    def get_test_cases(self, db: Session, skip: int = 0, limit: int = 100) -> List[TestCase]:
        """Get all test cases with pagination."""
        return self.repository.get_multi(db, skip, limit)

    def get_test_cases_by_requirement(self, db: Session, requirement_id: int) -> List[TestCase]:
        """Get all test cases for a specific requirement."""
        logger.info(f"Getting test cases for requirement: {requirement_id}")
        return db.query(TestCase).filter(TestCase.requirement_id == requirement_id).all()

    def delete_test_case(self, db: Session, test_case_id: int) -> None:
        """Delete a test case."""
        logger.info(f"Deleting test case: {test_case_id}")

        test_case = self.repository.get(db, test_case_id)
        if not test_case:
            raise TestCaseNotFoundError(f"Test case {test_case_id} not found")

        self.repository.delete(db, test_case_id)
        logger.info(f"Test case deleted successfully: {test_case_id}")
