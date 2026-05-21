from typing import List, Optional
from pydantic import BaseModel


class ReviewIssue(BaseModel):
    severity: str  # error, warning, suggestion
    line_number: Optional[int] = None
    column: Optional[int] = None
    message: str
    suggested_fix: Optional[str] = None


class FileReview(BaseModel):
    file_path: str
    passed: bool
    issues: List[ReviewIssue] = []
    summary: str
