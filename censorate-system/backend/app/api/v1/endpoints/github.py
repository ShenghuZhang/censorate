from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.github_repo import GitHubRepo

router = APIRouter()


@router.get("/projects/{project_id}/github")
def get_github_repo(project_id: str, db: Session = Depends(get_db)):
    """Get GitHub repository info for a project."""
    repo = (
        db.query(GitHubRepo)
        .filter(GitHubRepo.project_id == project_id)
        .first()
    )
    if not repo:
        raise HTTPException(status_code=404, detail="GitHub repository not found")
    return {
        "id": str(repo.id),
        "project_id": str(repo.project_id),
        "repo_name": repo.repo_name,
        "owner": repo.owner,
        "url": repo.url,
        "default_branch": repo.default_branch,
        "is_private": repo.is_private,
        "push_status": repo.push_status,
        "commit_sha": repo.commit_sha,
        "created_at": repo.created_at.isoformat() if repo.created_at else None,
    }
