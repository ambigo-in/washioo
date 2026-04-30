from pydantic import BaseModel
from datetime import date, time
from typing import Optional
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
