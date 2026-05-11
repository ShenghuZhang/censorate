"""Skills catalog service — lists available skills for the Censorate Hub.

Skill injection into chat requests is no longer done here. Instead,
skill_manager.py installs skills directly into Hermes as hub-installed
skills, and Hermes loads them natively from its skills directory.
"""

from __future__ import annotations

from typing import Dict, List, Optional
from sqlalchemy.orm import Session


class SkillCatalogService:
    """Lists available skills from the Censorate skill hub catalog."""

    def list_available_skills(self, db: Optional[Session] = None) -> List[Dict[str, str]]:
        """List all published, non-archived skills in the catalog."""
        from app.models.skill import Skill
        from app.core.database import SessionLocal

        local_db = db or SessionLocal()
        try:
            skills = local_db.query(Skill).filter(
                Skill.is_published == True,
                Skill.is_archived == False
            ).order_by(Skill.name).all()

            return [
                {
                    "id": s.slug,
                    "name": s.name,
                    "description": s.description or ""
                }
                for s in skills
            ]
        finally:
            if db is None:
                local_db.close()

    def build_hub_skills_message(self, capabilities: List[str]) -> Optional[Dict[str, str]]:
        """Build a system message listing hub skills available to the agent.

        Only returns the skill name + one-line description — just enough
        for the model to know the skill exists and decide to load it.
        Returns None if the agent has no hub skills assigned.
        """
        if not capabilities:
            return None

        from app.models.skill import Skill
        from app.core.database import SessionLocal

        db = SessionLocal()
        try:
            skills = db.query(Skill).filter(
                Skill.slug.in_(capabilities),
                Skill.is_published == True,
                Skill.is_archived == False,
            ).all()

            if not skills:
                return None

            lines = []
            for s in skills:
                lines.append(f"- {s.name}: {s.description or 'No description'}")

            content = (
                "Hub skills available (use skill_load to get full content):\n"
                + "\n".join(lines)
            )
            return {"role": "system", "content": content}
        finally:
            db.close()


_catalog_service: SkillCatalogService | None = None


def get_skill_catalog_service() -> SkillCatalogService:
    global _catalog_service
    if _catalog_service is None:
        _catalog_service = SkillCatalogService()
    return _catalog_service
