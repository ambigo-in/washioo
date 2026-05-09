from datetime import datetime

from models.booking_assignment_attempt import BookingAssignmentAttempt


def create_assignment_attempt(db, attempt_data):
    attempt = BookingAssignmentAttempt(**attempt_data)
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return attempt


def get_assignment_attempts_by_booking(db, booking_id):
    return (
        db.query(BookingAssignmentAttempt)
        .filter(BookingAssignmentAttempt.booking_id == booking_id)
        .order_by(BookingAssignmentAttempt.offered_at.asc())
        .all()
    )


def get_latest_open_attempt(db, booking_id, cleaner_id):
    return (
        db.query(BookingAssignmentAttempt)
        .filter(
            BookingAssignmentAttempt.booking_id == booking_id,
            BookingAssignmentAttempt.cleaner_id == cleaner_id,
            BookingAssignmentAttempt.status == "offered",
        )
        .order_by(BookingAssignmentAttempt.offered_at.desc())
        .first()
    )


def update_assignment_attempt(db, attempt, attempt_data):
    if not attempt:
        return None
    for key, value in attempt_data.items():
        setattr(attempt, key, value)
    db.commit()
    db.refresh(attempt)
    return attempt


def close_latest_open_attempt(db, booking_id, cleaner_id, status, reason=None):
    attempt = get_latest_open_attempt(db, booking_id, cleaner_id)
    if not attempt:
        return None
    return update_assignment_attempt(
        db,
        attempt,
        {
            "status": status,
            "reason": reason,
            "responded_at": datetime.utcnow(),
        },
    )
