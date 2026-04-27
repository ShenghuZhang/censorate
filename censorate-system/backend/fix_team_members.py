"""
Fix team members - ensure project has human users as team members
"""
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.project import Project
from app.models.team_member import TeamMember


def fix_team_members():
    db = SessionLocal()
    try:
        print("=" * 60)
        print("Fixing team members...")
        print("=" * 60)

        # Get users
        users = db.query(User).filter(
            User.email.in_(["alex.kim@example.com", "julian.rossi@example.com", "sarah.chen@example.com"])
        ).all()

        print(f"\nFound users: {[u.name for u in users]}")

        # Get or create project
        project = db.query(Project).filter(
            Project.name == "示例项目",
            Project.archived_at.is_(None)
        ).first()

        if not project:
            print("Project not found!")
            return

        print(f"\nUsing project: {project.name} [ID: {project.id}]")

        # Check existing team members
        existing_members = db.query(TeamMember).filter(
            TeamMember.project_id == project.id,
            TeamMember.archived_at.is_(None)
        ).all()

        print(f"\nExisting team members: {[m.nickname for m in existing_members]}")

        # Add human users as team members if not present
        for user in users:
            existing = db.query(TeamMember).filter(
                TeamMember.project_id == project.id,
                TeamMember.email == user.email,
                TeamMember.archived_at.is_(None)
            ).first()

            if not existing:
                member = TeamMember(
                    id=uuid.uuid4(),
                    project_id=project.id,
                    name=user.name,
                    nickname=user.name.split()[0],
                    email=user.email,
                    role="product_manager" if user.name == "Alex Kim" else "developer",
                    type="human"
                )
                db.add(member)
                print(f"Added team member: {user.name}")
            else:
                print(f"Team member already exists: {user.name}")

        # Add AI agents if not present
        ai_agents = [
            ("需求分析助手", "analysis"),
            ("方案设计助手", "design"),
            ("代码开发助手", "development"),
            ("测试助手", "testing")
        ]

        for ai_name, ai_role in ai_agents:
            existing = db.query(TeamMember).filter(
                TeamMember.project_id == project.id,
                TeamMember.name == ai_name,
                TeamMember.archived_at.is_(None)
            ).first()

            if not existing:
                member = TeamMember(
                    id=uuid.uuid4(),
                    project_id=project.id,
                    name=ai_name,
                    nickname=ai_name,
                    role=ai_role,
                    type="ai"
                )
                db.add(member)
                print(f"Added AI agent: {ai_name}")
            else:
                print(f"AI agent already exists: {ai_name}")

        db.commit()

        # Verify
        final_members = db.query(TeamMember).filter(
            TeamMember.project_id == project.id,
            TeamMember.archived_at.is_(None)
        ).all()

        print("\n" + "=" * 60)
        print("Final team members:")
        print("=" * 60)
        for m in final_members:
            print(f"  [{m.type}] {m.nickname} ({m.role})")

        print("\nDone!")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    fix_team_members()
