from datetime import datetime, timedelta
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext
from core.config import settings
import hashlib
import hmac
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_data(data: str):
    return pwd_context.hash(data)

def verify_hash(plain: str, hashed: str):
    return pwd_context.verify(plain, hashed)

def hash_identifier(value: str):
    normalized = "".join(value.split()).upper()
    return hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        normalized.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

def mask_identifier(value: str, visible_digits: int = 4):
    normalized = "".join(value.split()).upper()
    if len(normalized) <= visible_digits:
        return "*" * len(normalized)
    return f"{'*' * (len(normalized) - visible_digits)}{normalized[-visible_digits:]}"

def create_access_token(data: dict):
    to_encode = data.copy()
    issued_at = datetime.utcnow()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({
        "exp": expire,
        "iat": issued_at,
        "jti": str(uuid.uuid4()),
        "type": "access",
    })
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token(data: dict):
    to_encode = data.copy()
    # Add unique JTI (JWT ID) to track individual refresh tokens
    jti = str(uuid.uuid4())
    issued_at = datetime.utcnow()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({
        "exp": expire,
        "iat": issued_at,
        "jti": jti,
        "type": "refresh",
    })
    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token, jti  # Return both token and JTI for storage

class TokenExpired(Exception):
    pass

class TokenInvalid(Exception):
    pass

def decode_token_or_raise(token: str):
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except ExpiredSignatureError as exc:
        raise TokenExpired("Token expired") from exc
    except JWTError as exc:
        raise TokenInvalid("Invalid token") from exc

def decode_token(token: str):
    try:
        return decode_token_or_raise(token)
    except (TokenExpired, TokenInvalid):
        return None
