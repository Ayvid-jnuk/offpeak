from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import require_restaurant
from app.db.session import get_db
from app.models.offer import Offer
from app.models.recommendation import RevenueRecommendation
from app.models.user import User
from app.schemas.offer import OfferOut
from app.schemas.recommendation import RecommendationOut, CreateOfferFromRecommendationRequest
from app.services import recommendation_service, restaurant_service, offer_service

router = APIRouter(prefix="/api/v1/restaurants/me/recommendations", tags=["recommendations"])


def _get_owned_restaurant(user: User, db: Session):
    restaurant = restaurant_service.get_restaurant_for_owner(db, user.id)
    if restaurant is None:
        raise HTTPException(status_code=404, detail="No approved restaurant for this account")
    return restaurant


@router.get("/latest", response_model=RecommendationOut | None)
def latest_recommendation(user: User = Depends(require_restaurant), db: Session = Depends(get_db)):
    restaurant = _get_owned_restaurant(user, db)
    return recommendation_service.get_latest_recommendation(db, restaurant.id)


@router.post("/generate", response_model=RecommendationOut)
def generate_recommendation(user: User = Depends(require_restaurant), db: Session = Depends(get_db)):
    restaurant = _get_owned_restaurant(user, db)
    try:
        rec = recommendation_service.generate_recommendation(db, restaurant.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if rec is None:
        raise HTTPException(status_code=404, detail="Not enough historical data to generate a recommendation yet")
    return rec


@router.post("/{recommendation_id}/create-offer", response_model=OfferOut)
def create_offer_from_recommendation(
    recommendation_id: str,
    payload: CreateOfferFromRecommendationRequest,
    user: User = Depends(require_restaurant),
    db: Session = Depends(get_db),
):
    """This is the recommendation -> offer creation link: pre-filled values
    from the recommendation are used directly to publish a real offer."""
    restaurant = _get_owned_restaurant(user, db)
    rec = db.get(RevenueRecommendation, recommendation_id)
    if rec is None or rec.restaurant_id != restaurant.id:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    if rec.recommended_discount_percent <= 0:
        raise HTTPException(status_code=400, detail="This recommendation does not suggest running a discount")

    from datetime import date, timedelta, time as time_cls
    today = date.today()
    days_ahead = (rec.day_of_week - today.weekday()) % 7
    days_ahead = days_ahead or 7
    target_date = today + timedelta(days=days_ahead)

    offer_data = {
        "title": f"{restaurant.name}: Off-Peak Special",
        "description": rec.rationale,
        "discount_percent": rec.recommended_discount_percent,
        "start_date": target_date,
        "end_date": target_date,
        "start_time": time_cls(hour=rec.window_start_hour),
        "end_time": time_cls(hour=rec.window_end_hour),
        "max_redemptions": payload.max_redemptions,
        "source_recommendation_id": rec.id,
    }
    offer = offer_service.create_offer(db, restaurant.id, offer_data)
    return offer
