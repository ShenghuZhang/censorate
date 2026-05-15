#!/usr/bin/env python3
"""Skill Manager - synchronizes skills from Censorate Hub to Hermes local storage.

This script acts as a sidecar for Hermes agents deployed in Docker.
It supports multiple modes:
- One-shot sync
- Daemon mode with polling
- HTTP server mode with webhooks (for real-time updates)
- Hybrid mode (webhook + polling as fallback)

Usage:
    # One-shot sync
    python skill_manager.py --api-key <key> --hermes-data ./hermes_data

    # Daemon mode (polls every 5 minutes)
    python skill_manager.py --daemon --api-key <key> --hermes-data ./hermes_data

    # HTTP server mode (with webhook)
    python skill_manager.py --server --api-key <key> --hermes-data ./hermes_data

    # Hybrid mode (webhook + polling fallback)
    python skill_manager.py --server --daemon --api-key <key> --hermes-data ./hermes_data

Environment variables:
    CENSORATE_URL      - Censorate API base URL (default: http://localhost:8216/api/v1)
    HERMES_API_SERVER_KEY - Agent API key for Censorate Hub auth
    HERMES_HOME        - Path to hermes_data directory (default: ./hermes_data)
    SKILL_MANAGER_PORT - HTTP server port (default: 8765)
    SKILL_MANAGER_HOST - HTTP server host (default: 0.0.0.0)
    SKILL_MANAGER_INTERVAL - Polling interval in seconds (default: 300)
"""

import os
import sys
import json
import hashlib
import zipfile
import shutil
import argparse
import asyncio
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timezone
from io import BytesIO

try:
    import httpx
except ImportError:
    print("Error: httpx is required. Install with: pip install httpx")
    sys.exit(1)

try:
    from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
    from fastapi.responses import JSONResponse
    import uvicorn
except ImportError:
    print("Warning: fastapi/uvicorn not installed. Server mode will not be available.")
    FastAPI = None
    uvicorn = None


DEFAULT_CENSORATE_URL = "http://localhost:8216/api/v1"
DEFAULT_HERMES_DATA = "~/.hermes"
DEFAULT_SYNC_INTERVAL = 300  # seconds (5 minutes)
DEFAULT_PORT = 8765
DEFAULT_HOST = "0.0.0.0"


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
        self._last_sync_result: Optional[Dict] = None

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

    def install_skill_from_data(self, skill_data: Dict) -> Path:
        """Install a skill directly from data (received via webhook)."""
        slug = skill_data["slug"]
        category = skill_data.get("category", "uncategorized")
        version = skill_data.get("version", "1.0.0")
        files = skill_data.get("files", [])

        # Create temporary directory
        temp_dir = self.hermes_data / ".tmp" / slug
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir(parents=True, exist_ok=True)

        # Write all files
        for file_info in files:
            file_path = temp_dir / file_info["path"]
            file_path.parent.mkdir(parents=True, exist_ok=True)
            content = file_info.get("content", "")
            if content:
                file_path.write_text(content, encoding="utf-8")

        # Ensure category directory exists
        category_dir = self.skills_dir / category
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
        install_path = f"{category}/{slug}"
        content_hash = self._compute_skill_hash(target_dir)
        skill_files = self._get_skill_files(target_dir)
        self._register_in_lock(
            name=skill_name, slug=slug, category=category,
            version=version, install_path=install_path,
            files=skill_files, content_hash=content_hash,
        )

        return target_dir

    def sync_from_webhook_data(self, payload: Dict) -> Dict:
        """Sync skills directly from webhook payload data."""
        print(f"[SkillManager] Starting sync from webhook data at {datetime.now(timezone.utc).isoformat()}")

        capabilities = payload.get("capabilities", [])
        skills_data = payload.get("skills", [])
        agent_name = payload.get("agent_name", "unknown")

        print(f"[SkillManager] Agent '{agent_name}' has {len(capabilities)} capabilities, {len(skills_data)} skills received")

        state = self._load_state()
        results: Dict[str, List] = {
            "installed": [],
            "updated": [],
            "removed": [],
            "unchanged": [],
            "errors": []
        }

        # Create a map of received skills by slug
        received_skills = {s["slug"]: s for s in skills_data}

        # Install / update received skills
        for slug, skill_data in received_skills.items():
            current = state["installed"].get(slug)
            current_version = current.get("version") if current else None
            new_version = skill_data.get("version", "1.0.0")

            if current_version == new_version:
                results["unchanged"].append(slug)
                continue

            action = "updated" if current else "installed"
            try:
                print(f"[SkillManager] {action.capitalize()} {slug} v{new_version}...")
                self.install_skill_from_data(skill_data)
                state["installed"][slug] = {
                    "version": new_version,
                    "category": skill_data.get("category", "uncategorized"),
                    "installed_at": datetime.now(timezone.utc).isoformat()
                }
                results[action].append(slug)
            except Exception as e:
                print(f"[SkillManager] Error {action} {slug}: {e}")
                import traceback
                traceback.print_exc()
                results["errors"].append({"slug": slug, "action": action, "error": str(e)})

        # Remove skills no longer in capabilities
        for slug in list(state["installed"].keys()):
            if slug not in capabilities:
                try:
                    print(f"[SkillManager] Removing {slug}...")
                    if self.uninstall_skill(slug):
                        results["removed"].append(slug)
                    del state["installed"][slug]
                except Exception as e:
                    print(f"[SkillManager] Error removing {slug}: {e}")
                    import traceback
                    traceback.print_exc()
                    results["errors"].append({"slug": slug, "action": "removed", "error": str(e)})

        state["last_sync"] = datetime.now(timezone.utc).isoformat()
        self._save_state(state)
        self._last_sync_result = results

        total_changes = len(results["installed"]) + len(results["updated"]) + len(results["removed"])
        print(f"[SkillManager] Sync complete: {total_changes} changes, {len(results['errors'])} errors")
        return results

    def sync(self) -> Dict:
        """Perform a full sync: install new, update changed, remove stale skills."""
        print(f"[SkillManager] Starting sync at {datetime.now(timezone.utc).isoformat()}")
        state = self._load_state()
        try:
            remote_skills = {s["slug"]: s for s in self.list_remote_skills()}
        except Exception as e:
            print(f"[SkillManager] Error fetching remote skills: {e}")
            return {"installed": [], "updated": [], "removed": [], "unchanged": [], "errors": [str(e)]}

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
                import traceback
                traceback.print_exc()
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
                    import traceback
                    traceback.print_exc()
                    results["errors"].append({"slug": slug, "action": "removed", "error": str(e)})

        state["last_sync"] = datetime.now(timezone.utc).isoformat()
        self._save_state(state)
        self._last_sync_result = results

        total_changes = len(results["installed"]) + len(results["updated"]) + len(results["removed"])
        print(f"[SkillManager] Sync complete: {total_changes} changes, {len(results['errors'])} errors")
        return results

    @property
    def last_sync_result(self) -> Optional[Dict]:
        return self._last_sync_result

    def run_daemon(self, interval: int):
        """Run continuous sync loop."""
        import time
        print(f"[SkillManager] Daemon started. Syncing every {interval}s.")
        while True:
            try:
                self.sync()
            except Exception as e:
                print(f"[SkillManager] Sync failed: {e}")
                import traceback
                traceback.print_exc()
            time.sleep(interval)


def create_app(manager: SkillManager) -> FastAPI:
    """Create FastAPI application for skill-manager server mode."""
    if FastAPI is None:
        raise RuntimeError("fastapi not installed")

    app = FastAPI(title="Skill Manager", description="Sidecar for Hermes skill synchronization")

    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "healthy", "last_sync": manager._load_state().get("last_sync")}

    @app.get("/status")
    async def status():
        """Get current status and last sync result."""
        state = manager._load_state()
        return {
            "status": "running",
            "last_sync": state.get("last_sync"),
            "installed_skills": state.get("installed", {}),
            "last_sync_result": manager.last_sync_result
        }

    @app.post("/sync")
    async def trigger_sync(background_tasks: BackgroundTasks):
        """Trigger a sync in background."""
        async def do_sync():
            try:
                manager.sync()
            except Exception as e:
                print(f"[SkillManager] Webhook-triggered sync failed: {e}")

        background_tasks.add_task(do_sync)
        return {"status": "syncing"}

    @app.post("/webhook/agent-updated")
    async def agent_updated_webhook(request: Request, background_tasks: BackgroundTasks):
        """Webhook endpoint for agent updates (capabilities changed)."""
        try:
            payload = await request.json()
            agent_id = payload.get("agent_id")
            agent_name = payload.get("agent_name", "unknown")
            event_type = payload.get("event_type", "unknown")
            skills_count = len(payload.get("skills", [])) if payload.get("skills") else 0
            print(f"[SkillManager] Received webhook: agent={agent_id} ({agent_name}), event={event_type}, skills={skills_count}")

            # If payload contains skills data, use that directly
            if "skills" in payload:
                async def do_sync_from_data():
                    try:
                        manager.sync_from_webhook_data(payload)
                    except Exception as e:
                        print(f"[SkillManager] Webhook data sync failed: {e}")
                        import traceback
                        traceback.print_exc()

                background_tasks.add_task(do_sync_from_data)
                return {"status": "accepted", "message": "syncing from webhook data"}
        except Exception as e:
            print(f"[SkillManager] Error processing webhook payload: {e}")
            # Fall through to legacy sync

        # Legacy fallback: do a regular sync
        async def do_sync():
            try:
                manager.sync()
            except Exception as e:
                print(f"[SkillManager] Webhook-triggered sync failed: {e}")

        background_tasks.add_task(do_sync)
        return {"status": "accepted", "message": "sync triggered"}

    return app


async def run_server(manager: SkillManager, host: str, port: int):
    """Run the HTTP server."""
    app = create_app(manager)
    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


async def run_hybrid(manager: SkillManager, host: str, port: int, interval: int):
    """Run both server and daemon."""
    app = create_app(manager)
    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)

    async def poll_loop():
        import time
        print(f"[SkillManager] Polling started. Syncing every {interval}s.")
        while True:
            try:
                await asyncio.sleep(interval)
                manager.sync()
            except Exception as e:
                print(f"[SkillManager] Poll sync failed: {e}")

    # Run both tasks
    server_task = asyncio.create_task(server.serve())
    poll_task = asyncio.create_task(poll_loop())

    await asyncio.gather(server_task, poll_task)


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
        help="Run in daemon mode (continuous polling)"
    )
    parser.add_argument(
        "--server",
        action="store_true",
        help="Run in HTTP server mode (webhook support)"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=int(os.getenv("SKILL_MANAGER_INTERVAL", DEFAULT_SYNC_INTERVAL)),
        help="Sync interval in seconds (daemon/hybrid mode only)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("SKILL_MANAGER_PORT", DEFAULT_PORT)),
        help="HTTP server port (server/hybrid mode only)"
    )
    parser.add_argument(
        "--host",
        default=os.getenv("SKILL_MANAGER_HOST", DEFAULT_HOST),
        help="HTTP server host (server/hybrid mode only)"
    )

    args = parser.parse_args()

    # Track if real API key was provided
    has_real_api_key = bool(args.api_key)

    # API key is optional - only needed for polling mode
    if not has_real_api_key and args.daemon:
        print("Warning: API key not provided. Polling mode may not work correctly.")

    manager = SkillManager(
        censorate_url=args.censorate_url,
        api_key=args.api_key or "dummy",
        hermes_data=Path(args.hermes_data)
    )

    # Only do initial sync if we have a real API key
    if has_real_api_key:
        print("[SkillManager] Performing initial sync...")
        try:
            manager.sync()
        except Exception as e:
            print(f"[SkillManager] Initial sync failed: {e}")
    else:
        print("[SkillManager] Skipping initial sync (no API key provided, webhook-only mode)")

    if args.server and args.daemon:
        if FastAPI is None or uvicorn is None:
            print("Error: fastapi/uvicorn required for server mode. Install with: pip install fastapi uvicorn")
            sys.exit(1)
        print(f"[SkillManager] Starting hybrid mode (server + polling) on {args.host}:{args.port}")
        asyncio.run(run_hybrid(manager, args.host, args.port, args.interval))
    elif args.server:
        if FastAPI is None or uvicorn is None:
            print("Error: fastapi/uvicorn required for server mode. Install with: pip install fastapi uvicorn")
            sys.exit(1)
        print(f"[SkillManager] Starting server mode on {args.host}:{args.port}")
        asyncio.run(run_server(manager, args.host, args.port))
    elif args.daemon:
        manager.run_daemon(args.interval)
    else:
        results = manager.sync()
        print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
