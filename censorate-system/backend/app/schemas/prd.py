from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class Feature(BaseModel):
    name: str
    description: str
    priority: str  # P0, P1, P2
    acceptance_criteria: List[str]


class DataModel(BaseModel):
    name: str
    fields: List[Dict[str, str]]
    relationships: List[str]


class APIEndpoint(BaseModel):
    method: str
    path: str
    description: str
    request_body: Optional[Dict[str, Any]] = None
    response: Dict[str, Any]


class PRDOutput(BaseModel):
    project_name: str
    description: str
    features: List[Feature]
    user_stories: List[str]
    data_models: List[DataModel]
    api_endpoints: List[APIEndpoint]
    frontend_routes: List[Dict[str, str]]
    tech_stack_decisions: List[str]
