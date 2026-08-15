import asyncio
import logging
from datetime import datetime, timedelta

from core.config import settings
from core.database import SessionLocal
from repositories.booking_repository import (
    cancel_stale_unassigned_booking,
    get_stale_unassigned_bookings,
)
from services.notification_service import notify_customer_booking_auto_cancelled
from services.realtime_service import emit_role_event, emit_user_event

logger = logging.getLogger(__name__)


def auto_cancel_stale_unassigned_bookings(db):
    cutoff = datetime.utcnow() - timedelta(
        hours=settings.BOOKING_AUTO_CANCEL_UNASSIGNED_HOURS
    )
    stale_bookings = get_stale_unassigned_bookings(
        db,
        cutoff,
        limit=settings.BOOKING_AUTO_CANCEL_BATCH_SIZE,
    )
    cancelled_count = 0

    for stale_booking in stale_bookings:
        booking = cancel_stale_unassigned_booking(db, stale_booking.id, cutoff)
        if not booking:
            continue

        cancelled_count += 1
        try:
            notify_customer_booking_auto_cancelled(db, booking)
            emit_user_event(
                booking.customer_id,
                "booking_auto_cancelled",
                {
                    "booking_id": str(booking.id),
                    "booking_status": booking.booking_status,
                },
            )
        except Exception as exc:
            db.rollback()
            logger.warning(
                "Failed to notify customer for auto-cancelled booking %s: %s",
                booking.id,
                exc,
            )

        emit_role_event(
            "admin",
            "booking_auto_cancelled",
            {
                "booking_id": str(booking.id),
                "customer_id": str(booking.customer_id),
                "booking_status": booking.booking_status,
            },
        )

    if cancelled_count:
        logger.info("Auto-cancelled %s stale unassigned bookings", cancelled_count)
    return cancelled_count


async def run_booking_auto_cancel_loop(stop_event: asyncio.Event):
    while not stop_event.is_set():
        db = SessionLocal()
        try:
            auto_cancel_stale_unassigned_bookings(db)
        except Exception as exc:
            db.rollback()
            logger.exception("Booking auto-cancel sweep failed: %s", exc)
        finally:
            db.close()

        try:
            await asyncio.wait_for(
                stop_event.wait(),
                timeout=settings.BOOKING_AUTO_CANCEL_SWEEP_SECONDS,
            )
        except asyncio.TimeoutError:
            pass
