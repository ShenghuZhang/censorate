"""Seed data for code generation templates."""

DEFAULT_TEMPLATES = [
    {
        "name": "FastAPI + Next.js Monorepo",
        "slug": "fastapi-nextjs",
        "description": "FastAPI backend with Next.js frontend in a monorepo structure. "
                       "Includes PostgreSQL, SQLAlchemy ORM, JWT auth, and Tailwind CSS.",
        "tech_stack": {
            "backend": {"framework": "fastapi", "language": "python", "version": "3.11"},
            "frontend": {"framework": "nextjs", "language": "typescript", "version": "16"},
            "database": "postgresql",
            "orm": "sqlalchemy",
            "styling": "tailwindcss",
            "monorepo": True
        },
        "is_monorepo": True,
        "config": {
            "backend_port": 8000,
            "frontend_port": 3000,
            "root_structure": {
                "backend": ["app/", "tests/", "requirements.txt", "Dockerfile"],
                "frontend": ["app/", "public/", "package.json", "next.config.ts"],
                "root": ["docker-compose.yml", ".env.example", "README.md", ".gitignore"]
            }
        }
    }
]


def seed_templates():
    """Seed default templates into the database."""
    from app.core.database import SessionLocal
    from app.models.template import Template

    db = SessionLocal()
    try:
        existing = db.query(Template).count()
        if existing > 0:
            return

        for tmpl_data in DEFAULT_TEMPLATES:
            template = Template(**tmpl_data)
            db.add(template)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
