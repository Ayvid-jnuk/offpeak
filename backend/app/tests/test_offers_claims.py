from datetime import date, time, timedelta

import pytest

from app.models.restaurant import Restaurant
from app.models.user import User, UserRole
from app.services import offer_service, claim_service


def _make_restaurant(db):
    owner = User(email="owner@test.com", full_name="Owner", role=UserRole.RESTAURANT)
    db.add(owner)
    db.flush()
    restaurant = Restaurant(
        owner_user_id=owner.id, name="Test Bistro", cuisine="Test", address="1 Test St",
        description="Test", phone="123", email="r@test.com", opening_hours="9-5", seating_capacity=40,
    )
    db.add(restaurant)
    db.flush()
    return restaurant


def _make_diner(db, phone="+61499999999"):
    diner = User(phone_number=phone, full_name="Diner", role=UserRole.DINER)
    db.add(diner)
    db.flush()
    return diner


def _base_offer_data(**overrides):
    data = dict(
        title="Test Offer", description="desc", discount_percent=20,
        start_date=date.today(), end_date=date.today() + timedelta(days=7),
        start_time=time(14, 0), end_time=time(16, 0), max_redemptions=2,
    )
    data.update(overrides)
    return data


def test_create_offer_rejects_discount_over_100(db_session):
    restaurant = _make_restaurant(db_session)
    with pytest.raises(ValueError):
        offer_service.create_offer(db_session, restaurant.id, _base_offer_data(discount_percent=150))


def test_create_offer_rejects_end_before_start(db_session):
    restaurant = _make_restaurant(db_session)
    data = _base_offer_data(start_date=date.today() + timedelta(days=5), end_date=date.today())
    with pytest.raises(ValueError):
        offer_service.create_offer(db_session, restaurant.id, data)


def test_claiming_unavailable_offer_fails_when_exhausted(db_session):
    restaurant = _make_restaurant(db_session)
    offer = offer_service.create_offer(db_session, restaurant.id, _base_offer_data(max_redemptions=1))
    diner1 = _make_diner(db_session, "+61411111111")
    diner2 = _make_diner(db_session, "+61422222222")

    claim_service.claim_offer(db_session, offer.id, diner1.id)
    with pytest.raises(ValueError):
        claim_service.claim_offer(db_session, offer.id, diner2.id)


def test_cannot_claim_expired_offer(db_session):
    restaurant = _make_restaurant(db_session)
    offer = offer_service.create_offer(
        db_session, restaurant.id,
        _base_offer_data(start_date=date.today() - timedelta(days=10), end_date=date.today() - timedelta(days=1)),
    )
    diner = _make_diner(db_session)
    with pytest.raises(ValueError):
        claim_service.claim_offer(db_session, offer.id, diner.id)


def test_duplicate_active_claim_rejected(db_session):
    restaurant = _make_restaurant(db_session)
    offer = offer_service.create_offer(db_session, restaurant.id, _base_offer_data(max_redemptions=5))
    diner = _make_diner(db_session)
    claim_service.claim_offer(db_session, offer.id, diner.id)
    with pytest.raises(ValueError):
        claim_service.claim_offer(db_session, offer.id, diner.id)


def test_redeem_claim_success_and_duplicate_redemption_rejected(db_session):
    restaurant = _make_restaurant(db_session)
    offer = offer_service.create_offer(db_session, restaurant.id, _base_offer_data())
    diner = _make_diner(db_session)
    claim = claim_service.claim_offer(db_session, offer.id, diner.id)

    redeemed = claim_service.redeem_claim(db_session, claim.redemption_code, restaurant.id)
    assert redeemed.status.value == "REDEEMED"

    with pytest.raises(ValueError):
        claim_service.redeem_claim(db_session, claim.redemption_code, restaurant.id)


def test_redeeming_another_restaurants_claim_is_rejected(db_session):
    restaurant_a = _make_restaurant(db_session)

    owner_b = User(email="owner_b@test.com", full_name="Owner B", role=UserRole.RESTAURANT)
    db_session.add(owner_b)
    db_session.flush()
    restaurant_b = Restaurant(
        owner_user_id=owner_b.id, name="Other Bistro", cuisine="Test",
        address="2 Test St", description="Test", phone="456", email="r2@test.com",
        opening_hours="9-5", seating_capacity=30,
    )
    db_session.add(restaurant_b)
    db_session.flush()

    offer = offer_service.create_offer(db_session, restaurant_a.id, _base_offer_data())
    diner = _make_diner(db_session)
    claim = claim_service.claim_offer(db_session, offer.id, diner.id)

    with pytest.raises(ValueError):
        claim_service.redeem_claim(db_session, claim.redemption_code, restaurant_b.id)
