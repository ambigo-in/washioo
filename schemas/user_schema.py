from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, field_validator

from schemas.auth_schema import validate_indian_mobile


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

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        return validate_indian_mobile(value)


class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
