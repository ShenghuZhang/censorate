#!/usr/bin/env python
"""Test password verification."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.security import verify_password, get_password_hash
from app.core.database import SessionLocal
from app.models.user import User


def test_password():
    """Test password verification."""
    db = SessionLocal()

    try:
        user = db.query(User).filter(User.email == "test@example.com").first()
        if user:
            print(f"User found: {user.email}")
            print(f"Stored hash: {user.hashed_password[:50]}...")

            test_hash = get_password_hash("password123")
            print(f"\nNew hash for 'password123': {test_hash[:50]}...")

            result = verify_password("password123", user.hashed_password)
            print(f"\nVerification result: {result}")

            if not result:
                print("\nUpdating password...")
                user.hashed_password = test_hash
                db.commit()
                print("Password updated!")

                result2 = verify_password("password123", test_hash)
                print(f"New verification result: {result2}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    test_password()
