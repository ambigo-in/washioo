from sqlalchemy.orm import Session
from app.models.models import User, UserRole
from app.schemas.schemas import RegisterRequest, LoginRequest, TokenResponse, UserOut
from app.services import jwt_service
from fastapi import HTTPException, status
from uuid import uuid4
from datetime import datetime

def register_user(db: Session, payload: RegisterRequest):
    user = db.query(User).filter(User.phone_number == payload.phone_number).first()
    if user:
        raise HTTPException(status_code=400, detail="User already exists")
    new_user = User(
        id=uuid4(),
        phone_number=payload.phone_number,
        full_name=payload.full_name,
        role=UserRole.customer,
        is_verified=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def login_user(db: Session, payload: LoginRequest):
    user = db.query(User).filter(User.phone_number == payload.phone_number).first()
    if not user or not user.is_verified:
        raise HTTPException(status_code=401, detail="Invalid credentials or user not verified")
    tokens = jwt_service.create_tokens(user)
    return tokens
