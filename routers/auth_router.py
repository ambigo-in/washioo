import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
from schemas.auth_schema import (
    CleanerSignupRequest,
    CreateAdminRequest,
    LogoutRequest,
    RefreshTokenRequest,
    RoleSignupRequest,
    SendOTPRequest,
    SigninRequest,
)
from schemas.user_schema import UpdateUserRequest
from core.config import settings
from core.database import get_db
from core.rate_limiter import limiter
from repositories.user_repository import get_user_by_phone
from repositories.role_repository import user_has_role
from repositories.cleaner_repository import get_cleaner_profile_by_user_id
from services.auth_service import (
    create_admin_user,
    signup_user_for_role,
    signin_user_for_role,
)
from services.token_service import refresh_user_token, logout_user
from core.dependencies import get_current_user
from services.user_service import get_user_profile
from services.user_service import update_user_details_service
from services.booking_service import (
    get_customer_bookings_service,
    list_cleaner_assignments_service,
    format_customer_booking,
    format_cleaner_assignment,
    format_cleaner_profile,
)
from services.otp_service import create_and_send_otp
from core.role_dependencies import require_roles


AUTH_TAG = "Auth APIs"
ADMIN_TAG = "Admin APIs"
CLEANER_TAG = "Cleaner APIs"
CUSTOMER_TAG = "Customer APIs"
PROFILE_TAG = "Profile APIs"


logger = logging.getLogger(__name__)
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


def _raise_auth_error(exc: Exception, status_code: int = 400):
    logger.warning("Auth request failed: %s", exc)
    detail = str(exc) if settings.DEBUG else "Request could not be processed"
    raise HTTPException(status_code=status_code, detail=detail)


async def _send_role_otp(request: Request, db: Session, phone_number: str, role_name: str):
    user = get_user_by_phone(db, phone_number)
    user_roles = []
    if user:
        user_roles = [
            role
            for role in ("customer", "cleaner", "admin")
            if user_has_role(db, user.id, role)
        ]

    sent = await create_and_send_otp(
        db,
        phone_number,
        created_ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    if not sent:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to send OTP at the moment"
        )
    return {
        "message": f"{role_name.title()} OTP sent successfully",
        "user_exist": role_name in user_roles,
        "account_type": role_name if role_name in user_roles else (user_roles[0] if user_roles else role_name),
        "roles": user_roles,
    }


@router.post("/send-otp", tags=[AUTH_TAG])
@limiter.limit(settings.SEND_OTP_RATE_LIMIT)
def send_otp_api(request: Request):
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="Use role-specific OTP endpoints"
    )

@router.post("/customer/send-otp", tags=[AUTH_TAG])
@limiter.limit(settings.SEND_OTP_RATE_LIMIT)
async def send_customer_otp_api(request: Request, payload: SendOTPRequest, db: Session = Depends(get_db)):
    return await _send_role_otp(request, db, payload.phone_number, "customer")


@router.post("/customer/signup", tags=[AUTH_TAG])
@limiter.limit(settings.AUTH_RATE_LIMIT)
def customer_signup(request: Request, payload: RoleSignupRequest, db: Session = Depends(get_db)):
    try:
        access, refresh = signup_user_for_role(db, payload, "customer")
        user = get_user_by_phone(db, payload.phone_number)
        return _token_response("Customer signup successful", access, refresh, "customer", user)
    except Exception as e:
        _raise_auth_error(e)


@router.post("/customer/signin", tags=[AUTH_TAG])
@limiter.limit(settings.AUTH_RATE_LIMIT)
def customer_signin(request: Request, payload: SigninRequest, db: Session = Depends(get_db)):
    try:
        access, refresh = signin_user_for_role(db, payload, "customer")
        user = get_user_by_phone(db, payload.phone_number)
        return _token_response("Customer login successful", access, refresh, "customer", user)
    except Exception as e:
        _raise_auth_error(e)


@router.post("/cleaner/send-otp", tags=[AUTH_TAG])
@limiter.limit(settings.SEND_OTP_RATE_LIMIT)
async def send_cleaner_otp_api(request: Request, payload: SendOTPRequest, db: Session = Depends(get_db)):
    return await _send_role_otp(request, db, payload.phone_number, "cleaner")


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
        _raise_auth_error(e)


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
        _raise_auth_error(e)


@router.post("/admin/send-otp", tags=[AUTH_TAG])
@limiter.limit(settings.SEND_OTP_RATE_LIMIT)
async def send_admin_otp_api(request: Request, payload: SendOTPRequest, db: Session = Depends(get_db)):
    user = get_user_by_phone(db, payload.phone_number)
    if not user or not user_has_role(db, user.id, "admin"):
        return {
            "message": "If an admin account exists for this phone, an OTP has been sent",
            "user_exist": False,
            "account_type": "admin",
            "roles": [],
        }
    sent = await create_and_send_otp(
        db,
        payload.phone_number,
        created_ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    if not sent:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to send OTP at the moment"
        )
    return {
        "message": "Admin OTP sent successfully",
        "user_exist": True,
        "account_type": "admin",
        "roles": ["admin"],
    }


@router.post("/admin/signin", tags=[AUTH_TAG])
@limiter.limit(settings.AUTH_RATE_LIMIT)
def admin_signin(request: Request, payload: SigninRequest, db: Session = Depends(get_db)):
    try:
        access, refresh = signin_user_for_role(db, payload, "admin")
        user = get_user_by_phone(db, payload.phone_number)
        return _token_response("Admin login successful", access, refresh, "admin", user)
    except Exception as e:
        _raise_auth_error(e)


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
        _raise_auth_error(e)


@router.patch("/admin/{admin_id}", tags=[ADMIN_TAG])
def update_admin_account(
    admin_id: str,
    payload: UpdateUserRequest,
    db: Session = Depends(get_db),
    current_admin=Depends(require_roles(["admin"]))
):
    try:
        if not user_has_role(db, admin_id, "admin"):
            raise Exception("Admin account not found")
        admin = update_user_details_service(db, admin_id, payload)
        return {
            "message": "Admin account updated successfully",
            "admin": admin
        }
    except Exception as e:
        _raise_auth_error(e)


@router.post("/signup", tags=[AUTH_TAG])
@limiter.limit(settings.AUTH_RATE_LIMIT)
def signup(request: Request):
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="Use role-specific signup endpoints"
    )

@router.post("/signin", tags=[AUTH_TAG])
@limiter.limit(settings.AUTH_RATE_LIMIT)
def signin(request: Request):
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="Use role-specific signin endpoints"
    )
    
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
        _raise_auth_error(e, status_code=401)


@router.post("/logout", tags=[AUTH_TAG])
def logout_api(payload: LogoutRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        logout_user(db, payload.refresh_token)
        return {
            "message": "Logged out successfully"
        }
    except Exception as e:
        _raise_auth_error(e)


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
    current_cleaner=Depends(require_roles(["cleaner"])),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    assignments = list_cleaner_assignments_service(db, current_cleaner.id, limit=limit, offset=offset)
    assignment_list = [format_cleaner_assignment(assignment) for assignment in assignments]
    return {
        "message": "Cleaner jobs fetched successfully",
        "assignments": assignment_list,
        "total": len(assignment_list)
    }
@router.get("/customer/bookings", tags=[CUSTOMER_TAG])
def customer_bookings(
    db: Session = Depends(get_db),
    current_customer=Depends(require_roles(["customer"])),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    bookings = get_customer_bookings_service(db, current_customer.id, limit, offset)
    bookings_list = [format_customer_booking(booking) for booking in bookings]
    return {
        "message": "Customer bookings fetched successfully",
        "bookings": bookings_list,
        "total": len(bookings_list)
    }
