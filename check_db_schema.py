#!/usr/bin/env python3
"""Check database schema."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "censorate-system" / "backend"))

import sqlite3

db_path = Path(__file__).parent / "censorate-system" / "backend" / "database.db"
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

print("Checking skill_files table...")
cursor.execute("PRAGMA table_info(skill_files)")
for col in cursor.fetchall():
    print(f"  {col}")

print("\nFirst few rows of skill_files:")
cursor.execute("SELECT * FROM skill_files LIMIT 3")
for row in cursor.fetchall():
    print(f"  {row}")

conn.close()
