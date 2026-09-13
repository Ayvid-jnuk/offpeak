from datetime import datetime
from pydantic import BaseModel, Field


class CheckoutRequest(BaseModel):
    claim_id: str
    original_amount_cents: int = Field(gt=0)


class TransactionOut(BaseModel):
    id: str
    claim_id: str
    offer_id: str
    diner_id: str
    restaurant_id: str
    original_amount_cents: int
    discount_amount_cents: int
    final_amount_cents: int
    platform_commission_cents: int
    restaurant_payout_cents: int
    currency: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
