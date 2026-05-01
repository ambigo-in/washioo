from sqlalchemy.orm import joinedload
from models.booking_assignment import BookingAssignment
from models.booking import Booking
from models.cleaner_profile import CleanerProfile


def create_assignment(db, assignment_data):
    assignment = BookingAssignment(**assignment_data)
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


def get_assignment_by_id(db, assignment_id):
    return (
        db.query(BookingAssignment)
        .options(
            joinedload(BookingAssignment.booking).joinedload(Booking.service_category),
            joinedload(BookingAssignment.booking).joinedload(Booking.customer),
            joinedload(BookingAssignment.booking).joinedload(Booking.address),
            joinedload(BookingAssignment.cleaner).joinedload(CleanerProfile.user),
        )
        .filter(BookingAssignment.id == assignment_id)
        .first()
    )


def get_assignment_by_booking_id(db, booking_id):
    return (
        db.query(BookingAssignment)
        .options(
            joinedload(BookingAssignment.booking).joinedload(Booking.service_category),
            joinedload(BookingAssignment.booking).joinedload(Booking.customer),
            joinedload(BookingAssignment.booking).joinedload(Booking.address),
            joinedload(BookingAssignment.cleaner).joinedload(CleanerProfile.user),
        )
        .filter(BookingAssignment.booking_id == booking_id)
        .first()
    )


def get_cleaner_assignments(db, cleaner_id, status=None):
    query = (
        db.query(BookingAssignment)
        .options(
            joinedload(BookingAssignment.booking).joinedload(Booking.service_category),
            joinedload(BookingAssignment.booking).joinedload(Booking.customer),
            joinedload(BookingAssignment.booking).joinedload(Booking.address),
            joinedload(BookingAssignment.cleaner).joinedload(CleanerProfile.user),
        )
        .filter(BookingAssignment.cleaner_id == cleaner_id)
    )

    if status:
        query = query.filter(BookingAssignment.assignment_status == status)

    return query.order_by(BookingAssignment.assigned_at.desc()).all()


def get_all_assignments(db, status=None):
    query = db.query(BookingAssignment).options(
        joinedload(BookingAssignment.booking).joinedload(Booking.service_category),
        joinedload(BookingAssignment.booking).joinedload(Booking.customer),
        joinedload(BookingAssignment.booking).joinedload(Booking.address),
        joinedload(BookingAssignment.cleaner).joinedload(CleanerProfile.user),
    )

    if status:
        query = query.filter(BookingAssignment.assignment_status == status)

    return query.order_by(BookingAssignment.assigned_at.desc()).all()


def update_assignment(db, assignment_id, assignment_data):
    assignment = db.query(BookingAssignment).filter(BookingAssignment.id == assignment_id).first()
    if assignment:
        for key, value in assignment_data.items():
            setattr(assignment, key, value)
        db.commit()
        db.refresh(assignment)
    return assignment
