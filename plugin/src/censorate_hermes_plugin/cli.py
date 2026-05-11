"""Command-line interface for Censorate Hermes Plugin."""

import sys
import json
import argparse
import logging
from pathlib import Path
from typing import Optional

from . import __version__
from .config import Config
from .syncer import SkillSyncer


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def configure(args) -> None:
    """Configure the plugin."""
    config = Config()

    if args.url:
        config.censorate_url = args.url
    if args.api_key:
        config.api_key = args.api_key
    if args.agent_id:
        config.agent_id = args.agent_id
    if args.sync_interval:
        config.sync_interval = args.sync_interval

    config.save()
    print("Configuration saved successfully!")
    print(f"  Censorate URL: {config.censorate_url}")
    print(f"  Agent ID: {config.agent_id}")
    print(f"  Skills directory: {config.skills_dir}")


def sync(args) -> None:
    """Sync skills from Censorate."""
    config = Config()

    if not config.is_valid():
        print("Error: Plugin not configured. Run 'censorate configure' first.")
        sys.exit(1)

    syncer = SkillSyncer(config)

    try:
        results = syncer.sync_all()
        print(f"\nSync complete!")
        print(f"  Total: {results['total']}")
        print(f"  Updated: {len(results['updated'])}")
        print(f"  Skipped: {len(results['skipped'])}")
        print(f"  Failed: {len(results['failed'])}")

        if results['updated']:
            print(f"\nUpdated skills: {', '.join(results['updated'])}")
        if results['failed']:
            print(f"\nFailed skills: {', '.join(results['failed'])}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def install(args) -> None:
    """Install the plugin in Hermes."""
    config = Config()

    hermes_config_dir = Path.home() / ".hermes"
    hermes_config = hermes_config_dir / "config.json"

    hermes_config_dir.mkdir(parents=True, exist_ok=True)

    # Load or create Hermes config
    if hermes_config.exists():
        with open(hermes_config, "r") as f:
            hermes_conf = json.load(f)
    else:
        hermes_conf = {}

    # Add plugin to config
    if "plugins" not in hermes_conf:
        hermes_conf["plugins"] = []

    plugin_entry = "censorate_hermes_plugin.plugin"

    if plugin_entry not in hermes_conf["plugins"]:
        hermes_conf["plugins"].append(plugin_entry)

        # Add skills directory
        if "skill_paths" not in hermes_conf:
            hermes_conf["skill_paths"] = []

        skills_dir = str(config.skills_dir)
        if skills_dir not in hermes_conf["skill_paths"]:
            hermes_conf["skill_paths"].append(skills_dir)

        with open(hermes_config, "w") as f:
            json.dump(hermes_conf, f, indent=2)

        print(f"Plugin installed successfully!")
        print(f"  Config file: {hermes_config}")
    else:
        print(f"Plugin already installed.")


def status(args) -> None:
    """Show plugin status."""
    config = Config()

    print("Censorate Hermes Plugin Status")
    print("=" * 40)
    print(f"Version: {__version__}")
    print(f"Configured: {'Yes' if config.is_valid() else 'No'}")

    if config.is_valid():
        print(f"\nConfiguration:")
        print(f"  Censorate URL: {config.censorate_url}")
        print(f"  Agent ID: {config.agent_id}")
        print(f"  Sync interval: {config.sync_interval}s")
        print(f"  Sync on startup: {config.sync_on_startup}")
        print(f"  Background sync: {config.background_sync}")
        print(f"  Skills directory: {config.skills_dir}")

        # Check skills directory
        skills_dir = config.skills_dir
        if skills_dir.exists():
            skill_dirs = [d for d in skills_dir.iterdir() if d.is_dir()]
            print(f"\nSkills installed: {len(skill_dirs)}")
            for skill_dir in skill_dirs:
                print(f"  - {skill_dir.name}")
        else:
            print(f"\nSkills directory does not exist.")


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Censorate Hermes Plugin CLI",
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(title="Commands", dest="command")

    # Configure command
    config_parser = subparsers.add_parser(
        "configure",
        help="Configure the plugin",
    )
    config_parser.add_argument(
        "--url",
        help="Censorate API URL",
    )
    config_parser.add_argument(
        "--api-key",
        help="Censorate API key",
    )
    config_parser.add_argument(
        "--agent-id",
        help="Agent ID",
    )
    config_parser.add_argument(
        "--sync-interval",
        type=int,
        help="Sync interval in seconds",
    )

    # Sync command
    subparsers.add_parser(
        "sync",
        help="Sync skills from Censorate",
    )

    # Install command
    subparsers.add_parser(
        "install",
        help="Install the plugin in Hermes",
    )

    # Status command
    subparsers.add_parser(
        "status",
        help="Show plugin status",
    )

    args = parser.parse_args()

    if args.command == "configure":
        configure(args)
    elif args.command == "sync":
        sync(args)
    elif args.command == "install":
        install(args)
    elif args.command == "status":
        status(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
