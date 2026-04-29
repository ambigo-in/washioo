from sqlalchemy.orm import Session
from app.models.models import Booking, User, UserRole, BookingStatus
from app.schemas.schemas import UserCreate
from app.services import notification_service
from uuid import uuid4
from datetime import datetime
from fastapi import HTTPException

def get_all_bookings(db: Session):
    """Get all bookings"""
    return db.query(Booking).all()

def get_all_cleaners(db: Session):
    """Get all cleaners"""
    return db.query(User).filter(User.role == UserRole.cleaner).all()

def add_cleaner(db: Session, payload: UserCreate):
    """Add a new cleaner"""
    cleaner = db.query(User).filter(User.phone_number == payload.phone_number).first()
    if cleaner:
        raise HTTPException(status_code=400, detail="Cleaner already exists")
    
    new_cleaner = User(
        id=uuid4(),
        phone_number=payload.phone_number,
        full_name=payload.full_name,
        role=UserRole.cleaner,
        is_verified=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(new_cleaner)
    db.commit()
    db.refresh(new_cleaner)
    return new_cleaner

def assign_cleaner(db: Session, booking_id: str, cleaner_id: str):
    """Assign a cleaner to a booking"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    cleaner = db.query(User).filter(User.id == cleaner_id, User.role == UserRole.cleaner).first()
    if not cleaner:
        raise HTTPException(status_code=404, detail="Cleaner not found")
    
    booking.cleaner_id = cleaner_id
    booking.status = BookingStatus.assigned
    booking.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(booking)
    
    # Send SMS notification
    notification_service.send_cleaner_assigned_notification(cleaner.phone_number, booking)
    
    return {"success": True, "message": "Cleaner assigned", "booking_id": str(booking.id), "cleaner_id": str(cleaner_id)}

def get_booking_details(db: Session, booking_id: str):
    """Get details of a specific booking"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking
