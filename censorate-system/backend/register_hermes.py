import sys
import asyncio
from pathlib import Path
import os

sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.remote_agent import RemoteAgent


def _read_env_file_value(key: str) -> str | None:
    """Read a key from local .env files when the shell environment is not populated."""
    env_paths = [
        Path(__file__).parent / ".env",
        Path(__file__).parent.parent / ".env",
    ]

    for env_path in env_paths:
        if not env_path.exists():
            continue

        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            current_key, value = line.split("=", 1)
            if current_key.strip() == key:
                return value.strip().strip("\"'")

    return None


def _get_config_value(key: str, default: str = "") -> str:
    return os.getenv(key) or _read_env_file_value(key) or default


HERMES_BASE_URL = _get_config_value("HERMES_BASE_URL", "http://localhost:8642").rstrip("/")
HERMES_API_SERVER_KEY = _get_config_value("HERMES_API_SERVER_KEY", "").strip() or None


async def register():
    db = SessionLocal()
    try:
        # Check if it already exists
        existing = db.query(RemoteAgent).filter(RemoteAgent.name == "Local-Hermes").first()
        if not existing:
            hermes = RemoteAgent(
                name="Local-Hermes",
                agent_type="hermes",
                # Store only the base URL. The chat endpoint is appended by the API layer.
                endpoint_url=HERMES_BASE_URL,
                api_key=HERMES_API_SERVER_KEY,
                health_check_path="/health",
                description="Locally deployed Hermes Agent instance",
                status="offline"
            )
            db.add(hermes)
            db.commit()
            print("Success: Hermes Agent successfully registered to Censorate!")
        else:
            print("Info: Hermes Agent already exists in the system. Updating URL just in case...")
            existing.endpoint_url = HERMES_BASE_URL
            existing.api_key = HERMES_API_SERVER_KEY
            existing.health_check_path = "/health"
            db.commit()
            print("Success: URL updated!")
    except Exception as e:
        db.rollback()
        print(f"Error registering Hermes Agent: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(register())
