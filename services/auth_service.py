from datetime import datetime, timedelta
from repositories.user_repository import get_user_by_email, get_user_by_phone, get_user_with_roles, create_user
from repositories.token_repository import save_refresh_token
from core.security import create_access_token, create_refresh_token
from repositories.role_repository import get_role_by_name, assign_role_to_user, user_has_role
from repositories.cleaner_repository import create_cleaner_profile, get_cleaner_profile_by_user_id
from utils.twilio_helper import verify_otp
from core.config import settings
from core.security import hash_identifier, mask_identifier

def _get_role_or_raise(db, role_name: str):
    role = get_role_by_name(db, role_name)
    if not role:
        raise Exception("Invalid role selected")
    return role


def _create_tokens(db, user, role_name: str | None = None):
    token_data = {"sub": str(user.id)}
    if role_name:
        token_data["role"] = role_name

    access_token = create_access_token(token_data)
    refresh_token, jti = create_refresh_token({"sub": str(user.id)})

    save_refresh_token(
        db,
        user.id,
        jti,
        refresh_token,
        datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )

    return access_token, refresh_token


def _verify_signup_otp(payload):
    verification = verify_otp(payload.phone_number, payload.otp_code)
    if verification.status != "approved":
        raise Exception("Invalid OTP")


def _cleaner_profile_data_from_signup(payload):
    if not getattr(payload, "aadhaar_number", None):
        raise Exception("Aadhaar number is required for cleaner signup")

    data = {
        "aadhaar_number": mask_identifier(payload.aadhaar_number),
        "aadhaar_number_hash": hash_identifier(payload.aadhaar_number),
        "government_id_number": mask_identifier(payload.aadhaar_number),
    }
    if payload.driving_license_number is not None:
        data["driving_license_number"] = mask_identifier(payload.driving_license_number)
        data["driving_license_number_hash"] = hash_identifier(payload.driving_license_number)
    return data


def signup_user_for_role(db, payload, role_name: str, cleaner_profile_data: dict | None = None):
    _verify_signup_otp(payload)
    role = _get_role_or_raise(db, role_name)

    # Check if user already exists by phone
    existing_user = get_user_by_phone(db, payload.phone_number)

    if existing_user:
        if not existing_user.is_active:
            raise Exception("User account is inactive")
        user_with_email = get_user_by_email(db, payload.email)
        if user_with_email and user_with_email.id != existing_user.id:
            raise Exception("Email already in use")

        # User exists - check if they already have this role
        if user_has_role(db, existing_user.id, role_name):
            raise Exception(f"You already have the {role_name} role")
        
        # User doesn't have this role - assign it
        assign_role_to_user(db, existing_user.id, role.id)
        user = existing_user
    else:
        user_with_email = get_user_by_email(db, payload.email)
        if user_with_email:
            raise Exception("Email already in use")

        # User doesn't exist - create new user
        user = create_user(db, {
            "full_name": payload.full_name,
            "phone": payload.phone_number,
            "email": payload.email,
            "is_verified": True
        })
        
        # Assign role
        assign_role_to_user(db, user.id, role.id)

    if role_name == "cleaner" and not get_cleaner_profile_by_user_id(db, user.id):
        if cleaner_profile_data is None:
            cleaner_profile_data = _cleaner_profile_data_from_signup(payload)
        create_cleaner_profile(db, {"user_id": user.id, **cleaner_profile_data})

    return _create_tokens(db, user, role.role_name)


def signin_user_for_role(db, payload, role_name: str):
    user = get_user_by_phone(db, payload.phone_number)
    if not user:
        raise Exception("User not found")
    if not user.is_active:
        raise Exception("User account is inactive")
    if not user_has_role(db, user.id, role_name):
        raise Exception(f"This account is not registered as a {role_name}")

    verification = verify_otp(payload.phone_number, payload.otp_code)
    if verification.status != "approved":
        raise Exception("Invalid OTP")

    return _create_tokens(db, user, role_name)


def create_admin_user(db, payload):
    role = _get_role_or_raise(db, "admin")
    existing_user = get_user_by_phone(db, payload.phone_number)

    if existing_user:
        if not existing_user.is_active:
            raise Exception("User account is inactive")
        user_with_email = get_user_by_email(db, payload.email)
        if user_with_email and user_with_email.id != existing_user.id:
            raise Exception("Email already in use")
        if user_has_role(db, existing_user.id, "admin"):
            raise Exception("This account is already an admin")
        assign_role_to_user(db, existing_user.id, role.id)
        return get_user_with_roles(db, existing_user.id)

    user_with_email = get_user_by_email(db, payload.email)
    if user_with_email:
        raise Exception("Email already in use")

    user = create_user(db, {
        "full_name": payload.full_name,
        "phone": payload.phone_number,
        "email": payload.email,
        "is_verified": True
    })
    assign_role_to_user(db, user.id, role.id)
    return get_user_with_roles(db, user.id)
