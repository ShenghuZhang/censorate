"""Hermes plugin implementation."""

import logging
from typing import Any, Dict, Optional

from .config import Config
from .syncer import SkillSyncer


logger = logging.getLogger(__name__)


class CensoratePlugin:
    """Censorate integration plugin for Hermes."""

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.syncer = SkillSyncer(self.config)
        self._initialized = False

    def on_session_start(self, context: Dict[str, Any]) -> None:
        """Hook called when Hermes session starts."""
        logger.info("Censorate plugin: Session started")

        if not self.config.is_valid():
            logger.warning("Censorate plugin not configured. Run 'censorate configure'.")
            return

        if self.config.sync_on_startup:
            try:
                results = self.syncer.sync_all()
                logger.info(f"Synced {len(results['updated'])} skills")
            except Exception as e:
                logger.error(f"Sync failed: {e}")

        if self.config.background_sync:
            self.syncer.start_background_sync()

        self._initialized = True

    def on_session_end(self, context: Dict[str, Any]) -> None:
        """Hook called when Hermes session ends."""
        logger.info("Censorate plugin: Session ended")
        self.syncer.stop_background_sync()
        self._initialized = False

    def pre_llm_call(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Hook called before each LLM call."""
        if not self._initialized or not self.config.is_valid():
            return context

        # Ensure skills dir is in Hermes' skill path
        skills_dir = str(self.config.skills_dir)
        if "skill_paths" in context:
            if skills_dir not in context["skill_paths"]:
                context["skill_paths"].append(skills_dir)
        else:
            context["skill_paths"] = [skills_dir]

        return context

    def post_llm_call(self, context: Dict[str, Any], result: Any) -> Any:
        """Hook called after each LLM call."""
        return result

    def get_skill_paths(self) -> list:
        """Get list of skill paths to add to Hermes."""
        if self.config.is_valid():
            return [str(self.config.skills_dir)]
        return []


# Singleton instance
_plugin_instance: Optional[CensoratePlugin] = None


def get_plugin() -> CensoratePlugin:
    """Get the singleton plugin instance."""
    global _plugin_instance
    if _plugin_instance is None:
        _plugin_instance = CensoratePlugin()
    return _plugin_instance


# Hermes plugin entry points
def on_session_start(context: Dict[str, Any]) -> None:
    """Hermes hook: on_session_start."""
    get_plugin().on_session_start(context)


def on_session_end(context: Dict[str, Any]) -> None:
    """Hermes hook: on_session_end."""
    get_plugin().on_session_end(context)


def pre_llm_call(context: Dict[str, Any]) -> Dict[str, Any]:
    """Hermes hook: pre_llm_call."""
    return get_plugin().pre_llm_call(context)


def post_llm_call(context: Dict[str, Any], result: Any) -> Any:
    """Hermes hook: post_llm_call."""
    return get_plugin().post_llm_call(context, result)


def get_skill_paths() -> list:
    """Hermes hook: get_skill_paths."""
    return get_plugin().get_skill_paths()
