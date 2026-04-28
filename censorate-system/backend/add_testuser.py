"""Add testuser@example.com as a user and team member."""

import uuid
from app.core.database import SessionLocal, init_db
from app.models.user import User
from app.models.team_member import TeamMember
from app.models.project import Project
from datetime import datetime


def add_testuser():
    """Add testuser@example.com to the database."""
    # Initialize tables first
    init_db()

    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == "testuser@example.com").first()
        if existing_user:
            print(f"User testuser@example.com already exists with id: {existing_user.id}")
            user = existing_user
        else:
            # Create new user
            user = User(
                id=uuid.uuid4(),
                email="testuser@example.com",
                name="Test User",
                is_active=True,
                is_superuser=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"Created user: {user.email} (id: {user.id})")

        # Find the sample project ("示例项目")
        project = db.query(Project).filter(Project.name == "示例项目").first()
        if not project:
            print("Sample project not found, looking for any project...")
            project = db.query(Project).first()

        if not project:
            print("No project found!")
            return

        print(f"Using project: {project.name} (id: {project.id})")

        # Check if already a team member
        existing_member = db.query(TeamMember).filter(
            TeamMember.project_id == project.id,
            TeamMember.email == "testuser@example.com"
        ).first()

        if existing_member:
            print(f"Already a team member of {project.name}")
            return

        # Add as team member
        member = TeamMember(
            id=uuid.uuid4(),
            project_id=project.id,
            name="Test User",
            nickname="TestUser",
            email="testuser@example.com",
            role="developer",
            type="human",
            status="active",
            joined_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(member)
        db.commit()
        db.refresh(member)

        print(f"Added as team member to {project.name} with role: developer")
        print("✅ Done!")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    add_testuser()
