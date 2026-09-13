from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.loyalty import LoyaltyAccount, LoyaltyTransaction, LoyaltyTxnType


def ensure_loyalty_account(db: Session, diner_id: str) -> LoyaltyAccount:
    account = db.query(LoyaltyAccount).filter(LoyaltyAccount.diner_id == diner_id).first()
    if account is None:
        account = LoyaltyAccount(diner_id=diner_id)
        db.add(account)
        db.flush()
    return account


def earn_points(db: Session, diner_id: str, points: int, reason: str, transaction_id: str | None = None) -> LoyaltyAccount:
    if points < 0:
        raise ValueError("Cannot earn a negative number of points")
    account = ensure_loyalty_account(db, diner_id)
    account.points_balance += points
    account.lifetime_points_earned += points
    db.add(LoyaltyTransaction(
        loyalty_account_id=account.id, type=LoyaltyTxnType.EARNED,
        points=points, reason=reason, transaction_id=transaction_id,
    ))
    db.flush()
    return account


def redeem_points_for_credit(db: Session, diner_id: str, points: int) -> LoyaltyAccount:
    if points <= 0:
        raise ValueError("Points to redeem must be positive")
    if points % settings.LOYALTY_POINTS_PER_CREDIT != 0:
        raise ValueError(f"Points must be redeemed in multiples of {settings.LOYALTY_POINTS_PER_CREDIT}")

    account = ensure_loyalty_account(db, diner_id)
    if account.points_balance < points:
        raise ValueError("Insufficient points balance")

    credits_units = points // settings.LOYALTY_POINTS_PER_CREDIT
    credit_cents = credits_units * settings.LOYALTY_CREDIT_VALUE_CENTS

    account.points_balance -= points
    account.credits_available_cents += credit_cents

    db.add(LoyaltyTransaction(
        loyalty_account_id=account.id, type=LoyaltyTxnType.REDEEMED,
        points=-points, reason=f"Redeemed for ${credit_cents / 100:.2f} platform credit",
    ))
    db.commit()
    db.refresh(account)
    return account


def get_account_with_activity(db: Session, diner_id: str, limit: int = 20) -> tuple[LoyaltyAccount, list[LoyaltyTransaction]]:
    account = ensure_loyalty_account(db, diner_id)
    db.commit()
    activity = (
        db.query(LoyaltyTransaction)
        .filter(LoyaltyTransaction.loyalty_account_id == account.id)
        .order_by(LoyaltyTransaction.created_at.desc())
        .limit(limit)
        .all()
    )
    return account, activity
