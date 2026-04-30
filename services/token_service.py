from datetime import datetime, timedelta
from core.security import (
    create_access_token,
    create_refresh_token,
    hash_data,
    verify_hash,
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
    stored_tokens = db.query(get_refresh_token.__globals__['RefreshToken']).all()

    valid_token = None
    for token in stored_tokens:
        if verify_hash(refresh_token, token.token_hash):
            valid_token = token
            break

    if not valid_token:
        raise Exception("Refresh token revoked or invalid")

    revoke_token(db, valid_token.token_hash)

    new_access = create_access_token({"sub": user_id})
    new_refresh = create_refresh_token({"sub": user_id})

    save_refresh_token(
        db,
        user_id,
        hash_data(new_refresh),
        datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )

    return new_access, new_refresh


def logout_user(db, refresh_token: str):
    stored_tokens = db.query(get_refresh_token.__globals__['RefreshToken']).all()

    for token in stored_tokens:
        if verify_hash(refresh_token, token.token_hash):
            revoke_token(db, token.token_hash)
            return True

    raise Exception("Invalid token")