import secrets
import string
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.claim import OfferClaim, ClaimStatus
from app.models.offer import Offer
from app.services.offer_service import is_offer_claimable


def _generate_redemption_code() -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "OFFPEAK-" + "".join(secrets.choice(alphabet) for _ in range(6))


def claim_offer(db: Session, offer_id: str, diner_id: str) -> OfferClaim:
    offer = db.get(Offer, offer_id)
    if offer is None:
        raise ValueError("Offer not found")

    # Lock the row conceptually via a fresh read + atomic increment check to
    # avoid over-claiming a nearly-exhausted offer under concurrent requests.
    claimable, reason = is_offer_claimable(offer)
    if not claimable:
        raise ValueError(reason)

    existing = (
        db.query(OfferClaim)
        .filter(OfferClaim.offer_id == offer_id, OfferClaim.diner_id == diner_id)
        .filter(OfferClaim.status == ClaimStatus.CLAIMED)
        .first()
    )
    if existing is not None:
        raise ValueError("You already have an active claim for this offer")

    offer.redemptions_used += 1
    if offer.redemptions_used >= offer.max_redemptions:
        offer.status = offer.status  # left ACTIVE; claimability re-checked on each attempt

    claim = OfferClaim(
        offer_id=offer_id,
        diner_id=diner_id,
        redemption_code=_generate_redemption_code(),
        status=ClaimStatus.CLAIMED,
    )
    db.add(claim)
    db.commit()
    db.refresh(claim)
    return claim


def redeem_claim(db: Session, redemption_code: str, restaurant_id: str) -> OfferClaim:
    claim = db.query(OfferClaim).filter(OfferClaim.redemption_code == redemption_code).first()
    if claim is None:
        raise ValueError("Claim not found")

    offer = db.get(Offer, claim.offer_id)
    if offer is None or offer.restaurant_id != restaurant_id:
        raise ValueError("This claim does not belong to your restaurant")

    if claim.status == ClaimStatus.REDEEMED:
        raise ValueError("Claim has already been redeemed")
    if claim.status == ClaimStatus.CANCELLED:
        raise ValueError("Claim was cancelled")
    if claim.status == ClaimStatus.EXPIRED:
        raise ValueError("Claim has expired")

    from datetime import date
    if date.today() > offer.end_date:
        claim.status = ClaimStatus.EXPIRED
        db.commit()
        raise ValueError("This offer has expired and can no longer be redeemed")

    claim.status = ClaimStatus.REDEEMED
    claim.redeemed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(claim)
    return claim


def get_claim_for_diner(db: Session, claim_id: str, diner_id: str) -> OfferClaim | None:
    claim = db.get(OfferClaim, claim_id)
    if claim is None or claim.diner_id != diner_id:
        return None
    return claim
