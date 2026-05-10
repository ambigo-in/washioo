from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from schemas.booking_schema import (
    AdminUpdateBookingRequest,
    AssignBookingRequest,
    CancelBookingRequest,
    CleanerAssignmentActionRequest,
    CompleteAssignmentRequest,
    CreateAddressRequest,
    CreateBookingRequest,
    CreateCleanerProfileRequest,
    CreateServiceRequest,
    UpdateAddressRequest,
    UpdateBookingRequest,
    UpdateCleanerAvailabilityRequest,
    UpdateCleanerLocationRequest,
    UpdateCleanerProfileRequest,
    UpdateServiceRequest,
    VerifyCleanerIdentityRequest,
)
from core.database import get_db
from core.role_dependencies import require_roles
from repositories.service_repository import get_all_services, get_service_by_id, create_service, update_service, delete_service
from repositories.address_repository import create_address, get_user_addresses, get_address_by_id, update_address, delete_address
from services.booking_service import (
    create_new_booking, get_customer_bookings_service, 
    get_all_bookings_service, format_admin_booking, format_customer_booking,
    count_customer_bookings_service, count_all_bookings_service,
    get_bookings_by_status_service, count_bookings_by_status_service,
    get_customer_booking_service, update_customer_booking_service,
    cancel_customer_booking_service, get_admin_booking_service,
    update_admin_booking_service, create_cleaner_profile_service,
    get_or_create_cleaner_profile_service,
    list_cleaner_profiles_service, get_cleaner_profile_service,
    update_cleaner_profile_service, delete_cleaner_profile_service,
    auto_assign_booking_service,
    update_current_cleaner_availability_service, assign_booking_to_cleaner_service, format_address,
    update_current_cleaner_location_service,
    list_cleaner_assignments_service, list_all_assignments_service,
    get_cleaner_assignment_service, accept_assignment_service,
    reject_assignment_service, start_assignment_service,
    complete_assignment_service, format_cleaner_profile, format_assignment,
    format_assignment_summary,
)


PUBLIC_TAG = "Public APIs"
CUSTOMER_TAG = "Customer APIs"
CLEANER_TAG = "Cleaner APIs"
ADMIN_TAG = "Admin APIs"
ADDRESS_TAG = "Address APIs"


router = APIRouter(prefix="/services")

# ============================================================
# SERVICE ENDPOINTS
# ============================================================

def format_service_category(service):
    return {
        "id": str(service.id),
        "service_name": service.service_name,
        "description": service.description,
        "base_price": float(service.base_price),
        "estimated_duration_minutes": service.estimated_duration_minutes,
        "allow_extra_payment": bool(getattr(service, "allow_extra_payment", False)),
        "max_extra_amount": (
            float(service.max_extra_amount)
            if getattr(service, "max_extra_amount", None) is not None
            else None
        ),
        "extra_payment_instructions": getattr(
            service,
            "extra_payment_instructions",
            None,
        ),
        "is_active": service.is_active,
    }

@router.get("/", tags=[PUBLIC_TAG])
def get_services(
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Get all available services"""
    try:
        services = get_all_services(db, limit, offset)
        service_list = [format_service_category(service) for service in services]
        return {
            "message": "Services fetched successfully",
            "services": service_list,
            "total": len(service_list)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail="Request could not be processed")


@router.get("/service-categories/{service_id}", tags=[PUBLIC_TAG])
def get_service_category(service_id: str, db: Session = Depends(get_db)):
    """Get one service category"""
    service = get_service_by_id(db, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    return {
        "message": "Service fetched successfully",
        "service": format_service_category(service)
    }


@router.post("/admin/service-categories", tags=[ADMIN_TAG], status_code=status.HTTP_201_CREATED)
def create_service_category_admin(
    payload: CreateServiceRequest,
    db: Session = Depends(get_db),
    current_admin=Depends(require_roles(["admin"]))
):
    """Admin create service category"""
    try:
        service = create_service(db, payload.model_dump(exclude_unset=True))
        return {
            "message": "Service created successfully",
            "service": format_service_category(service)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail="Request could not be processed")


@router.patch("/admin/service-categories/{service_id}", tags=[ADMIN_TAG])
def update_service_category_admin(
    service_id: str,
    payload: UpdateServiceRequest,
    db: Session = Depends(get_db),
    current_admin=Depends(require_roles(["admin"]))
):
    """Admin update service category"""
    service = update_service(db, service_id, payload.model_dump(exclude_unset=True))
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    return {
        "message": "Service updated successfully",
        "service": format_service_category(service)
    }


@router.delete("/admin/service-categories/{service_id}", tags=[ADMIN_TAG])
def delete_service_category_admin(
    service_id: str,
    db: Session = Depends(get_db),
    current_admin=Depends(require_roles(["admin"]))
):
    """Admin soft delete service category"""
    service = delete_service(db, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    return {
        "message": "Service deactivated successfully",
        "service_id": str(service.id)
    }


# ============================================================
# ADDRESS ENDPOINTS
# ============================================================

@router.post("/address", tags=[ADDRESS_TAG, CUSTOMER_TAG], status_code=status.HTTP_201_CREATED)
def create_user_address(
    payload: CreateAddressRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["customer"]))
):
    """Create a new address for customer"""
    try:
        address_data = payload.model_dump()
        address_data["user_id"] = current_user.id
        address_data["location_verified"] = True

        address = create_address(db, address_data)

        return {
            "message": "Address created successfully",
            "address": format_address(address)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail="Request could not be processed")


@router.get("/addresses", tags=[ADDRESS_TAG, CUSTOMER_TAG])
def get_user_addresses_api(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["customer"]))
):
    """Get all addresses for current user"""
    try:
        addresses = get_user_addresses(db, current_user.id)
        address_list = [format_address(addr) for addr in addresses]

        return {
            "message": "Addresses fetched successfully",
            "addresses": address_list,
            "total": len(address_list)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail="Request could not be processed")


@router.patch("/address/{address_id}", tags=[ADDRESS_TAG, CUSTOMER_TAG])
def update_user_address(
    address_id: str,
    payload: UpdateAddressRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["customer"]))
):
    """Update current user's address"""
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
        "address": format_address(updated)
    }


@router.delete("/address/{address_id}", tags=[ADDRESS_TAG, CUSTOMER_TAG])
def delete_user_address(
    address_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["customer"]))
):
    """Delete current user's address"""
    address = get_address_by_id(db, address_id)
    if not address or address.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Address not found")

    deleted_address, deletion_type = delete_address(db, address_id)
    if not deleted_address:
        raise HTTPException(status_code=404, detail="Address not found")
    return {
        "message": "Address removed successfully",
        "address_id": address_id,
        "deletion_type": deletion_type,
    }


# ============================================================
# BOOKING ENDPOINTS - CUSTOMER
# ============================================================

@router.post("/book", tags=[CUSTOMER_TAG], status_code=status.HTTP_201_CREATED)
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
                "assignment": format_assignment_summary(booking.assignment) if booking.assignment else None,
                "estimated_price": float(booking.estimated_price),
                "created_at": booking.created_at.isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail="Request could not be processed")


@router.get("/my-bookings", tags=[CUSTOMER_TAG])
def get_my_bookings(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["customer"])),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Get customer's own bookings"""
    try:
        bookings = get_customer_bookings_service(db, current_user.id, limit, offset)
        
        bookings_list = [format_customer_booking(booking) for booking in bookings]
        
        return {
            "message": "Bookings fetched successfully",
            "bookings": bookings_list,
            "total": count_customer_bookings_service(db, current_user.id)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail="Request could not be processed")


@router.get("/my-bookings/{booking_id}", tags=[CUSTOMER_TAG])
def get_my_booking_details(
    booking_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["customer"]))
):
    """Get customer's booking details"""
    try:
        booking = get_customer_booking_service(db, current_user.id, booking_id)
        return {
            "message": "Booking fetched successfully",
            "booking": format_customer_booking(booking)
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail="Request could not be processed")


@router.patch("/my-bookings/{booking_id}", tags=[CUSTOMER_TAG])
def update_my_booking(
    booking_id: str,
    payload: UpdateBookingRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["customer"]))
):
    """Update customer booking before assignment"""
    try:
        booking = update_customer_booking_service(db, current_user.id, booking_id, payload)
        return {
            "message": "Booking updated successfully",
            "booking": format_customer_booking(booking)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail="Request could not be processed")


@router.post("/my-bookings/{booking_id}/cancel", tags=[CUSTOMER_TAG])
def cancel_my_booking(
    booking_id: str,
    payload: CancelBookingRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["customer"]))
):
    """Cancel customer booking"""
    try:
        booking = cancel_customer_booking_service(db, current_user.id, booking_id)
        return {
            "message": "Booking cancelled successfully",
            "booking": format_customer_booking(booking)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail="Request could not be processed")


# ============================================================
# BOOKING ENDPOINTS - ADMIN
# ============================================================

@router.get("/admin/all-bookings", tags=[ADMIN_TAG])
def get_all_bookings_admin(
    db: Session = Depends(get_db),
    current_admin=Depends(require_roles(["admin"])),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Admin view all bookings"""
    try:
        bookings = get_all_bookings_service(db, limit, offset)
        
        bookings_list = [format_admin_booking(booking) for booking in bookings]
        
        return {
            "message": "All bookings fetched successfully",
            "bookings": bookings_list,
            "total": count_all_bookings_service(db)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail="Request could not be processed")


@router.get("/admin/bookings/{booking_id}", tags=[ADMIN_TAG])
def get_booking_admin(
    booking_id: str,
    db: Session = Depends(get_db),
    current_admin=Depends(require_roles(["admin"]))
):
    """Admin view one booking"""
    try:
        booking = get_admin_booking_service(db, booking_id)
        return {
            "message": "Booking fetched successfully",
            "booking": format_admin_booking(booking)
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail="Request could not be processed")


@router.patch("/admin/bookings/{booking_id}", tags=[ADMIN_TAG])
def update_booking_admin(
    booking_id: str,
    payload: AdminUpdateBookingRequest,
    db: Session = Depends(get_db),
    current_admin=Depends(require_roles(["admin"]))
):
    """Admin update booking"""
    try:
        booking = update_admin_booking_service(db, booking_id, payload)
        return {
            "message": "Booking updated successfully",
            "booking": format_admin_booking(booking)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail="Request could not be processed")


@router.get("/admin/customers/{customer_id}/bookings", tags=[ADMIN_TAG])
def get_customer_bookings_admin(
    customer_id: str,
    db: Session = Depends(get_db),
    current_admin=Depends(require_roles(["admin"])),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Admin view bookings for a particular customer"""
    try:
        bookings = get_customer_bookings_service(db, customer_id, limit, offset)
        bookings_list = [format_customer_booking(booking) for booking in bookings]
        return {
            "message": "Customer bookings fetched successfully",
            "customer_id": customer_id,
            "bookings": bookings_list,
            "total": count_customer_bookings_service(db, customer_id)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail="Request could not be processed")


@router.post("/admin/bookings/{booking_id}/assign", tags=[ADMIN_TAG])
def assign_booking_admin(
    booking_id: str,
    payload: AssignBookingRequest,
    db: Session = Depends(get_db),
    current_admin=Depends(require_roles(["admin"]))
):
    """Admin assign or reassign a booking to a cleaner"""
    try:
        assignment = assign_booking_to_cleaner_service(db, booking_id, current_admin.id, payload)
        return {
            "message": "Booking assigned successfully",
            "assignment": format_assignment(assignment)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail="Request could not be processed")


@router.post("/admin/bookings/{booking_id}/auto-assign", tags=[ADMIN_TAG])
def auto_assign_booking_admin(
    booking_id: str,
    db: Session = Depends(get_db),
    current_admin=Depends(require_roles(["admin"]))
):
    """Admin trigger auto assignment for a pending booking"""
    try:
        result = auto_assign_booking_service(db, booking_id, current_admin.id)
        return {
            "message": "Auto assignment completed" if result["assigned"] else "Auto assignment could not find a cleaner",
            "assigned": result["assigned"],
            "reason": result["reason"],
            "score": result.get("score"),
            "distance_km": result.get("distance_km"),
            "candidates": result.get("candidates", 0),
            "assignment": format_assignment(result["assignment"]) if result.get("assignment") else None,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail="Request could not be processed")


@router.get("/admin/bookings-by-status/{status}", tags=[ADMIN_TAG])
def get_bookings_by_status_admin(
    status: str,
    db: Session = Depends(get_db),
    current_admin=Depends(require_roles(["admin"])),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Admin view bookings filtered by status"""
    valid_statuses = ["pending", "assigned", "accepted", "in_progress", "completed", "cancelled"]
    
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid status. Valid statuses: {', '.join(valid_statuses)}"
        )
    
    try:
        bookings = get_bookings_by_status_service(db, status, limit, offset)
        
        bookings_list = [format_admin_booking(booking) for booking in bookings]
        
        return {
            "message": f"Bookings with status '{status}' fetched successfully",
            "status": status,
            "bookings": bookings_list,
            "total": count_bookings_by_status_service(db, status)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail="Request could not be processed")


# ============================================================
# CLEANER PROFILE ENDPOINTS
# ============================================================

@router.post("/admin/cleaners", tags=[ADMIN_TAG], status_code=status.HTTP_201_CREATED)
def create_cleaner_profile_admin(
    payload: CreateCleanerProfileRequest,
    db: Session = Depends(get_db),
    current_admin=Depends(require_roles(["admin"]))
):
    """Admin create cleaner profile for a user with cleaner role"""
    try:
        cleaner = create_cleaner_profile_service(db, payload)
        return {
            "message": "Cleaner profile created successfully",
            "cleaner": format_cleaner_profile(cleaner, include_sensitive_identity=True)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail="Request could not be processed")


@router.get("/admin/cleaners", tags=[ADMIN_TAG])
def list_cleaners_admin(
    approval_status: str | None = None,
    availability_status: str | None = None,
    db: Session = Depends(get_db),
    current_admin=Depends(require_roles(["admin"])),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Admin list cleaner profiles"""
    try:
        cleaners = list_cleaner_profiles_service(db, approval_status, availability_status, limit, offset)
        cleaner_list = [
            format_cleaner_profile(cleaner, include_sensitive_identity=True)
            for cleaner in cleaners
        ]
        return {
            "message": "Cleaners fetched successfully",
            "cleaners": cleaner_list,
            "total": len(cleaner_list)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail="Request could not be processed")


@router.get("/admin/cleaners/{cleaner_id}", tags=[ADMIN_TAG])
def get_cleaner_admin(
    cleaner_id: str,
    db: Session = Depends(get_db),
    current_admin=Depends(require_roles(["admin"]))
):
    """Admin get cleaner profile"""
    try:
        cleaner = get_cleaner_profile_service(db, cleaner_id)
        return {
            "message": "Cleaner fetched successfully",
            "cleaner": format_cleaner_profile(cleaner, include_sensitive_identity=True)
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail="Request could not be processed")


@router.patch("/admin/cleaners/{cleaner_id}", tags=[ADMIN_TAG])
def update_cleaner_admin(
    cleaner_id: str,
    payload: UpdateCleanerProfileRequest,
    db: Session = Depends(get_db),
    current_admin=Depends(require_roles(["admin"]))
):
    """Admin update cleaner profile"""
    try:
        cleaner = update_cleaner_profile_service(db, cleaner_id, payload)
        return {
            "message": "Cleaner updated successfully",
            "cleaner": format_cleaner_profile(cleaner, include_sensitive_identity=True)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail="Request could not be processed")


@router.delete("/admin/cleaners/{cleaner_id}", tags=[ADMIN_TAG])
def delete_cleaner_admin(
    cleaner_id: str,
    db: Session = Depends(get_db),
    current_admin=Depends(require_roles(["admin"]))
):
    """Admin delete cleaner profile"""
    try:
        delete_cleaner_profile_service(db, cleaner_id)
        return {
            "message": "Cleaner profile deleted successfully",
            "cleaner_id": cleaner_id
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail="Request could not be processed")


@router.get("/cleaner/profile", tags=[CLEANER_TAG])
def get_current_cleaner_profile(
    db: Session = Depends(get_db),
    current_cleaner=Depends(require_roles(["cleaner"]))
):
    """Cleaner view own profile"""
    try:
        cleaner = get_or_create_cleaner_profile_service(db, current_cleaner.id)
        return {
            "message": "Cleaner profile fetched successfully",
            "cleaner": format_cleaner_profile(cleaner)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail="Request could not be processed")


@router.post("/cleaner/profile/verify-identity", tags=[CLEANER_TAG])
def verify_current_cleaner_identity(
    payload: VerifyCleanerIdentityRequest,
    db: Session = Depends(get_db),
    current_cleaner=Depends(require_roles(["cleaner"]))
):
    """Cleaner verifies phone last 4 digits to view own full identity details"""
    try:
        phone_last_four = (current_cleaner.phone or "")[-4:]
        if payload.phone_last_four != phone_last_four:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Identity verification failed")
        cleaner = get_or_create_cleaner_profile_service(db, current_cleaner.id)
        return {
            "message": "Cleaner identity verified successfully",
            "cleaner": format_cleaner_profile(cleaner, include_sensitive_identity=True)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail="Request could not be processed")


@router.patch("/cleaner/availability", tags=[CLEANER_TAG])
def update_current_cleaner_availability(
    payload: UpdateCleanerAvailabilityRequest,
    db: Session = Depends(get_db),
    current_cleaner=Depends(require_roles(["cleaner"]))
):
    """Cleaner update own availability"""
    try:
        cleaner = update_current_cleaner_availability_service(db, current_cleaner.id, payload)
        return {
            "message": "Availability updated successfully",
            "cleaner": format_cleaner_profile(cleaner)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail="Request could not be processed")


@router.patch("/cleaner/location", tags=[CLEANER_TAG])
def update_current_cleaner_location(
    payload: UpdateCleanerLocationRequest,
    db: Session = Depends(get_db),
    current_cleaner=Depends(require_roles(["cleaner"]))
):
    """Cleaner updates live location used by auto assignment"""
    try:
        cleaner = update_current_cleaner_location_service(db, current_cleaner.id, payload)
        return {
            "message": "Cleaner location updated successfully",
            "cleaner": format_cleaner_profile(cleaner)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail="Request could not be processed")


# ============================================================
# ASSIGNMENT ENDPOINTS
# ============================================================

@router.get("/admin/assignments", tags=[ADMIN_TAG])
def list_assignments_admin(
    status: str | None = None,
    db: Session = Depends(get_db),
    current_admin=Depends(require_roles(["admin"])),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Admin list all assignments"""
    try:
        assignments = list_all_assignments_service(db, status, limit, offset)
        assignment_list = [format_assignment(assignment) for assignment in assignments]
        return {
            "message": "Assignments fetched successfully",
            "assignments": assignment_list,
            "total": len(assignment_list)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail="Request could not be processed")


@router.get("/cleaner/assignments", tags=[CLEANER_TAG])
def list_cleaner_assignments(
    status: str | None = None,
    db: Session = Depends(get_db),
    current_cleaner=Depends(require_roles(["cleaner"])),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Cleaner fetch assigned bookings/services"""
    try:
        assignments = list_cleaner_assignments_service(db, current_cleaner.id, status, limit, offset)
        assignment_list = [format_assignment(assignment) for assignment in assignments]
        return {
            "message": "Cleaner assignments fetched successfully",
            "assignments": assignment_list,
            "total": len(assignment_list)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail="Request could not be processed")


@router.get("/cleaner/assignments/{assignment_id}", tags=[CLEANER_TAG])
def get_cleaner_assignment(
    assignment_id: str,
    db: Session = Depends(get_db),
    current_cleaner=Depends(require_roles(["cleaner"]))
):
    """Cleaner fetch one assigned booking/service"""
    try:
        assignment = get_cleaner_assignment_service(db, current_cleaner.id, assignment_id)
        return {
            "message": "Assignment fetched successfully",
            "assignment": format_assignment(assignment)
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail="Request could not be processed")


@router.post("/cleaner/assignments/{assignment_id}/accept", tags=[CLEANER_TAG])
def accept_assignment(
    assignment_id: str,
    payload: CleanerAssignmentActionRequest,
    db: Session = Depends(get_db),
    current_cleaner=Depends(require_roles(["cleaner"]))
):
    """Cleaner accept assigned service"""
    try:
        assignment = accept_assignment_service(db, current_cleaner.id, assignment_id, payload)
        return {
            "message": "Assignment accepted successfully",
            "assignment": format_assignment(assignment)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail="Request could not be processed")


@router.post("/cleaner/assignments/{assignment_id}/reject", tags=[CLEANER_TAG])
def reject_assignment(
    assignment_id: str,
    payload: CleanerAssignmentActionRequest,
    db: Session = Depends(get_db),
    current_cleaner=Depends(require_roles(["cleaner"]))
):
    """Cleaner reject assigned service"""
    try:
        assignment = reject_assignment_service(db, current_cleaner.id, assignment_id, payload)
        return {
            "message": "Assignment rejected successfully",
            "assignment": format_assignment(assignment)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail="Request could not be processed")


@router.post("/cleaner/assignments/{assignment_id}/start", tags=[CLEANER_TAG])
def start_assignment(
    assignment_id: str,
    payload: CleanerAssignmentActionRequest,
    db: Session = Depends(get_db),
    current_cleaner=Depends(require_roles(["cleaner"]))
):
    """Cleaner start accepted service"""
    try:
        assignment = start_assignment_service(db, current_cleaner.id, assignment_id, payload)
        return {
            "message": "Assignment started successfully",
            "assignment": format_assignment(assignment)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail="Request could not be processed")


@router.post("/cleaner/assignments/{assignment_id}/complete", tags=[CLEANER_TAG])
def complete_assignment(
    assignment_id: str,
    payload: CompleteAssignmentRequest,
    db: Session = Depends(get_db),
    current_cleaner=Depends(require_roles(["cleaner"]))
):
    """Cleaner complete in-progress service and optionally submit payment collection details"""
    try:
        assignment = complete_assignment_service(db, current_cleaner.id, assignment_id, payload)
        return {
            "message": "Assignment completed successfully",
            "assignment": format_assignment(assignment)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail="Request could not be processed")
