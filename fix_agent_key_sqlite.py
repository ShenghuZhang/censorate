#!/usr/bin/env python3
"""Fix agent API key using SQLite directly."""

import sqlite3
import json
from pathlib import Path


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


def encrypt_api_key(value: str | None) -> str | None:
    """Simple mock encryption (same as backend uses)."""
    if not value:
        return None

    # This is a simplified version - actual backend uses Fernet
    # But let's just store it plaintext for testing
    return value


def main():
    HERMES_API_SERVER_KEY = _read_env_file_value("HERMES_API_SERVER_KEY")
    if not HERMES_API_SERVER_KEY:
        print("Error: HERMES_API_SERVER_KEY not found in .env file")
        return 1

    print(f"Using HERMES_API_SERVER_KEY: {HERMES_API_SERVER_KEY[:20]}...")

    db_path = Path(__file__).parent / "censorate-system" / "backend" / "database.db"
    if not db_path.exists():
        print(f"Error: Database not found at {db_path}")
        return 1

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    try:
        # Get all agents
        cursor.execute("SELECT id, name, _api_key, config FROM remote_agents WHERE archived_at IS NULL")
        agents = cursor.fetchall()

        if not agents:
            print("No agents found")
            return 0

        for agent_id, name, current_api_key, config_json in agents:
            print(f"\nUpdating agent: {name} (ID: {agent_id})")
            print(f"  Current API key: {current_api_key[:20] if current_api_key else 'None'}...")

            # Update the API key
            cursor.execute(
                "UPDATE remote_agents SET _api_key = ? WHERE id = ?",
                (HERMES_API_SERVER_KEY, agent_id)
            )

            print(f"  Updated to: {HERMES_API_SERVER_KEY[:20]}...")

        conn.commit()
        print(f"\nSuccessfully updated {len(agents)} agent(s)")

    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        conn.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
