"""Remote Agent Service - Manages remote agent health checks with connection pooling and parallel execution."""

import httpx
import asyncio
from datetime import datetime, timezone
from typing import List, Tuple, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.remote_agent import RemoteAgent, RemoteAgentHealthHistory
from app.core.config import Settings


class RemoteAgentService:
    """Service for managing remote agents with connection pooling and parallel health checks."""

    def __init__(self, settings: Settings):
        """Initialize remote agent service."""
        self.settings = settings
        self._client: Optional[httpx.AsyncClient] = None

    async def get_client(self) -> httpx.AsyncClient:
        """Get or create httpx client with connection pooling."""
        if self._client is None or self._client.is_closed:
            timeout = httpx.Timeout(10.0, connect=5.0)
            limits = httpx.Limits(
                max_connections=20,
                max_keepalive_connections=10,
                keepalive_expiry=30.0
            )
            self._client = httpx.AsyncClient(
                timeout=timeout,
                limits=limits,
                http2=True
            )
        return self._client

    async def close(self) -> None:
        """Close the httpx client and cleanup resources."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def check_agent_health(
        self,
        agent: RemoteAgent
    ) -> Tuple[str, int | None, str | None]:
        """
        Check health of a single remote agent.

        Args:
            agent: RemoteAgent instance

        Returns:
            Tuple of (status: str, response_time_ms: int | None, error_message: str | None)
        """
        health_url = f"{agent.endpoint_url.rstrip('/')}{agent.health_check_path}"
        start_time = datetime.now(timezone.utc)

        try:
            # Create a fresh client without http2 for localhost testing
            timeout = httpx.Timeout(10.0, connect=5.0)
            async with httpx.AsyncClient(timeout=timeout, http2=False) as client:
                headers = {}
                if agent.api_key:
                    headers["Authorization"] = f"Bearer {agent.api_key}"

                response = await client.get(health_url, headers=headers)
                response.raise_for_status()

                response_time = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
                return "online", response_time, None

        except httpx.HTTPStatusError as e:
            return "error", None, f"HTTP {e.response.status_code}"
        except httpx.TimeoutException:
            return "offline", None, "Connection timeout"
        except httpx.ConnectError as e:
            return "offline", None, f"Connection failed: {str(e)}"
        except Exception as e:
            import traceback
            return "error", None, f"{str(e)}\n{traceback.format_exc()}"

    async def check_all_agents_health(
        self,
        agents: List[RemoteAgent]
    ) -> List[Tuple[RemoteAgent, str, int | None, str | None]]:
        """
        Check health of all agents in parallel.

        Args:
            agents: List of RemoteAgent instances

        Returns:
            List of tuples (agent, status, response_time_ms, error_message)
        """
        tasks = [self.check_agent_health(agent) for agent in agents]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        output = []
        for agent, result in zip(agents, results):
            if isinstance(result, Exception):
                output.append((agent, "error", None, str(result)))
            else:
                status, response_time, error = result
                output.append((agent, status, response_time, error))

        return output

    def record_health_history(
        self,
        db: Session,
        agent: RemoteAgent,
        status: str,
        response_time_ms: int | None,
        error_message: str | None
    ) -> RemoteAgentHealthHistory:
        """
        Record a health check history entry.

        Args:
            db: Database session
            agent: RemoteAgent instance
            status: Health check status
            response_time_ms: Response time in milliseconds
            error_message: Error message if any

        Returns:
            Created RemoteAgentHealthHistory instance
        """
        history = RemoteAgentHealthHistory(
            agent_id=agent.id,
            status=status,
            response_time_ms=response_time_ms,
            error_message=error_message,
            checked_at=datetime.utcnow()
        )
        db.add(history)
        db.flush()
        return history

    def update_agent_status(
        self,
        db: Session,
        agent: RemoteAgent,
        status: str,
        response_time_ms: int | None,
        error_message: str | None
    ) -> RemoteAgent:
        """
        Update agent status in database with alert state management.

        Args:
            db: Database session
            agent: RemoteAgent instance
            status: New status ('online', 'offline', 'error')
            response_time_ms: Response time in milliseconds
            error_message: Error message if any

        Returns:
            Updated RemoteAgent instance
        """
        # Record health history first
        self.record_health_history(db, agent, status, response_time_ms, error_message)

        # Update agent status
        agent.status = status
        agent.last_health_check = datetime.utcnow()

        # Update consecutive failures and alert state
        if status == "online":
            agent.consecutive_failures = 0
            # If alert was acknowledged and agent is back online, reset acknowledgement
            if agent.alert_acknowledged:
                agent.alert_acknowledged = False
                agent.alert_acknowledged_at = None
                agent.alert_acknowledged_by = None
        else:
            agent.consecutive_failures += 1

            # Check if alert should be triggered
            if (agent.consecutive_failures >= agent.alert_after_consecutive_failures and
                not agent.alert_acknowledged):
                # Alert threshold reached - in a real system, you would send an alert here
                # (email, Slack, etc.)
                pass

        db.commit()
        db.refresh(agent)
        return agent

    def get_health_history(
        self,
        db: Session,
        agent_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[RemoteAgentHealthHistory]:
        """
        Get health history for an agent.

        Args:
            db: Database session
            agent_id: Agent ID
            limit: Maximum number of entries to return
            offset: Offset for pagination

        Returns:
            List of RemoteAgentHealthHistory instances
        """
        return db.query(RemoteAgentHealthHistory).filter(
            RemoteAgentHealthHistory.agent_id == agent_id
        ).order_by(
            RemoteAgentHealthHistory.checked_at.desc()
        ).limit(limit).offset(offset).all()

    def acknowledge_alert(
        self,
        db: Session,
        agent_id: str,
        acknowledged_by: str | None = None
    ) -> RemoteAgent:
        """
        Acknowledge an alert for an agent.

        Args:
            db: Database session
            agent_id: Agent ID
            acknowledged_by: User who acknowledged the alert

        Returns:
            Updated RemoteAgent instance
        """
        agent = db.query(RemoteAgent).filter(
            RemoteAgent.id == agent_id,
            RemoteAgent.archived_at.is_(None)
        ).first()

        if not agent:
            raise ValueError("Agent not found")

        agent.alert_acknowledged = True
        agent.alert_acknowledged_at = datetime.utcnow()
        agent.alert_acknowledged_by = acknowledged_by

        db.commit()
        db.refresh(agent)
        return agent

    def update_alert_thresholds(
        self,
        db: Session,
        agent_id: str,
        alert_after_consecutive_failures: int | None = None,
        alert_after_offline_minutes: int | None = None,
        warning_latency_ms: int | None = None,
        critical_latency_ms: int | None = None
    ) -> RemoteAgent:
        """
        Update alert thresholds for an agent.

        Args:
            db: Database session
            agent_id: Agent ID
            alert_after_consecutive_failures: New threshold for consecutive failures
            alert_after_offline_minutes: New threshold for offline minutes
            warning_latency_ms: New warning latency threshold
            critical_latency_ms: New critical latency threshold

        Returns:
            Updated RemoteAgent instance
        """
        agent = db.query(RemoteAgent).filter(
            RemoteAgent.id == agent_id,
            RemoteAgent.archived_at.is_(None)
        ).first()

        if not agent:
            raise ValueError("Agent not found")

        if alert_after_consecutive_failures is not None:
            agent.alert_after_consecutive_failures = alert_after_consecutive_failures
        if alert_after_offline_minutes is not None:
            agent.alert_after_offline_minutes = alert_after_offline_minutes
        if warning_latency_ms is not None:
            agent.warning_latency_ms = warning_latency_ms
        if critical_latency_ms is not None:
            agent.critical_latency_ms = critical_latency_ms

        db.commit()
        db.refresh(agent)
        return agent


# Singleton instance
_remote_agent_service: Optional[RemoteAgentService] = None


def get_remote_agent_service() -> RemoteAgentService:
    """Get singleton remote agent service instance."""
    global _remote_agent_service
    if _remote_agent_service is None:
        settings = Settings.get()
        _remote_agent_service = RemoteAgentService(settings)
    return _remote_agent_service
