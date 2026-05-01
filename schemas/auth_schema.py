from pydantic import BaseModel, EmailStr
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

class SignupRequest(BaseModel):
    full_name: str
    phone_number: str
    email: EmailStr
    otp_code: str
    role: Literal["customer", "cleaner", "admin"]
