from datetime import date, timedelta

from app.models.restaurant import Restaurant
from app.models.metrics import RestaurantMetric
from app.models.user import User, UserRole
from app.services import recommendation_service


def _make_restaurant(db, capacity=50):
    owner = User(email="rec_owner@test.com", full_name="Owner", role=UserRole.RESTAURANT)
    db.add(owner)
    db.flush()
    restaurant = Restaurant(
        owner_user_id=owner.id, name="Rec Bistro", cuisine="Test", address="1 Test St",
        description="Test", phone="123", email="rec@test.com", opening_hours="9-5",
        seating_capacity=capacity,
    )
    db.add(restaurant)
    db.flush()
    return restaurant


def _add_metric(db, restaurant, day_of_week, hour, covers, capacity=50, days_ago=7):
    db.add(RestaurantMetric(
        restaurant_id=restaurant.id, date=date.today() - timedelta(days=days_ago),
        day_of_week=day_of_week, hour=hour, capacity=capacity, covers=covers,
        revenue_cents=covers * 3000, average_bill_cents=3000,
    ))


def test_no_data_returns_none(db_session):
    restaurant = _make_restaurant(db_session)
    rec = recommendation_service.generate_recommendation(db_session, restaurant.id)
    assert rec is None


def test_quiet_window_gets_recommended_discount(db_session):
    restaurant = _make_restaurant(db_session, capacity=50)
    # Tuesday 14:00 is consistently quiet (15% occupancy)
    for i in range(3):
        _add_metric(db_session, restaurant, day_of_week=1, hour=14, covers=8, days_ago=7 * (i + 1))
    # Every other slot is busy (80% occupancy)
    for i in range(3):
        _add_metric(db_session, restaurant, day_of_week=1, hour=19, covers=40, days_ago=7 * (i + 1))
    db_session.flush()

    rec = recommendation_service.generate_recommendation(db_session, restaurant.id)
    assert rec is not None
    assert rec.day_of_week == 1
    assert rec.window_start_hour == 14
    assert rec.recommended_discount_percent > 0
    assert rec.estimated_additional_covers >= 0
    assert rec.estimated_incremental_revenue_cents >= 0
    assert "Recommended discount" in rec.rationale


def test_healthy_occupancy_recommends_no_discount(db_session):
    restaurant = _make_restaurant(db_session, capacity=50)
    for i in range(3):
        _add_metric(db_session, restaurant, day_of_week=2, hour=13, covers=35, days_ago=7 * (i + 1))  # 70%
    db_session.flush()

    rec = recommendation_service.generate_recommendation(db_session, restaurant.id)
    assert rec is not None
    assert rec.recommended_discount_percent == 0
    assert "isn't recommended" in rec.rationale


def test_discount_never_exceeds_safeguard_ceiling(db_session):
    restaurant = _make_restaurant(db_session, capacity=50)
    for i in range(3):
        _add_metric(db_session, restaurant, day_of_week=3, hour=15, covers=2, days_ago=7 * (i + 1))  # 4%
    db_session.flush()

    rec = recommendation_service.generate_recommendation(db_session, restaurant.id)
    assert rec.recommended_discount_percent <= 30  # never an "obviously irrational" discount
