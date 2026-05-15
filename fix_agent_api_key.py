#!/usr/bin/env python3
"""Fix agent API key to match HERMES_API_SERVER_KEY in .env file."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "censorate-system" / "backend"))

from app.core.database import SessionLocal
from app.models.remote_agent import RemoteAgent


def _read_env_file_value(key: str) -> str | None:
    """Read a key from .env file."""
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        return None

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        current_key, value = line.split("=", 1)
        if current_key.strip() == key:
            return value.strip().strip("\"'")
    return None


def main():
    HERMES_API_SERVER_KEY = _read_env_file_value("HERMES_API_SERVER_KEY")
    if not HERMES_API_SERVER_KEY:
        print("Error: HERMES_API_SERVER_KEY not found in .env file")
        return 1

    print(f"Using HERMES_API_SERVER_KEY: {HERMES_API_SERVER_KEY[:10]}...")

    db = SessionLocal()
    try:
        # Update all agents to use this API key
        agents = db.query(RemoteAgent).filter(RemoteAgent.archived_at.is_(None)).all()

        if not agents:
            print("No agents found")
            return 0

        for agent in agents:
            print(f"Updating agent: {agent.name} (ID: {agent.id})")
            agent.api_key = HERMES_API_SERVER_KEY

        db.commit()
        print(f"Successfully updated {len(agents)} agent(s)")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        db.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
