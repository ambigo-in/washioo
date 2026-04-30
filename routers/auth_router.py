from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.auth_schema import *
from core.database import get_db
from repositories.user_repository import get_user_by_phone
from services.auth_service import signup_user, signin_user
from services.token_service import refresh_user_token, logout_user
from core.dependencies import get_current_user
from services.user_service import get_user_profile
from utils.twilio_helper import send_otp    

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/send-otp")
def send_otp_api(payload: SendOTPRequest, db: Session = Depends(get_db)):
    user = get_user_by_phone(db, payload.phone_number)
    send_otp(payload.phone_number)
    return {
        "message": "OTP sent successfully",
        "user_exist": bool(user)
    }

@router.post("/signup")
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    try:
        access, refresh = signup_user(db, payload)
        return {
            "message": "User created successfully",
            "access_token": access,
            "refresh_token": refresh,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/signin")
def signin(payload: SigninRequest, db: Session = Depends(get_db)):
    try:
        access, refresh = signin_user(db, payload)
        return {
            "message": "Login successful",
            "access_token": access,
            "refresh_token": refresh,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/refresh-token")
def refresh_token_api(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    try:
        access, refresh = refresh_user_token(db, payload.refresh_token)
        return {
            "access_token": access,
            "refresh_token": refresh,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/logout")
def logout_api(payload: LogoutRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        logout_user(db, payload.refresh_token)
        return {
            "message": "Logged out successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me")
def get_user_details(current_user=Depends(get_current_user)):
    return {
        "message": "User details fetched successfully",
        "user": get_user_profile(current_user)
    }