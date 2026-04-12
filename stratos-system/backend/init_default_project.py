#!/usr/bin/env python
"""Initialize default project and agents with proper UUIDs."""

import sys
import os
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import Base, engine, SessionLocal
from app.models.project import Project
from app.models.team_member import TeamMember


def init_default_project():
    """Initialize default project and agents with proper UUIDs."""
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Check if default project exists (look by slug instead of fixed ID)
        dummy_project = db.query(Project).filter(Project.slug == "default-project").first()

        if not dummy_project:
            print("Creating default project...")
            dummy_project = Project(
                id=str(uuid.uuid4()),
                name="Default Project",
                slug="default-project",
                description="The default project for Stratos",
                project_type="software",
                created_by="default-user",
                settings={}
            )
            db.add(dummy_project)
            db.flush()  # Flush to get the ID
            print(f"Default project created with ID: {dummy_project.id}")
        else:
            print(f"Default project already exists with ID: {dummy_project.id}")

        # Check if default agents exist
        existing_agents = db.query(TeamMember).filter(
            TeamMember.project_id == dummy_project.id,
            TeamMember.type == "ai"
        ).all()

        existing_roles = {a.role for a in existing_agents}

        default_agents = [
            {
                "name": "Analysis Agent",
                "nickname": "Alex",
                "role": "analysis_agent",
                "skills": ["requirements_analysis", "stakeholder_interview", "risk_identification"],
                "memory_enabled": True
            },
            {
                "name": "Design Agent",
                "nickname": "Diana",
                "role": "design_agent",
                "skills": ["system_design", "architecture", "prototyping"],
                "memory_enabled": True
            },
            {
                "name": "Development Agent",
                "nickname": "Devon",
                "role": "development_agent",
                "skills": ["coding", "code_review", "testing"],
                "memory_enabled": True
            },
            {
                "name": "Testing Agent",
                "nickname": "Tina",
                "role": "testing_agent",
                "skills": ["test_design", "quality_assurance", "bug_reporting"],
                "memory_enabled": True
            }
        ]

        for agent_data in default_agents:
            if agent_data["role"] not in existing_roles:
                print(f"Creating {agent_data['name']}...")
                agent = TeamMember(
                    id=str(uuid.uuid4()),
                    project_id=dummy_project.id,
                    name=agent_data["name"],
                    nickname=agent_data["nickname"],
                    role=agent_data["role"],
                    type="ai",
                    status="active",
                    skills=agent_data["skills"],
                    memory_enabled=agent_data["memory_enabled"],
                    deepagent_config={}
                )
                db.add(agent)

        db.commit()
        print("\n✅ Default project and agents initialized successfully!")
        print(f"📦 Project ID: {dummy_project.id}")
        print(f"📦 Project Slug: {dummy_project.slug}")

        # Save project ID to a file for frontend reference
        with open(os.path.join(os.path.dirname(__file__), '.project_id'), 'w') as f:
            f.write(str(dummy_project.id))
        print(f"📝 Project ID saved to .project_id")

    except Exception as e:
        print(f"Error initializing: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # Remove old database to start fresh
    db_path = os.path.join(os.path.dirname(__file__), 'database.db')
    if os.path.exists(db_path):
        print("Removing old database...")
        os.remove(db_path)

    init_default_project()
