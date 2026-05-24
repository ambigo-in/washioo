import logging
import math
from datetime import datetime, timedelta
from decimal import Decimal

from repositories.assignment_repository import (
    create_assignment,
    get_assignment_by_booking_id,
    get_assignment_by_id,
    update_assignment,
)
from repositories.assignment_attempt_repository import (
    close_latest_open_attempt,
    create_assignment_attempt,
    get_assignment_attempts_by_booking,
)
from repositories.booking_repository import get_booking_by_id, update_booking
from repositories.cleaner_repository import (
    count_cleaner_active_assignments,
    get_auto_assignable_cleaners,
)
from services.notification_service import notify_cleaner_booking_assigned
from services.realtime_service import emit_role_event, emit_user_event


logger = logging.getLogger(__name__)

MAX_LOCATION_AGE_MINUTES = 30
DEFAULT_SERVICE_RADIUS_KM = 8
ASSIGNMENT_ACCEPT_MINUTES = 5


def _haversine_km(lat1, lon1, lat2, lon2):
    radius_km = 6371.0
    phi1 = math.radians(float(lat1))
    phi2 = math.radians(float(lat2))
    delta_phi = math.radians(float(lat2) - float(lat1))
    delta_lambda = math.radians(float(lon2) - float(lon1))

    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )
    return radius_km * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _score_cleaner(db, cleaner, booking):
    address = booking.address
    if not address or address.latitude is None or address.longitude is None:
        return None

    if not cleaner.last_location_at:
        return None

    location_age = datetime.utcnow() - cleaner.last_location_at
    if location_age > timedelta(minutes=MAX_LOCATION_AGE_MINUTES):
        return None

    distance_km = _haversine_km(
        cleaner.current_latitude,
        cleaner.current_longitude,
        address.latitude,
        address.longitude,
    )
    service_radius = float(cleaner.service_radius_km or DEFAULT_SERVICE_RADIUS_KM)
    if distance_km > service_radius:
        return None

    active_jobs = count_cleaner_active_assignments(db, cleaner.id)
    rating = float(cleaner.average_rating or cleaner.rating or 0)
    completed_jobs = cleaner.total_jobs_completed or 0

    score = (
        max(0, 100 - distance_km * 10)
        + rating * 10
        - active_jobs * 20
        - min(completed_jobs, 100) * 0.05
    )

    return {
        "cleaner": cleaner,
        "distance_km": round(distance_km, 2),
        "score": round(score, 2),
        "active_jobs": active_jobs,
    }


def auto_assign_booking(db, booking_id, excluded_cleaner_ids=None, assigned_by_admin=None):
    previous_attempts = get_assignment_attempts_by_booking(db, booking_id)
    excluded = {
        str(attempt.cleaner_id)
        for attempt in previous_attempts
        if attempt.status in ["offered", "accepted", "rejected", "expired"]
    }
    excluded.update(str(cleaner_id) for cleaner_id in (excluded_cleaner_ids or []))
    booking = get_booking_by_id(db, booking_id)
    if not booking:
        raise Exception("Booking not found")

    if booking.booking_status not in ["pending", "assigned"]:
        return {
            "assigned": False,
            "reason": "booking_not_assignable",
            "assignment": None,
        }

    existing_assignment = get_assignment_by_booking_id(db, booking_id)
    if (
        existing_assignment
        and existing_assignment.assignment_status == "assigned"
        and existing_assignment.expires_at
        and existing_assignment.expires_at <= datetime.utcnow()
    ):
        close_latest_open_attempt(
            db,
            existing_assignment.booking_id,
            existing_assignment.cleaner_id,
            "expired",
            "Cleaner did not respond before assignment expiry.",
        )
        excluded.add(str(existing_assignment.cleaner_id))
        existing_assignment = update_assignment(
            db,
            existing_assignment.id,
            {
                "assignment_status": "rejected",
                "rejected_reason": "Auto assignment expired",
            },
        )
        update_booking(db, booking_id, {"booking_status": "pending"})

    if existing_assignment and existing_assignment.assignment_status in [
        "accepted",
        "in_progress",
        "completed",
    ]:
        return {
            "assigned": False,
            "reason": "active_assignment_exists",
            "assignment": existing_assignment,
        }

    booking_customer_id = str(booking.customer_id) if booking.customer_id else None
    candidates = []
    for cleaner in get_auto_assignable_cleaners(db):
        if str(cleaner.id) in excluded:
            continue
        if booking_customer_id and str(cleaner.user_id) == booking_customer_id:
            continue
        scored = _score_cleaner(db, cleaner, booking)
        if scored:
            candidates.append(scored)

    candidates.sort(key=lambda item: item["score"], reverse=True)
    if not candidates:
        update_booking(db, booking_id, {"booking_status": "pending"})
        emit_role_event(
            "admin",
            "admin_action_required",
            {
                "booking_id": str(booking_id),
                "reason": "no_available_cleaner",
            },
        )
        return {
            "assigned": False,
            "reason": "no_available_cleaner",
            "assignment": existing_assignment,
        }

    selected = candidates[0]
    now = datetime.utcnow()
    expires_at = now + timedelta(minutes=ASSIGNMENT_ACCEPT_MINUTES)
    assignment_data = {
        "cleaner_id": selected["cleaner"].id,
        "assigned_by_admin": assigned_by_admin,
        "assigned_at": now,
        "accepted_at": None,
        "started_at": None,
        "completed_at": None,
        "assignment_status": "assigned",
        "cleaner_notes": "Auto assigned",
        "expires_at": expires_at,
        "rejected_reason": None,
        "auto_assigned": True,
        "assignment_rank": 1,
        "assignment_score": Decimal(str(selected["score"])),
        "distance_km": Decimal(str(selected["distance_km"])),
    }

    if existing_assignment:
        assignment = update_assignment(db, existing_assignment.id, assignment_data)
    else:
        assignment_data["booking_id"] = booking_id
        assignment = create_assignment(db, assignment_data)

    update_booking(db, booking_id, {"booking_status": "assigned"})
    assignment = get_assignment_by_id(db, assignment.id)
    create_assignment_attempt(
        db,
        {
            "booking_id": booking_id,
            "cleaner_id": selected["cleaner"].id,
            "assignment_id": assignment.id,
            "status": "offered",
            "score": Decimal(str(selected["score"])),
            "distance_km": Decimal(str(selected["distance_km"])),
            "reason": "Auto assignment offer",
            "offered_at": now,
            "expires_at": expires_at,
        },
    )
    try:
        if assignment.cleaner and assignment.cleaner.user_id:
            notify_cleaner_booking_assigned(db, assignment.cleaner.user_id, assignment)
    except Exception as exc:
        db.rollback()
        logger.warning("Failed to notify auto-assigned cleaner for booking %s: %s", booking_id, exc)

    event_data = {
        "booking_id": str(booking_id),
        "assignment_id": str(assignment.id),
        "cleaner_id": str(selected["cleaner"].id),
        "distance_km": selected["distance_km"],
        "score": selected["score"],
    }
    emit_role_event("admin", "booking_auto_assigned", event_data)
    if booking.customer_id:
        emit_user_event(booking.customer_id, "booking_assignment_updated", event_data)

    return {
        "assigned": True,
        "reason": "assigned",
        "assignment": assignment,
        "score": selected["score"],
        "distance_km": selected["distance_km"],
        "candidates": len(candidates),
    }
