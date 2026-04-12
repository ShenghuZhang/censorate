"""Initialize database with default user."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, engine
from app.core.security import get_password_hash


def init_db():
    """Initialize database with default user."""
    db = SessionLocal()

    try:
        # Create users table if not exists
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            avatar_url TEXT,
            hashed_password TEXT,
            is_active BOOLEAN DEFAULT 1,
            is_superuser BOOLEAN DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            archived_at DATETIME
        );
        """
        db.execute(create_table_sql)

        # Check if default user exists
        existing_user = db.execute(
            "SELECT * FROM users WHERE email = 'admin@stratos.local'"
        ).fetchone()

        if not existing_user:
            # Create default admin user
            from app.core.database import Base
            from app.models.user import User

            admin_user = User(
                email="admin@stratos.local",
                name="Admin User",
                hashed_password=get_password_hash("admin123"),
                is_active=True,
                is_superuser=True
            )
            db.add(admin_user)

            # Create a test user
            test_user = User(
                email="test@stratos.local",
                name="Test User",
                hashed_password=get_password_hash("test123"),
                is_active=True,
                is_superuser=False
            )
            db.add(test_user)

            db.commit()
            print("Database initialized successfully!")
            print("Admin user created: admin@stratos.local / admin123")
            print("Test user created: test@stratos.local / test123")
        else:
            print("Default user already exists.")

    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
