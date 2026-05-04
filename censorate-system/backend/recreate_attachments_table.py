"""Recreate attachments table with new MinIO structure."""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import Base, engine
from app.models.attachment import Attachment
from sqlalchemy import text


def recreate_table():
    """Drop and recreate attachments table."""
    with engine.begin() as conn:
        # Drop table if exists
        conn.execute(text("DROP TABLE IF EXISTS attachments CASCADE"))
        print("Dropped existing attachments table")

    # Create table
    Attachment.__table__.create(bind=engine, checkfirst=True)
    print("Created new attachments table with MinIO support!")


if __name__ == "__main__":
    recreate_table()
