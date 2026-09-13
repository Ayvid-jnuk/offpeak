import enum
import uuid
from datetime import datetime, date, time

from sqlalchemy import String, Enum, DateTime, Date, Time, Integer, Numeric, ForeignKey, func, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class OfferStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    EXPIRED = "EXPIRED"


class Offer(Base):
    __tablename__ = "offers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    restaurant_id: Mapped[str] = mapped_column(String(36), ForeignKey("restaurants.id"), index=True)

    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    discount_percent: Mapped[int] = mapped_column(Integer)  # 1-100

    start_date: Mapped[date] = mapped_column(Date, index=True)
    end_date: Mapped[date] = mapped_column(Date, index=True)
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)

    max_redemptions: Mapped[int] = mapped_column(Integer)
    redemptions_used: Mapped[int] = mapped_column(Integer, default=0)

    status: Mapped[OfferStatus] = mapped_column(Enum(OfferStatus), default=OfferStatus.ACTIVE, index=True)

    # Set when this offer was created from a revenue recommendation, so the
    # UI/analytics can show the recommendation -> offer connection.
    source_recommendation_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("revenue_recommendations.id"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
