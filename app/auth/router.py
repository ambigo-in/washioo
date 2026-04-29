from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.schemas import SendOTPRequest, VerifyOTPRequest, RegisterRequest, LoginRequest, TokenResponse, UserOut
from app.database.session import SessionLocal
from app.models import models
from app.services import twilio_service, jwt_service
from app.auth import utils

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/send-otp")
def send_otp(payload: SendOTPRequest):
    return twilio_service.send_otp(payload.phone_number)

@router.post("/verify-otp")
def verify_otp(payload: VerifyOTPRequest):
    return twilio_service.verify_otp(payload.phone_number, payload.otp_code)

@router.post("/register", response_model=UserOut)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    return utils.register_user(db, payload)

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    return utils.login_user(db, payload)
