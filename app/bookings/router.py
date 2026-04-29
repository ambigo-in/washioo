from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.schemas.schemas import BookingCreate, BookingOut
from app.database.session import SessionLocal
from app.models.models import Booking, User, Vehicle, Package, BookingStatus
from app.bookings import utils

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=BookingOut)
def create_booking(payload: BookingCreate, db: Session = Depends(get_db)):
    return utils.create_booking(db, payload)

@router.get("/", response_model=List[BookingOut])
def list_bookings(db: Session = Depends(get_db)):
    return utils.list_bookings(db)

@router.get("/{booking_id}", response_model=BookingOut)
def get_booking(booking_id: str, db: Session = Depends(get_db)):
    return utils.get_booking(db, booking_id)

@router.patch("/{booking_id}/status", response_model=BookingOut)
def update_booking_status(booking_id: str, status: BookingStatus, db: Session = Depends(get_db)):
    return utils.update_booking_status(db, booking_id, status)
