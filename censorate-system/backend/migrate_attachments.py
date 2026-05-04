"""Migration script to add attachments table."""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import Base, engine
from app.models.attachment import Attachment


def migrate():
    """Run the migration."""
    print("Creating attachments table...")
    Attachment.__table__.create(bind=engine, checkfirst=True)
    print("Attachments table created successfully!")


if __name__ == "__main__":
    migrate()
