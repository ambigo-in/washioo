import os
from datetime import datetime, timedelta
from jose import jwt
from app.schemas.schemas import TokenResponse

JWT_SECRET = os.getenv("JWT_SECRET", "supersecret")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

def create_tokens(user):
    access_token = create_token({"sub": str(user.id), "role": user.role.value}, ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token = create_token({"sub": str(user.id)}, REFRESH_TOKEN_EXPIRE_MINUTES)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )

def create_token(data: dict, expires_minutes: int):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt
