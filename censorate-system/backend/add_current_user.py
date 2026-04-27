"""
Add current user (you) to the system as a real user
"""
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.project import Project
from app.models.team_member import TeamMember


def add_current_user():
    db = SessionLocal()
    try:
        print("=" * 60)
        print("Adding current user (you) to the system...")
        print("=" * 60)

        # Check if you already exist
        your_email = "you@example.com"
        you = db.query(User).filter(User.email == your_email).first()

        if not you:
            you = User(
                id=uuid.uuid4(),
                email=your_email,
                name="你",
                is_superuser=True
            )
            db.add(you)
            db.flush()
            print(f"\nCreated user: {you.name} ({you.email})")
        else:
            print(f"\nFound existing user: {you.name} ({you.email})")

        # Get the project
        project = db.query(Project).filter(
            Project.name == "示例项目",
            Project.archived_at.is_(None)
        ).first()

        if not project:
            print("\nProject not found!")
            return

        print(f"\nUsing project: {project.name}")

        # Add you as a team member if not already present
        existing_member = db.query(TeamMember).filter(
            TeamMember.project_id == project.id,
            TeamMember.email == your_email,
            TeamMember.archived_at.is_(None)
        ).first()

        if not existing_member:
            member = TeamMember(
                id=uuid.uuid4(),
                project_id=project.id,
                name=you.name,
                nickname="你",
                email=you.email,
                role="project_manager",
                type="human"
            )
            db.add(member)
            print(f"\nAdded you as team member: {you.name}")
        else:
            print(f"\nYou are already a team member: {existing_member.nickname}")

        db.commit()

        # Verify
        print("\n" + "=" * 60)
        print("All team members:")
        print("=" * 60)
        final_members = db.query(TeamMember).filter(
            TeamMember.project_id == project.id,
            TeamMember.archived_at.is_(None)
        ).all()
        for m in final_members:
            marker = " [YOU]" if m.email == your_email else ""
            print(f"  [{m.type}] {m.nickname} ({m.role}){marker}")

        print("\nDone! Now you are in the system!")
        print(f"\nYou can log in with:")
        print(f"  Email: {your_email}")
        print(f"  Name: {you.name}")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    add_current_user()
