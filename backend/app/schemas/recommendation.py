from datetime import datetime
from pydantic import BaseModel


class RecommendationOut(BaseModel):
    id: str
    restaurant_id: str
    day_of_week: int
    window_start_hour: int
    window_end_hour: int
    historical_occupancy_pct: float
    available_capacity: int
    recommended_discount_percent: int
    estimated_additional_covers: int
    estimated_incremental_revenue_cents: int
    rationale: str
    was_used_for_offer: bool
    created_at: datetime

    class Config:
        from_attributes = True


class CreateOfferFromRecommendationRequest(BaseModel):
    recommendation_id: str
    max_redemptions: int = 20
