"""Scheduler - Automated health check scheduling for remote agents."""

import asyncio
import logging
from typing import Optional
from datetime import datetime, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

from app.core.config import Settings
from app.api.deps import get_db
from app.models.remote_agent import RemoteAgent
from app.services.remote_agent_service import get_remote_agent_service

logger = logging.getLogger(__name__)


class RemoteAgentHealthScheduler:
    """Scheduler for automated remote agent health checks."""

    def __init__(self, settings: Settings):
        """Initialize scheduler."""
        self.settings = settings
        self.scheduler: Optional[AsyncIOScheduler] = None
        self._db_session: Optional[Session] = None
        self._running = False

    async def start(self) -> None:
        """Start the scheduler."""
        if not self.settings.SCHEDULER_ENABLED:
            logger.info("Scheduler is disabled in settings")
            return

        if self._running:
            logger.warning("Scheduler is already running")
            return

        logger.info("Starting remote agent health scheduler...")

        # Create scheduler
        self.scheduler = AsyncIOScheduler()

        # Get a database session
        # We'll get a new session for each health check run
        # to avoid stale connections

        # Add initial job to refresh agent health check schedules
        self.scheduler.add_job(
            self._refresh_schedules,
            trigger=IntervalTrigger(minutes=5),
            id="refresh_schedules",
            name="Refresh agent health check schedules",
            replace_existing=True
        )

        # Start scheduler
        self.scheduler.start()
        self._running = True

        # Do initial schedule refresh immediately
        await self._refresh_schedules()

        logger.info("Remote agent health scheduler started")

    async def stop(self) -> None:
        """Stop the scheduler."""
        if not self._running:
            return

        logger.info("Stopping remote agent health scheduler...")

        if self.scheduler:
            self.scheduler.shutdown(wait=True)

        # Cleanup remote agent service client
        service = get_remote_agent_service()
        await service.close()

        self._running = False
        logger.info("Remote agent health scheduler stopped")

    async def _refresh_schedules(self) -> None:
        """Refresh health check schedules for all agents."""
        try:
            # Get a new database session
            db_gen = get_db()
            db = next(db_gen)

            try:
                # Get all active agents
                agents = db.query(RemoteAgent).filter(
                    RemoteAgent.archived_at.is_(None)
                ).all()

                logger.info(f"Refreshing health check schedules for {len(agents)} agents")

                # Remove all agent-specific jobs
                for job in self.scheduler.get_jobs():
                    if job.id.startswith("agent_health_"):
                        self.scheduler.remove_job(job.id)

                # Add job for each agent
                for agent in agents:
                    job_id = f"agent_health_{agent.id}"
                    interval_seconds = agent.health_check_interval or 30

                    self.scheduler.add_job(
                        self._check_single_agent_health,
                        trigger=IntervalTrigger(seconds=interval_seconds),
                        id=job_id,
                        name=f"Health check for {agent.name}",
                        args=[str(agent.id)],
                        replace_existing=True
                    )

                    logger.debug(f"Scheduled health check for agent {agent.name} every {interval_seconds}s")

            finally:
                # Close the session
                try:
                    db.close()
                except:
                    pass

        except Exception as e:
            logger.error(f"Failed to refresh health check schedules: {e}", exc_info=True)

    async def _check_single_agent_health(self, agent_id: str) -> None:
        """Check health of a single agent (called by scheduler)."""
        try:
            # Get a new database session
            db_gen = get_db()
            db = next(db_gen)

            try:
                # Get agent
                agent = db.query(RemoteAgent).filter(
                    RemoteAgent.id == agent_id,
                    RemoteAgent.archived_at.is_(None)
                ).first()

                if not agent:
                    logger.warning(f"Agent {agent_id} not found, removing health check job")
                    job_id = f"agent_health_{agent_id}"
                    if self.scheduler and self.scheduler.get_job(job_id):
                        self.scheduler.remove_job(job_id)
                    return

                # Check health
                service = get_remote_agent_service()
                status_str, response_time, message = await service.check_agent_health(agent)

                # Update agent with health history and alert management
                service.update_agent_status(db, agent, status_str, response_time, message)

                logger.debug(
                    f"Health check for {agent.name}: {status_str}"
                    f"{f' ({response_time}ms)' if response_time else ''}"
                    f"{f' - {message}' if message else ''}"
                )

            finally:
                # Close the session
                try:
                    db.close()
                except:
                    pass

        except Exception as e:
            logger.error(f"Failed to check health for agent {agent_id}: {e}", exc_info=True)


# Singleton instance
_health_scheduler: Optional[RemoteAgentHealthScheduler] = None


def get_health_scheduler() -> RemoteAgentHealthScheduler:
    """Get singleton health scheduler instance."""
    global _health_scheduler
    if _health_scheduler is None:
        settings = Settings.get()
        _health_scheduler = RemoteAgentHealthScheduler(settings)
    return _health_scheduler


@asynccontextmanager
async def health_scheduler_lifespan():
    """Lifespan context manager for health scheduler."""
    scheduler = get_health_scheduler()
    await scheduler.start()
    try:
        yield
    finally:
        await scheduler.stop()
