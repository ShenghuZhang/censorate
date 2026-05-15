#!/usr/bin/env python3
"""Test script to check skills in database."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "censorate-system" / "backend"))

import sqlite3

db_path = Path(__file__).parent / "censorate-system" / "backend" / "database.db"

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

print("Skills in database:")
cursor.execute("SELECT id, slug, name, category, is_published, latest_version_id FROM skills WHERE is_archived = 0")
for row in cursor.fetchall():
    skill_id, slug, name, category, is_published, latest_version_id = row
    print(f"\n  ID: {skill_id}")
    print(f"  Slug: {slug}")
    print(f"  Name: {name}")
    print(f"  Category: {category}")
    print(f"  Published: {is_published}")

conn.close()
