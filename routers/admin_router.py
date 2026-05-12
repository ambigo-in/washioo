from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.role_dependencies import require_roles
from services.notification_service import (
    format_notification,
    list_user_notifications_service,
    mark_user_notification_read_service,
)
from services.cleanup_service import (
    cleanup_assignment_attempts,
    cleanup_audit_logs,
    cleanup_notifications,
    cleanup_otp_codes,
    cleanup_push_subscriptions,
    cleanup_refresh_tokens,
    get_cleanup_preview,
    run_all_cleanups,
)


router = APIRouter(prefix="/admin", tags=["Admin APIs"])


def _cleanup_response(db, target, deleted_count):
    db.commit()
    return {
        "message": "Cleanup completed successfully",
        "target": target,
        "deleted_count": deleted_count,
    }


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


@router.get("/cleanup/preview")
def preview_admin_cleanup(
    db: Session = Depends(get_db),
    current_admin=Depends(require_roles(["admin"])),
):
    return {
        "message": "Cleanup preview fetched successfully",
        "items": get_cleanup_preview(db),
    }


@router.delete("/cleanup/otp-codes")
def cleanup_admin_otp_codes(
    retention_hours: int = Query(24, ge=1, le=720),
    db: Session = Depends(get_db),
    current_admin=Depends(require_roles(["admin"])),
):
    deleted_count = cleanup_otp_codes(db, retention_hours=retention_hours)
    return _cleanup_response(db, "otp_codes", deleted_count)


@router.delete("/cleanup/refresh-tokens")
def cleanup_admin_refresh_tokens(
    retention_days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db),
    current_admin=Depends(require_roles(["admin"])),
):
    deleted_count = cleanup_refresh_tokens(db, retention_days=retention_days)
    return _cleanup_response(db, "refresh_tokens", deleted_count)


@router.delete("/cleanup/notifications")
def cleanup_admin_notifications(
    read_days: int = Query(30, ge=1, le=365),
    unread_days: int = Query(90, ge=1, le=730),
    db: Session = Depends(get_db),
    current_admin=Depends(require_roles(["admin"])),
):
    deleted_count = cleanup_notifications(
        db,
        read_days=read_days,
        unread_days=unread_days,
    )
    return _cleanup_response(db, "notifications", deleted_count)


@router.delete("/cleanup/assignment-attempts")
def cleanup_admin_assignment_attempts(
    retention_days: int = Query(60, ge=1, le=730),
    db: Session = Depends(get_db),
    current_admin=Depends(require_roles(["admin"])),
):
    deleted_count = cleanup_assignment_attempts(
        db,
        retention_days=retention_days,
    )
    return _cleanup_response(db, "assignment_attempts", deleted_count)


@router.delete("/cleanup/push-subscriptions")
def cleanup_admin_push_subscriptions(
    inactive_days: int = Query(30, ge=1, le=365),
    unused_days: int = Query(180, ge=1, le=1095),
    db: Session = Depends(get_db),
    current_admin=Depends(require_roles(["admin"])),
):
    deleted_count = cleanup_push_subscriptions(
        db,
        inactive_days=inactive_days,
        unused_days=unused_days,
    )
    return _cleanup_response(db, "push_subscriptions", deleted_count)


@router.delete("/cleanup/audit-logs")
def cleanup_admin_audit_logs(
    retention_days: int = Query(90, ge=1, le=1095),
    db: Session = Depends(get_db),
    current_admin=Depends(require_roles(["admin"])),
):
    deleted_count = cleanup_audit_logs(db, retention_days=retention_days)
    return _cleanup_response(db, "audit_logs", deleted_count)


@router.post("/cleanup/run-all")
def run_all_admin_cleanups(
    db: Session = Depends(get_db),
    current_admin=Depends(require_roles(["admin"])),
):
    results = run_all_cleanups(db)
    db.commit()
    return {
        "message": "All cleanup tasks completed successfully",
        "results": results,
        "deleted_count": sum(results.values()),
    }
