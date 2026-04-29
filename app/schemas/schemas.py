from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from enum import Enum
from datetime import datetime

class UserRole(str, Enum):
    customer = "customer"
    admin = "admin"
    cleaner = "cleaner"

class VehicleType(str, Enum):
    car = "car"
    bike = "bike"

class BookingStatus(str, Enum):
    pending = "pending"
    assigned = "assigned"
    en_route = "en_route"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"
    failed = "failed"

class PaymentStatus(str, Enum):
    unpaid = "unpaid"
    paid = "paid"

class PaymentMethod(str, Enum):
    cash = "cash"
    upi = "upi"

class UserBase(BaseModel):
    phone_number: str
    full_name: Optional[str] = None
    role: UserRole

class UserCreate(UserBase):
    pass

class UserOut(UserBase):
    id: UUID
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class VehicleBase(BaseModel):
    vehicle_type: VehicleType
    vehicle_model: str
    vehicle_number: str

class VehicleCreate(VehicleBase):
    pass

class VehicleOut(VehicleBase):
    id: UUID
    user_id: UUID
    created_at: datetime

    class Config:
        orm_mode = True

class PackageBase(BaseModel):
    vehicle_type: VehicleType
    package_name: str
    description: Optional[str]
    price: float
    duration_minutes: int

class PackageOut(PackageBase):
    id: UUID

    class Config:
        orm_mode = True

class BookingBase(BaseModel):
    vehicle_id: UUID
    package_id: UUID
    address: str
    latitude: float
    longitude: float
    scheduled_at: Optional[datetime]
    payment_method: Optional[PaymentMethod]

class BookingCreate(BookingBase):
    pass

class BookingOut(BookingBase):
    id: UUID
    user_id: UUID
    cleaner_id: Optional[UUID]
    status: BookingStatus
    payment_status: PaymentStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class CleanerLocationBase(BaseModel):
    latitude: float
    longitude: float

class CleanerLocationUpdate(CleanerLocationBase):
    pass

class CleanerLocationOut(CleanerLocationBase):
    id: UUID
    cleaner_id: UUID
    updated_at: datetime

    class Config:
        orm_mode = True

# Auth Schemas
class SendOTPRequest(BaseModel):
    phone_number: str = Field(..., example="+919876543210")

class VerifyOTPRequest(BaseModel):
    phone_number: str = Field(..., example="+919876543210")
    otp_code: str = Field(..., example="123456")

class RegisterRequest(BaseModel):
    phone_number: str
    full_name: str

class LoginRequest(BaseModel):
    phone_number: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
