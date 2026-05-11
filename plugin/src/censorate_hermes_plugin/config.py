"""Configuration management for Censorate Hermes Plugin."""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any


class Config:
    """Manages plugin configuration."""

    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path.home() / ".hermes"
        self.config_file = self.config_dir / "censorate.json"
        self.env_file = self.config_dir / ".env"

        self.config_dir.mkdir(parents=True, exist_ok=True)

        self._config: Dict[str, Any] = {}
        self._api_key: Optional[str] = None

        self.load()

    def load(self) -> None:
        """Load configuration from files."""
        # Load main config
        if self.config_file.exists():
            with open(self.config_file, "r") as f:
                self._config = json.load(f)

        # Load API key from env file
        if self.env_file.exists():
            with open(self.env_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        if key.strip() == "CENSORATE_API_KEY":
                            self._api_key = value.strip()

    def save(self) -> None:
        """Save configuration to files."""
        # Save main config
        with open(self.config_file, "w") as f:
            json.dump(self._config, f, indent=2)

        # Save env file with secure permissions
        env_lines = []
        if self.env_file.exists():
            with open(self.env_file, "r") as f:
                for line in f:
                    if not line.strip().startswith("CENSORATE_API_KEY="):
                        env_lines.append(line.rstrip("\n"))

        if self._api_key:
            env_lines.append(f"CENSORATE_API_KEY={self._api_key}")

        with open(self.env_file, "w") as f:
            f.write("\n".join(env_lines) + "\n")

        # Set secure permissions
        os.chmod(self.env_file, 0o600)

    @property
    def censorate_url(self) -> str:
        return self._config.get("censorate_url", "http://localhost:8216/api/v1")

    @censorate_url.setter
    def censorate_url(self, value: str) -> None:
        self._config["censorate_url"] = value.rstrip("/")

    @property
    def agent_id(self) -> Optional[str]:
        return self._config.get("agent_id")

    @agent_id.setter
    def agent_id(self, value: str) -> None:
        self._config["agent_id"] = value

    @property
    def api_key(self) -> Optional[str]:
        return self._api_key

    @api_key.setter
    def api_key(self, value: str) -> None:
        self._api_key = value

    @property
    def sync_interval(self) -> int:
        return self._config.get("sync_interval", 300)

    @sync_interval.setter
    def sync_interval(self, value: int) -> None:
        self._config["sync_interval"] = value

    @property
    def sync_on_startup(self) -> bool:
        return self._config.get("sync_on_startup", True)

    @sync_on_startup.setter
    def sync_on_startup(self, value: bool) -> None:
        self._config["sync_on_startup"] = value

    @property
    def background_sync(self) -> bool:
        return self._config.get("background_sync", True)

    @background_sync.setter
    def background_sync(self, value: bool) -> None:
        self._config["background_sync"] = value

    @property
    def skills_dir(self) -> Path:
        path_str = self._config.get("skills_dir", str(self.config_dir / "censorate_skills"))
        return Path(path_str).expanduser()

    @skills_dir.setter
    def skills_dir(self, value: Path) -> None:
        self._config["skills_dir"] = str(value)

    def is_valid(self) -> bool:
        """Check if configuration is valid."""
        return bool(
            self.censorate_url
            and self.agent_id
            and self.api_key
        )
