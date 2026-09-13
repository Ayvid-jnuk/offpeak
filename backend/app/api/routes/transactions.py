from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import require_diner
from app.db.session import get_db
from app.models.claim import OfferClaim, ClaimStatus
from app.models.offer import Offer
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.transaction import CheckoutRequest, TransactionOut
from app.services import transaction_service

router = APIRouter(prefix="/api/v1/transactions", tags=["transactions"])


@router.post("", response_model=TransactionOut)
def checkout(payload: CheckoutRequest, user: User = Depends(require_diner), db: Session = Depends(get_db)):
    claim = db.get(OfferClaim, payload.claim_id)
    if claim is None or claim.diner_id != user.id:
        raise HTTPException(status_code=404, detail="Claim not found")
    if claim.status != ClaimStatus.REDEEMED:
        raise HTTPException(status_code=400, detail="Claim must be redeemed by the restaurant before checkout")

    offer = db.get(Offer, claim.offer_id)
    try:
        txn = transaction_service.checkout(db, claim, offer, payload.original_amount_cents)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return txn


@router.get("/{transaction_id}", response_model=TransactionOut)
def get_transaction(transaction_id: str, user: User = Depends(require_diner), db: Session = Depends(get_db)):
    txn = db.get(Transaction, transaction_id)
    if txn is None or txn.diner_id != user.id:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return txn
