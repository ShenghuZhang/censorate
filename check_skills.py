#!/usr/bin/env python3
"""Check what skills are available in the database."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "censorate-system" / "backend"))

from app.core.database import SessionLocal
from app.models.skill import Skill


def main():
    db = SessionLocal()
    try:
        skills = db.query(Skill).filter(Skill.is_archived == False).all()

        print(f"Found {len(skills)} skills:")
        for skill in skills:
            print(f"  - {skill.name} (slug: {skill.slug}, category: {skill.category})")
            print(f"    Published: {skill.is_published}")
            print(f"    Latest version ID: {skill.latest_version_id}")

        if not skills:
            print("No skills found in database.")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        db.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
