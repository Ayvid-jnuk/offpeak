import enum
import uuid
from datetime import datetime

from sqlalchemy import String, Enum, DateTime, Integer, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class LoyaltyTxnType(str, enum.Enum):
    EARNED = "EARNED"
    REDEEMED = "REDEEMED"
    ADJUSTED = "ADJUSTED"


class LoyaltyAccount(Base):
    __tablename__ = "loyalty_accounts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    diner_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), unique=True, index=True)

    points_balance: Mapped[int] = mapped_column(Integer, default=0)
    lifetime_points_earned: Mapped[int] = mapped_column(Integer, default=0)
    credits_available_cents: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class LoyaltyTransaction(Base):
    """Append-only ledger. points_balance on LoyaltyAccount is a cached
    projection of this ledger, never the source of truth on its own."""
    __tablename__ = "loyalty_transactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    loyalty_account_id: Mapped[str] = mapped_column(String(36), ForeignKey("loyalty_accounts.id"), index=True)

    type: Mapped[LoyaltyTxnType] = mapped_column(Enum(LoyaltyTxnType), index=True)
    points: Mapped[int] = mapped_column(Integer)  # positive for EARNED, negative for REDEEMED
    reason: Mapped[str] = mapped_column(String(255))
    transaction_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("transactions.id"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
