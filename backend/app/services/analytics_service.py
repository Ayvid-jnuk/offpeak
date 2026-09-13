from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.claim import OfferClaim, ClaimStatus
from app.models.metrics import RestaurantMetric
from app.models.offer import Offer, OfferStatus
from app.models.recommendation import RevenueRecommendation
from app.models.restaurant import Restaurant, RestaurantApplication, ApplicationStatus
from app.models.transaction import Transaction, TransactionStatus
from app.models.user import User, UserRole


def restaurant_analytics(db: Session, restaurant_id: str) -> dict:
    today = date.today()

    today_txns = (
        db.query(Transaction)
        .filter(Transaction.restaurant_id == restaurant_id)
        .filter(func.date(Transaction.created_at) == today)
        .filter(Transaction.status == TransactionStatus.COMPLETED)
        .all()
    )
    today_revenue_cents = sum(t.restaurant_payout_cents for t in today_txns)

    all_txns = (
        db.query(Transaction)
        .filter(Transaction.restaurant_id == restaurant_id, Transaction.status == TransactionStatus.COMPLETED)
        .all()
    )
    offer_revenue_cents = sum(t.final_amount_cents for t in all_txns)
    avg_txn_cents = round(offer_revenue_cents / len(all_txns)) if all_txns else 0

    claims = (
        db.query(OfferClaim)
        .join(Offer, Offer.id == OfferClaim.offer_id)
        .filter(Offer.restaurant_id == restaurant_id)
        .all()
    )
    redeemed = [c for c in claims if c.status == ClaimStatus.REDEEMED]
    redemption_rate = round(len(redeemed) / len(claims) * 100, 1) if claims else 0.0

    latest_rec = (
        db.query(RevenueRecommendation)
        .filter(RevenueRecommendation.restaurant_id == restaurant_id)
        .order_by(RevenueRecommendation.created_at.desc())
        .first()
    )

    metrics = db.query(RestaurantMetric).filter(RestaurantMetric.restaurant_id == restaurant_id).all()
    unused_capacity_pct = 0.0
    if metrics:
        total_capacity = sum(m.capacity for m in metrics)
        total_covers = sum(m.covers for m in metrics)
        unused_capacity_pct = round((1 - total_covers / total_capacity) * 100, 1) if total_capacity else 0.0

    best_offer = None
    offers = db.query(Offer).filter(Offer.restaurant_id == restaurant_id).all()
    if offers:
        best_offer = max(offers, key=lambda o: o.redemptions_used, default=None)

    return {
        "today_revenue_cents": today_revenue_cents,
        "offer_revenue_cents": offer_revenue_cents,
        "redemption_rate_pct": redemption_rate,
        "average_transaction_cents": avg_txn_cents,
        "estimated_incremental_revenue_cents": latest_rec.estimated_incremental_revenue_cents if latest_rec else 0,
        "unused_capacity_pct": unused_capacity_pct,
        "best_performing_offer": best_offer.title if best_offer else None,
        "best_performing_time_window": (
            f"{latest_rec.window_start_hour:02d}:00-{latest_rec.window_end_hour:02d}:00" if latest_rec else None
        ),
        "total_claims": len(claims),
        "total_redemptions": len(redeemed),
    }


def admin_dashboard(db: Session) -> dict:
    restaurants_count = db.query(func.count(Restaurant.id)).scalar() or 0
    pending_count = (
        db.query(func.count(RestaurantApplication.id))
        .filter(RestaurantApplication.status == ApplicationStatus.PENDING)
        .scalar() or 0
    )
    active_offers = db.query(func.count(Offer.id)).filter(Offer.status == OfferStatus.ACTIVE).scalar() or 0
    claims_count = db.query(func.count(OfferClaim.id)).scalar() or 0

    completed_txns = db.query(Transaction).filter(Transaction.status == TransactionStatus.COMPLETED).all()
    gross_transaction_value_cents = sum(t.final_amount_cents for t in completed_txns)
    platform_commission_cents = sum(t.platform_commission_cents for t in completed_txns)

    active_diners = db.query(func.count(User.id)).filter(User.role == UserRole.DINER).scalar() or 0

    return {
        "restaurants": restaurants_count,
        "pending_applications": pending_count,
        "active_offers": active_offers,
        "claims": claims_count,
        "transactions": len(completed_txns),
        "gross_transaction_value_cents": gross_transaction_value_cents,
        "platform_commission_cents": platform_commission_cents,
        "active_diners": active_diners,
    }
