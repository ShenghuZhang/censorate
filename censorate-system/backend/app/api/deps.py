from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Dependency to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_agent(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
):
    """Dependency to authenticate a remote agent via its API key.

    Extracts Bearer token from Authorization header, looks up the
    corresponding RemoteAgent by decrypting stored API keys.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    api_key = credentials.credentials

    from app.models.remote_agent import RemoteAgent
    agents = db.query(RemoteAgent).filter(RemoteAgent.archived_at.is_(None)).all()

    for agent in agents:
        if agent.api_key and agent.api_key == api_key:
            return agent

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API key",
        headers={"WWW-Authenticate": "Bearer"},
    )
