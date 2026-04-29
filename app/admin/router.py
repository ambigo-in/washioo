from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.schemas.schemas import BookingOut, UserOut, UserCreate
from app.database.session import SessionLocal
from app.models.models import Booking, User, UserRole
from app.admin import utils

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/bookings", response_model=List[BookingOut])
def get_all_bookings(db: Session = Depends(get_db)):
    """Get all bookings"""
    return utils.get_all_bookings(db)

@router.get("/cleaners", response_model=List[UserOut])
def get_all_cleaners(db: Session = Depends(get_db)):
    """Get all cleaners"""
    return utils.get_all_cleaners(db)

@router.post("/cleaners", response_model=UserOut)
def add_cleaner(payload: UserCreate, db: Session = Depends(get_db)):
    """Add a new cleaner"""
    return utils.add_cleaner(db, payload)

@router.post("/bookings/{booking_id}/assign")
def assign_cleaner_to_booking(booking_id: str, cleaner_id: str, db: Session = Depends(get_db)):
    """Assign a cleaner to a booking"""
    return utils.assign_cleaner(db, booking_id, cleaner_id)

@router.get("/bookings/{booking_id}", response_model=BookingOut)
def get_booking_details(booking_id: str, db: Session = Depends(get_db)):
    """Get details of a specific booking"""
    return utils.get_booking_details(db, booking_id)
