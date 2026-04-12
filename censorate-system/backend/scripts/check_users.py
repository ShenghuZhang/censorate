#!/usr/bin/env python
"""Check users in database."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.user import User


def check_users():
    """Check users in database."""
    db = SessionLocal()

    try:
        users = db.query(User).all()
        print(f"Total users in database: {len(users)}")
        for user in users:
            print(f"\n  ID: {user.id}")
            print(f"  Email: {user.email}")
            print(f"  Name: {user.name}")
            print(f"  Active: {user.is_active}")
            print(f"  Has password hash: {'Yes' if user.hashed_password else 'No'}")

    except Exception as e:
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    check_users()
