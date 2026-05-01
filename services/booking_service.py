from datetime import datetime
import uuid
from repositories.booking_repository import (
    create_booking, get_booking_by_id, get_customer_bookings, get_all_bookings,
    get_customer_booking_by_id, update_booking
)
from repositories.service_repository import get_service_by_id
from repositories.address_repository import get_address_by_id, create_address
from repositories.assignment_repository import (
    create_assignment, get_assignment_by_id, get_assignment_by_booking_id,
    get_cleaner_assignments, get_all_assignments, update_assignment
)
from repositories.cleaner_repository import (
    create_cleaner_profile, get_cleaner_profile_by_id, get_cleaner_profile_by_user_id,
    get_all_cleaner_profiles, update_cleaner_profile, delete_cleaner_profile,
    user_has_cleaner_role
)
from repositories.user_repository import get_user_with_roles

BOOKING_STATUSES = ["pending", "assigned", "accepted", "in_progress", "completed", "cancelled"]
ASSIGNMENT_STATUSES = ["assigned", "accepted", "rejected", "completed"]

def generate_booking_reference():
    """Generate unique booking reference"""
    return f"BK-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

def create_new_booking(db, customer_id, payload):
    """Create a new booking"""
    
    # Validate service exists
    service = get_service_by_id(db, payload.service_category_id)
    if not service or not service.is_active:
        raise Exception("Service not found or inactive")
    
    # Handle address
    address_id = payload.address_id
    if payload.address:
        # Create new address
        address_data = payload.address.dict()
        address_data["user_id"] = customer_id
        address = create_address(db, address_data)
        address_id = str(address.id)
    elif not address_id:
        raise Exception("Please provide an address or address_id")
    
    # Verify address exists and belongs to customer
    address = get_address_by_id(db, address_id)
    if not address or address.user_id != customer_id:
        raise Exception("Invalid address")
    
    # Create booking
    booking_data = {
        "booking_reference": generate_booking_reference(),
        "customer_id": customer_id,
        "service_category_id": payload.service_category_id,
        "address_id": address_id,
        "scheduled_date": payload.scheduled_date,
        "scheduled_time": payload.scheduled_time,
        "special_instructions": payload.special_instructions,
        "booking_status": "pending",
        "estimated_price": service.base_price
    }
    
    booking = create_booking(db, booking_data)
    return booking

def get_customer_bookings_service(db, customer_id):
    """Get all bookings for a customer"""
    return get_customer_bookings(db, customer_id)

def get_all_bookings_service(db):
    """Get all bookings (admin view)"""
    return get_all_bookings(db)

def get_customer_booking_service(db, customer_id, booking_id):
    booking = get_customer_booking_by_id(db, customer_id, booking_id)
    if not booking:
        raise Exception("Booking not found")
    return booking

def get_admin_booking_service(db, booking_id):
    booking = get_booking_by_id(db, booking_id)
    if not booking:
        raise Exception("Booking not found")
    return booking

def update_customer_booking_service(db, customer_id, booking_id, payload):
    """Allow customer to edit their booking before it is assigned."""
    booking = get_customer_booking_by_id(db, customer_id, booking_id)
    if not booking:
        raise Exception("Booking not found")
    if booking.booking_status != "pending":
        raise Exception("Only pending bookings can be updated by customer")

    booking_data = payload.model_dump(exclude_unset=True)

    if "service_category_id" in booking_data:
        service = get_service_by_id(db, booking_data["service_category_id"])
        if not service or not service.is_active:
            raise Exception("Service not found or inactive")
        booking_data["estimated_price"] = service.base_price

    if "address_id" in booking_data:
        address = get_address_by_id(db, booking_data["address_id"])
        if not address or address.user_id != customer_id:
            raise Exception("Invalid address")

    return update_booking(db, booking_id, booking_data)

def cancel_customer_booking_service(db, customer_id, booking_id):
    booking = get_customer_booking_by_id(db, customer_id, booking_id)
    if not booking:
        raise Exception("Booking not found")
    if booking.booking_status in ["completed", "cancelled"]:
        raise Exception("Booking cannot be cancelled")
    if booking.booking_status == "in_progress":
        raise Exception("Booking is already in progress")

    return update_booking(db, booking_id, {"booking_status": "cancelled"})

def update_admin_booking_service(db, booking_id, payload):
    booking = get_booking_by_id(db, booking_id)
    if not booking:
        raise Exception("Booking not found")

    booking_data = payload.model_dump(exclude_unset=True)

    if "booking_status" in booking_data and booking_data["booking_status"] not in BOOKING_STATUSES:
        raise Exception("Invalid booking status")

    if "service_category_id" in booking_data:
        service = get_service_by_id(db, booking_data["service_category_id"])
        if not service:
            raise Exception("Service not found")

    if "address_id" in booking_data:
        address = get_address_by_id(db, booking_data["address_id"])
        if not address:
            raise Exception("Address not found")

    return update_booking(db, booking_id, booking_data)

def create_cleaner_profile_service(db, payload):
    user = get_user_with_roles(db, payload.user_id)
    if not user:
        raise Exception("User not found")
    if not user_has_cleaner_role(db, payload.user_id):
        raise Exception("User does not have cleaner role")

    existing_profile = get_cleaner_profile_by_user_id(db, payload.user_id)
    if existing_profile:
        raise Exception("Cleaner profile already exists for this user")

    return create_cleaner_profile(db, payload.model_dump(exclude_unset=True))

def get_or_create_cleaner_profile_service(db, user_id):
    profile = get_cleaner_profile_by_user_id(db, user_id)
    if profile:
        return profile
    if not user_has_cleaner_role(db, user_id):
        raise Exception("User does not have cleaner role")
    return create_cleaner_profile(db, {"user_id": user_id})

def list_cleaner_profiles_service(db, approval_status=None, availability_status=None):
    return get_all_cleaner_profiles(db, approval_status, availability_status)

def get_cleaner_profile_service(db, cleaner_id):
    cleaner = get_cleaner_profile_by_id(db, cleaner_id)
    if not cleaner:
        raise Exception("Cleaner profile not found")
    return cleaner

def update_cleaner_profile_service(db, cleaner_id, payload):
    cleaner = get_cleaner_profile_by_id(db, cleaner_id)
    if not cleaner:
        raise Exception("Cleaner profile not found")

    cleaner_data = payload.model_dump(exclude_unset=True)
    return update_cleaner_profile(db, cleaner_id, cleaner_data)

def delete_cleaner_profile_service(db, cleaner_id):
    cleaner = delete_cleaner_profile(db, cleaner_id)
    if not cleaner:
        raise Exception("Cleaner profile not found")
    return cleaner

def update_current_cleaner_availability_service(db, user_id, payload):
    cleaner = get_or_create_cleaner_profile_service(db, user_id)
    if cleaner.approval_status != "approved" and payload.availability_status != "offline":
        raise Exception("Cleaner must be approved before becoming available or busy")
    return update_cleaner_profile(
        db,
        cleaner.id,
        {"availability_status": payload.availability_status}
    )

def assign_booking_to_cleaner_service(db, booking_id, admin_id, payload):
    booking = get_booking_by_id(db, booking_id)
    if not booking:
        raise Exception("Booking not found")
    if booking.booking_status in ["completed", "cancelled", "in_progress"]:
        raise Exception("Booking cannot be assigned in its current status")

    cleaner = get_cleaner_profile_by_id(db, payload.cleaner_id)
    if not cleaner:
        raise Exception("Cleaner profile not found")
    if cleaner.approval_status != "approved":
        raise Exception("Cleaner is not approved")
    if cleaner.availability_status != "available":
        raise Exception("Cleaner is not available")

    existing_assignment = get_assignment_by_booking_id(db, booking_id)
    assignment_data = {
        "cleaner_id": payload.cleaner_id,
        "assigned_by_admin": admin_id,
        "assigned_at": datetime.utcnow(),
        "accepted_at": None,
        "started_at": None,
        "completed_at": None,
        "assignment_status": "assigned",
        "cleaner_notes": payload.cleaner_notes
    }

    if existing_assignment:
        assignment = update_assignment(db, existing_assignment.id, assignment_data)
    else:
        assignment_data["booking_id"] = booking_id
        assignment = create_assignment(db, assignment_data)

    update_booking(db, booking_id, {"booking_status": "assigned"})
    return get_assignment_by_id(db, assignment.id)

def list_cleaner_assignments_service(db, user_id, status=None):
    cleaner = get_or_create_cleaner_profile_service(db, user_id)
    if status and status not in ASSIGNMENT_STATUSES:
        raise Exception("Invalid assignment status")
    return get_cleaner_assignments(db, cleaner.id, status)

def list_all_assignments_service(db, status=None):
    if status and status not in ASSIGNMENT_STATUSES:
        raise Exception("Invalid assignment status")
    return get_all_assignments(db, status)

def get_cleaner_assignment_service(db, user_id, assignment_id):
    cleaner = get_or_create_cleaner_profile_service(db, user_id)
    assignment = get_assignment_by_id(db, assignment_id)
    if not assignment or assignment.cleaner_id != cleaner.id:
        raise Exception("Assignment not found")
    return assignment

def accept_assignment_service(db, user_id, assignment_id, payload):
    assignment = get_cleaner_assignment_service(db, user_id, assignment_id)
    if assignment.assignment_status != "assigned":
        raise Exception("Only assigned bookings can be accepted")
    if assignment.booking and assignment.booking.booking_status != "assigned":
        raise Exception("Booking is not available for acceptance")

    assignment = update_assignment(db, assignment_id, {
        "assignment_status": "accepted",
        "accepted_at": datetime.utcnow(),
        "cleaner_notes": payload.cleaner_notes
    })
    update_booking(db, assignment.booking_id, {"booking_status": "accepted"})
    update_cleaner_profile(db, assignment.cleaner_id, {"availability_status": "busy"})
    return get_assignment_by_id(db, assignment_id)

def reject_assignment_service(db, user_id, assignment_id, payload):
    assignment = get_cleaner_assignment_service(db, user_id, assignment_id)
    if assignment.assignment_status != "assigned":
        raise Exception("Assignment cannot be rejected")

    assignment = update_assignment(db, assignment_id, {
        "assignment_status": "rejected",
        "cleaner_notes": payload.cleaner_notes
    })
    update_booking(db, assignment.booking_id, {"booking_status": "pending"})
    update_cleaner_profile(db, assignment.cleaner_id, {"availability_status": "available"})
    return get_assignment_by_id(db, assignment_id)

def start_assignment_service(db, user_id, assignment_id, payload):
    assignment = get_cleaner_assignment_service(db, user_id, assignment_id)
    if assignment.assignment_status != "accepted":
        raise Exception("Only accepted assignments can be started")
    if assignment.started_at:
        raise Exception("Assignment has already been started")
    if assignment.booking and assignment.booking.booking_status != "accepted":
        raise Exception("Booking is not ready to start")

    assignment = update_assignment(db, assignment_id, {
        "started_at": datetime.utcnow(),
        "cleaner_notes": payload.cleaner_notes
    })
    update_booking(db, assignment.booking_id, {"booking_status": "in_progress"})
    return get_assignment_by_id(db, assignment_id)

def complete_assignment_service(db, user_id, assignment_id, payload):
    assignment = get_cleaner_assignment_service(db, user_id, assignment_id)
    if not assignment.started_at:
        raise Exception("Assignment must be started before completion")
    if assignment.assignment_status != "accepted":
        raise Exception("Assignment cannot be completed")
    if assignment.booking and assignment.booking.booking_status != "in_progress":
        raise Exception("Booking is not in progress")

    assignment = update_assignment(db, assignment_id, {
        "assignment_status": "completed",
        "completed_at": datetime.utcnow(),
        "cleaner_notes": payload.cleaner_notes
    })

    booking_data = {"booking_status": "completed"}
    if payload.final_price is not None:
        booking_data["final_price"] = payload.final_price
    update_booking(db, assignment.booking_id, booking_data)

    cleaner = get_cleaner_profile_by_id(db, assignment.cleaner_id)
    update_cleaner_profile(db, assignment.cleaner_id, {
        "availability_status": "available",
        "total_jobs_completed": (cleaner.total_jobs_completed or 0) + 1
    })
    return get_assignment_by_id(db, assignment_id)

def format_admin_booking(booking):
    """Format booking for admin response"""
    return {
        "id": str(booking.id),
        "booking_reference": booking.booking_reference,
        "customer_id": str(booking.customer_id),
        "customer_name": booking.customer.full_name if booking.customer else None,
        "customer_phone": booking.customer.phone if booking.customer else None,
        "service_name": booking.service_category.service_name if booking.service_category else None,
        "service_category_id": str(booking.service_category_id),
        "scheduled_date": str(booking.scheduled_date),
        "scheduled_time": str(booking.scheduled_time),
        "booking_status": booking.booking_status,
        "estimated_price": float(booking.estimated_price),
        "final_price": float(booking.final_price) if booking.final_price else None,
        "special_instructions": booking.special_instructions,
        "address": format_address(booking.address),
        "assignment": format_assignment_summary(booking.assignment),
        "created_at": booking.created_at.isoformat()
    }

def format_customer_booking(booking):
    """Format booking for customer response"""
    return {
        "id": str(booking.id),
        "booking_reference": booking.booking_reference,
        "service_name": booking.service_category.service_name if booking.service_category else None,
        "scheduled_date": str(booking.scheduled_date),
        "scheduled_time": str(booking.scheduled_time),
        "booking_status": booking.booking_status,
        "estimated_price": float(booking.estimated_price),
        "final_price": float(booking.final_price) if booking.final_price else None,
        "special_instructions": booking.special_instructions,
        "address": format_address(booking.address),
        "assignment": format_assignment_summary(booking.assignment),
        "created_at": booking.created_at.isoformat()
    }

def format_address(address):
    if not address:
        return None
    return {
        "id": str(address.id),
        "address_label": address.address_label,
        "address_line1": address.address_line1,
        "address_line2": address.address_line2,
        "landmark": address.landmark,
        "city": address.city,
        "state": address.state,
        "pincode": address.pincode,
        "country": address.country,
        "latitude": float(address.latitude) if address.latitude is not None else None,
        "longitude": float(address.longitude) if address.longitude is not None else None,
        "is_default": address.is_default,
    }

def format_cleaner_profile(cleaner):
    if not cleaner:
        return None
    return {
        "id": str(cleaner.id),
        "user_id": str(cleaner.user_id),
        "full_name": cleaner.user.full_name if cleaner.user else None,
        "phone": cleaner.user.phone if cleaner.user else None,
        "email": cleaner.user.email if cleaner.user else None,
        "vehicle_type": cleaner.vehicle_type,
        "government_id_number": cleaner.government_id_number,
        "service_radius_km": float(cleaner.service_radius_km) if cleaner.service_radius_km is not None else None,
        "approval_status": cleaner.approval_status,
        "availability_status": cleaner.availability_status,
        "rating": float(cleaner.rating) if cleaner.rating is not None else 0,
        "total_jobs_completed": cleaner.total_jobs_completed or 0,
        "created_at": cleaner.created_at.isoformat() if cleaner.created_at else None,
    }

def format_assignment_summary(assignment):
    if not assignment:
        return None
    return {
        "id": str(assignment.id),
        "cleaner_id": str(assignment.cleaner_id),
        "assignment_status": assignment.assignment_status,
        "assigned_at": assignment.assigned_at.isoformat() if assignment.assigned_at else None,
        "accepted_at": assignment.accepted_at.isoformat() if assignment.accepted_at else None,
        "started_at": assignment.started_at.isoformat() if assignment.started_at else None,
        "completed_at": assignment.completed_at.isoformat() if assignment.completed_at else None,
        "cleaner_notes": assignment.cleaner_notes,
    }

def format_assignment(assignment):
    if not assignment:
        return None
    booking = assignment.booking
    return {
        **format_assignment_summary(assignment),
        "booking_id": str(assignment.booking_id),
        "assigned_by_admin": str(assignment.assigned_by_admin),
        "cleaner": format_cleaner_profile(assignment.cleaner),
        "booking": format_admin_booking(booking) if booking else None,
    }
