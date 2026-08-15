from models.booking import Booking
from models.booking_assignment import BookingAssignment
from models.cleaner_profile import CleanerProfile
from sqlalchemy import or_
from sqlalchemy.orm import joinedload, selectinload

INACTIVE_ASSIGNMENT_STATUSES = ["rejected", "cancelled"]


def _unassigned_booking_filter():
    return or_(
        ~Booking.assignment.has(),
        Booking.assignment.has(
            BookingAssignment.assignment_status.in_(INACTIVE_ASSIGNMENT_STATUSES)
        ),
    )

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
            joinedload(Booking.vehicle),
            joinedload(Booking.assignment).joinedload(BookingAssignment.cleaner).joinedload(CleanerProfile.user),
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
            selectinload(Booking.service_category),
            selectinload(Booking.address),
            selectinload(Booking.vehicle),
            selectinload(Booking.assignment).selectinload(BookingAssignment.cleaner).selectinload(CleanerProfile.user),
            selectinload(Booking.payment)
        )
        .filter(Booking.customer_id == customer_id)
        .order_by(Booking.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

def count_customer_bookings(db, customer_id):
    """Count all bookings for a customer before pagination."""
    return db.query(Booking).filter(Booking.customer_id == customer_id).count()

def get_all_bookings(db, limit=50, offset=0):
    """Get all bookings (admin view)"""
    return (
        db.query(Booking)
        .options(
            selectinload(Booking.customer),
            selectinload(Booking.service_category),
            selectinload(Booking.address),
            selectinload(Booking.vehicle),
            selectinload(Booking.assignment).selectinload(BookingAssignment.cleaner).selectinload(CleanerProfile.user),
            selectinload(Booking.payment)
        )
        .order_by(Booking.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

def count_all_bookings(db):
    """Count all bookings before pagination."""
    return db.query(Booking).count()

def get_bookings_by_status(db, status, limit=50, offset=0):
    """Get bookings by status (admin view)"""
    return (
        db.query(Booking)
        .options(
            selectinload(Booking.customer),
            selectinload(Booking.service_category),
            selectinload(Booking.address),
            selectinload(Booking.vehicle),
            selectinload(Booking.assignment).selectinload(BookingAssignment.cleaner).selectinload(CleanerProfile.user),
            selectinload(Booking.payment)
        )
        .filter(Booking.booking_status == status)
        .order_by(Booking.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

def count_bookings_by_status(db, status):
    """Count bookings by status before pagination."""
    return db.query(Booking).filter(Booking.booking_status == status).count()

def get_stale_unassigned_bookings(db, cutoff, limit=100):
    """Get pending bookings that have not received a cleaner assignment."""
    return (
        db.query(Booking)
        .options(
            selectinload(Booking.customer),
            selectinload(Booking.service_category),
            selectinload(Booking.address),
            selectinload(Booking.assignment),
        )
        .filter(
            Booking.booking_status == "pending",
            Booking.created_at <= cutoff,
            _unassigned_booking_filter(),
        )
        .order_by(Booking.created_at.asc())
        .limit(limit)
        .all()
    )

def cancel_stale_unassigned_booking(db, booking_id, cutoff):
    """Cancel a booking only if it is still pending and unassigned."""
    booking = (
        db.query(Booking)
        .filter(
            Booking.id == booking_id,
            Booking.booking_status == "pending",
            Booking.created_at <= cutoff,
            _unassigned_booking_filter(),
        )
        .first()
    )
    if not booking:
        return None

    booking.booking_status = "cancelled"
    db.commit()
    db.refresh(booking)
    return booking

def get_customer_booking_by_id(db, customer_id, booking_id):
    """Get one booking that belongs to a customer"""
    return (
        db.query(Booking)
        .options(
            joinedload(Booking.service_category),
            joinedload(Booking.address),
            joinedload(Booking.vehicle),
            joinedload(Booking.assignment).joinedload(BookingAssignment.cleaner).joinedload(CleanerProfile.user),
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

