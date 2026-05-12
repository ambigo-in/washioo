from datetime import datetime, timedelta

from sqlalchemy import and_, or_

from models.audit_log import AuditLog
from models.booking_assignment_attempt import BookingAssignmentAttempt
from models.notification import Notification
from models.otp import OTPCode
from models.push_subscription import PushSubscription
from models.refresh_token import RefreshToken


DEFAULT_CLEANUP_RETENTION = {
    "otp_codes_hours": 24,
    "refresh_tokens_days": 7,
    "read_notifications_days": 30,
    "unread_notifications_days": 90,
    "assignment_attempts_days": 60,
    "push_subscriptions_days": 30,
    "unused_push_subscriptions_days": 180,
    "audit_logs_days": 90,
}


def _cutoff(**kwargs):
    return datetime.utcnow() - timedelta(**kwargs)


def _delete_query(query):
    deleted_count = query.delete(synchronize_session=False)
    return int(deleted_count or 0)


def _cleanup_item(key, label, count):
    return {
        "key": key,
        "label": label,
        "eligible_records": int(count or 0),
    }


def get_cleanup_preview(db, retention=None):
    retention = {**DEFAULT_CLEANUP_RETENTION, **(retention or {})}
    return [
        _cleanup_item(
            "otp_codes",
            "Expired OTP codes",
            db.query(OTPCode)
            .filter(OTPCode.expires_at < _cutoff(hours=retention["otp_codes_hours"]))
            .count(),
        ),
        _cleanup_item(
            "refresh_tokens",
            "Expired or old revoked refresh tokens",
            db.query(RefreshToken)
            .filter(
                or_(
                    RefreshToken.expires_at
                    < _cutoff(days=retention["refresh_tokens_days"]),
                    and_(
                        RefreshToken.revoked_at.isnot(None),
                        RefreshToken.revoked_at
                        < _cutoff(days=retention["refresh_tokens_days"]),
                    ),
                )
            )
            .count(),
        ),
        _cleanup_item(
            "notifications",
            "Old notifications",
            db.query(Notification)
            .filter(
                or_(
                    and_(
                        Notification.is_read.is_(True),
                        Notification.created_at
                        < _cutoff(days=retention["read_notifications_days"]),
                    ),
                    and_(
                        Notification.is_read.is_(False),
                        Notification.created_at
                        < _cutoff(days=retention["unread_notifications_days"]),
                    ),
                )
            )
            .count(),
        ),
        _cleanup_item(
            "assignment_attempts",
            "Old rejected, expired, or skipped assignment attempts",
            db.query(BookingAssignmentAttempt)
            .filter(
                BookingAssignmentAttempt.status.in_(
                    ["rejected", "expired", "skipped"]
                ),
                BookingAssignmentAttempt.offered_at
                < _cutoff(days=retention["assignment_attempts_days"]),
            )
            .count(),
        ),
        _cleanup_item(
            "push_subscriptions",
            "Inactive or long-unused push subscriptions",
            db.query(PushSubscription)
            .filter(
                or_(
                    and_(
                        PushSubscription.is_active.is_(False),
                        PushSubscription.updated_at
                        < _cutoff(days=retention["push_subscriptions_days"]),
                    ),
                    and_(
                        PushSubscription.last_used_at.isnot(None),
                        PushSubscription.last_used_at
                        < _cutoff(days=retention["unused_push_subscriptions_days"]),
                    ),
                )
            )
            .count(),
        ),
        _cleanup_item(
            "audit_logs",
            "Old audit logs",
            db.query(AuditLog)
            .filter(
                AuditLog.created_at < _cutoff(days=retention["audit_logs_days"])
            )
            .count(),
        ),
    ]


def cleanup_otp_codes(db, retention_hours=None):
    cutoff = _cutoff(
        hours=retention_hours or DEFAULT_CLEANUP_RETENTION["otp_codes_hours"]
    )
    return _delete_query(db.query(OTPCode).filter(OTPCode.expires_at < cutoff))


def cleanup_refresh_tokens(db, retention_days=None):
    cutoff = _cutoff(
        days=retention_days or DEFAULT_CLEANUP_RETENTION["refresh_tokens_days"]
    )
    return _delete_query(
        db.query(RefreshToken).filter(
            or_(
                RefreshToken.expires_at < cutoff,
                and_(
                    RefreshToken.revoked_at.isnot(None),
                    RefreshToken.revoked_at < cutoff,
                ),
            )
        )
    )


def cleanup_notifications(db, read_days=None, unread_days=None):
    read_cutoff = _cutoff(
        days=read_days or DEFAULT_CLEANUP_RETENTION["read_notifications_days"]
    )
    unread_cutoff = _cutoff(
        days=unread_days or DEFAULT_CLEANUP_RETENTION["unread_notifications_days"]
    )
    return _delete_query(
        db.query(Notification).filter(
            or_(
                and_(
                    Notification.is_read.is_(True),
                    Notification.created_at < read_cutoff,
                ),
                and_(
                    Notification.is_read.is_(False),
                    Notification.created_at < unread_cutoff,
                ),
            )
        )
    )


def cleanup_assignment_attempts(db, retention_days=None):
    cutoff = _cutoff(
        days=retention_days
        or DEFAULT_CLEANUP_RETENTION["assignment_attempts_days"]
    )
    return _delete_query(
        db.query(BookingAssignmentAttempt).filter(
            BookingAssignmentAttempt.status.in_(["rejected", "expired", "skipped"]),
            BookingAssignmentAttempt.offered_at < cutoff,
        )
    )


def cleanup_push_subscriptions(db, inactive_days=None, unused_days=None):
    inactive_cutoff = _cutoff(
        days=inactive_days
        or DEFAULT_CLEANUP_RETENTION["push_subscriptions_days"]
    )
    unused_cutoff = _cutoff(
        days=unused_days
        or DEFAULT_CLEANUP_RETENTION["unused_push_subscriptions_days"]
    )
    return _delete_query(
        db.query(PushSubscription).filter(
            or_(
                and_(
                    PushSubscription.is_active.is_(False),
                    PushSubscription.updated_at < inactive_cutoff,
                ),
                and_(
                    PushSubscription.last_used_at.isnot(None),
                    PushSubscription.last_used_at < unused_cutoff,
                ),
            )
        )
    )


def cleanup_audit_logs(db, retention_days=None):
    cutoff = _cutoff(
        days=retention_days or DEFAULT_CLEANUP_RETENTION["audit_logs_days"]
    )
    return _delete_query(db.query(AuditLog).filter(AuditLog.created_at < cutoff))


def run_all_cleanups(db):
    results = {
        "otp_codes": cleanup_otp_codes(db),
        "refresh_tokens": cleanup_refresh_tokens(db),
        "notifications": cleanup_notifications(db),
        "assignment_attempts": cleanup_assignment_attempts(db),
        "push_subscriptions": cleanup_push_subscriptions(db),
        "audit_logs": cleanup_audit_logs(db),
    }
    return results
