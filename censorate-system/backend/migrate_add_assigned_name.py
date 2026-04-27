"""
Migration: Add assigned_to_name to requirements
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import engine
from sqlalchemy import text


def migrate():
    """Run migration"""
    with engine.connect() as conn:
        try:
            print("Adding assigned_to_name column to requirements...")
            conn.execute(
                text("ALTER TABLE requirements ADD COLUMN assigned_to_name VARCHAR(255)")
            )
            conn.commit()
            print("Migration completed successfully!")

        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("Column already exists, skipping migration")
            else:
                print(f"Error: {e}")
                raise


if __name__ == "__main__":
    print("Running migration...")
    migrate()
