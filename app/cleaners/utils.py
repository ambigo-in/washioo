from sqlalchemy.orm import Session
from app.models.models import Booking, BookingStatus, CleanerLocation, User
from app.schemas.schemas import CleanerLocationUpdate
from uuid import uuid4
from datetime import datetime
from fastapi import HTTPException

def get_cleaner_jobs(db: Session, cleaner_id: str):
    """Get all jobs assigned to a cleaner"""
    jobs = db.query(Booking).filter(
        Booking.cleaner_id == cleaner_id,
        Booking.status.in_([BookingStatus.assigned, BookingStatus.en_route, BookingStatus.in_progress])
    ).all()
    return jobs

def update_job_status(db: Session, booking_id: str, status: BookingStatus):
    """Update the status of a job"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    booking.status = status
    booking.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(booking)
    return {"success": True, "booking_id": str(booking.id), "status": status}

def update_cleaner_location(db: Session, cleaner_id: str, payload: CleanerLocationUpdate):
    """Update cleaner's GPS location"""
    location = db.query(CleanerLocation).filter(CleanerLocation.cleaner_id == cleaner_id).first()
    
    if location:
        location.latitude = payload.latitude
        location.longitude = payload.longitude
        location.updated_at = datetime.utcnow()
    else:
        location = CleanerLocation(
            id=uuid4(),
            cleaner_id=cleaner_id,
            latitude=payload.latitude,
            longitude=payload.longitude,
            updated_at=datetime.utcnow()
        )
        db.add(location)
    
    db.commit()
    db.refresh(location)
    return {"success": True, "message": "Location updated"}

def get_cleaner_location(db: Session, cleaner_id: str):
    """Get cleaner's current location"""
    location = db.query(CleanerLocation).filter(CleanerLocation.cleaner_id == cleaner_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location
