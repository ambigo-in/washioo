from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from core.role_dependencies import require_roles
from repositories.address_repository import get_address_by_id, update_address
from schemas.booking_schema import UpdateAddressRequest
from services.booking_service import format_address

router = APIRouter(prefix="/customer", tags=["Customer APIs"])


@router.patch("/addresses/{address_id}")
def update_customer_address(
    address_id: str,
    payload: UpdateAddressRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["customer"])),
):
    """Update current customer's address with required verified coordinates."""
    address = get_address_by_id(db, address_id)
    if not address or address.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Address not found")

    update_data = payload.model_dump(exclude_unset=True)
    next_latitude = update_data.get("latitude", address.latitude)
    next_longitude = update_data.get("longitude", address.longitude)
    if next_latitude is None or next_longitude is None:
        raise HTTPException(status_code=400, detail="Latitude and longitude are required")

    update_data["location_verified"] = True
    updated = update_address(db, address_id, update_data)
    return {
        "message": "Address updated successfully",
        "address": format_address(updated),
    }
