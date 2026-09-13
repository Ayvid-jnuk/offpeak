from datetime import date, time, datetime
from pydantic import BaseModel, Field


class OfferCreateRequest(BaseModel):
    title: str
    description: str | None = None
    discount_percent: int = Field(gt=0, le=100)
    start_date: date
    end_date: date
    start_time: time
    end_time: time
    max_redemptions: int = Field(gt=0)
    source_recommendation_id: str | None = None


class OfferUpdateRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None  # ACTIVE / INACTIVE
    max_redemptions: int | None = None


class OfferOut(BaseModel):
    id: str
    restaurant_id: str
    title: str
    description: str | None
    discount_percent: int
    start_date: date
    end_date: date
    start_time: time
    end_time: time
    max_redemptions: int
    redemptions_used: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class OfferWithRestaurantOut(OfferOut):
    restaurant_name: str
    restaurant_cuisine: str
    restaurant_rating: float
    restaurant_image_url: str | None
