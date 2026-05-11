#!/usr/bin/env python3
"""Skill Manager - synchronizes skills from Censorate Hub to Hermes local storage.

This script acts as a sidecar for Hermes agents deployed in Docker.
It polls the Censorate Hub API for skills assigned to the agent (via capabilities),
downloads them as ZIP archives, and extracts them into the Hermes skill directory.

Usage:
    # One-shot sync
    python skill_manager.py --api-key <key> --hermes-data ./hermes_data

    # Daemon mode (syncs every hour)
    python skill_manager.py --daemon --api-key <key> --hermes-data ./hermes_data

Environment variables:
    CENSORATE_URL      - Censorate API base URL (default: http://localhost:8216/api/v1)
    HERMES_API_SERVER_KEY - Agent API key for Censorate Hub auth
    HERMES_HOME        - Path to hermes_data directory (default: ./hermes_data)
"""

import os
import sys
import json
import hashlib
import zipfile
import shutil
import argparse
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timezone
from io import BytesIO

try:
    import httpx
except ImportError:
    print("Error: httpx is required. Install with: pip install httpx")
    sys.exit(1)


DEFAULT_CENSORATE_URL = "http://localhost:8216/api/v1"
DEFAULT_HERMES_DATA = "./hermes_data"
DEFAULT_SYNC_INTERVAL = 3600  # seconds


class SkillManager:
    """Manages skill synchronization between Censorate Hub and local Hermes storage."""

    def __init__(
        self,
        censorate_url: str,
        api_key: str,
        hermes_data: Path,
    ):
        self.censorate_url = censorate_url.rstrip("/")
        self.api_key = api_key
        self.hermes_data = Path(hermes_data)
        self.skills_dir = self.hermes_data / "skills"
        self.state_file = self.hermes_data / ".skill_manager_state.json"
        self.headers = {"Authorization": f"Bearer {api_key}"}
        self.skills_dir.mkdir(parents=True, exist_ok=True)

    def _load_state(self) -> Dict:
        """Load persisted sync state."""
        if self.state_file.exists():
            try:
                return json.loads(self.state_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, IOError):
                pass
        return {"installed": {}, "last_sync": None}

    def _save_state(self, state: Dict):
        """Persist sync state to disk."""
        self.state_file.write_text(
            json.dumps(state, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

    # ── Hermes .hub/lock.json management ──────────────────────────────────

    @property
    def _lock_file(self) -> Path:
        return self.skills_dir / ".hub" / "lock.json"

    def _load_lock(self) -> Dict:
        """Load the Hermes hub lock file."""
        if self._lock_file.exists():
            try:
                return json.loads(self._lock_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                pass
        return {"version": 1, "installed": {}}

    def _save_lock(self, data: Dict):
        """Persist the Hermes hub lock file."""
        self._lock_file.parent.mkdir(parents=True, exist_ok=True)
        self._lock_file.write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8"
        )

    def _compute_skill_hash(self, skill_dir: Path) -> str:
        """Compute a SHA256 hash over all files in the skill directory."""
        hasher = hashlib.sha256()
        for fpath in sorted(skill_dir.rglob("*")):
            if fpath.is_file():
                hasher.update(fpath.read_bytes())
                hasher.update(fpath.relative_to(skill_dir).as_posix().encode())
        return hasher.hexdigest()

    def _get_skill_files(self, skill_dir: Path) -> List[str]:
        """List relative file paths within a skill directory."""
        return sorted(
            f.relative_to(skill_dir).as_posix()
            for f in skill_dir.rglob("*")
            if f.is_file()
        )

    def _extract_skill_name(self, skill_dir: Path) -> Optional[str]:
        """Extract the skill name from SKILL.md YAML frontmatter."""
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            return None
        try:
            content = skill_md.read_text(encoding="utf-8")[:4000]
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    for line in parts[1].strip().split("\n"):
                        if line.startswith("name:"):
                            return line.split(":", 1)[1].strip()
        except Exception:
            pass
        return None

    def _register_in_lock(self, name: str, slug: str, category: str,
                          version: str, install_path: str,
                          files: List[str], content_hash: str):
        """Register an installed skill in Hermes .hub/lock.json."""
        lock = self._load_lock()
        now = datetime.now(timezone.utc).isoformat()
        lock["installed"][name] = {
            "source": "censorate-hub",
            "identifier": slug,
            "trust_level": "trusted",
            "scan_verdict": "clean",
            "content_hash": content_hash,
            "install_path": install_path,
            "files": files,
            "metadata": {"hub": "censorate-skills-proxy", "version": version},
            "installed_at": now,
            "updated_at": now,
        }
        self._save_lock(lock)

    def _remove_from_lock(self, name: str):
        """Remove a skill from Hermes .hub/lock.json."""
        lock = self._load_lock()
        if name in lock.get("installed", {}):
            del lock["installed"][name]
            self._save_lock(lock)

    def list_remote_skills(self) -> List[Dict]:
        """Fetch the list of skills available to this agent from Censorate Hub."""
        url = f"{self.censorate_url}/remote-agents/skills"
        resp = httpx.get(url, headers=self.headers, timeout=30.0)
        resp.raise_for_status()
        data = resp.json()
        return data.get("skills", [])

    def download_skill(self, slug: str, version: Optional[str] = None) -> bytes:
        """Download a skill ZIP from Censorate Hub."""
        url = f"{self.censorate_url}/remote-agents/skills/{slug}/download"
        if version:
            url += f"?version={version}"
        resp = httpx.get(url, headers=self.headers, timeout=120.0)
        resp.raise_for_status()
        return resp.content

    def _extract_category_from_manifest(self, skill_dir: Path) -> Optional[str]:
        """Try to extract a category from SKILL.md frontmatter for directory placement."""
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            return None

        try:
            import frontmatter
            post = frontmatter.loads(skill_md.read_text(encoding="utf-8"))
            metadata = post.metadata

            # Prefer explicit category field
            if "category" in metadata:
                return str(metadata["category"]).lower().strip()

            # Fallback to metadata.hermes.tags[0]
            if "metadata" in metadata and isinstance(metadata["metadata"], dict):
                hermes_meta = metadata["metadata"].get("hermes", {})
                if isinstance(hermes_meta, dict):
                    tags = hermes_meta.get("tags", [])
                    if tags:
                        return str(tags[0]).lower().strip()
        except Exception:
            pass
        return None

    def install_skill(self, slug: str, category: str, version: str, zip_content: bytes) -> Path:
        """Install or update a skill by extracting its ZIP to the proper category directory."""
        # Extract to a temporary location first
        temp_dir = self.hermes_data / ".tmp" / slug
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(BytesIO(zip_content)) as zf:
            zf.extractall(temp_dir)

        # Determine final category from manifest if possible
        extracted_category = self._extract_category_from_manifest(temp_dir)
        final_category = extracted_category or category or "uncategorized"

        # Ensure category directory exists
        category_dir = self.skills_dir / final_category
        category_dir.mkdir(parents=True, exist_ok=True)

        target_dir = category_dir / slug
        if target_dir.exists():
            shutil.rmtree(target_dir)

        # Move from temp to final location
        shutil.move(str(temp_dir), str(target_dir))

        # Clean up temp parent if still exists
        temp_parent = temp_dir.parent
        if temp_parent.exists() and temp_parent.name == ".tmp":
            try:
                temp_parent.rmdir()
            except OSError:
                pass

        # Register in Hermes .hub/lock.json
        skill_name = self._extract_skill_name(target_dir) or slug
        install_path = f"{final_category}/{slug}"
        content_hash = self._compute_skill_hash(target_dir)
        files = self._get_skill_files(target_dir)
        self._register_in_lock(
            name=skill_name, slug=slug, category=final_category,
            version=version, install_path=install_path,
            files=files, content_hash=content_hash,
        )

        return target_dir

    def uninstall_skill(self, slug: str) -> bool:
        """Remove a skill by searching all category directories."""
        removed = False
        for category_dir in self.skills_dir.iterdir():
            if not category_dir.is_dir() or category_dir.name.startswith("."):
                continue
            target = category_dir / slug
            if target.exists():
                # Extract skill name before removing for lock cleanup
                skill_name = self._extract_skill_name(target) or slug
                shutil.rmtree(target)
                self._remove_from_lock(skill_name)
                removed = True
                # Try to remove empty category directory
                try:
                    category_dir.rmdir()
                except OSError:
                    pass
        return removed

    def sync(self) -> Dict:
        """Perform a full sync: install new, update changed, remove stale skills."""
        state = self._load_state()
        remote_skills = {s["slug"]: s for s in self.list_remote_skills()}
        results: Dict[str, List] = {
            "installed": [],
            "updated": [],
            "removed": [],
            "unchanged": [],
            "errors": []
        }

        # Install / update
        for slug, manifest in remote_skills.items():
            current = state["installed"].get(slug)
            current_version = current.get("version") if current else None

            if current_version == manifest["version"]:
                results["unchanged"].append(slug)
                continue

            action = "updated" if current else "installed"
            try:
                print(f"[SkillManager] {action.capitalize()} {slug} v{manifest['version']}...")
                zip_content = self.download_skill(slug, manifest["version"])
                self.install_skill(
                    slug,
                    manifest.get("category", "uncategorized"),
                    manifest["version"],
                    zip_content
                )
                state["installed"][slug] = {
                    "version": manifest["version"],
                    "category": manifest.get("category", "uncategorized"),
                    "installed_at": datetime.now(timezone.utc).isoformat()
                }
                results[action].append(slug)
            except Exception as e:
                print(f"[SkillManager] Error {action} {slug}: {e}")
                results["errors"].append({"slug": slug, "action": action, "error": str(e)})

        # Remove skills no longer in capabilities
        for slug in list(state["installed"].keys()):
            if slug not in remote_skills:
                try:
                    print(f"[SkillManager] Removing {slug}...")
                    if self.uninstall_skill(slug):
                        results["removed"].append(slug)
                    del state["installed"][slug]
                except Exception as e:
                    print(f"[SkillManager] Error removing {slug}: {e}")
                    results["errors"].append({"slug": slug, "action": "removed", "error": str(e)})

        state["last_sync"] = datetime.now(timezone.utc).isoformat()
        self._save_state(state)
        return results

    def run_daemon(self, interval: int):
        """Run continuous sync loop."""
        import time
        print(f"[SkillManager] Daemon started. Syncing every {interval}s.")
        while True:
            try:
                results = self.sync()
                total_changes = len(results["installed"]) + len(results["updated"]) + len(results["removed"])
                if total_changes > 0:
                    print(f"[SkillManager] Sync complete: {total_changes} changes.")
                else:
                    print(f"[SkillManager] Sync complete: no changes.")
            except Exception as e:
                print(f"[SkillManager] Sync failed: {e}")
            time.sleep(interval)


def main():
    parser = argparse.ArgumentParser(description="Sync skills from Censorate Hub to Hermes")
    parser.add_argument(
        "--censorate-url",
        default=os.getenv("CENSORATE_URL", DEFAULT_CENSORATE_URL),
        help="Censorate API base URL"
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv("HERMES_API_SERVER_KEY"),
        help="Agent API key for Censorate Hub authentication"
    )
    parser.add_argument(
        "--hermes-data",
        default=os.getenv("HERMES_HOME", DEFAULT_HERMES_DATA),
        help="Path to hermes_data directory"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run in daemon mode (continuous syncing)"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=DEFAULT_SYNC_INTERVAL,
        help="Sync interval in seconds (daemon mode only)"
    )

    args = parser.parse_args()

    if not args.api_key:
        print("Error: API key required. Set HERMES_API_SERVER_KEY env var or use --api-key")
        sys.exit(1)

    manager = SkillManager(
        censorate_url=args.censorate_url,
        api_key=args.api_key,
        hermes_data=Path(args.hermes_data)
    )

    if args.daemon:
        manager.run_daemon(args.interval)
    else:
        results = manager.sync()
        print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
