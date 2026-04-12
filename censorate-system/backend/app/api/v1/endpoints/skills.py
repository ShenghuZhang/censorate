"""Skills API endpoints - manage AI Agent skills."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import get_db
from app.services.skill_service import SkillService

router = APIRouter()
skill_service = SkillService()


@router.get("/skills")
def list_skills():
    """
    List all available AI Agent skills.

    Returns a list of skills with metadata including name, description,
    and category.
    """
    skills = skill_service.get_skills()
    return {
        "count": len(skills),
        "skills": [skill.to_dict() for skill in skills]
    }


@router.get("/skills/categories")
def list_skill_categories():
    """
    List all skill categories.

    Returns a list of unique category names.
    """
    categories = skill_service.get_skill_categories()
    return {"categories": categories}


@router.get("/skills/summary")
def get_skills_summary():
    """
    Get summary statistics about available skills.

    Returns count, categories, and sample skills.
    """
    return skill_service.get_skills_summary()


@router.get("/skills/{skill_name}")
def get_skill(skill_name: str):
    """
    Get detailed information about a specific skill.

    Includes full skill content and metadata.
    """
    skill = skill_service.get_skill(skill_name)
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill '{skill_name}' not found"
        )

    return {
        "name": skill.name,
        "description": skill.description,
        "content": skill.content,
        "metadata": skill.metadata,
        "file_path": skill.file_path
    }


@router.get("/skills/category/{category}")
def list_skills_by_category(category: str):
    """
    List skills in a specific category.

    Args:
        category: Category name to filter by.
    """
    skills = skill_service.get_skills_by_category(category)
    return {
        "category": category,
        "count": len(skills),
        "skills": [skill.to_dict() for skill in skills]
    }


@router.get("/skills/search/{query}")
def search_skills(query: str):
    """
    Search skills by name or description.

    Args:
        query: Search query string.
    """
    skills = skill_service.search_skills(query)
    return {
        "query": query,
        "count": len(skills),
        "skills": [skill.to_dict() for skill in skills]
    }


@router.post("/skills/reload")
def reload_skills():
    """
    Reload all skills from disk.

    This should be called after adding or modifying skills.
    """
    skills = skill_service.reload_skills()
    return {
        "status": "success",
        "message": "Skills reloaded successfully",
        "count": len(skills),
        "skills": [skill.to_dict() for skill in skills]
    }


@router.post("/skills/{skill_name}/execute")
def execute_skill(skill_name: str, input_data: dict):
    """
    Execute a skill with the given input data.

    Args:
        skill_name: Name of the skill to execute.
        input_data: Input data for the skill.
    """
    result = skill_service.execute_skill(skill_name, input_data)
    return result
