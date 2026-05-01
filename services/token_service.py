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
from core.config import settings


def refresh_user_token(db, refresh_token: str):
    payload = decode_token(refresh_token)
    if not payload:
        raise Exception("Invalid refresh token")

    user_id = payload.get("sub")
    valid_token = get_refresh_token(db, refresh_token)

    if not valid_token:
        raise Exception("Refresh token revoked or invalid")
    if str(valid_token.user_id) != str(user_id):
        raise Exception("Refresh token does not belong to this user")

    revoke_token(db, valid_token.token_hash)

    new_access = create_access_token({"sub": user_id})
    new_refresh = create_refresh_token({"sub": user_id})

    save_refresh_token(
        db,
        user_id,
        new_refresh,  # Store raw JWT - JWTs are self-verifying via signature
        datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )

    return new_access, new_refresh


def logout_user(db, refresh_token: str):
    stored_token = get_refresh_token(db, refresh_token)
    if stored_token:
        revoke_token(db, stored_token.token_hash)
        return True

    raise Exception("Invalid token")
