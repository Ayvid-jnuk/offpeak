from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class SendOtpRequest(BaseModel):
    phone_number: str = Field(min_length=6, max_length=20)


class SendOtpResponse(BaseModel):
    message: str
    dev_otp: str | None = None  # only populated in OTP_DEV_MODE, for demo convenience


class VerifyOtpRequest(BaseModel):
    phone_number: str
    code: str
    full_name: str | None = None  # used on first-time signup


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: str


class EmailLoginRequest(BaseModel):
    email: EmailStr
    password: str


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    full_name: str


class MeOut(BaseModel):
    id: str
    full_name: str | None
    email: EmailStr | None
    phone_number: str | None
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class UpdateMeRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=255)