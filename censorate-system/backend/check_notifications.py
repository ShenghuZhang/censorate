"""Check if notifications are being created in the database."""

from app.core.database import SessionLocal
from app.models.notification import Notification
from app.models.user import User


def check_notifications():
    """Check notifications in the database."""
    db = SessionLocal()
    try:
        # Print all users
        print("=== Users ===")
        users = db.query(User).all()
        for user in users:
            print(f"  {user.id} - {user.email} ({user.name})")

        # Print all notifications
        print("\n=== Notifications ===")
        notifications = db.query(Notification).all()
        if not notifications:
            print("  No notifications found!")
        else:
            for n in notifications:
                print(f"  {n.id} - {n.type}: {n.title}")
                print(f"    To user: {n.user_id}")
                print(f"    Read: {n.read}")
                print(f"    Created: {n.created_at}")
                print()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    check_notifications()
