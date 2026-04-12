"""
Tests for SkillService.
"""

import pytest
from unittest.mock import Mock, MagicMock
from sqlalchemy.orm import Session
from app.services.skill_service import SkillService


class TestSkillService:
    """Tests for SkillService functionality."""

    def test_get_skills(self):
        """Test getting all skills."""
        # Setup
        skill_service = SkillService()

        # Execute
        skills = skill_service.get_skills()

        # Verify
        assert isinstance(skills, list)

    def test_get_skill(self):
        """Test getting a specific skill."""
        # Setup
        skill_service = SkillService()
        existing_skills = skill_service.get_skills()

        if existing_skills:
            # Execute
            skill_name = existing_skills[0].name
            skill = skill_service.get_skill(skill_name)

            # Verify
            assert skill is not None
            assert skill.name == skill_name

    def test_search_skills(self):
        """Test searching skills."""
        # Setup
        skill_service = SkillService()

        # Execute
        results = skill_service.search_skills("analysis")

        # Verify
        assert isinstance(results, list)

    def test_execute_skill(self):
        """Test executing a skill."""
        # Setup
        skill_service = SkillService()
        existing_skills = skill_service.get_skills()

        if existing_skills:
            # Execute
            skill_name = existing_skills[0].name
            result = skill_service.execute_skill(skill_name, {"test": "data"})

            # Verify
            assert isinstance(result, dict)
            assert "success" in result
