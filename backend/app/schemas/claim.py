from datetime import datetime
from pydantic import BaseModel


class ClaimOut(BaseModel):
    id: str
    offer_id: str
    diner_id: str
    redemption_code: str
    status: str
    claimed_at: datetime
    redeemed_at: datetime | None

    class Config:
        from_attributes = True


class RedeemRequest(BaseModel):
    redemption_code: str
