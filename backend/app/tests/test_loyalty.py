import pytest

from app.models.user import User, UserRole
from app.services import loyalty_service


def _make_diner(db):
    user = User(phone_number="+61400111222", full_name="Test Diner", role=UserRole.DINER)
    db.add(user)
    db.flush()
    return user


def test_earning_points_updates_balance_and_lifetime(db_session):
    diner = _make_diner(db_session)
    loyalty_service.earn_points(db_session, diner.id, 120, reason="Purchase")
    account = loyalty_service.ensure_loyalty_account(db_session, diner.id)
    assert account.points_balance == 120
    assert account.lifetime_points_earned == 120


def test_500_points_redeems_for_10_dollar_credit(db_session):
    diner = _make_diner(db_session)
    loyalty_service.earn_points(db_session, diner.id, 500, reason="Purchase")
    account = loyalty_service.redeem_points_for_credit(db_session, diner.id, 500)
    assert account.points_balance == 0
    assert account.credits_available_cents == 1000  # $10.00


def test_cannot_redeem_more_points_than_balance(db_session):
    diner = _make_diner(db_session)
    loyalty_service.earn_points(db_session, diner.id, 200, reason="Purchase")
    with pytest.raises(ValueError):
        loyalty_service.redeem_points_for_credit(db_session, diner.id, 500)


def test_cannot_redeem_non_multiple_of_500(db_session):
    diner = _make_diner(db_session)
    loyalty_service.earn_points(db_session, diner.id, 700, reason="Purchase")
    with pytest.raises(ValueError):
        loyalty_service.redeem_points_for_credit(db_session, diner.id, 300)


def test_cannot_earn_negative_points(db_session):
    diner = _make_diner(db_session)
    with pytest.raises(ValueError):
        loyalty_service.earn_points(db_session, diner.id, -50, reason="Bad")


def test_ledger_records_every_transaction(db_session):
    diner = _make_diner(db_session)
    loyalty_service.earn_points(db_session, diner.id, 500, reason="Purchase A")
    loyalty_service.earn_points(db_session, diner.id, 100, reason="Purchase B")
    loyalty_service.redeem_points_for_credit(db_session, diner.id, 500)
    account, activity = loyalty_service.get_account_with_activity(db_session, diner.id)
    assert len(activity) == 3
    assert account.points_balance == 100
