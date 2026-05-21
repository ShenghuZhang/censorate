from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import Settings

settings = Settings.get()

# For SQLite, we need to use connect_args={"check_same_thread": False}
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency injection for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    from app.models import (
        user, template, generation_project, generated_file, pipeline_step, github_repo
    )
    from app.models.base import BaseModel
    BaseModel.metadata.create_all(bind=engine)

    from app.seed_data.templates import seed_templates
    seed_templates()


def migrate_to_v2():
    """Drop all old tables and create new schema for v2."""
    from app.models.base import BaseModel
    BaseModel.metadata.drop_all(bind=engine)
    init_db()
