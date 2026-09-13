from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.user import UserRole
from app.schemas.auth import (
    SendOtpRequest, SendOtpResponse, VerifyOtpRequest, TokenResponse,
    EmailLoginRequest,
)
from app.services import auth_service

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/send-otp", response_model=SendOtpResponse)
def send_otp(payload: SendOtpRequest):
    code = auth_service.send_otp(payload.phone_number)
    return SendOtpResponse(
        message="Verification code sent." + (" (dev mode: no real SMS is sent)" if settings.OTP_DEV_MODE else ""),
        dev_otp=code if settings.OTP_DEV_MODE else None,
    )


@router.post("/verify-otp", response_model=TokenResponse)
def verify_otp(payload: VerifyOtpRequest, db: Session = Depends(get_db)):
    user = auth_service.verify_otp(db, payload.phone_number, payload.code, payload.full_name)
    if user is None:
        raise HTTPException(status_code=400, detail="Invalid or expired verification code")
    token = auth_service.issue_token(user)
    return TokenResponse(access_token=token, role=user.role.value, user_id=user.id)


@router.post("/login", response_model=TokenResponse)
def login(payload: EmailLoginRequest, db: Session = Depends(get_db)):
    """Email+password login, used by restaurant staff and admins."""
    user = auth_service.authenticate_email(db, payload.email, payload.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = auth_service.issue_token(user)
    return TokenResponse(access_token=token, role=user.role.value, user_id=user.id)
