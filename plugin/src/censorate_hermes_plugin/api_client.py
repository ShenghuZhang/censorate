"""Censorate API client."""

import os
import zipfile
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional
import requests


class CensorateAPI:
    """Client for Censorate API."""

    def __init__(self, base_url: str, api_key: str, agent_id: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.agent_id = agent_id
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        })

    def get_bound_skills(self) -> List[Dict[str, Any]]:
        """Get skills bound to the agent."""
        url = f"{self.base_url}/remote-agents/{self.agent_id}/skills"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json().get("skills", [])

    def download_skill(self, skill_slug: str, version: Optional[str] = None) -> bytes:
        """Download a skill package."""
        url = f"{self.base_url}/skills/{skill_slug}/download"
        params = {}
        if version:
            params["version"] = version
        response = self.session.get(url, params=params, stream=True)
        response.raise_for_status()
        return response.content

    def extract_skill(self, skill_data: bytes, target_dir: Path) -> None:
        """Extract skill package to target directory."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as f:
            f.write(skill_data)
            temp_zip_path = f.name

        try:
            target_dir.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(temp_zip_path, "r") as zip_ref:
                zip_ref.extractall(target_dir)

        finally:
            os.unlink(temp_zip_path)

    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information."""
        url = f"{self.base_url}/remote-agents/{self.agent_id}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def report_skill_status(self, skill_slug: str, status: str, message: Optional[str] = None) -> None:
        """Report skill installation status."""
        url = f"{self.base_url}/remote-agents/{self.agent_id}/skills/{skill_slug}/status"
        data = {"status": status}
        if message:
            data["message"] = message
        response = self.session.post(url, json=data)
        response.raise_for_status()
