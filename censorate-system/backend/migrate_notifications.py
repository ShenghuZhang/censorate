"""Database migration to add notification tables."""

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

        # Verify tables were created
        print("Checking for notification tables...")
        if engine.url.drivername.startswith('sqlite'):
            result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%notification%'"))
        else:
            # For PostgreSQL
            result = db.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tablename LIKE '%notification%'"))

        tables = [row[0] for row in result]
        print(f"Notification-related tables: {tables}\n")

        print("Migration completed successfully!")

    except Exception as e:
        print(f"Error during migration: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
