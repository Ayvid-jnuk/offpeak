import enum
import uuid
from datetime import datetime

from sqlalchemy import String, Enum, DateTime, func, Integer, Text, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ApplicationStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class RestaurantApplication(Base):
    __tablename__ = "restaurant_applications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    applicant_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)

    name: Mapped[str] = mapped_column(String(255))
    cuisine: Mapped[str] = mapped_column(String(100))
    address: Mapped[str] = mapped_column(String(500))
    description: Mapped[str] = mapped_column(Text)
    phone: Mapped[str] = mapped_column(String(32))
    email: Mapped[str] = mapped_column(String(255))
    opening_hours: Mapped[str] = mapped_column(String(500))
    seating_capacity: Mapped[int] = mapped_column(Integer)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus), default=ApplicationStatus.PENDING, index=True
    )
    reviewed_by_admin_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    review_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    restaurant: Mapped["Restaurant"] = relationship(back_populates="application", uselist=False)


class Restaurant(Base):
    __tablename__ = "restaurants"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    application_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("restaurant_applications.id"), nullable=True
    )
    owner_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)

    name: Mapped[str] = mapped_column(String(255), index=True)
    cuisine: Mapped[str] = mapped_column(String(100), index=True)
    address: Mapped[str] = mapped_column(String(500))
    description: Mapped[str] = mapped_column(Text)
    phone: Mapped[str] = mapped_column(String(32))
    email: Mapped[str] = mapped_column(String(255))
    opening_hours: Mapped[str] = mapped_column(String(500))
    seating_capacity: Mapped[int] = mapped_column(Integer)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    rating: Mapped[float] = mapped_column(Numeric(2, 1), default=4.5)
    latitude: Mapped[float | None] = mapped_column(Numeric(9, 6), nullable=True)
    longitude: Mapped[float | None] = mapped_column(Numeric(9, 6), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    application: Mapped["RestaurantApplication"] = relationship(back_populates="restaurant")
