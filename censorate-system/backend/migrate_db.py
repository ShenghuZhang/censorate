"""Database migration to add missing remote_agent columns."""

from app.core.database import SessionLocal, engine
from sqlalchemy import text

def migrate():
    """Run database migration."""
    db = SessionLocal()
    try:
        # Check and add missing columns
        print("Checking remote_agents table...")

        # Get existing columns
        result = db.execute(text("PRAGMA table_info(remote_agents)"))
        existing_columns = [row[1] for row in result]
        print(f"Existing columns: {existing_columns}")

        # Columns to add
        new_columns = [
            ("consecutive_failures", "INTEGER", "DEFAULT 0"),
            ("last_alert_sent_at", "DATETIME", ""),
            ("alert_acknowledged", "BOOLEAN", "DEFAULT 0"),
            ("alert_acknowledged_at", "DATETIME", ""),
            ("alert_acknowledged_by", "VARCHAR(255)", ""),
            ("alert_after_consecutive_failures", "INTEGER", "DEFAULT 3"),
            ("alert_after_offline_minutes", "INTEGER", "DEFAULT 5"),
            ("warning_latency_ms", "INTEGER", "DEFAULT 1000"),
            ("critical_latency_ms", "INTEGER", "DEFAULT 2000"),
        ]

        for col_name, col_type, col_default in new_columns:
            if col_name not in existing_columns:
                print(f"Adding column: {col_name}")
                alter_sql = f"ALTER TABLE remote_agents ADD COLUMN {col_name} {col_type} {col_default}"
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
