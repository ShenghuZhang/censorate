from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_agent
from app.models.remote_agent import RemoteAgent
from app.schemas.remote_agent import (
    RemoteAgentCreate, RemoteAgentUpdate, RemoteAgentResponse,
    HealthCheckResponse, AgentChatRequest, AgentChatResponse,
    RemoteAgentHealthHistoryResponse, RemoteAgentWithHistoryResponse,
    AgentAcknowledgement, AgentThresholdUpdate,
    AgentSkillManifest, AgentSkillListResponse, AgentSkillFileInfo
)
from app.services.remote_agent_service import get_remote_agent_service
from app.services.skills_proxy_service import get_skill_catalog_service
from app.services import get_skill_service

import httpx
import json
import asyncio
import threading
from io import BytesIO
from pathlib import Path

router = APIRouter()


def _trigger_skill_sync_via_webhook(agent: RemoteAgent, censorate_url: str, db: Session):
    """Trigger skill sync via webhook if skill_manager_url is configured.

    This sends complete skills data to the skill-manager sidecar.
    Falls back to in-process sync if webhook isn't configured.
    """
    skill_manager_url = agent.config.get("skill_manager_url") if agent.config else None

    if skill_manager_url:
        # Use webhook for real-time sync with sidecar
        def _send_webhook():
            try:
                import httpx
                from app.models.skill import Skill
                from app.services import get_skill_service

                webhook_url = f"{skill_manager_url.rstrip('/')}/webhook/agent-updated"
                print(f"[SkillManager] Sending webhook to {webhook_url}")

                # Get skill service
                skill_service = get_skill_service()

                # Get all skills for this agent
                capabilities = agent.capabilities or []
                skills = db.query(Skill).filter(
                    Skill.slug.in_(capabilities),
                    Skill.is_published == True,
                    Skill.is_archived == False
                ).all()

                # Build skills data
                skills_data = []
                for skill in skills:
                    version = None
                    if skill.latest_version_id:
                        version = skill_service.version_repo.get(db, skill.latest_version_id)

                    if version:
                        files = skill_service.get_files_for_version(db, version.id)
                        file_infos = []
                        for f in files:
                            try:
                                content = skill_service.get_file_content(db, version.id, f.path)
                                content_str = content.decode("utf-8", errors="ignore") if content else None
                            except Exception:
                                content_str = None
                            file_infos.append({
                                "path": f.path,
                                "content_type": f.content_type,
                                "file_size": f.file_size,
                                "content": content_str
                            })

                        skills_data.append({
                            "slug": skill.slug,
                            "name": skill.name,
                            "description": skill.description,
                            "category": skill.category,
                            "version": version.version,
                            "manifest": version.manifest or {},
                            "files": file_infos
                        })

                # Send complete data to skill-manager
                httpx.post(
                    webhook_url,
                    json={
                        "agent_id": str(agent.id),
                        "agent_name": agent.name,
                        "event_type": "capabilities_updated",
                        "capabilities": capabilities,
                        "skills": skills_data
                    },
                    timeout=30.0
                )
                print(f"[SkillManager] Webhook sent successfully with {len(skills_data)} skills")
            except Exception as e:
                print(f"[SkillManager] Webhook failed: {e}")
                import traceback
                traceback.print_exc()

        threading.Thread(target=_send_webhook, daemon=True).start()
    else:
        # Fall back to in-process sync (legacy behavior)
        from app.core.config import Settings
        settings = Settings.get()
        hermes_data_path = settings.HERMES_DATA_PATH or "./hermes_data"
        if agent.api_key:
            _trigger_skill_sync_in_process(agent.api_key, hermes_data_path, censorate_url)


def _trigger_skill_sync_in_process(api_key: str, hermes_data_path: str, censorate_url: str):
    """Run skill_manager sync in a background thread (legacy mode)."""
    def _run():
        try:
            import importlib.util
            import sys
            from pathlib import Path

            # Try to import from daemon directory first, fall back to scripts
            daemon_script = Path(__file__).parent.parent.parent.parent / "daemon" / "skill_manager.py"
            if daemon_script.exists():
                spec = importlib.util.spec_from_file_location("skill_manager", daemon_script)
                skill_manager = importlib.util.module_from_spec(spec)
                sys.modules["skill_manager"] = skill_manager
                spec.loader.exec_module(skill_manager)
                SkillManager = skill_manager.SkillManager
            else:
                # Fall back to scripts directory (for backwards compatibility)
                try:
                    from scripts.skill_manager import SkillManager
                except ImportError:
                    print("[SkillManager] skill_manager.py not found, skipping sync")
                    return

            manager = SkillManager(
                censorate_url=censorate_url,
                api_key=api_key,
                hermes_data=Path(hermes_data_path),
            )
            results = manager.sync()
            total = (
                len(results.get("installed", []))
                + len(results.get("updated", []))
                + len(results.get("removed", []))
            )
            if total > 0 or results.get("errors"):
                print(f"[SkillManager] Agent-triggered sync: "
                      f"installed={len(results.get('installed', []))} "
                      f"updated={len(results.get('updated', []))} "
                      f"removed={len(results.get('removed', []))} "
                      f"errors={len(results.get('errors', []))}")
                if total > 0 and not results.get("errors"):
                    print("[SkillManager] Skills updated on disk. "
                          "Hermes will pick up changes on next session start.")
        except Exception as e:
            print(f"[SkillManager] Background sync failed: {e}")
            import traceback
            traceback.print_exc()

    threading.Thread(target=_run, daemon=True).start()


# --- Remote Agents CRUD ---


@router.get("/remote-agents/available-skills")
def list_available_skills():
    """List all available skills that can be assigned to agents."""
    catalog = get_skill_catalog_service()
    return catalog.list_available_skills()


@router.get("/remote-agents", response_model=List[RemoteAgentResponse])
def list_remote_agents(db: Session = Depends(get_db)):
    """List all registered remote agents."""
    agents = db.query(RemoteAgent).filter(
        RemoteAgent.archived_at.is_(None)
    ).all()
    return agents


@router.post("/remote-agents", response_model=RemoteAgentResponse, status_code=status.HTTP_201_CREATED)
def register_remote_agent(
    data: RemoteAgentCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Register a new remote agent."""
    # Check if name already exists
    existing = db.query(RemoteAgent).filter(
        RemoteAgent.name == data.name,
        RemoteAgent.archived_at.is_(None)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Remote agent with name '{data.name}' already exists"
        )

    try:
        agent_data = data.model_dump()
        # Extract api_key if present
        api_key = agent_data.pop('api_key', None)

        # Auto-set skill_manager_url if config doesn't have it and env var is set
        from app.core.config import Settings
        settings = Settings.get()
        if settings.SKILL_MANAGER_URL:
            if not agent_data.get('config'):
                agent_data['config'] = {}
            if 'skill_manager_url' not in agent_data['config']:
                agent_data['config']['skill_manager_url'] = settings.SKILL_MANAGER_URL

        # Create agent without api_key first
        agent = RemoteAgent(**agent_data)
        # Set api_key separately if provided
        if api_key is not None:
            agent.api_key = api_key
        db.add(agent)
        db.commit()
        db.refresh(agent)
    except Exception as e:
        db.rollback()
        print(f"Error creating agent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create agent: {str(e)}"
        )

    if agent.capabilities and agent.api_key:
        try:
            base_url = str(request.base_url).rstrip("/")
            censorate_url = f"{base_url}{settings.API_PREFIX}"
            _trigger_skill_sync_via_webhook(agent, censorate_url, db)
        except Exception as e:
            print(f"Warning: Failed to trigger skill sync: {e}")

    return agent


# ===== Agent Skill Hub (Self-Managed Skills) =====
# NOTE: Must be registered BEFORE /remote-agents/{agent_id} to avoid route conflicts.

def _verify_skill_access(agent: RemoteAgent, slug: str):
    """Verify that the agent has the given skill in its capabilities."""
    caps = agent.capabilities or []
    if slug not in caps:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Skill '{slug}' is not in this agent's capabilities"
        )


def _build_agent_skill_manifest(
    db: Session,
    skill,
    version,
    base_url: str
) -> AgentSkillManifest:
    """Build an agent-facing manifest for a skill version."""
    skill_service = get_skill_service()

    files = skill_service.get_files_for_version(db, version.id)
    file_infos = [
        AgentSkillFileInfo(
            path=f.path,
            content_type=f.content_type,
            file_size=f.file_size,
            sha256_hash=f.sha256_hash
        )
        for f in files
    ]

    download_url = f"{base_url}/remote-agents/skills/{skill.slug}/download"
    if version.version:
        download_url += f"?version={version.version}"

    return AgentSkillManifest(
        slug=skill.slug,
        name=skill.name,
        description=skill.description,
        category=skill.category,
        version=version.version,
        manifest=version.manifest or {},
        files=file_infos,
        download_url=download_url,
        published_at=version.created_at
    )


@router.get("/remote-agents/skills", response_model=AgentSkillListResponse)
def list_agent_skills(
    request: Request,
    agent: RemoteAgent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """List all skills available to the authenticated agent (via capabilities)."""
    from app.models.skill import Skill

    skill_service = get_skill_service()
    caps = agent.capabilities or []

    if not caps:
        return AgentSkillListResponse(count=0, skills=[])

    skills = db.query(Skill).filter(
        Skill.slug.in_(caps),
        Skill.is_published == True,
        Skill.is_archived == False
    ).all()

    base_url = str(request.base_url).rstrip("/")
    manifests = []
    for skill in skills:
        version = None
        if skill.latest_version_id:
            version = skill_service.version_repo.get(db, skill.latest_version_id)
        if not version:
            continue
        manifests.append(_build_agent_skill_manifest(db, skill, version, base_url))

    return AgentSkillListResponse(count=len(manifests), skills=manifests)


@router.get("/remote-agents/skills/{slug}", response_model=AgentSkillManifest)
def get_agent_skill_manifest(
    slug: str,
    request: Request,
    agent: RemoteAgent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """Get the manifest for a specific skill (agent must have it in capabilities)."""
    _verify_skill_access(agent, slug)

    skill_service = get_skill_service()

    skill = skill_service.get_skill(db, slug)
    version = None
    if skill.latest_version_id:
        version = skill_service.version_repo.get(db, skill.latest_version_id)
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No version available for this skill"
        )

    base_url = str(request.base_url).rstrip("/")
    return _build_agent_skill_manifest(db, skill, version, base_url)


@router.get("/remote-agents/skills/{slug}/download")
def download_agent_skill(
    slug: str,
    version: Optional[str] = None,
    agent: RemoteAgent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """Download a skill as a ZIP (agent must have it in capabilities)."""
    _verify_skill_access(agent, slug)

    skill_service = get_skill_service()

    skill = skill_service.get_skill(db, slug)

    ver = None
    if version:
        ver = skill_service.get_version(db, skill.id, version)
        version_id = ver.id
    else:
        version_id = skill.latest_version_id

    if not version_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No version available"
        )

    zip_content = skill_service.generate_zip(db, skill.id, version_id)
    version_str = ver.version if ver else "latest"
    filename = f"{skill.slug}-{version_str}.zip"

    return StreamingResponse(
        BytesIO(zip_content),
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "private, max-age=60"
        }
    )


@router.get("/remote-agents/skills/{slug}/files/{file_path:path}")
def download_agent_skill_file(
    slug: str,
    file_path: str,
    version: Optional[str] = None,
    agent: RemoteAgent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """Download a single file from a skill (agent must have it in capabilities)."""
    _verify_skill_access(agent, slug)

    skill_service = get_skill_service()

    skill = skill_service.get_skill(db, slug)

    if version:
        ver = skill_service.get_version(db, skill.id, version)
        version_id = ver.id
    else:
        version_id = skill.latest_version_id

    if not version_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No version available"
        )

    content = skill_service.get_file_content(db, version_id, file_path)
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    file_record = skill_service.file_repo.get_by_version_and_path(db, version_id, file_path)
    media_type = file_record.content_type if file_record else "application/octet-stream"

    return StreamingResponse(
        BytesIO(content),
        media_type=media_type,
        headers={"Content-Disposition": f'inline; filename="{file_path}"'}
    )


@router.get("/remote-agents/{agent_id}", response_model=RemoteAgentResponse)
def get_remote_agent(agent_id: str, db: Session = Depends(get_db)):
    """Get a remote agent by ID."""
    agent = db.query(RemoteAgent).filter(
        RemoteAgent.id == agent_id,
        RemoteAgent.archived_at.is_(None)
    ).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Remote agent not found"
        )
    return agent


@router.get("/remote-agents/{agent_id}/with-history", response_model=RemoteAgentWithHistoryResponse)
def get_remote_agent_with_history(
    agent_id: str,
    history_limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get a remote agent by ID with recent health history."""
    agent = db.query(RemoteAgent).filter(
        RemoteAgent.id == agent_id,
        RemoteAgent.archived_at.is_(None)
    ).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Remote agent not found"
        )

    service = get_remote_agent_service()
    history = service.get_health_history(db, agent_id, limit=history_limit)

    return RemoteAgentWithHistoryResponse(
        **RemoteAgentResponse.model_validate(agent).model_dump(),
        recent_health_history=history
    )


@router.put("/remote-agents/{agent_id}", response_model=RemoteAgentResponse)
def update_remote_agent(
    agent_id: str,
    data: RemoteAgentUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Update a remote agent."""
    agent = db.query(RemoteAgent).filter(
        RemoteAgent.id == agent_id,
        RemoteAgent.archived_at.is_(None)
    ).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Remote agent not found"
        )

    update_data = data.model_dump(exclude_unset=True)

    # Auto-set skill_manager_url if config doesn't have it and env var is set
    from app.core.config import Settings
    settings = Settings.get()
    if settings.SKILL_MANAGER_URL:
        if "config" in update_data:
            if not update_data["config"]:
                update_data["config"] = {}
            if 'skill_manager_url' not in update_data["config"]:
                # Check existing agent config too
                existing_config = agent.config or {}
                if 'skill_manager_url' not in existing_config:
                    update_data["config"]["skill_manager_url"] = settings.SKILL_MANAGER_URL

    # Detect capabilities change to trigger skill sync
    caps_changed = False
    if "capabilities" in update_data:
        old_caps = set(agent.capabilities or [])
        new_caps = set(update_data["capabilities"] or [])
        caps_changed = (old_caps != new_caps)

    for field, value in update_data.items():
        if hasattr(agent, field):
            setattr(agent, field, value)

    db.commit()
    db.refresh(agent)

    if caps_changed and agent.api_key:
        base_url = str(request.base_url).rstrip("/")
        censorate_url = f"{base_url}{settings.API_PREFIX}"
        _trigger_skill_sync_via_webhook(agent, censorate_url, db)

    return agent


@router.delete("/remote-agents/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
def unregister_remote_agent(agent_id: str, db: Session = Depends(get_db)):
    """Unregister (archive) a remote agent."""
    agent = db.query(RemoteAgent).filter(
        RemoteAgent.id == agent_id
    ).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Remote agent not found"
        )

    agent.archived_at = datetime.utcnow()
    db.commit()
    return None


# --- Health Check ---


@router.post("/remote-agents/{agent_id}/health", response_model=HealthCheckResponse)
async def check_agent_health(agent_id: str, db: Session = Depends(get_db)):
    """Trigger a health check for a specific agent."""
    agent = db.query(RemoteAgent).filter(
        RemoteAgent.id == agent_id,
        RemoteAgent.archived_at.is_(None)
    ).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Remote agent not found"
        )

    service = get_remote_agent_service()
    status_str, response_time, message = await service.check_agent_health(agent)

    # Use enhanced update_agent_status that records history and manages alerts
    service.update_agent_status(db, agent, status_str, response_time, message)

    return HealthCheckResponse(
        status=status_str,
        response_time_ms=response_time,
        last_health_check=agent.last_health_check,
        message=message
    )


@router.post("/remote-agents/health/all")
async def check_all_agents_health(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Trigger health checks for all agents (background task)."""
    agents = db.query(RemoteAgent).filter(
        RemoteAgent.archived_at.is_(None)
    ).all()

    service = get_remote_agent_service()

    async def check_all_and_update():
        """Check all agents health in parallel and update database."""
        results = await service.check_all_agents_health(agents)
        for agent, status_str, response_time, error in results:
            # Use enhanced update that records history
            service.update_agent_status(db, agent, status_str, response_time, error)

    # Add proper background task (no lambda wrapper)
    background_tasks.add_task(check_all_and_update)

    return {"status": "started", "count": len(agents)}


# --- Health History ---


@router.get("/remote-agents/{agent_id}/health-history", response_model=List[RemoteAgentHealthHistoryResponse])
def get_agent_health_history(
    agent_id: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get health check history for a specific agent."""
    # Verify agent exists
    agent = db.query(RemoteAgent).filter(
        RemoteAgent.id == agent_id,
        RemoteAgent.archived_at.is_(None)
    ).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Remote agent not found"
        )

    service = get_remote_agent_service()
    history = service.get_health_history(db, agent_id, limit=limit, offset=offset)
    return history


@router.post("/remote-agents/{agent_id}/acknowledge-alert", response_model=RemoteAgentResponse)
def acknowledge_agent_alert(
    agent_id: str,
    data: AgentAcknowledgement,
    db: Session = Depends(get_db)
):
    """Acknowledge an alert for an agent."""
    service = get_remote_agent_service()
    try:
        agent = service.acknowledge_alert(db, agent_id, data.acknowledged_by)
        return agent
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put("/remote-agents/{agent_id}/thresholds", response_model=RemoteAgentResponse)
def update_agent_thresholds(
    agent_id: str,
    data: AgentThresholdUpdate,
    db: Session = Depends(get_db)
):
    """Update alert thresholds for an agent."""
    service = get_remote_agent_service()
    try:
        agent = service.update_alert_thresholds(
            db,
            agent_id,
            alert_after_consecutive_failures=data.alert_after_consecutive_failures,
            alert_after_offline_minutes=data.alert_after_offline_minutes,
            warning_latency_ms=data.warning_latency_ms,
            critical_latency_ms=data.critical_latency_ms
        )
        return agent
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# --- Chat ---


@router.post("/remote-agents/{agent_id}/chat", response_model=AgentChatResponse)
async def send_chat_message(
    agent_id: str,
    request: AgentChatRequest,
    db: Session = Depends(get_db)
):
    """Send a chat message to a remote agent."""
    agent = db.query(RemoteAgent).filter(
        RemoteAgent.id == agent_id,
        RemoteAgent.archived_at.is_(None)
    ).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Remote agent not found"
        )

    if agent.status != "online":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agent is not online"
        )

    # Create a fresh client without http2 for better compatibility
    # (similar to health check implementation)
    try:
        timeout = httpx.Timeout(120.0, connect=5.0)
        headers = {"Content-Type": "application/json"}
        # Use the property getter which automatically decrypts
        if agent.api_key:
            headers["Authorization"] = f"Bearer {agent.api_key}"

        # Ensure endpoint URL has protocol and no trailing slash
        endpoint = agent.endpoint_url.strip()
        if not endpoint.startswith(('http://', 'https://')):
            endpoint = f'http://{endpoint}'
        endpoint = endpoint.rstrip('/')

        print(f"[DEBUG] Agent endpoint: {agent.endpoint_url}")
        print(f"[DEBUG] Normalized endpoint: {endpoint}")
        print(f"[DEBUG] Agent type: {agent.agent_type}")

        # Use fresh client with HTTP/2 disabled for better compatibility
        async with httpx.AsyncClient(timeout=timeout, http2=False) as client:
            # Check agent type to determine chat endpoint format
            if agent.agent_type == "hermes":
                # Hermes agent uses OpenAI compatible format
                chat_url = f"{endpoint}/v1/chat/completions"
                print(f"[DEBUG] Using Hermes format, chat_url: {chat_url}")

                # Use project_id as X-Hermes-Session-Id for continuity, fallback to thread_id
                session_id = request.project_id or request.thread_id
                if session_id:
                    headers["X-Hermes-Session-Id"] = session_id

                # Skills are managed by skill_manager (hub-installed in Hermes).
                # Inject hub skill metadata so the model knows which skills are available.
                catalog = get_skill_catalog_service()
                hub_msg = catalog.build_hub_skills_message(agent.capabilities or [])

                messages = []
                if hub_msg:
                    messages.append(hub_msg)
                messages.append({"role": "user", "content": request.message})

                payload = {
                    "model": "hermes-agent",
                    "messages": messages,
                    **(request.config or {}),
                }

                response = await client.post(
                    chat_url,
                    headers=headers,
                    json=payload,
                    timeout=timeout
                )
                response.raise_for_status()
                result = response.json()

                # Parse OpenAI compatible response
                response_text = "No response"
                if result.get("choices") and len(result["choices"]) > 0:
                    choice = result["choices"][0]
                    if choice.get("message"):
                        response_text = choice["message"].get("content", response_text)
                    elif choice.get("text"):
                        response_text = choice.get("text", response_text)

                thread_id = request.thread_id or f"thread-{agent_id}-{int(datetime.utcnow().timestamp())}"

            else:
                # Custom agent format
                chat_url = f"{endpoint}/chat"
                print(f"[DEBUG] Using custom format, chat_url: {chat_url}")

                response = await client.post(
                    chat_url,
                    headers=headers,
                    json={
                        "message": request.message,
                        "thread_id": request.thread_id,
                        **(request.config or {})
                    },
                    timeout=timeout
                )
                response.raise_for_status()
                result = response.json()

                response_text = result.get("response", result.get("message", "No response"))
                thread_id = result.get("thread_id", request.thread_id or f"thread-{agent_id}-{int(datetime.utcnow().timestamp())}")

            return AgentChatResponse(
                response=response_text,
                thread_id=thread_id,
                agent_id=agent.id,
                timestamp=datetime.utcnow()
            )
    except httpx.HTTPStatusError as e:
        error_detail = f"Agent returned error: {e.response.status_code}"
        if 'chat_url' in locals():
            error_detail += f" (URL: {chat_url})"
        try:
            error_data = e.response.json()
            if error_data.get("error"):
                error_detail += f" - {error_data['error'].get('message', str(error_data['error']))}"
        except:
            pass
        print(f"[DEBUG] HTTP error: {error_detail}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )
    except Exception as e:
        import traceback
        error_msg = f"Failed to communicate with agent: {str(e)}"
        if 'chat_url' in locals():
            error_msg += f" (URL: {chat_url})"
        print(f"[ERROR] Chat request failed: {e}")
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )


@router.get("/remote-agents/{agent_id}/chat/stream")
async def stream_chat_message(
    agent_id: str,
    message: str,
    thread_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Stream a chat with a remote agent using SSE."""
    agent = db.query(RemoteAgent).filter(
        RemoteAgent.id == agent_id,
        RemoteAgent.archived_at.is_(None)
    ).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Remote agent not found"
        )

    if agent.status != "online":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agent is not online"
        )

    async def generate():
        yield f"data: {json.dumps({'type': 'status', 'content': 'connecting'})}\n\n"
        await asyncio.sleep(0.1)

        yield f"data: {json.dumps({'type': 'status', 'content': 'typing'})}\n\n"
        await asyncio.sleep(0.2)

        # Simple fallback response for now
        response = f"Received: {message}"
        for char in response:
            yield f"data: {json.dumps({'type': 'text', 'content': char})}\n\n"
            await asyncio.sleep(0.03)

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

