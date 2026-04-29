import os
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials

JWT_SECRET = os.getenv("JWT_SECRET", "supersecret")
JWT_ALGORITHM = "HS256"

security = HTTPBearer()

def verify_token(credentials: HTTPAuthCredentials = Depends(security)):
    """Verify JWT token from Authorization header"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        role = payload.get("role")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return {"user_id": user_id, "role": role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

def verify_customer(token_data: dict = Depends(verify_token)):
    """Verify that user is a customer"""
    if token_data.get("role") != "customer":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only customers can access this")
    return token_data

def verify_cleaner(token_data: dict = Depends(verify_token)):
    """Verify that user is a cleaner"""
    if token_data.get("role") != "cleaner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only cleaners can access this")
    return token_data

def verify_admin(token_data: dict = Depends(verify_token)):
    """Verify that user is an admin"""
    if token_data.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can access this")
    return token_data
