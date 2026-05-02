from pydantic import BaseModel
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

class CreateAddressRequest(BaseModel):
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
    is_default: Optional[bool] = None

class CreateServiceRequest(BaseModel):
    service_name: str
    description: Optional[str] = None
    base_price: Decimal
    estimated_duration_minutes: Optional[int] = None
    is_active: Optional[bool] = True

class UpdateServiceRequest(BaseModel):
    service_name: Optional[str] = None
    description: Optional[str] = None
    base_price: Optional[Decimal] = None
    estimated_duration_minutes: Optional[int] = None
    is_active: Optional[bool] = None

class ServiceCategorySchema(BaseModel):
    id: str
    service_name: str
    description: Optional[str] = None
    base_price: Decimal
    estimated_duration_minutes: Optional[int] = None
    is_active: bool

    class Config:
        from_attributes = True

class CreateBookingRequest(BaseModel):
    service_category_id: str
    address_id: Optional[str] = None  # If null, use default address
    address: Optional[CreateAddressRequest] = None  # Create new address if provided
    scheduled_date: date
    scheduled_time: time
    special_instructions: Optional[str] = None

class UpdateBookingRequest(BaseModel):
    service_category_id: Optional[str] = None
    address_id: Optional[str] = None
    scheduled_date: Optional[date] = None
    scheduled_time: Optional[time] = None
    special_instructions: Optional[str] = None

class AdminUpdateBookingRequest(UpdateBookingRequest):
    booking_status: Optional[Literal["pending", "assigned", "accepted", "in_progress", "completed", "cancelled"]] = None
    estimated_price: Optional[Decimal] = None
    final_price: Optional[Decimal] = None

class CancelBookingRequest(BaseModel):
    reason: Optional[str] = None

class CreateCleanerProfileRequest(BaseModel):
    user_id: str
    vehicle_type: Optional[str] = None
    aadhaar_number: str
    driving_license_number: Optional[str] = None
    government_id_number: Optional[str] = None
    service_radius_km: Optional[Decimal] = None
    approval_status: Optional[Literal["pending", "approved", "rejected", "suspended"]] = "pending"
    availability_status: Optional[Literal["offline", "available", "busy"]] = "offline"

class UpdateCleanerProfileRequest(BaseModel):
    vehicle_type: Optional[str] = None
    aadhaar_number: Optional[str] = None
    driving_license_number: Optional[str] = None
    government_id_number: Optional[str] = None
    service_radius_km: Optional[Decimal] = None
    approval_status: Optional[Literal["pending", "approved", "rejected", "suspended"]] = None
    availability_status: Optional[Literal["offline", "available", "busy"]] = None

class UpdateCleanerAvailabilityRequest(BaseModel):
    availability_status: Literal["offline", "available", "busy"]

class AssignBookingRequest(BaseModel):
    cleaner_id: str
    cleaner_notes: Optional[str] = None

class CleanerAssignmentActionRequest(BaseModel):
    cleaner_notes: Optional[str] = None

class CompleteAssignmentRequest(BaseModel):
    cleaner_notes: Optional[str] = None
    final_price: Optional[Decimal] = None

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
