from datetime import datetime, timedelta
from repositories.user_repository import get_user_by_email, get_user_by_phone, get_user_with_roles, create_user
from repositories.token_repository import save_refresh_token
from core.security import create_access_token, create_refresh_token
from repositories.role_repository import get_role_by_name, assign_role_to_user, user_has_role
from repositories.cleaner_repository import create_cleaner_profile, get_cleaner_profile_by_user_id
from services.otp_service import verify_otp_code
from core.config import settings
from core.security import hash_identifier

def _get_role_or_raise(db, role_name: str):
    role = get_role_by_name(db, role_name)
    if not role:
        raise Exception("Invalid role selected")
    return role


def _user_role_names(user) -> list[str]:
    return [
        user_role.role.role_name
        for user_role in user.user_roles
        if user_role.role
    ]


def _create_tokens(db, user, active_role: str | None = None):
    user = get_user_with_roles(db, user.id)
    roles = _user_role_names(user)
    if active_role and active_role not in roles:
        raise Exception("Active role is not assigned to this user")
    if not active_role and roles:
        active_role = roles[0]

    token_data = {
        "sub": str(user.id),
        "active_role": active_role,
        "roles": roles,
        # Backward-compatible alias. Frontends should prefer active_role.
        "role": active_role,
    }

    access_token = create_access_token(token_data)
    refresh_token, jti = create_refresh_token(token_data)

    save_refresh_token(
        db,
        user.id,
        jti,
        refresh_token,
        datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )

    return access_token, refresh_token


def _verify_signup_otp(db, payload):
    if not verify_otp_code(db, payload.phone_number, payload.otp_code):
        raise Exception("Invalid OTP")


def _apply_terms_acceptance(user, accepted: bool):
    if not accepted:
        return
    user.terms_accepted = True
    if user.terms_accepted_at is None:
        user.terms_accepted_at = datetime.utcnow()


def _get_user_by_signup_email(db, email):
    if not email:
        return None
    return get_user_by_email(db, email)


def _cleaner_profile_data_from_signup(payload):
    if not getattr(payload, "aadhaar_number", None):
        raise Exception("Aadhaar number is required for cleaner signup")

    data = {
        "aadhaar_number": payload.aadhaar_number,
        "aadhaar_number_hash": hash_identifier(payload.aadhaar_number),
        "government_id_number": payload.aadhaar_number,
    }
    if settings.DRIVING_LICENSE_REQUIRED and not payload.driving_license_number:
        raise Exception("Driving license number is required for cleaner signup")
    if payload.driving_license_number is not None:
        data["driving_license_number"] = payload.driving_license_number
        data["driving_license_number_hash"] = hash_identifier(payload.driving_license_number)
    return data


def signup_user_for_role(db, payload, role_name: str, cleaner_profile_data: dict | None = None):
    _verify_signup_otp(db, payload)
    role = _get_role_or_raise(db, role_name)

    # Check if user already exists by phone
    existing_user = get_user_by_phone(db, payload.phone_number)

    if existing_user:
        if not existing_user.is_active:
            raise Exception("User account is inactive")
        user_with_email = _get_user_by_signup_email(db, payload.email)
        if user_with_email and user_with_email.id != existing_user.id:
            raise Exception("Email already in use")

        # User exists - check if they already have this role
        if user_has_role(db, existing_user.id, role_name):
            raise Exception(f"You already have the {role_name} role")
        
        # User doesn't have this role - assign it
        assign_role_to_user(db, existing_user.id, role.id)
        user = existing_user
    else:
        user_with_email = _get_user_by_signup_email(db, payload.email)
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

    _apply_terms_acceptance(user, getattr(payload, "terms_accepted", False))
    db.commit()

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

    if not verify_otp_code(db, payload.phone_number, payload.otp_code):
        raise Exception("Invalid OTP")

    _apply_terms_acceptance(user, getattr(payload, "terms_accepted", False))
    db.commit()

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
