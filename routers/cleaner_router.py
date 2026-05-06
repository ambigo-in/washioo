from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.role_dependencies import require_roles
from schemas.notification_schema import (
    DeleteWebPushSubscriptionRequest,
    WebPushSubscriptionRequest,
)
from services.booking_service import get_cleaner_booking_service, format_cleaner_booking_detail
from services.notification_service import (
    delete_web_push_subscription_service,
    format_notification,
    get_web_push_public_config,
    list_user_notifications_service,
    mark_user_notification_read_service,
    save_web_push_subscription_service,
)

router = APIRouter(prefix="/cleaner", tags=["Cleaner APIs"])


@router.get("/push/public-key")
def get_cleaner_web_push_public_key(
    current_cleaner=Depends(require_roles(["cleaner"])),
):
    """Frontend uses this VAPID public key to subscribe the cleaner browser."""
    return {
        "message": "Web Push configuration fetched successfully",
        "web_push": get_web_push_public_config(),
    }


@router.post("/push/subscriptions", status_code=status.HTTP_201_CREATED)
def save_cleaner_web_push_subscription(
    payload: WebPushSubscriptionRequest,
    db: Session = Depends(get_db),
    current_cleaner=Depends(require_roles(["cleaner"])),
    user_agent: str | None = Header(default=None),
):
    """Save or refresh this browser's Web Push subscription for the cleaner."""
    try:
        subscription = save_web_push_subscription_service(
            db,
            current_cleaner.id,
            payload,
            user_agent=user_agent,
        )
        return {
            "message": "Push subscription saved successfully",
            "subscription": {
                "id": str(subscription.id),
                "is_active": bool(subscription.is_active),
            },
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Request could not be processed")


@router.delete("/push/subscriptions")
def delete_cleaner_web_push_subscription(
    payload: DeleteWebPushSubscriptionRequest,
    db: Session = Depends(get_db),
    current_cleaner=Depends(require_roles(["cleaner"])),
):
    """Delete this browser's Web Push subscription, usually during logout."""
    delete_web_push_subscription_service(db, current_cleaner.id, payload)
    return {"message": "Push subscription removed successfully"}


@router.get("/notifications")
def list_cleaner_notifications(
    unread_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_cleaner=Depends(require_roles(["cleaner"])),
):
    notifications = list_user_notifications_service(
        db,
        current_cleaner.id,
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
def mark_cleaner_notification_read(
    notification_id: str,
    db: Session = Depends(get_db),
    current_cleaner=Depends(require_roles(["cleaner"])),
):
    try:
        notification = mark_user_notification_read_service(db, current_cleaner.id, notification_id)
        return {
            "message": "Notification marked as read",
            "notification": format_notification(notification),
        }
    except Exception as exc:
        raise HTTPException(status_code=404, detail="Notification not found")


@router.get("/bookings/{booking_id}")
def get_cleaner_booking_details(
    booking_id: str,
    db: Session = Depends(get_db),
    current_cleaner=Depends(require_roles(["cleaner"])),
):
    """Cleaner can view details only for bookings assigned to them."""
    try:
        booking = get_cleaner_booking_service(db, current_cleaner.id, booking_id)
        return {
            "message": "Booking fetched successfully",
            "booking": format_cleaner_booking_detail(booking),
        }
    except Exception as exc:
        raise HTTPException(status_code=404, detail="Request could not be processed")
