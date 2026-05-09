import re

from pydantic import BaseModel, EmailStr, Field, field_validator


PHONE_ERROR = "Enter a valid 10-digit Indian mobile number"


def validate_indian_mobile(value: str) -> str:
    value = value.strip()
    if not re.match(r"^[6-9]\d{9}$", value):
        raise ValueError(PHONE_ERROR)
    return value


class SendOTPRequest(BaseModel):
    phone_number: str

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        return validate_indian_mobile(value)

class SigninRequest(BaseModel):
    phone_number: str
    otp_code: str

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        return validate_indian_mobile(value)

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class LogoutRequest(BaseModel):
    refresh_token: str

class RoleSignupRequest(BaseModel):
    full_name: str
    phone_number: str
    email: EmailStr | None = None
    otp_code: str

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        return validate_indian_mobile(value)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_optional_email(cls, value):
        if value is None:
            return None
        if isinstance(value, str) and not value.strip():
            return None
        return value

class CleanerSignupRequest(RoleSignupRequest):
    aadhaar_number: str = Field(..., pattern=r"^\d{12}$")
    driving_license_number: str | None = Field(
        default=None,
        pattern=r"^[A-Za-z0-9]{15,16}$",
    )

    @field_validator("driving_license_number", mode="before")
    @classmethod
    def normalize_optional_driving_license(cls, value):
        if value is None:
            return None
        if isinstance(value, str) and not value.strip():
            return None
        return value.strip().upper().replace(" ", "")

class CreateAdminRequest(BaseModel):
    full_name: str
    phone_number: str
    email: EmailStr

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        return validate_indian_mobile(value)
