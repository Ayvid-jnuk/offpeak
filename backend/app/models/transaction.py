import enum
import uuid
from datetime import datetime

from sqlalchemy import String, Enum, DateTime, Integer, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TransactionStatus(str, enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class Transaction(Base):
    """
    All monetary fields are stored as integer cents to avoid floating point
    rounding errors. currency is a fixed ISO code for the demo.
    """
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    claim_id: Mapped[str] = mapped_column(String(36), ForeignKey("offer_claims.id"), index=True)
    offer_id: Mapped[str] = mapped_column(String(36), ForeignKey("offers.id"), index=True)
    diner_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    restaurant_id: Mapped[str] = mapped_column(String(36), ForeignKey("restaurants.id"), index=True)

    original_amount_cents: Mapped[int] = mapped_column(Integer)
    discount_amount_cents: Mapped[int] = mapped_column(Integer)
    final_amount_cents: Mapped[int] = mapped_column(Integer)
    platform_commission_cents: Mapped[int] = mapped_column(Integer)
    restaurant_payout_cents: Mapped[int] = mapped_column(Integer)
    currency: Mapped[str] = mapped_column(String(3), default="AUD")

    status: Mapped[TransactionStatus] = mapped_column(Enum(TransactionStatus), default=TransactionStatus.PENDING, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
