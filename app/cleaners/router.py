from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.schemas.schemas import BookingOut, CleanerLocationUpdate, CleanerLocationOut
from app.database.session import SessionLocal
from app.models.models import Booking, BookingStatus, User, UserRole, CleanerLocation
from app.cleaners import utils

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/jobs", response_model=List[BookingOut])
def get_assigned_jobs(cleaner_id: str, db: Session = Depends(get_db)):
    """Get all jobs assigned to a cleaner"""
    return utils.get_cleaner_jobs(db, cleaner_id)

@router.patch("/jobs/{booking_id}/status")
def update_job_status(booking_id: str, status: BookingStatus, db: Session = Depends(get_db)):
    """Update status of a job"""
    return utils.update_job_status(db, booking_id, status)

@router.patch("/location")
def update_cleaner_location(cleaner_id: str, payload: CleanerLocationUpdate, db: Session = Depends(get_db)):
    """Update cleaner's GPS location"""
    return utils.update_cleaner_location(db, cleaner_id, payload)

@router.get("/location/{cleaner_id}", response_model=CleanerLocationOut)
def get_cleaner_location(cleaner_id: str, db: Session = Depends(get_db)):
    """Get cleaner's current location"""
    return utils.get_cleaner_location(db, cleaner_id)
