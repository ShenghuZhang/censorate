"""Database migration to add missing columns for requirements enhancement."""

from app.core.database import SessionLocal, engine, init_db
from sqlalchemy import text

def migrate():
    """Run database migration."""
    db = SessionLocal()
    try:
        # First, initialize all tables through SQLAlchemy
        print("Initializing all tables through SQLAlchemy...")
        init_db()
        print("Tables initialized\n")

        # Check and add missing columns to requirements table
        print("Checking requirements table...")

        # Get existing columns
        result = db.execute(text("PRAGMA table_info(requirements)"))
        existing_columns = [row[1] for row in result]
        print(f"Existing columns: {existing_columns}")

        # Columns to add
        new_columns = [
            ("expected_completion_at", "DATETIME", ""),
            ("last_forward_assigned_to", "VARCHAR(255)", ""),
            ("last_forward_expected_at", "DATETIME", ""),
            ("last_forward_status", "VARCHAR(50)", ""),
            ("return_count", "INTEGER", "DEFAULT 0"),
            ("last_returned_at", "DATETIME", ""),
        ]

        for col_name, col_type, col_default in new_columns:
            if col_name not in existing_columns:
                print(f"Adding column: {col_name}")
                alter_sql = f"ALTER TABLE requirements ADD COLUMN {col_name} {col_type} {col_default}"
                db.execute(text(alter_sql))
                db.commit()
                print(f"  Added {col_name}")
            else:
                print(f"  Column {col_name} already exists")

        print("\nMigration completed successfully!")

    except Exception as e:
        print(f"Error during migration: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
