#!/usr/bin/env python3
"""Test sending a webhook directly to skill-manager."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "censorate-system" / "backend"))

import sqlite3
import httpx
import json

# Get data from database
db_path = Path(__file__).parent / "censorate-system" / "backend" / "database.db"
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Get agent
agent_id = "bf12d1ff-5b69-4808-a56f-003a9d2a3234"
cursor.execute("SELECT id, name, capabilities FROM remote_agents WHERE id = ?", (agent_id,))
agent_row = cursor.fetchone()
agent_name = agent_row[1]
capabilities = json.loads(agent_row[2]) if agent_row[2] else []

print(f"Agent: {agent_name}")
print(f"Capabilities: {capabilities}")

# Get skills data
skills_data = []
for slug in capabilities:
    cursor.execute("""
        SELECT s.id, s.slug, s.name, s.description, s.category, s.latest_version_id
        FROM skills s
        WHERE s.slug = ? AND s.is_archived = 0
    """, (slug,))
    skill_row = cursor.fetchone()
    if skill_row:
        skill_id, slug, name, description, category, latest_version_id = skill_row

        if latest_version_id:
            # Get version
            cursor.execute("SELECT version, manifest FROM skill_versions WHERE id = ?", (latest_version_id,))
            version_row = cursor.fetchone()
            if version_row:
                version, manifest_json = version_row
                manifest = json.loads(manifest_json) if manifest_json else {}

                # Get files
                cursor.execute("""
                    SELECT path, content_type, file_size, content
                    FROM skill_files
                    WHERE version_id = ?
                """, (latest_version_id,))
                files = []
                for file_row in cursor.fetchall():
                    path, content_type, file_size, content = file_row
                    files.append({
                        "path": path,
                        "content_type": content_type,
                        "file_size": file_size,
                        "content": content.decode("utf-8", errors="ignore") if content else None
                    })

                skills_data.append({
                    "slug": slug,
                    "name": name,
                    "description": description,
                    "category": category,
                    "version": version,
                    "manifest": manifest,
                    "files": files
                })

conn.close()

print(f"\nFound {len(skills_data)} skills")

# Send webhook
webhook_url = "http://localhost:8765/webhook/agent-updated"
payload = {
    "agent_id": agent_id,
    "agent_name": agent_name,
    "event_type": "capabilities_updated",
    "capabilities": capabilities,
    "skills": skills_data
}

print(f"\nSending webhook to {webhook_url}...")
response = httpx.post(webhook_url, json=payload, timeout=30.0)
print(f"Response: {response.status_code}")
print(f"Response body: {response.text}")
