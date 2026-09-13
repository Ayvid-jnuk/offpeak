import uuid
from datetime import datetime

from sqlalchemy import String, Integer, Numeric, ForeignKey, func, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RevenueRecommendation(Base):
    """
    A snapshot of what the transparent recommendation engine computed for a
    restaurant's quietest window, at the time it was generated. Stored so
    the "Create Offer" flow can reference exactly what was recommended, and
    so analytics can show recommendation -> offer conversion.
    """
    __tablename__ = "revenue_recommendations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    restaurant_id: Mapped[str] = mapped_column(String(36), ForeignKey("restaurants.id"), index=True)

    day_of_week: Mapped[int] = mapped_column(Integer)  # 0=Monday
    window_start_hour: Mapped[int] = mapped_column(Integer)
    window_end_hour: Mapped[int] = mapped_column(Integer)

    historical_occupancy_pct: Mapped[float] = mapped_column(Numeric(5, 2))
    available_capacity: Mapped[int] = mapped_column(Integer)

    recommended_discount_percent: Mapped[int] = mapped_column(Integer)
    estimated_additional_covers: Mapped[int] = mapped_column(Integer)
    estimated_incremental_revenue_cents: Mapped[int] = mapped_column(Integer)

    rationale: Mapped[str] = mapped_column(String(1000))
    was_used_for_offer: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
