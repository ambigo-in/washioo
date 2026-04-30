from models.booking import Booking
from sqlalchemy.orm import joinedload

def create_booking(db, booking_data):
    """Create a new booking"""
    booking = Booking(**booking_data)
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking

def get_booking_by_id(db, booking_id):
    """Get booking by ID with relationships"""
    return (
        db.query(Booking)
        .options(
            joinedload(Booking.customer),
            joinedload(Booking.service_category),
            joinedload(Booking.address)
        )
        .filter(Booking.id == booking_id)
        .first()
    )

def get_booking_by_reference(db, booking_reference):
    """Get booking by reference"""
    return db.query(Booking).filter(Booking.booking_reference == booking_reference).first()

def get_customer_bookings(db, customer_id):
    """Get all bookings for a customer"""
    return (
        db.query(Booking)
        .options(
            joinedload(Booking.service_category),
            joinedload(Booking.address)
        )
        .filter(Booking.customer_id == customer_id)
        .order_by(Booking.created_at.desc())
        .all()
    )

def get_all_bookings(db):
    """Get all bookings (admin view)"""
    return (
        db.query(Booking)
        .options(
            joinedload(Booking.customer),
            joinedload(Booking.service_category),
            joinedload(Booking.address)
        )
        .order_by(Booking.created_at.desc())
        .all()
    )

def get_bookings_by_status(db, status):
    """Get bookings by status (admin view)"""
    return (
        db.query(Booking)
        .options(
            joinedload(Booking.customer),
            joinedload(Booking.service_category)
        )
        .filter(Booking.booking_status == status)
        .order_by(Booking.created_at.desc())
        .all()
    )

def update_booking_status(db, booking_id, status):
    """Update booking status"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if booking:
        booking.booking_status = status
        db.commit()
        db.refresh(booking)
    return booking

def update_booking(db, booking_id, booking_data):
    """Update booking"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if booking:
        for key, value in booking_data.items():
            setattr(booking, key, value)
        db.commit()
        db.refresh(booking)
    return booking
