#!/usr/bin/env python
"""Create users with valid email domains."""

import sys
import os
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import Base, engine, SessionLocal
from app.core.security import get_password_hash
from app.models.user import User


def create_valid_users():
    """Create users with valid email domains."""
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Delete any existing invalid users
        db.query(User).filter(User.email.like("%@stratos.local")).delete()
        db.commit()

        # Create test user with valid domain
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

        # Create admin user with valid domain
        admin_user = db.query(User).filter(User.email == "admin@example.com").first()
        if not admin_user:
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
            print("Admin user created: admin@example.com / admin123")

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
    create_valid_users()
