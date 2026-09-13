from datetime import datetime
from pydantic import BaseModel


class LoyaltyTxnOut(BaseModel):
    id: str
    type: str
    points: int
    reason: str
    created_at: datetime

    class Config:
        from_attributes = True


class LoyaltyAccountOut(BaseModel):
    points_balance: int
    lifetime_points_earned: int
    credits_available_cents: int
    recent_activity: list[LoyaltyTxnOut]


class LoyaltyRedeemRequest(BaseModel):
    points: int
