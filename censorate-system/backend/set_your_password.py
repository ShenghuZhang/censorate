"""
Set a password for you user
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash


def set_password():
    db = SessionLocal()
    try:
        your_email = "you@example.com"
        you = db.query(User).filter(User.email == your_email).first()

        if not you:
            print(f"User {your_email} not found!")
            return

        # Set password to "123456"
        you.hashed_password = get_password_hash("123456")
        db.commit()

        print("=" * 60)
        print("Password set successfully!")
        print("=" * 60)
        print(f"\nYou can now log in with:")
        print(f"  Email: {your_email}")
        print(f"  Password: 123456")
        print(f"  Name: {you.name}")
        print("\nOr you can use any email to log in - the system will create the user automatically!")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    set_password()
