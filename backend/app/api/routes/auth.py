from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.auth import (
    SendOtpRequest, SendOtpResponse, VerifyOtpRequest, TokenResponse,
    EmailLoginRequest, MeOut, UpdateMeRequest,
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


@router.get("/me", response_model=MeOut)
def get_me(user: User = Depends(get_current_user)):
    return user


@router.patch("/me", response_model=MeOut)
def update_me(payload: UpdateMeRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user.full_name = payload.full_name
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(payload: EmailLoginRequest, db: Session = Depends(get_db)):
    """Email+password login, used by restaurant staff and admins."""
    user = auth_service.authenticate_email(db, payload.email, payload.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = auth_service.issue_token(user)
    return TokenResponse(access_token=token, role=user.role.value, user_id=user.id)