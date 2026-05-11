from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.role_dependencies import require_roles
from services.notification_service import (
    format_notification,
    list_user_notifications_service,
    mark_user_notification_read_service,
)


router = APIRouter(prefix="/admin", tags=["Admin APIs"])


@router.get("/notifications")
def list_admin_notifications(
    unread_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_admin=Depends(require_roles(["admin"])),
):
    notifications = list_user_notifications_service(
        db,
        current_admin.id,
        unread_only=unread_only,
        limit=limit,
        offset=offset,
    )
    notification_list = [format_notification(notification) for notification in notifications]
    return {
        "message": "Notifications fetched successfully",
        "notifications": notification_list,
        "total": len(notification_list),
    }


@router.patch("/notifications/{notification_id}/read")
def mark_admin_notification_read(
    notification_id: str,
    db: Session = Depends(get_db),
    current_admin=Depends(require_roles(["admin"])),
):
    try:
        notification = mark_user_notification_read_service(
            db,
            current_admin.id,
            notification_id,
        )
        return {
            "message": "Notification marked as read",
            "notification": format_notification(notification),
        }
    except Exception:
        raise HTTPException(status_code=404, detail="Notification not found")
