import enum
import uuid
from datetime import datetime

from sqlalchemy import String, Enum, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ClaimStatus(str, enum.Enum):
    CLAIMED = "CLAIMED"
    REDEEMED = "REDEEMED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class OfferClaim(Base):
    __tablename__ = "offer_claims"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    offer_id: Mapped[str] = mapped_column(String(36), ForeignKey("offers.id"), index=True)
    diner_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)

    redemption_code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    status: Mapped[ClaimStatus] = mapped_column(Enum(ClaimStatus), default=ClaimStatus.CLAIMED, index=True)

    claimed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    redeemed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
