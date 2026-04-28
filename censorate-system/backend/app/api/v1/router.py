from fastapi import APIRouter
from app.api.v1.endpoints import (
    projects, requirements, tasks, agents, test_cases, auth, skills, automation, analytics, remote_agents, github_repos, profile, notifications
)

api_router = APIRouter()

api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(requirements.router, tags=["requirements"])
api_router.include_router(tasks.router, tags=["tasks"])
api_router.include_router(agents.router, tags=["agents"])
api_router.include_router(test_cases.router, tags=["test-cases"])
api_router.include_router(skills.router, tags=["skills"])
api_router.include_router(automation.router, tags=["automation"])
api_router.include_router(analytics.router, tags=["analytics"])
api_router.include_router(remote_agents.router, tags=["remote-agents"])
api_router.include_router(github_repos.router, tags=["github-repos"])
api_router.include_router(profile.router, tags=["profile"])
api_router.include_router(notifications.router, tags=["notifications"])
