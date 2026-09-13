from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.claim import OfferClaim, ClaimStatus
from app.models.offer import Offer
from app.models.transaction import Transaction, TransactionStatus
from app.services.loyalty_service import earn_points


def _cents(value: Decimal) -> int:
    return int(value.to_integral_value(rounding=ROUND_HALF_UP))


def compute_amounts(original_amount_cents: int, discount_percent: int) -> dict:
    """
    All money math done with Decimal, result truncated/rounded to integer
    cents at the end — never floating point. Commission rate comes from
    config so it stays a single source of truth.
    """
    if original_amount_cents <= 0:
        raise ValueError("original_amount_cents must be positive")
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("discount_percent must be between 0 and 100")

    original = Decimal(original_amount_cents)
    discount_pct = Decimal(discount_percent) / Decimal(100)
    commission_rate = Decimal(settings.PLATFORM_COMMISSION_RATE)

    discount_amount = _cents(original * discount_pct)
    final_amount = original_amount_cents - discount_amount
    if final_amount < 0:
        raise ValueError("Computed final amount cannot be negative")

    commission = _cents(Decimal(final_amount) * commission_rate)
    if commission < 0:
        raise ValueError("Computed commission cannot be negative")

    restaurant_payout = final_amount - commission
    if restaurant_payout < 0:
        raise ValueError("Computed restaurant payout cannot be negative")

    return {
        "discount_amount_cents": discount_amount,
        "final_amount_cents": final_amount,
        "platform_commission_cents": commission,
        "restaurant_payout_cents": restaurant_payout,
    }


def checkout(db: Session, claim: OfferClaim, offer: Offer, original_amount_cents: int) -> Transaction:
    if claim.status != ClaimStatus.REDEEMED:
        raise ValueError("Claim must be redeemed before checkout")

    amounts = compute_amounts(original_amount_cents, offer.discount_percent)

    txn = Transaction(
        claim_id=claim.id,
        offer_id=offer.id,
        diner_id=claim.diner_id,
        restaurant_id=offer.restaurant_id,
        original_amount_cents=original_amount_cents,
        discount_amount_cents=amounts["discount_amount_cents"],
        final_amount_cents=amounts["final_amount_cents"],
        platform_commission_cents=amounts["platform_commission_cents"],
        restaurant_payout_cents=amounts["restaurant_payout_cents"],
        currency="AUD",
        status=TransactionStatus.COMPLETED,
    )
    db.add(txn)
    db.flush()

    # $1 spent = 1 loyalty point, based on what the diner actually paid.
    dollars_paid = amounts["final_amount_cents"] // 100
    points = int(dollars_paid) * settings.LOYALTY_POINTS_PER_DOLLAR
    if points > 0:
        earn_points(db, claim.diner_id, points, reason=f"Purchase at offer {offer.title}", transaction_id=txn.id)

    db.commit()
    db.refresh(txn)
    return txn
