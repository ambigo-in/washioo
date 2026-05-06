from datetime import datetime

from models.notification import Notification
from models.push_subscription import PushSubscription


def create_notification(db, notification_data):
    notification = Notification(**notification_data)
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def get_user_notifications(db, user_id, unread_only=False, limit=50, offset=0):
    query = db.query(Notification).filter(Notification.user_id == user_id)
    if unread_only:
        query = query.filter(Notification.is_read.is_(False))
    return (
        query.order_by(Notification.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def get_user_notification_by_id(db, user_id, notification_id):
    return (
        db.query(Notification)
        .filter(Notification.id == notification_id, Notification.user_id == user_id)
        .first()
    )


def mark_notification_read(db, notification):
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return notification


def upsert_push_subscription(db, user_id, endpoint, p256dh, auth, user_agent=None):
    subscription = (
        db.query(PushSubscription)
        .filter(PushSubscription.endpoint == endpoint)
        .first()
    )
    if subscription:
        subscription.user_id = user_id
        subscription.p256dh = p256dh
        subscription.auth = auth
        subscription.user_agent = user_agent
        subscription.is_active = True
        subscription.updated_at = datetime.utcnow()
    else:
        subscription = PushSubscription(
            user_id=user_id,
            endpoint=endpoint,
            p256dh=p256dh,
            auth=auth,
            user_agent=user_agent,
            is_active=True,
        )
        db.add(subscription)
    db.commit()
    db.refresh(subscription)
    return subscription


def get_active_push_subscriptions(db, user_id):
    return (
        db.query(PushSubscription)
        .filter(PushSubscription.user_id == user_id, PushSubscription.is_active.is_(True))
        .all()
    )


def mark_push_subscription_used(db, subscription):
    subscription.last_used_at = datetime.utcnow()
    db.commit()


def deactivate_push_subscription(db, subscription):
    subscription.is_active = False
    subscription.updated_at = datetime.utcnow()
    db.commit()


def delete_push_subscription_by_endpoint(db, user_id, endpoint):
    subscription = (
        db.query(PushSubscription)
        .filter(PushSubscription.user_id == user_id, PushSubscription.endpoint == endpoint)
        .first()
    )
    if subscription:
        db.delete(subscription)
        db.commit()
    return subscription
