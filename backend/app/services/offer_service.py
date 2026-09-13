from datetime import date, datetime, timezone

from sqlalchemy.orm import Session

from app.models.offer import Offer, OfferStatus
from app.models.recommendation import RevenueRecommendation


def create_offer(db: Session, restaurant_id: str, data: dict) -> Offer:
    if data["discount_percent"] <= 0 or data["discount_percent"] > 100:
        raise ValueError("discount_percent must be between 1 and 100")
    if data["start_date"] > data["end_date"]:
        raise ValueError("start_date must be before or equal to end_date")
    if data["max_redemptions"] <= 0:
        raise ValueError("max_redemptions must be positive")

    offer = Offer(
        restaurant_id=restaurant_id,
        title=data["title"],
        description=data.get("description"),
        discount_percent=data["discount_percent"],
        start_date=data["start_date"],
        end_date=data["end_date"],
        start_time=data["start_time"],
        end_time=data["end_time"],
        max_redemptions=data["max_redemptions"],
        status=OfferStatus.ACTIVE,
        source_recommendation_id=data.get("source_recommendation_id"),
    )
    db.add(offer)

    if data.get("source_recommendation_id"):
        rec = db.get(RevenueRecommendation, data["source_recommendation_id"])
        if rec is not None:
            rec.was_used_for_offer = True

    db.commit()
    db.refresh(offer)
    return offer


def update_offer(db: Session, offer: Offer, data: dict) -> Offer:
    if data.get("title") is not None:
        offer.title = data["title"]
    if data.get("description") is not None:
        offer.description = data["description"]
    if data.get("max_redemptions") is not None:
        if data["max_redemptions"] < offer.redemptions_used:
            raise ValueError("max_redemptions cannot be less than redemptions already used")
        offer.max_redemptions = data["max_redemptions"]
    if data.get("status") is not None:
        if data["status"] not in (OfferStatus.ACTIVE.value, OfferStatus.INACTIVE.value):
            raise ValueError("status must be ACTIVE or INACTIVE")
        offer.status = OfferStatus(data["status"])
    db.commit()
    db.refresh(offer)
    return offer


def is_offer_claimable(offer: Offer) -> tuple[bool, str | None]:
    today = date.today()
    if offer.status != OfferStatus.ACTIVE:
        return False, "Offer is not active"
    if today < offer.start_date or today > offer.end_date:
        return False, "Offer is not within its valid date range"
    if offer.redemptions_used >= offer.max_redemptions:
        return False, "Offer has reached its maximum redemptions"
    return True, None


def list_discoverable_offers(db: Session):
    today = date.today()
    return (
        db.query(Offer)
        .filter(Offer.status == OfferStatus.ACTIVE)
        .filter(Offer.start_date <= today, Offer.end_date >= today)
        .all()
    )
