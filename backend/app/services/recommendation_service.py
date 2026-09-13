"""
Revenue Intelligence engine.

Deliberately NOT a machine-learning model — a transparent, auditable set of
rules over the seeded historical `restaurant_metrics` data. This keeps the
"why" explainable to a restaurant owner, and keeps the core recommendation
flow fully functional with zero dependency on an external AI API.

Algorithm summary:
  1. Group historical hourly snapshots by (day_of_week, hour).
  2. For each bucket, compute average occupancy = covers / capacity.
  3. Find the bucket(s) with the lowest sustained occupancy that still has
     enough historical data points to be meaningful (>= MIN_SAMPLES).
  4. Map occupancy band -> recommended discount using a fixed table.
  5. Estimate additional covers and incremental revenue from the discount's
     expected demand lift (a conservative, documented assumption — not a
     guarantee).
"""
from collections import defaultdict
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.metrics import RestaurantMetric
from app.models.recommendation import RevenueRecommendation
from app.models.restaurant import Restaurant

MIN_SAMPLES = 2
DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Conservative, documented assumption: a discount lifts covers roughly in
# proportion to its size, capped so estimates stay plausible for a prototype.
DEMAND_LIFT_PER_DISCOUNT_POINT = 0.9  # e.g. 20% discount -> ~18% more covers in that window


def _discount_for_occupancy(occupancy_pct: float) -> int:
    if occupancy_pct < 30:
        return 28
    if occupancy_pct < 45:
        return 20
    if occupancy_pct < 60:
        return 12
    return 0


def generate_recommendation(db: Session, restaurant_id: str) -> RevenueRecommendation | None:
    restaurant = db.get(Restaurant, restaurant_id)
    if restaurant is None:
        raise ValueError("Restaurant not found")

    rows = db.query(RestaurantMetric).filter(RestaurantMetric.restaurant_id == restaurant_id).all()
    if not rows:
        return None

    buckets: dict[tuple[int, int], list[RestaurantMetric]] = defaultdict(list)
    for row in rows:
        buckets[(row.day_of_week, row.hour)].append(row)

    scored = []
    for (dow, hour), items in buckets.items():
        if len(items) < MIN_SAMPLES:
            continue
        avg_occupancy = sum((i.covers / i.capacity) for i in items) / len(items) * 100
        avg_capacity = sum(i.capacity for i in items) / len(items)
        avg_covers = sum(i.covers for i in items) / len(items)
        scored.append({
            "day_of_week": dow,
            "hour": hour,
            "occupancy_pct": avg_occupancy,
            "capacity": avg_capacity,
            "covers": avg_covers,
        })

    if not scored:
        return None

    # Quietest bucket = lowest average occupancy.
    quietest = min(scored, key=lambda s: s["occupancy_pct"])

    discount = _discount_for_occupancy(quietest["occupancy_pct"])
    if discount == 0:
        rationale = (
            f"{DAY_NAMES[quietest['day_of_week']]} {quietest['hour']:02d}:00 is your quietest "
            f"tracked window, but average occupancy ({quietest['occupancy_pct']:.0f}%) is already "
            "healthy enough that a discount isn't recommended right now."
        )
        available_capacity = max(0, int(quietest["capacity"] - quietest["covers"]))
        additional_covers = 0
        incremental_revenue_cents = 0
    else:
        available_capacity = max(0, int(quietest["capacity"] - quietest["covers"]))
        lift_fraction = min(discount * DEMAND_LIFT_PER_DISCOUNT_POINT / 100, 1.0)
        additional_covers = min(available_capacity, round(quietest["covers"] * lift_fraction))
        # Estimate revenue from additional covers at the restaurant's
        # observed average bill, net of the discount being offered.
        avg_bill_cents = _average_bill_cents(rows)
        gross_extra_cents = additional_covers * avg_bill_cents
        incremental_revenue_cents = round(gross_extra_cents * (1 - discount / 100))
        rationale = (
            f"{DAY_NAMES[quietest['day_of_week']]} {quietest['hour']:02d}:00 is historically your "
            f"quietest period. Average occupancy: {quietest['occupancy_pct']:.0f}%. "
            f"Recommended discount: {discount}%. Estimated additional covers: +{additional_covers}. "
            f"Estimated incremental revenue: +${incremental_revenue_cents / 100:.0f}."
        )

    rec = RevenueRecommendation(
        restaurant_id=restaurant_id,
        day_of_week=quietest["day_of_week"],
        window_start_hour=quietest["hour"],
        window_end_hour=min(quietest["hour"] + 2, 23),
        historical_occupancy_pct=round(quietest["occupancy_pct"], 2),
        available_capacity=available_capacity,
        recommended_discount_percent=discount,
        estimated_additional_covers=additional_covers,
        estimated_incremental_revenue_cents=incremental_revenue_cents,
        rationale=rationale,
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


def _average_bill_cents(rows: list[RestaurantMetric]) -> int:
    non_zero = [r.average_bill_cents for r in rows if r.average_bill_cents > 0]
    if not non_zero:
        return 3500
    return round(sum(non_zero) / len(non_zero))


def get_latest_recommendation(db: Session, restaurant_id: str) -> RevenueRecommendation | None:
    return (
        db.query(RevenueRecommendation)
        .filter(RevenueRecommendation.restaurant_id == restaurant_id)
        .order_by(RevenueRecommendation.created_at.desc())
        .first()
    )
