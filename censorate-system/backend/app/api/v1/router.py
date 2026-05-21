from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, templates, generation_projects, pipeline, generated_files, github
)

api_router = APIRouter()

api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(templates.router, prefix="/templates", tags=["templates"])
api_router.include_router(generation_projects.router, prefix="/generation-projects", tags=["generation-projects"])
api_router.include_router(pipeline.router, tags=["pipeline"])
api_router.include_router(generated_files.router, tags=["generated-files"])
api_router.include_router(github.router, tags=["github"])
