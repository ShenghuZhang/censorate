"""
Check database data
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.project import Project
from app.models.team_member import TeamMember
from app.models.user import User


def check_data():
    db = SessionLocal()
    try:
        print("=" * 60)
        print("Checking database data...")
        print("=" * 60)

        # Check users
        print("\n[1] Users:")
        users = db.query(User).all()
        for user in users:
            print(f"  - {user.name} ({user.email}) [ID: {user.id}]")

        # Check projects
        print("\n[2] Projects:")
        projects = db.query(Project).all()
        for project in projects:
            print(f"  - {project.name} [ID: {project.id}]")

            # Check team members for this project
            print("\n[3] Team Members for project:")
            members = db.query(TeamMember).filter(
                TeamMember.project_id == project.id,
                TeamMember.archived_at.is_(None)
            ).all()
            for member in members:
                print(f"  - [{member.type}] {member.nickname} ({member.role}) [ID: {member.id}]")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    check_data()
