from datetime import datetime, timedelta
from repositories.user_repository import get_user_by_phone, create_user
from repositories.token_repository import save_refresh_token
from core.security import create_access_token, create_refresh_token
from repositories.role_repository import get_role_by_name, assign_role_to_user, user_has_role
from repositories.cleaner_repository import create_cleaner_profile, get_cleaner_profile_by_user_id
from utils.twilio_helper import verify_otp
from core.config import settings

def signup_user(db, payload):
    verification = verify_otp(payload.phone_number, payload.otp_code)

    if verification.status != "approved":
        raise Exception("Invalid OTP")

    # Fetch role
    role = get_role_by_name(db, payload.role)

    if not role:
        raise Exception("Invalid role selected")

    # Check if user already exists by phone
    existing_user = get_user_by_phone(db, payload.phone_number)

    if existing_user:
        if not existing_user.is_active:
            raise Exception("User account is inactive")

        # User exists - check if they already have this role
        if user_has_role(db, existing_user.id, payload.role):
            raise Exception(f"You already have the {payload.role} role")
        
        # User doesn't have this role - assign it
        assign_role_to_user(db, existing_user.id, role.id)
        user = existing_user
    else:
        # User doesn't exist - create new user
        user = create_user(db, {
            "full_name": payload.full_name,
            "phone": payload.phone_number,
            "email": payload.email,
            "is_verified": True
        })
        
        # Assign role
        assign_role_to_user(db, user.id, role.id)

    if payload.role == "cleaner" and not get_cleaner_profile_by_user_id(db, user.id):
        create_cleaner_profile(db, {"user_id": user.id})

    # Generate tokens
    access_token = create_access_token({
        "sub": str(user.id),
        "role": role.role_name
    })

    refresh_token = create_refresh_token({
        "sub": str(user.id)
    })

    save_refresh_token(
        db,
        user.id,
        refresh_token,  # Store raw JWT - JWTs are self-verifying via signature
        datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )

    return access_token, refresh_token

def signin_user(db, payload):
    user = get_user_by_phone(db, payload.phone_number)
    if not user:
        raise Exception("User not found")
    if not user.is_active:
        raise Exception("User account is inactive")

    verification = verify_otp(payload.phone_number, payload.otp_code)
    if verification.status != "approved":
        raise Exception("Invalid OTP")

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    save_refresh_token(
        db,
        user.id,
        refresh_token,  # Store raw JWT - JWTs are self-verifying via signature
        datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )

    return access_token, refresh_token
