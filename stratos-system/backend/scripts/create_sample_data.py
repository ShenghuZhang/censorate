#!/usr/bin/env python
"""Create sample requirements data."""

import sys
import os
from uuid import uuid4

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import Base, engine, SessionLocal
from app.models.project import Project
from app.models.requirement import Requirement


def create_sample_data():
    """Create sample requirements."""
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Get the first project
        project = db.query(Project).first()
        if not project:
            print("No project found!")
            return

        print(f"Using project: {project.name}")

        # Update project type to match frontend expectations
        if project.project_type == "software":
            project.project_type = "technical"
            db.commit()
            print("Updated project type to 'technical'")

        # Delete existing requirements
        db.query(Requirement).filter(Requirement.project_id == project.id).delete()
        db.commit()

        # Create sample requirements using new 4-state system
        sample_requirements = [
            {
                "title": "User login system",
                "description": "Create user authentication and authorization system",
                "status": "backlog",
                "priority": "high",
                "req_number": 1
            },
            {
                "title": "Dashboard design",
                "description": "Design and implement the main dashboard UI",
                "status": "todo",
                "priority": "medium",
                "req_number": 2
            },
            {
                "title": "API endpoints",
                "description": "Create REST API endpoints for all resources",
                "status": "todo",
                "priority": "high",
                "req_number": 3
            }
        ]

        for req_data in sample_requirements:
            requirement = Requirement(
                id=str(uuid4()),
                project_id=project.id,
                req_number=req_data["req_number"],
                title=req_data["title"],
                description=req_data["description"],
                status=req_data["status"],
                priority=req_data["priority"],
                source="manual",
                created_by="demo-user",
                lark_editable=False,
                return_count=0
            )
            db.add(requirement)

        db.commit()
        print(f"\n✅ Created {len(sample_requirements)} sample requirements!")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_sample_data()
