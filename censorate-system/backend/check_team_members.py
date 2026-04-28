"""Check team members and their IDs."""

from app.core.database import SessionLocal
from app.models.team_member import TeamMember


def check_team_members():
    """Check team members in the database."""
    db = SessionLocal()
    try:
        # Print all team members
        print("=== Team Members ===")
        members = db.query(TeamMember).all()
        for member in members:
            print(f"  {member.id} - {member.name} ({member.email})")
            print(f"    Type: {member.type}, Role: {member.role}")
            print()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    check_team_members()
