#!/usr/bin/env python
"""Register a test user directly."""

import sys
import os
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import Base, engine, SessionLocal
from app.core.security import get_password_hash
from app.models.user import User


def register_test_user():
    """Register test user directly."""
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Delete existing test users
        db.query(User).filter(User.email.in_(["test@example.com", "admin@example.com"])).delete()
        db.commit()

        # Create test user
        print("Creating test user...")
        test_user = User(
            id=str(uuid.uuid4()),
            email="test@example.com",
            name="Test User",
            hashed_password=get_password_hash("password123"),
            is_active=True,
            is_superuser=False
        )
        db.add(test_user)

        # Create admin user
        print("Creating admin user...")
        admin_user = User(
            id=str(uuid.uuid4()),
            email="admin@example.com",
            name="Admin User",
            hashed_password=get_password_hash("admin123"),
            is_active=True,
            is_superuser=True
        )
        db.add(admin_user)

        db.commit()
        print("\n✅ Users created successfully!")
        print("\nAvailable accounts:")
        print("  - test@example.com / password123")
        print("  - admin@example.com / admin123")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    register_test_user()
