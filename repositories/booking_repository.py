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
            joinedload(Booking.address),
            joinedload(Booking.assignment),
            joinedload(Booking.payment)
        )
        .filter(Booking.id == booking_id)
        .first()
    )

def get_booking_by_reference(db, booking_reference):
    """Get booking by reference"""
    return db.query(Booking).filter(Booking.booking_reference == booking_reference).first()

def get_customer_bookings(db, customer_id, limit=50, offset=0):
    """Get all bookings for a customer"""
    return (
        db.query(Booking)
        .options(
            joinedload(Booking.service_category),
            joinedload(Booking.address),
            joinedload(Booking.assignment),
            joinedload(Booking.payment)
        )
        .filter(Booking.customer_id == customer_id)
        .order_by(Booking.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

def get_all_bookings(db, limit=50, offset=0):
    """Get all bookings (admin view)"""
    return (
        db.query(Booking)
        .options(
            joinedload(Booking.customer),
            joinedload(Booking.service_category),
            joinedload(Booking.address),
            joinedload(Booking.assignment),
            joinedload(Booking.payment)
        )
        .order_by(Booking.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

def get_bookings_by_status(db, status, limit=50, offset=0):
    """Get bookings by status (admin view)"""
    return (
        db.query(Booking)
        .options(
            joinedload(Booking.customer),
            joinedload(Booking.service_category),
            joinedload(Booking.address),
            joinedload(Booking.assignment),
            joinedload(Booking.payment)
        )
        .filter(Booking.booking_status == status)
        .order_by(Booking.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

def get_customer_booking_by_id(db, customer_id, booking_id):
    """Get one booking that belongs to a customer"""
    return (
        db.query(Booking)
        .options(
            joinedload(Booking.service_category),
            joinedload(Booking.address),
            joinedload(Booking.assignment),
            joinedload(Booking.payment)
        )
        .filter(Booking.id == booking_id, Booking.customer_id == customer_id)
        .first()
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

