from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from core.role_dependencies import require_roles
from repositories.address_repository import get_address_by_id, update_address
from schemas.booking_schema import (
    CreateCustomerVehicleRequest,
    UpdateAddressRequest,
    UpdateCustomerVehicleRequest,
)
from services.booking_service import (
    create_customer_vehicle_service,
    delete_customer_vehicle_service,
    format_address,
    format_customer_vehicle,
    list_customer_vehicles_service,
    update_customer_vehicle_service,
)

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


@router.get("/vehicles")
def list_customer_vehicles(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["customer"])),
):
    vehicles = list_customer_vehicles_service(db, current_user.id)
    return {
        "message": "Vehicles fetched successfully",
        "vehicles": [format_customer_vehicle(vehicle) for vehicle in vehicles],
        "total": len(vehicles),
    }


@router.post("/vehicles", status_code=201)
def create_customer_vehicle(
    payload: CreateCustomerVehicleRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["customer"])),
):
    vehicle = create_customer_vehicle_service(db, current_user.id, payload)
    return {
        "message": "Vehicle created successfully",
        "vehicle": format_customer_vehicle(vehicle),
    }


@router.patch("/vehicles/{vehicle_id}")
def update_customer_vehicle(
    vehicle_id: str,
    payload: UpdateCustomerVehicleRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["customer"])),
):
    try:
        vehicle = update_customer_vehicle_service(db, current_user.id, vehicle_id, payload)
        return {
            "message": "Vehicle updated successfully",
            "vehicle": format_customer_vehicle(vehicle),
        }
    except Exception:
        raise HTTPException(status_code=404, detail="Vehicle not found")


@router.delete("/vehicles/{vehicle_id}")
def delete_customer_vehicle(
    vehicle_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["customer"])),
):
    try:
        delete_customer_vehicle_service(db, current_user.id, vehicle_id)
        return {
            "message": "Vehicle deleted successfully",
            "vehicle_id": vehicle_id,
        }
    except Exception:
        raise HTTPException(status_code=404, detail="Vehicle not found")
