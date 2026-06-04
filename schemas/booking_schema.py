from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import date, time
from typing import Literal, Optional
from decimal import Decimal

class AddressSchema(BaseModel):
    id: Optional[str] = None
    address_label: Optional[str] = None
    address_line1: str
    address_line2: Optional[str] = None
    landmark: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    country: Optional[str] = "India"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_default: Optional[bool] = False

def _normalize_coordinate(value: Optional[float]) -> Optional[float]:
    if value is None:
        return None
    return round(float(value), 6)

class CreateAddressRequest(BaseModel):
    address_label: Optional[str] = None
    address_line1: str
    address_line2: Optional[str] = None
    landmark: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    country: Optional[str] = "India"
    latitude: float
    longitude: float
    location_verified: Optional[bool] = True
    is_default: Optional[bool] = False

    @field_validator("latitude", "longitude")
    @classmethod
    def normalize_coordinate(cls, value: float) -> float:
        return round(float(value), 6)

class UpdateAddressRequest(BaseModel):
    address_label: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    landmark: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_verified: Optional[bool] = None
    is_default: Optional[bool] = None

    @field_validator("latitude", "longitude")
    @classmethod
    def normalize_coordinate(cls, value: Optional[float]) -> Optional[float]:
        return _normalize_coordinate(value)

    @model_validator(mode="after")
    def coordinates_must_be_paired(self):
        if (self.latitude is None) != (self.longitude is None):
            raise ValueError("Both latitude and longitude are required together")
        return self

class CreateServiceRequest(BaseModel):
    service_name: str
    description: Optional[str] = None
    base_price: Decimal = Field(..., gt=0)
    estimated_duration_minutes: Optional[int] = Field(default=None, gt=0)
    allow_extra_payment: Optional[bool] = False
    max_extra_amount: Optional[Decimal] = Field(default=None, ge=0)
    extra_payment_instructions: Optional[str] = None
    is_active: Optional[bool] = True

class UpdateServiceRequest(BaseModel):
    service_name: Optional[str] = None
    description: Optional[str] = None
    base_price: Optional[Decimal] = Field(default=None, gt=0)
    estimated_duration_minutes: Optional[int] = Field(default=None, gt=0)
    allow_extra_payment: Optional[bool] = None
    max_extra_amount: Optional[Decimal] = Field(default=None, ge=0)
    extra_payment_instructions: Optional[str] = None
    is_active: Optional[bool] = None

class CreateCustomerVehicleRequest(BaseModel):
    vehicle_type: Literal["bike", "car"]
    make: Optional[str] = Field(default=None, max_length=100)
    model: Optional[str] = Field(default=None, max_length=100)
    license_plate: Optional[str] = Field(default=None, max_length=30)
    is_default: Optional[bool] = False

class UpdateCustomerVehicleRequest(BaseModel):
    vehicle_type: Optional[Literal["bike", "car"]] = None
    make: Optional[str] = Field(default=None, max_length=100)
    model: Optional[str] = Field(default=None, max_length=100)
    license_plate: Optional[str] = Field(default=None, max_length=30)
    is_default: Optional[bool] = None

class ServiceCategorySchema(BaseModel):
    id: str
    service_name: str
    description: Optional[str] = None
    base_price: Decimal
    estimated_duration_minutes: Optional[int] = None
    allow_extra_payment: bool = False
    max_extra_amount: Optional[Decimal] = None
    extra_payment_instructions: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True

class CreateBookingRequest(BaseModel):
    service_category_id: str
    address_id: Optional[str] = None  # If null, use default address
    address: Optional[CreateAddressRequest] = None  # Create new address if provided
    vehicle_id: Optional[str] = None
    scheduled_date: date
    scheduled_time: time
    special_instructions: Optional[str] = None

class UpdateBookingRequest(BaseModel):
    service_category_id: Optional[str] = None
    address_id: Optional[str] = None
    vehicle_id: Optional[str] = None
    scheduled_date: Optional[date] = None
    scheduled_time: Optional[time] = None
    special_instructions: Optional[str] = None

class AdminUpdateBookingRequest(UpdateBookingRequest):
    booking_status: Optional[Literal["pending", "assigned", "accepted", "in_progress", "completed", "cancelled"]] = None
    estimated_price: Optional[Decimal] = Field(default=None, gt=0)
    final_price: Optional[Decimal] = Field(default=None, gt=0)

class CancelBookingRequest(BaseModel):
    reason: Optional[str] = None

class CreateCleanerProfileRequest(BaseModel):
    user_id: str
    vehicle_type: Optional[str] = None
    aadhaar_number: str = Field(..., pattern=r"^\d{12}$")
    driving_license_number: Optional[str] = Field(default=None, pattern=r"^[A-Za-z0-9]{15,16}$")
    service_radius_km: Optional[Decimal] = None
    approval_status: Optional[Literal["pending", "approved", "rejected", "suspended"]] = "pending"
    availability_status: Optional[Literal["offline", "available", "busy"]] = "offline"

    @field_validator("driving_license_number", mode="before")
    @classmethod
    def normalize_optional_driving_license(cls, value):
        if value is None:
            return None
        if isinstance(value, str) and not value.strip():
            return None
        return value.strip().upper().replace(" ", "")

class UpdateCleanerProfileRequest(BaseModel):
    vehicle_type: Optional[str] = None
    aadhaar_number: Optional[str] = Field(default=None, pattern=r"^\d{12}$")
    driving_license_number: Optional[str] = Field(default=None, pattern=r"^[A-Za-z0-9]{15,16}$")
    service_radius_km: Optional[Decimal] = None
    approval_status: Optional[Literal["pending", "approved", "rejected", "suspended"]] = None
    availability_status: Optional[Literal["offline", "available", "busy"]] = None

    @field_validator("driving_license_number", mode="before")
    @classmethod
    def normalize_optional_driving_license(cls, value):
        if value is None:
            return None
        if isinstance(value, str) and not value.strip():
            return None
        return value.strip().upper().replace(" ", "")

class UpdateCleanerAvailabilityRequest(BaseModel):
    availability_status: Literal["offline", "available", "busy"]

class UpdateCleanerLocationRequest(BaseModel):
    latitude: float
    longitude: float

    @field_validator("latitude", "longitude")
    @classmethod
    def normalize_coordinate(cls, value: float) -> float:
        return round(float(value), 6)

class VerifyCleanerIdentityRequest(BaseModel):
    phone_last_four: str = Field(..., pattern=r"^\d{4}$")

class CleanerAadhaarUploadRequest(BaseModel):
    aadhaar_number: Optional[str] = Field(default=None, pattern=r"^\d{12}$")

class CleanerDrivingLicenseUploadRequest(BaseModel):
    driving_license_number: Optional[str] = Field(default=None, pattern=r"^[A-Za-z0-9]{15,16}$")

    @field_validator("driving_license_number", mode="before")
    @classmethod
    def normalize_optional_driving_license(cls, value):
        if value is None:
            return None
        if isinstance(value, str) and not value.strip():
            return None
        return value.strip().upper().replace(" ", "")

class AdminCleanerReviewRequest(BaseModel):
    reason: Optional[str] = Field(default=None, max_length=500)

class AssignBookingRequest(BaseModel):
    cleaner_id: str
    cleaner_notes: Optional[str] = None

class CleanerAssignmentActionRequest(BaseModel):
    cleaner_notes: Optional[str] = None

class CompleteAssignmentRequest(BaseModel):
    cleaner_notes: Optional[str] = None
    final_price: Optional[Decimal] = Field(default=None, gt=0)
    payment_method: Optional[Literal["UPI", "Cash"]] = None
    payment_type: Optional[Literal["upi", "cash"]] = None
    collected_amount: Optional[Decimal] = Field(default=None, gt=0)
    transaction_reference: Optional[str] = None
    collected_by_cleaner: Optional[bool] = None

class BookingResponse(BaseModel):
    id: str
    booking_reference: str
    customer_id: str
    service_category_id: str
    scheduled_date: date
    scheduled_time: time
    booking_status: str
    estimated_price: Decimal
    final_price: Optional[Decimal] = None
    special_instructions: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True

class AdminBookingResponse(BaseModel):
    id: str
    booking_reference: str
    customer_id: str
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    service_name: Optional[str] = None
    service_category_id: str
    scheduled_date: date
    scheduled_time: time
    booking_status: str
    estimated_price: Decimal
    final_price: Optional[Decimal] = None
    special_instructions: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True
