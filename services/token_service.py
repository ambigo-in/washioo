from datetime import datetime, timedelta
from core.security import (
    create_access_token,
    create_refresh_token,
    decode_token
)
from repositories.token_repository import (
    get_refresh_token,
    save_refresh_token,
    revoke_token
)
from repositories.user_repository import get_user_with_roles
from core.config import settings


def refresh_user_token(db, refresh_token: str):
    """Refresh access token using valid refresh token"""
    payload = decode_token(refresh_token)
    if not payload:
        raise Exception("Invalid or malformed refresh token")

    user_id = payload.get("sub")
    if not user_id:
        raise Exception("Invalid token: missing user ID")
    
    # Verify and retrieve the stored token
    valid_token = get_refresh_token(db, refresh_token)
    if not valid_token:
        raise Exception("Refresh token revoked, expired, or invalid")
    
    if str(valid_token.user_id) != str(user_id):
        raise Exception("Refresh token does not belong to this user")

    user = get_user_with_roles(db, user_id)
    if not user or not user.is_active:
        raise Exception("User not found or inactive")

    # Revoke old token
    revoke_token(db, valid_token.jti)

    # Create new tokens
    new_access = create_access_token({"sub": user_id})
    new_refresh_token, new_jti = create_refresh_token({"sub": user_id})

    # Save new refresh token with hashing
    save_refresh_token(
        db,
        user_id,
        new_jti,
        new_refresh_token,
        datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )

    return new_access, new_refresh_token


def logout_user(db, refresh_token: str):
    """Logout user by revoking their refresh token"""
    stored_token = get_refresh_token(db, refresh_token)
    if stored_token:
        revoke_token(db, stored_token.jti)
        return True

    raise Exception("Invalid or already revoked token")
