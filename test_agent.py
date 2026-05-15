#!/usr/bin/env python3
"""Test script to check agent in database."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "censorate-system" / "backend"))

import sqlite3

db_path = Path(__file__).parent / "censorate-system" / "backend" / "database.db"

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

print("Agents in database:")
cursor.execute("SELECT id, name, config, capabilities FROM remote_agents WHERE archived_at IS NULL")
for row in cursor.fetchall():
    agent_id, name, config_json, caps_json = row
    print(f"\n  ID: {agent_id}")
    print(f"  Name: {name}")
    print(f"  Config: {config_json}")
    print(f"  Capabilities: {caps_json}")

conn.close()
