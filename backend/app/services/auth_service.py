"""
Authentication service.

Two flows are supported:
  - Diners: phone number + simulated OTP (no real SMS infra required).
  - Restaurant/Admin: email + password (set during application / seeding).

The OTP flow is intentionally simple and swappable: `_generate_or_fetch_otp`
is the single seam that would be replaced by a real SMS provider integration.
Codes/passwords are never written to logs.
"""
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User, UserRole

# In-memory OTP store for the demo: {phone_number: code}. A real deployment
# would persist this with expiry + rate limiting, or delegate entirely to
# the SMS provider's verification API.
_otp_store: dict[str, str] = {}


def send_otp(phone_number: str) -> str:
    code = settings.OTP_STATIC_CODE if settings.OTP_DEV_MODE else _random_code()
    _otp_store[phone_number] = code
    return code


def _random_code() -> str:
    import random
    return f"{random.randint(0, 999999):06d}"


def verify_otp(db: Session, phone_number: str, code: str, full_name: str | None = None) -> User | None:
    expected = _otp_store.get(phone_number)
    if expected is None or expected != code:
        return None

    user = db.query(User).filter(User.phone_number == phone_number).first()
    if user is None:
        user = User(
            phone_number=phone_number,
            full_name=full_name or "Diner",
            role=UserRole.DINER,
            is_phone_verified=True,
        )
        db.add(user)
        db.flush()
        from app.services.loyalty_service import ensure_loyalty_account
        ensure_loyalty_account(db, user.id)
    else:
        user.is_phone_verified = True

    del _otp_store[phone_number]
    db.commit()
    db.refresh(user)
    return user


def authenticate_email(db: Session, email: str, password: str) -> User | None:
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.hashed_password:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_user_with_password(db: Session, email: str, password: str, full_name: str, role: UserRole) -> User:
    user = User(
        email=email,
        hashed_password=hash_password(password),
        full_name=full_name,
        role=role,
        is_active=True,
    )
    db.add(user)
    db.flush()
    return user


def issue_token(user: User) -> str:
    return create_access_token(subject=user.id, role=user.role.value)
