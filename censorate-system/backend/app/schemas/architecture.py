from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class FileSpec(BaseModel):
    path: str
    content_description: str
    language: str
    is_config: bool = False
    depends_on: List[str] = []


class ArchitectureOutput(BaseModel):
    project_name: str
    file_tree: List[FileSpec]
    backend_dependencies: List[str] = []
    frontend_dependencies: List[str] = []
    environment_variables: List[Dict[str, str]] = []
    database_models: List[Dict[str, Any]] = []
    docker_config: Optional[Dict[str, Any]] = None
