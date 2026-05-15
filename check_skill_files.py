#!/usr/bin/env python3
"""Check skill files in database."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "censorate-system" / "backend"))

import sqlite3

db_path = Path(__file__).parent / "censorate-system" / "backend" / "database.db"

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

print("Checking skill versions and files...")

# Get skills with their latest versions
cursor.execute("""
    SELECT s.id, s.slug, s.name, s.latest_version_id, sv.id, sv.version
    FROM skills s
    LEFT JOIN skill_versions sv ON s.latest_version_id = sv.id
    WHERE s.is_archived = 0
""")

for row in cursor.fetchall():
    skill_id, slug, name, latest_version_id, version_id, version = row
    print(f"\nSkill: {name} ({slug})")
    print(f"  Latest version ID: {latest_version_id}")

    if version_id:
        # Check for files
        cursor.execute("""
            SELECT path, content_type, file_size
            FROM skill_files
            WHERE version_id = ?
        """, (version_id,))
        files = cursor.fetchall()
        if files:
            print(f"  Files:")
            for f in files:
                path, content_type, file_size = f
                print(f"    - {path} ({content_type}, {file_size} bytes)")
        else:
            print(f"  No files found for this version")

conn.close()
