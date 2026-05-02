from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from schemas.auth_schema import *
from core.config import settings
from core.database import get_db
from core.rate_limiter import limiter
from repositories.user_repository import get_user_by_phone
from repositories.role_repository import user_has_role
from repositories.cleaner_repository import get_cleaner_profile_by_user_id
from services.auth_service import (
    create_admin_user,
    signup_user,
    signin_user,
    signup_user_for_role,
    signin_user_for_role,
)
from services.token_service import refresh_user_token, logout_user
from core.dependencies import get_current_user
from services.user_service import get_user_profile
from services.booking_service import (
    get_customer_bookings_service,
    list_cleaner_assignments_service,
    format_customer_booking,
    format_assignment,
    format_cleaner_profile,
)
from utils.twilio_helper import send_otp  
from core.role_dependencies import require_roles


AUTH_TAG = "Auth APIs"
ADMIN_TAG = "Admin APIs"
CLEANER_TAG = "Cleaner APIs"
CUSTOMER_TAG = "Customer APIs"
PROFILE_TAG = "Profile APIs"


router = APIRouter(prefix="/auth")


def _token_response(message: str, access: str, refresh: str, account_type: str | None = None, user=None, extra=None):
    response = {
        "message": message,
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer",
    }
    if account_type:
        response["account_type"] = account_type
    if user:
        response["user"] = get_user_profile(user)
    if extra:
        response.update(extra)
    return response


def _send_role_otp(db: Session, phone_number: str, role_name: str):
    user = get_user_by_phone(db, phone_number)
    send_otp(phone_number)
    return {
        "message": f"{role_name.title()} OTP sent successfully",
        "user_exist": bool(user),
        "has_role": bool(user and user_has_role(db, user.id, role_name))
    }


@router.post("/send-otp", tags=[AUTH_TAG])
@limiter.limit(settings.SEND_OTP_RATE_LIMIT)
def send_otp_api(request: Request, payload: SendOTPRequest, db: Session = Depends(get_db)):
    user = get_user_by_phone(db, payload.phone_number)
    send_otp(payload.phone_number)
    return {
        "message": "OTP sent successfully",
        "user_exist": bool(user)
    }

@router.post("/customer/send-otp", tags=[AUTH_TAG])
@limiter.limit(settings.SEND_OTP_RATE_LIMIT)
def send_customer_otp_api(request: Request, payload: SendOTPRequest, db: Session = Depends(get_db)):
    return _send_role_otp(db, payload.phone_number, "customer")


@router.post("/customer/signup", tags=[AUTH_TAG])
@limiter.limit(settings.AUTH_RATE_LIMIT)
def customer_signup(request: Request, payload: RoleSignupRequest, db: Session = Depends(get_db)):
    try:
        access, refresh = signup_user_for_role(db, payload, "customer")
        user = get_user_by_phone(db, payload.phone_number)
        return _token_response("Customer signup successful", access, refresh, "customer", user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/customer/signin", tags=[AUTH_TAG])
@limiter.limit(settings.AUTH_RATE_LIMIT)
def customer_signin(request: Request, payload: SigninRequest, db: Session = Depends(get_db)):
    try:
        access, refresh = signin_user_for_role(db, payload, "customer")
        user = get_user_by_phone(db, payload.phone_number)
        return _token_response("Customer login successful", access, refresh, "customer", user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/cleaner/send-otp", tags=[AUTH_TAG])
@limiter.limit(settings.SEND_OTP_RATE_LIMIT)
def send_cleaner_otp_api(request: Request, payload: SendOTPRequest, db: Session = Depends(get_db)):
    return _send_role_otp(db, payload.phone_number, "cleaner")


@router.post("/cleaner/signup", tags=[AUTH_TAG])
@limiter.limit(settings.AUTH_RATE_LIMIT)
def cleaner_signup(request: Request, payload: CleanerSignupRequest, db: Session = Depends(get_db)):
    try:
        access, refresh = signup_user_for_role(db, payload, "cleaner")
        user = get_user_by_phone(db, payload.phone_number)
        cleaner = get_cleaner_profile_by_user_id(db, user.id)
        return _token_response(
            "Cleaner signup successful",
            access,
            refresh,
            "cleaner",
            user,
            {"cleaner": format_cleaner_profile(cleaner)}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/cleaner/signin", tags=[AUTH_TAG])
@limiter.limit(settings.AUTH_RATE_LIMIT)
def cleaner_signin(request: Request, payload: SigninRequest, db: Session = Depends(get_db)):
    try:
        access, refresh = signin_user_for_role(db, payload, "cleaner")
        user = get_user_by_phone(db, payload.phone_number)
        cleaner = get_cleaner_profile_by_user_id(db, user.id)
        return _token_response(
            "Cleaner login successful",
            access,
            refresh,
            "cleaner",
            user,
            {"cleaner": format_cleaner_profile(cleaner)}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/admin/send-otp", tags=[AUTH_TAG])
@limiter.limit(settings.SEND_OTP_RATE_LIMIT)
def send_admin_otp_api(request: Request, payload: SendOTPRequest, db: Session = Depends(get_db)):
    user = get_user_by_phone(db, payload.phone_number)
    if not user or not user_has_role(db, user.id, "admin"):
        raise HTTPException(status_code=404, detail="Admin account not found")
    send_otp(payload.phone_number)
    return {
        "message": "Admin OTP sent successfully",
        "user_exist": True,
        "has_role": True
    }


@router.post("/admin/signin", tags=[AUTH_TAG])
@limiter.limit(settings.AUTH_RATE_LIMIT)
def admin_signin(request: Request, payload: SigninRequest, db: Session = Depends(get_db)):
    try:
        access, refresh = signin_user_for_role(db, payload, "admin")
        user = get_user_by_phone(db, payload.phone_number)
        return _token_response("Admin login successful", access, refresh, "admin", user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/admin/create", tags=[ADMIN_TAG])
def create_admin_account(
    payload: CreateAdminRequest,
    db: Session = Depends(get_db),
    current_admin=Depends(require_roles(["admin"]))
):
    try:
        admin = create_admin_user(db, payload)
        return {
            "message": "Admin account created successfully",
            "admin": get_user_profile(admin)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/signup", tags=[AUTH_TAG])
@limiter.limit(settings.AUTH_RATE_LIMIT)
def signup(request: Request, payload: SignupRequest, db: Session = Depends(get_db)):
    try:
        # Check if user already exists
        existing_user = get_user_by_phone(db, payload.phone_number)
        is_new_user = not existing_user
        
        access, refresh = signup_user(db, payload)
        
        message = "User created successfully" if is_new_user else f"Role '{payload.role}' added successfully to existing account"
        
        return {
            "message": message,
            "access_token": access,
            "refresh_token": refresh,
            "token_type": "bearer",
            "is_new_user": is_new_user
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/signin", tags=[AUTH_TAG])
@limiter.limit(settings.AUTH_RATE_LIMIT)
def signin(request: Request, payload: SigninRequest, db: Session = Depends(get_db)):
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
    
@router.post("/refresh-token", tags=[AUTH_TAG])
@limiter.limit(settings.REFRESH_RATE_LIMIT)
def refresh_token_api(request: Request, payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    try:
        access, refresh = refresh_user_token(db, payload.refresh_token)
        return {
            "access_token": access,
            "refresh_token": refresh,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/logout", tags=[AUTH_TAG])
def logout_api(payload: LogoutRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        logout_user(db, payload.refresh_token)
        return {
            "message": "Logged out successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me", tags=[PROFILE_TAG])
def get_user_details(current_user=Depends(require_roles(["customer", "cleaner", "admin"]))):
    return {
        "message": "User details fetched successfully",
        "user": get_user_profile(current_user)
    }

@router.get("/admin/dashboard", tags=[ADMIN_TAG])
def admin_dashboard(current_admin=Depends(require_roles(["admin"]))):
    return {
        "message": "Welcome Admin",
        "admin_id": str(current_admin.id),
        "roles": [ur.role.role_name for ur in current_admin.user_roles]
    }

@router.get("/cleaner/jobs", tags=[CLEANER_TAG])
def cleaner_jobs(
    db: Session = Depends(get_db),
    current_cleaner=Depends(require_roles(["cleaner"]))
):
    assignments = list_cleaner_assignments_service(db, current_cleaner.id)
    assignment_list = [format_assignment(assignment) for assignment in assignments]
    return {
        "message": "Cleaner jobs fetched successfully",
        "assignments": assignment_list,
        "total": len(assignment_list)
    }
@router.get("/customer/bookings", tags=[CUSTOMER_TAG])
def customer_bookings(
    db: Session = Depends(get_db),
    current_customer=Depends(require_roles(["customer"]))
):
    bookings = get_customer_bookings_service(db, current_customer.id)
    bookings_list = [format_customer_booking(booking) for booking in bookings]
    return {
        "message": "Customer bookings fetched successfully",
        "bookings": bookings_list,
        "total": len(bookings_list)
    }
