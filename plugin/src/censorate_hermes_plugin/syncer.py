"""Skill synchronization logic."""

import time
import threading
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from .config import Config
from .api_client import CensorateAPI


logger = logging.getLogger(__name__)


class SkillSyncer:
    """Manages skill synchronization from Censorate."""

    def __init__(self, config: Config):
        self.config = config
        self._client: Optional[CensorateAPI] = None
        self._background_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    @property
    def client(self) -> CensorateAPI:
        if not self._client:
            self._client = CensorateAPI(
                self.config.censorate_url,
                self.config.api_key,
                self.config.agent_id,
            )
        return self._client

    def sync_all(self) -> Dict[str, Any]:
        """Sync all skills from Censorate."""
        logger.info("Starting skill synchronization...")

        if not self.config.is_valid():
            raise ValueError("Invalid configuration. Please run 'censorate configure'.")

        skills_dir = self.config.skills_dir
        skills_dir.mkdir(parents=True, exist_ok=True)

        # Get bound skills
        skills = self.client.get_bound_skills()
        logger.info(f"Found {len(skills)} bound skills")

        results = {
            "total": len(skills),
            "updated": [],
            "failed": [],
            "skipped": [],
        }

        for skill in skills:
            slug = skill.get("slug")
            version = skill.get("version", "latest")

            try:
                skill_dir = skills_dir / slug

                # Check if we need to update
                if self._should_update(skill_dir, skill):
                    logger.info(f"Updating skill {slug}@{version}")
                    skill_data = self.client.download_skill(slug, version)
                    self.client.extract_skill(skill_data, skill_dir)
                    self.client.report_skill_status(slug, "installed")
                    results["updated"].append(slug)
                else:
                    logger.debug(f"Skill {slug} is up to date, skipping")
                    results["skipped"].append(slug)

            except Exception as e:
                logger.error(f"Failed to sync skill {slug}: {e}")
                try:
                    self.client.report_skill_status(slug, "failed", str(e))
                except:
                    pass
                results["failed"].append(slug)

        logger.info(f"Sync complete: {len(results['updated'])} updated, {len(results['skipped'])} skipped, {len(results['failed'])} failed")
        return results

    def _should_update(self, skill_dir: Path, skill_info: Dict[str, Any]) -> bool:
        """Check if a skill should be updated."""
        if not skill_dir.exists():
            return True

        meta_file = skill_dir / "_meta.json"
        if not meta_file.exists():
            return True

        try:
            import json
            with open(meta_file, "r") as f:
                meta = json.load(f)
            current_version = meta.get("version")
            new_version = skill_info.get("version")
            return current_version != new_version
        except:
            return True

    def start_background_sync(self) -> None:
        """Start background synchronization thread."""
        if self._background_thread and self._background_thread.is_alive():
            logger.warning("Background sync already running")
            return

        self._stop_event.clear()
        self._background_thread = threading.Thread(
            target=self._background_sync_loop,
            daemon=True,
        )
        self._background_thread.start()
        logger.info("Background sync started")

    def stop_background_sync(self) -> None:
        """Stop background synchronization thread."""
        self._stop_event.set()
        if self._background_thread:
            self._background_thread.join(timeout=5.0)
        logger.info("Background sync stopped")

    def _background_sync_loop(self) -> None:
        """Background sync loop."""
        while not self._stop_event.is_set():
            try:
                self.sync_all()
            except Exception as e:
                logger.error(f"Background sync failed: {e}")

            self._stop_event.wait(self.config.sync_interval)
