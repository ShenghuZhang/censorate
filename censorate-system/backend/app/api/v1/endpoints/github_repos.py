from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.github_repo import GitHubRepo
from app.models.project import Project
from app.schemas.github_repo import GitHubRepoCreate, GitHubRepoUpdate, GitHubRepoResponse

router = APIRouter()


@router.get("/projects/{project_id}/github-repos", response_model=List[GitHubRepoResponse])
def list_github_repos(project_id: str, db: Session = Depends(get_db)):
    """List all GitHub repositories for a project."""
    # Check if project exists
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.archived_at.is_(None)
    ).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    repos = db.query(GitHubRepo).filter(GitHubRepo.project_id == project_id).all()
    return repos


@router.post("/projects/{project_id}/github-repos", response_model=GitHubRepoResponse, status_code=status.HTTP_201_CREATED)
def create_github_repo(
    project_id: str,
    repo_in: GitHubRepoCreate,
    db: Session = Depends(get_db)
):
    """Add a GitHub repository to a project."""
    # Check if project exists
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.archived_at.is_(None)
    ).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    repo = GitHubRepo(
        project_id=project_id,
        url=repo_in.url,
        description=repo_in.description
    )
    db.add(repo)
    db.commit()
    db.refresh(repo)
    return repo


@router.delete("/projects/{project_id}/github-repos/{repo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_github_repo(
    project_id: str,
    repo_id: str,
    db: Session = Depends(get_db)
):
    """Delete a GitHub repository from a project."""
    repo = db.query(GitHubRepo).filter(
        GitHubRepo.id == repo_id,
        GitHubRepo.project_id == project_id
    ).first()
    if not repo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GitHub repository not found"
        )

    db.delete(repo)
    db.commit()
    return None
