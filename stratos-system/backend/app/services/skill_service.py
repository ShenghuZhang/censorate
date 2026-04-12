"""Skill Service - manages AI Agent skills.

Provides functionality to load, query, and execute AI Agent skills.
"""

from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from app.utils.skill_loader import get_skill_loader, Skill
from app.core.exceptions import NotFoundException


class SkillService:
    """Service for managing AI Agent skills."""

    def __init__(self):
        """Initialize skill service with skill loader."""
        self.skill_loader = get_skill_loader()

    def get_skills(self) -> List[Skill]:
        """Get all available skills.

        Returns:
            List of all loaded skills.
        """
        return self.skill_loader.get_all_skills()

    def get_skill(self, name: str) -> Optional[Skill]:
        """Get a single skill by name.

        Args:
            name: Skill name to retrieve.

        Returns:
            Skill instance or None if not found.
        """
        return self.skill_loader.get_skill(name)

    def get_skill_or_raise(self, name: str) -> Skill:
        """Get a single skill by name or raise exception.

        Args:
            name: Skill name to retrieve.

        Returns:
            Skill instance.

        Raises:
            NotFoundException: If skill not found.
        """
        skill = self.skill_loader.get_skill(name)
        if not skill:
            raise NotFoundException(f"Skill '{name}' not found")
        return skill

    def get_skills_by_category(self, category: str) -> List[Skill]:
        """Get skills by category.

        Args:
            category: Category to filter by.

        Returns:
            List of skills in the specified category.
        """
        return self.skill_loader.get_skills_by_category(category)

    def search_skills(self, query: str) -> List[Skill]:
        """Search skills by name or description.

        Args:
            query: Search query string.

        Returns:
            List of skills matching the search query.
        """
        query = query.lower()
        return [
            skill for skill in self.skill_loader.get_all_skills()
            if query in skill.name.lower() or query in skill.description.lower()
        ]

    def reload_skills(self) -> List[Skill]:
        """Reload all skills from disk.

        Returns:
            List of reloaded skills.
        """
        self.skill_loader.reload_skills()
        return self.skill_loader.get_all_skills()

    def execute_skill(
        self,
        name: str,
        input_data: Dict[str, Any],
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """Execute a skill.

        Args:
            name: Skill name to execute.
            input_data: Input data for the skill.
            db: Optional database session.

        Returns:
            Skill execution result.
        """
        skill = self.get_skill_or_raise(name)

        # TODO: Implement actual skill execution
        return {
            "skill": name,
            "success": True,
            "input": input_data,
            "result": {"message": "Skill execution not implemented yet"},
            "skill_metadata": skill.to_dict()
        }

    def get_skill_categories(self) -> List[str]:
        """Get all available skill categories.

        Returns:
            List of unique skill categories.
        """
        categories = set()
        for skill in self.skill_loader.get_all_skills():
            category = skill.metadata.get("category", "uncategorized")
            categories.add(category)
        return sorted(list(categories))

    def get_skills_summary(self) -> Dict[str, Any]:
        """Get summary statistics about skills.

        Returns:
            Summary statistics.
        """
        skills = self.skill_loader.get_all_skills()
        categories = self.get_skill_categories()

        category_counts: Dict[str, int] = {}
        for category in categories:
            category_counts[category] = len(self.get_skills_by_category(category))

        return {
            "total_skills": len(skills),
            "categories": categories,
            "category_counts": category_counts,
            "sample_skills": [
                {"name": skill.name, "description": skill.description}
                for skill in skills[:5]
            ]
        }
