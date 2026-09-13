import uuid
from datetime import date as date_type, datetime

from sqlalchemy import String, Date, Integer, Numeric, ForeignKey, func, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RestaurantMetric(Base):
    """
    Historical, per-hour occupancy/revenue snapshots used purely as the
    seeded dataset the recommendation engine reads from. This is demo data,
    not a live POS feed.
    """
    __tablename__ = "restaurant_metrics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    restaurant_id: Mapped[str] = mapped_column(String(36), ForeignKey("restaurants.id"), index=True)

    date: Mapped[date_type] = mapped_column(Date, index=True)
    day_of_week: Mapped[int] = mapped_column(Integer, index=True)  # 0=Monday ... 6=Sunday
    hour: Mapped[int] = mapped_column(Integer, index=True)  # 0-23

    capacity: Mapped[int] = mapped_column(Integer)
    covers: Mapped[int] = mapped_column(Integer)
    revenue_cents: Mapped[int] = mapped_column(Integer)
    average_bill_cents: Mapped[int] = mapped_column(Integer)
    weather_condition: Mapped[str | None] = mapped_column(String(50), nullable=True)
    event_flag: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
