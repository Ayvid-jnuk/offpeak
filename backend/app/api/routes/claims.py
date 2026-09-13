from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import require_diner, require_restaurant
from app.db.session import get_db
from app.models.claim import OfferClaim
from app.models.user import User
from app.schemas.claim import ClaimOut, RedeemRequest
from app.services import claim_service, restaurant_service

router = APIRouter(prefix="/api/v1/claims", tags=["claims"])


@router.post("/offers/{offer_id}", response_model=ClaimOut)
def claim_offer(offer_id: str, user: User = Depends(require_diner), db: Session = Depends(get_db)):
    try:
        claim = claim_service.claim_offer(db, offer_id, user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return claim


@router.get("", response_model=list[ClaimOut])
def my_claims(user: User = Depends(require_diner), db: Session = Depends(get_db)):
    return db.query(OfferClaim).filter(OfferClaim.diner_id == user.id).order_by(OfferClaim.claimed_at.desc()).all()


@router.get("/{claim_id}", response_model=ClaimOut)
def get_claim(claim_id: str, user: User = Depends(require_diner), db: Session = Depends(get_db)):
    claim = claim_service.get_claim_for_diner(db, claim_id, user.id)
    if claim is None:
        raise HTTPException(status_code=404, detail="Claim not found")
    return claim


@router.post("/redeem", response_model=ClaimOut)
def redeem_claim(payload: RedeemRequest, user: User = Depends(require_restaurant), db: Session = Depends(get_db)):
    restaurant = restaurant_service.get_restaurant_for_owner(db, user.id)
    if restaurant is None:
        raise HTTPException(status_code=404, detail="No approved restaurant for this account")
    try:
        claim = claim_service.redeem_claim(db, payload.redemption_code, restaurant.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return claim


@router.get("/restaurant/list", response_model=list[ClaimOut])
def restaurant_claims(user: User = Depends(require_restaurant), db: Session = Depends(get_db)):
    """All claims across this restaurant's offers (for the redemption screen)."""
    from app.models.offer import Offer
    restaurant = restaurant_service.get_restaurant_for_owner(db, user.id)
    if restaurant is None:
        raise HTTPException(status_code=404, detail="No approved restaurant for this account")
    return (
        db.query(OfferClaim)
        .join(Offer, Offer.id == OfferClaim.offer_id)
        .filter(Offer.restaurant_id == restaurant.id)
        .order_by(OfferClaim.claimed_at.desc())
        .all()
    )
