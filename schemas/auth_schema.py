from pydantic import BaseModel, EmailStr, Field

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
    aadhaar_number: str = Field(..., pattern=r"^\d{12}$")
    driving_license_number: str | None = Field(default=None, min_length=6, max_length=30)

class CreateAdminRequest(BaseModel):
    full_name: str
    phone_number: str
    email: EmailStr
