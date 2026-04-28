#!/usr/bin/env python3
"""Remove team member you@example.com"""

import sys
sys.path.insert(0, '.')

from app.core.database import SessionLocal
from app.models.project import Project
from app.models.team_member import TeamMember

def main():
    db = SessionLocal()
    try:
        print("=" * 60)
        print("Removing team member you@example.com")
        print("=" * 60)

        # Find sample project
        project = db.query(Project).filter(
            Project.name == "示例项目"
        ).first()

        if not project:
            print("\n❌ Sample project not found!")
            return

        print(f"\n✅ Found project: {project.name}")

        # Find the member
        member = db.query(TeamMember).filter(
            TeamMember.project_id == project.id,
            TeamMember.email == "you@example.com"
        ).first()

        if not member:
            print("\n❌ Member you@example.com not found!")
            return

        print(f"\nFound member: {member.name} ({member.email})")
        print(f"Deleting...")

        db.delete(member)
        db.commit()

        print("\n" + "=" * 60)
        print("✅ Member you@example.com removed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
