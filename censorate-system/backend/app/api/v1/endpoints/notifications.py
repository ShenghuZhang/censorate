"""Notification endpoints - API routes for notifications."""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import get_current_user
from app.schemas.notification import (
    NotificationResponse,
    UserNotificationPreferenceResponse,
    UserNotificationPreferenceUpdate,
    UnreadCountResponse
)
from app.services.notification_service import get_notification_service

router = APIRouter()
notification_service = get_notification_service()


@router.get("/notifications", response_model=List[NotificationResponse])
def list_notifications(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    unread_only: bool = Query(False),
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get notifications for the current user."""
    try:
        notifications = notification_service.get_user_notifications(
            db, UUID(current_user_id), limit, offset, unread_only
        )
        return notifications
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )


@router.get("/notifications/unread-count", response_model=UnreadCountResponse)
def get_unread_count(
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get count of unread notifications."""
    try:
        count = notification_service.get_unread_count(db, UUID(current_user_id))
        return {"count": count}
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )


@router.put("/notifications/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_read(
    notification_id: str,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a notification as read."""
    try:
        notification = notification_service.mark_as_read(db, UUID(notification_id))
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        # Verify ownership
        if str(notification.user_id) != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to modify this notification"
            )
        return notification
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ID format"
        )


@router.put("/notifications/read-all")
def mark_all_read(
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read."""
    try:
        count = notification_service.mark_all_as_read(db, UUID(current_user_id))
        return {"message": f"Marked {count} notifications as read", "count": count}
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )


@router.delete("/notifications/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(
    notification_id: str,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete (archive) a notification."""
    try:
        from app.models.notification import Notification
        notification = db.query(Notification).filter(
            Notification.id == UUID(notification_id)
        ).first()

        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        if str(notification.user_id) != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this notification"
            )

        notification_service.delete_notification(db, UUID(notification_id))
        return None
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ID format"
        )


@router.get("/notifications/preferences", response_model=UserNotificationPreferenceResponse)
def get_preferences(
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get notification preferences for current user."""
    try:
        preferences = notification_service.get_user_preferences(db, UUID(current_user_id))
        return preferences
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )


@router.put("/notifications/preferences", response_model=UserNotificationPreferenceResponse)
def update_preferences(
    preferences_in: UserNotificationPreferenceUpdate,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update notification preferences."""
    try:
        preferences = notification_service.update_user_preferences(
            db, UUID(current_user_id), preferences_in.model_dump(exclude_unset=True)
        )
        return preferences
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
