from sqlalchemy.orm import Session
from app.models.models import Booking, BookingStatus
from app.schemas.schemas import BookingCreate
from uuid import uuid4
from datetime import datetime
from fastapi import HTTPException

def create_booking(db: Session, payload: BookingCreate):
    new_booking = Booking(
        id=uuid4(),
        user_id=None,  # Set from auth context in real app
        vehicle_id=payload.vehicle_id,
        package_id=payload.package_id,
        cleaner_id=None,
        address=payload.address,
        latitude=payload.latitude,
        longitude=payload.longitude,
        scheduled_at=payload.scheduled_at,
        status=BookingStatus.pending,
        payment_status=None,
        payment_method=payload.payment_method,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return new_booking

def list_bookings(db: Session):
    return db.query(Booking).all()

def get_booking(db: Session, booking_id: str):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

def update_booking_status(db: Session, booking_id: str, status: BookingStatus):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    booking.status = status
    booking.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(booking)
    return booking
