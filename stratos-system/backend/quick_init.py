#!/usr/bin/env python
"""Quick initialization script."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import Base, engine, SessionLocal
from app.core.security import get_password_hash
from app.models.user import User


def quick_init():
    """Quick initialization function."""
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

    db = SessionLocal()

    try:
        # Check if admin user exists
        admin_user = db.query(User).filter(User.email == "admin@stratos.com").first()

        if not admin_user:
            print("Creating admin user...")
            admin = User(
                email="admin@stratos.com",
                name="Admin User",
                hashed_password=get_password_hash("admin123"),
                is_active=True,
                is_superuser=True
            )
            db.add(admin)
            print("Admin user created successfully!")

        # Check if test user exists
        test_user = db.query(User).filter(User.email == "test@stratos.com").first()

        if not test_user:
            print("Creating test user...")
            test = User(
                email="test@stratos.com",
                name="Test User",
                hashed_password=get_password_hash("test123"),
                is_active=True,
                is_superuser=False
            )
            db.add(test)
            print("Test user created successfully!")

        db.commit()

    except Exception as e:
        print(f"Error initializing users: {e}")
        db.rollback()
        raise
    finally:
        db.close()

    print("\n✅ Database initialized successfully!")
    print("📦 Admin user: admin@stratos.com / admin123")
    print("👤 Test user: test@stratos.com / test123")


if __name__ == "__main__":
    quick_init()
