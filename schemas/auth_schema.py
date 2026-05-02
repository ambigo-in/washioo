from pydantic import BaseModel, EmailStr, Field
from typing import Literal

class SendOTPRequest(BaseModel):
    phone_number: str

class SigninRequest(BaseModel):
    phone_number: str
    otp_code: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class LogoutRequest(BaseModel):
    refresh_token: str

class RoleSignupRequest(BaseModel):
    full_name: str
    phone_number: str
    email: EmailStr
    otp_code: str

class CleanerSignupRequest(RoleSignupRequest):
    aadhaar_number: str = Field(..., min_length=12, max_length=20)
    driving_license_number: str | None = None

class SignupRequest(BaseModel):
    full_name: str
    phone_number: str
    email: EmailStr
    otp_code: str
    role: Literal["customer", "cleaner", "admin"]

class CreateAdminRequest(BaseModel):
    full_name: str
    phone_number: str
    email: EmailStr
