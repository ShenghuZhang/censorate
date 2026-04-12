"""Skill loader for Stratos AI Agent system.

Loads and manages skills from the skills directory.
Skills are defined in SKILL.md files with frontmatter.
"""

import os
import re
from typing import Dict, List, Optional, Any
from pathlib import Path
import frontmatter


class Skill:
    """Represents a single AI Agent skill."""

    def __init__(
        self,
        name: str,
        description: str,
        file_path: str,
        content: str,
        metadata: Dict[str, Any] = None
    ):
        """Initialize a skill."""
        self.name = name
        self.description = description
        self.file_path = file_path
        self.content = content
        self.metadata = metadata or {}

    def __repr__(self):
        return f"<Skill {self.name}>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata
        }


class SkillLoader:
    """Loads and manages skills from the skills directory."""

    SKILL_FILE_PATTERN = re.compile(r"SKILL\.md", re.IGNORECASE)
    SKILL_DIR = os.path.join(os.path.dirname(__file__), "..", "skills")

    def __init__(self):
        """Initialize skill loader."""
        self._skills: Dict[str, Skill] = {}
        self._loaded = False

    def load_skills(self) -> Dict[str, Skill]:
        """Load all skills from skills directory.

        Returns:
            Dictionary of skills keyed by name.
        """
        if self._loaded and self._skills:
            return self._skills

        self._skills = {}
        skills_dir = Path(self.SKILL_DIR)

        if not skills_dir.exists():
            return self._skills

        # Traverse all subdirectories
        for skill_file in skills_dir.rglob("SKILL.md"):
            try:
                skill = self._load_single_skill(skill_file)
                if skill:
                    self._skills[skill.name] = skill
            except Exception as e:
                print(f"Error loading skill from {skill_file}: {e}")

        self._loaded = True
        return self._skills

    def _load_single_skill(self, file_path: Path) -> Optional[Skill]:
        """Load a single skill from a SKILL.md file."""
        with open(file_path, "r", encoding="utf-8") as f:
            post = frontmatter.load(f)

        # Extract metadata from frontmatter
        name = post.get("name")
        description = post.get("description")

        if not name or not description:
            print(f"Skill {file_path} missing name or description")
            return None

        return Skill(
            name=name,
            description=description,
            file_path=str(file_path),
            content=post.content.strip(),
            metadata=dict(post.metadata)
        )

    def get_skill(self, name: str) -> Optional[Skill]:
        """Get a skill by name.

        Args:
            name: Skill name to retrieve.

        Returns:
            Skill instance or None if not found.
        """
        if not self._loaded:
            self.load_skills()

        return self._skills.get(name)

    def get_all_skills(self) -> List[Skill]:
        """Get all loaded skills.

        Returns:
            List of all skill instances.
        """
        if not self._loaded:
            self.load_skills()

        return list(self._skills.values())

    def get_skills_by_category(self, category: str) -> List[Skill]:
        """Get skills by category.

        Args:
            category: Category to filter by.

        Returns:
            List of skills in the specified category.
        """
        if not self._loaded:
            self.load_skills()

        category = category.lower()
        return [
            skill for skill in self._skills.values()
            if skill.metadata.get("category", "").lower() == category
        ]

    def reload_skills(self) -> Dict[str, Skill]:
        """Reload all skills from disk.

        Returns:
            Dictionary of reloaded skills.
        """
        self._loaded = False
        return self.load_skills()


# Singleton instance
_skill_loader = None


def get_skill_loader() -> SkillLoader:
    """Get singleton instance of SkillLoader.

    Returns:
        SkillLoader instance.
    """
    global _skill_loader
    if _skill_loader is None:
        _skill_loader = SkillLoader()
        _skill_loader.load_skills()

    return _skill_loader


if __name__ == "__main__":
    # Test loading skills
    loader = get_skill_loader()
    skills = loader.get_all_skills()

    print(f"Loaded {len(skills)} skills:")
    for skill in skills:
        print(f"\n- {skill.name}: {skill.description}")
