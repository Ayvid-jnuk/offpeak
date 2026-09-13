from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import require_diner
from app.db.session import get_db
from app.models.user import User
from app.schemas.loyalty import LoyaltyAccountOut, LoyaltyRedeemRequest
from app.services import loyalty_service

router = APIRouter(prefix="/api/v1/loyalty", tags=["loyalty"])


@router.get("", response_model=LoyaltyAccountOut)
def my_loyalty(user: User = Depends(require_diner), db: Session = Depends(get_db)):
    account, activity = loyalty_service.get_account_with_activity(db, user.id)
    return LoyaltyAccountOut(
        points_balance=account.points_balance,
        lifetime_points_earned=account.lifetime_points_earned,
        credits_available_cents=account.credits_available_cents,
        recent_activity=activity,
    )


@router.post("/redeem", response_model=LoyaltyAccountOut)
def redeem(payload: LoyaltyRedeemRequest, user: User = Depends(require_diner), db: Session = Depends(get_db)):
    try:
        loyalty_service.redeem_points_for_credit(db, user.id, payload.points)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    account, activity = loyalty_service.get_account_with_activity(db, user.id)
    return LoyaltyAccountOut(
        points_balance=account.points_balance,
        lifetime_points_earned=account.lifetime_points_earned,
        credits_available_cents=account.credits_available_cents,
        recent_activity=activity,
    )
