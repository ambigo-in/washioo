from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    id: str
    full_name: Optional[str]
    phone: str
    email: Optional[EmailStr]
    is_verified: bool
    is_active: bool
    roles: List[str]
    created_at: datetime


class UpdateUserRequest(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
