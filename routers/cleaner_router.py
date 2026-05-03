from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from core.role_dependencies import require_roles
from services.booking_service import get_cleaner_booking_service, format_cleaner_booking_detail

router = APIRouter(prefix="/cleaner", tags=["Cleaner APIs"])


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
