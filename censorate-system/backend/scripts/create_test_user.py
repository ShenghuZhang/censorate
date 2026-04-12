#!/usr/bin/env python
"""Create a test user directly."""

import sys
import os
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import Base, engine, SessionLocal
from app.core.security import get_password_hash
from app.models.user import User


def create_test_user():
    """Create test user directly."""
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Check if test user exists
        test_user = db.query(User).filter(User.email == "test@example.com").first()

        if not test_user:
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
            db.commit()
            print("Test user created: test@example.com / password123")
        else:
            print("Test user already exists.")

        # Also create admin user
        admin_user = db.query(User).filter(User.email == "admin@stratos.local").first()
        if not admin_user:
            print("Creating admin user...")
            admin_user = User(
                id=str(uuid.uuid4()),
                email="admin@stratos.local",
                name="Admin User",
                hashed_password=get_password_hash("admin123"),
                is_active=True,
                is_superuser=True
            )
            db.add(admin_user)
            db.commit()
            print("Admin user created: admin@stratos.local / admin123")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_test_user()
