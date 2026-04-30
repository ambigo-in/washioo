from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.booking_schema import CreateBookingRequest, CreateAddressRequest
from core.database import get_db
from core.dependencies import get_current_user
from core.role_dependencies import require_roles
from repositories.service_repository import get_all_services
from repositories.address_repository import create_address, get_user_addresses
from services.booking_service import (
    create_new_booking, get_customer_bookings_service, 
    get_all_bookings_service, format_admin_booking, format_customer_booking
)


router = APIRouter(prefix="/services", tags=["Services & Bookings"])

# ============================================================
# SERVICE ENDPOINTS
# ============================================================

@router.get("/")
def get_services(db: Session = Depends(get_db)):
    """Get all available services"""
    try:
        services = get_all_services(db)
        service_list = [
            {
                "id": str(service.id),
                "service_name": service.service_name,
                "description": service.description,
                "base_price": float(service.base_price),
                "estimated_duration_minutes": service.estimated_duration_minutes,
                "is_active": service.is_active
            }
            for service in services
        ]
        return {
            "message": "Services fetched successfully",
            "services": service_list,
            "total": len(service_list)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================
# ADDRESS ENDPOINTS
# ============================================================

@router.post("/address")
def create_user_address(
    payload: CreateAddressRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Create a new address for customer"""
    try:
        address_data = payload.dict()
        address_data["user_id"] = current_user.id
        
        address = create_address(db, address_data)
        
        return {
            "message": "Address created successfully",
            "address": {
                "id": str(address.id),
                "address_label": address.address_label,
                "address_line1": address.address_line1,
                "address_line2": address.address_line2,
                "landmark": address.landmark,
                "city": address.city,
                "state": address.state,
                "pincode": address.pincode,
                "country": address.country,
                "is_default": address.is_default
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/addresses")
def get_user_addresses_api(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Get all addresses for current user"""
    try:
        addresses = get_user_addresses(db, current_user.id)
        
        address_list = [
            {
                "id": str(addr.id),
                "address_label": addr.address_label,
                "address_line1": addr.address_line1,
                "address_line2": addr.address_line2,
                "landmark": addr.landmark,
                "city": addr.city,
                "state": addr.state,
                "pincode": addr.pincode,
                "country": addr.country,
                "is_default": addr.is_default
            }
            for addr in addresses
        ]
        
        return {
            "message": "Addresses fetched successfully",
            "addresses": address_list,
            "total": len(address_list)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================
# BOOKING ENDPOINTS - CUSTOMER
# ============================================================

@router.post("/book")
def book_service(
    payload: CreateBookingRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["customer"]))
):
    """Customer books a service"""
    try:
        booking = create_new_booking(db, current_user.id, payload)
        
        return {
            "message": "Booking created successfully",
            "booking": {
                "id": str(booking.id),
                "booking_reference": booking.booking_reference,
                "service_id": str(booking.service_category_id),
                "scheduled_date": str(booking.scheduled_date),
                "scheduled_time": str(booking.scheduled_time),
                "booking_status": booking.booking_status,
                "estimated_price": float(booking.estimated_price),
                "created_at": booking.created_at.isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/my-bookings")
def get_my_bookings(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["customer"]))
):
    """Get customer's own bookings"""
    try:
        bookings = get_customer_bookings_service(db, current_user.id)
        
        bookings_list = [format_customer_booking(booking) for booking in bookings]
        
        return {
            "message": "Bookings fetched successfully",
            "bookings": bookings_list,
            "total": len(bookings_list)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================
# BOOKING ENDPOINTS - ADMIN
# ============================================================

@router.get("/admin/all-bookings")
def get_all_bookings_admin(
    db: Session = Depends(get_db),
    current_admin=Depends(require_roles(["admin"]))
):
    """Admin view all bookings"""
    try:
        bookings = get_all_bookings_service(db)
        
        bookings_list = [format_admin_booking(booking) for booking in bookings]
        
        return {
            "message": "All bookings fetched successfully",
            "bookings": bookings_list,
            "total": len(bookings_list)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/admin/bookings-by-status/{status}")
def get_bookings_by_status_admin(
    status: str,
    db: Session = Depends(get_db),
    current_admin=Depends(require_roles(["admin"]))
):
    """Admin view bookings filtered by status"""
    valid_statuses = ["pending", "assigned", "accepted", "in_progress", "completed", "cancelled"]
    
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid status. Valid statuses: {', '.join(valid_statuses)}"
        )
    
    try:
        from repositories.booking_repository import get_bookings_by_status
        bookings = get_bookings_by_status(db, status)
        
        bookings_list = [format_admin_booking(booking) for booking in bookings]
        
        return {
            "message": f"Bookings with status '{status}' fetched successfully",
            "status": status,
            "bookings": bookings_list,
            "total": len(bookings_list)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
