from datetime import datetime
import uuid
from repositories.booking_repository import (
    create_booking, get_booking_by_id, get_customer_bookings, get_all_bookings
)
from repositories.service_repository import get_service_by_id
from repositories.address_repository import get_address_by_id, create_address
from repositories.user_repository import get_user_by_phone

def generate_booking_reference():
    """Generate unique booking reference"""
    return f"BK-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

def create_new_booking(db, customer_id, payload):
    """Create a new booking"""
    
    # Validate service exists
    service = get_service_by_id(db, payload.service_category_id)
    if not service:
        raise Exception("Service not found")
    
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
        "created_at": booking.created_at.isoformat()
    }
