import json
import logging

from core.config import settings
from repositories.notification_repository import (
    create_notification,
    deactivate_push_subscription,
    delete_push_subscription_by_endpoint,
    get_active_push_subscriptions,
    get_user_notification_by_id,
    get_user_notifications,
    mark_notification_read,
    mark_push_subscription_used,
    upsert_push_subscription,
)
from services.realtime_service import emit_user_event

logger = logging.getLogger(__name__)


def get_web_push_public_config():
    return {
        "enabled": settings.WEB_PUSH_ENABLED,
        "public_key": settings.WEB_PUSH_VAPID_PUBLIC_KEY if settings.WEB_PUSH_ENABLED else None,
    }


def save_web_push_subscription_service(db, user_id, payload, user_agent=None):
    return upsert_push_subscription(
        db,
        user_id=user_id,
        endpoint=payload.endpoint,
        p256dh=payload.keys.p256dh,
        auth=payload.keys.auth,
        user_agent=user_agent,
    )


def delete_web_push_subscription_service(db, user_id, payload):
    return delete_push_subscription_by_endpoint(db, user_id, payload.endpoint)


def list_user_notifications_service(db, user_id, unread_only=False, limit=50, offset=0):
    return get_user_notifications(db, user_id, unread_only, limit, offset)


def mark_user_notification_read_service(db, user_id, notification_id):
    notification = get_user_notification_by_id(db, user_id, notification_id)
    if not notification:
        raise Exception("Notification not found")
    return mark_notification_read(db, notification)


def notify_cleaner_booking_assigned(db, cleaner_user_id, assignment):
    booking = assignment.booking
    service_name = booking.service_category.service_name if booking and booking.service_category else "service"
    scheduled_date = str(booking.scheduled_date) if booking and booking.scheduled_date else None
    scheduled_time = str(booking.scheduled_time) if booking and booking.scheduled_time else None
    schedule_text = " ".join(part for part in [scheduled_date, scheduled_time] if part)

    title = "New booking assigned"
    message = f"You have been assigned a {service_name} booking"
    if schedule_text:
        message = f"{message} for {schedule_text}"

    notification = create_notification(db, {
        "user_id": cleaner_user_id,
        "title": title,
        "message": message,
        "notification_type": "booking_assigned",
        "url": f"/cleaner/bookings/{assignment.booking_id}",
    })

    data = {
        "notification_id": str(notification.id),
        "type": "booking_assigned",
        "assignment_id": str(assignment.id),
        "booking_id": str(assignment.booking_id),
        "url": f"/cleaner/bookings/{assignment.booking_id}",
    }
    emit_user_event(
        cleaner_user_id,
        "notification_created",
        {
            "notification": format_notification(notification),
            **data,
        },
    )
    send_web_push_to_user(db, cleaner_user_id, title, message, data)
    return notification


def notify_user_booking_status_change(db, user_id, title, message, notification_type, booking_id=None, url=None):
    notification = create_notification(db, {
        "user_id": user_id,
        "title": title,
        "message": message,
        "notification_type": notification_type,
        "url": url,
    })

    data = {
        "notification_id": str(notification.id),
        "type": notification_type,
    }
    if booking_id is not None:
        data["booking_id"] = str(booking_id)
    if url is not None:
        data["url"] = url

    emit_user_event(
        user_id,
        "notification_created",
        {
            "notification": format_notification(notification),
            **data,
        },
    )
    send_web_push_to_user(db, user_id, title, message, data)
    return notification


def notify_customer_booking_accepted(db, booking):
    title = "Cleaner assigned"
    message = f"A cleaner accepted your booking {booking.booking_reference or ''}."
    url = f"/customer/bookings/{booking.id}"
    return notify_user_booking_status_change(
        db,
        booking.customer_id,
        title,
        message,
        "booking_accepted",
        booking_id=booking.id,
        url=url,
    )


def notify_customer_service_started(db, booking):
    title = "Service started"
    message = f"Your service {booking.booking_reference or ''} has started."
    url = f"/customer/bookings/{booking.id}"
    return notify_user_booking_status_change(
        db,
        booking.customer_id,
        title,
        message,
        "service_started",
        booking_id=booking.id,
        url=url,
    )


def notify_customer_service_completed(db, booking):
    title = "Service completed"
    message = f"Your service {booking.booking_reference or ''} has been completed."
    url = f"/customer/bookings/{booking.id}"
    return notify_user_booking_status_change(
        db,
        booking.customer_id,
        title,
        message,
        "service_completed",
        booking_id=booking.id,
        url=url,
    )


def notify_customer_booking_rejected(db, booking):
    title = "Booking not accepted"
    message = f"Your booking {booking.booking_reference or ''} was not accepted by the cleaner and will be reassigned."
    url = f"/customer/bookings/{booking.id}"
    return notify_user_booking_status_change(
        db,
        booking.customer_id,
        title,
        message,
        "booking_rejected",
        booking_id=booking.id,
        url=url,
    )


def notify_admin_booking_assignment_accepted(db, assignment):
    booking = assignment.booking
    cleaner_name = None
    if assignment.cleaner and assignment.cleaner.user:
        cleaner_name = assignment.cleaner.user.full_name
    cleaner_name = cleaner_name or "Cleaner"
    title = "Booking accepted by cleaner"
    message = f"{cleaner_name} has accepted booking {booking.booking_reference or ''}."
    url = f"/admin/bookings/{booking.id}"
    return notify_user_booking_status_change(
        db,
        assignment.assigned_by_admin,
        title,
        message,
        "booking_assignment_accepted",
        booking_id=booking.id,
        url=url,
    )


def notify_admin_booking_assignment_rejected(db, assignment):
    booking = assignment.booking
    cleaner_name = None
    if assignment.cleaner and assignment.cleaner.user:
        cleaner_name = assignment.cleaner.user.full_name
    cleaner_name = cleaner_name or "Cleaner"
    title = "Booking rejected by cleaner"
    message = f"{cleaner_name} has rejected booking {booking.booking_reference or ''}. Please assign another cleaner."
    url = f"/admin/bookings/{booking.id}"
    return notify_user_booking_status_change(
        db,
        assignment.assigned_by_admin,
        title,
        message,
        "booking_assignment_rejected",
        booking_id=booking.id,
        url=url,
    )


def send_web_push_to_user(db, user_id, title, body, data=None):
    if not settings.WEB_PUSH_ENABLED:
        logger.info("Web Push disabled; stored notification only for user %s", user_id)
        return {"sent": 0, "failed": 0, "disabled": True}
    try:
        from pywebpush import WebPushException, webpush
    except ImportError:
        logger.warning("pywebpush is not installed; stored notification only for user %s", user_id)
        return {"sent": 0, "failed": 0, "disabled": True}

    payload = json.dumps({
        "title": title,
        "body": body,
        "data": data or {},
    })
    subscriptions = get_active_push_subscriptions(db, user_id)
    sent = 0
    failed = 0

    for subscription in subscriptions:
        subscription_info = {
            "endpoint": subscription.endpoint,
            "keys": {
                "p256dh": subscription.p256dh,
                "auth": subscription.auth,
            },
        }
        try:
            webpush(
                subscription_info=subscription_info,
                data=payload,
                vapid_private_key=settings.WEB_PUSH_VAPID_PRIVATE_KEY,
                vapid_claims={"sub": settings.WEB_PUSH_VAPID_SUBJECT},
            )
            mark_push_subscription_used(db, subscription)
            sent += 1
        except WebPushException as exc:
            failed += 1
            status_code = getattr(getattr(exc, "response", None), "status_code", None)
            if status_code in [404, 410]:
                deactivate_push_subscription(db, subscription)
            logger.warning("Web Push delivery failed for user %s: %s", user_id, exc)

    return {"sent": sent, "failed": failed, "disabled": False}


def format_notification(notification):
    return {
        "id": str(notification.id),
        "title": notification.title,
        "message": notification.message,
        "notification_type": notification.notification_type,
        "url": notification.url,
        "is_read": bool(notification.is_read),
        "created_at": notification.created_at.isoformat() if notification.created_at else None,
    }
