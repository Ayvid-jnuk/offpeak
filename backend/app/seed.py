"""
Seed the database with realistic demo data so the app looks alive
immediately: 5 restaurants (approved) + 1 pending application, historical
occupancy data, active + expired offers, a diner with loyalty history and
past transactions, and documented demo accounts.

Run with: python -m app.seed
"""
import random
from datetime import date, datetime, time, timedelta, timezone

from app.core.security import hash_password
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.claim import OfferClaim, ClaimStatus
from app.models.loyalty import LoyaltyAccount, LoyaltyTransaction, LoyaltyTxnType
from app.models.metrics import RestaurantMetric
from app.models.offer import Offer, OfferStatus
from app.models.restaurant import Restaurant, RestaurantApplication, ApplicationStatus
from app.models.transaction import Transaction, TransactionStatus
from app.models.user import User, UserRole

random.seed(42)

RESTAURANTS = [
    dict(name="Luna Bistro", cuisine="Italian", seating_capacity=60,
         address="12 Flinders Ln, Melbourne VIC", phone="+61 3 9000 1111",
         email="luna@offpeak.app", opening_hours="Mon-Sun 11:00-22:00",
         description="Neighbourhood Italian spot known for handmade pasta and a cosy dining room.",
         image_url="https://images.unsplash.com/photo-1517248135467-4c7edcad34c4"),
    dict(name="Sakura House", cuisine="Japanese", seating_capacity=45,
         address="88 Bourke St, Melbourne VIC", phone="+61 3 9000 2222",
         email="sakura@offpeak.app", opening_hours="Tue-Sun 11:30-21:30",
         description="Modern Japanese izakaya with a sushi counter and seasonal small plates.",
         image_url="https://images.unsplash.com/photo-1579584425555-c3ce17fd4351"),
    dict(name="Momo Corner", cuisine="Nepalese", seating_capacity=35,
         address="203 Swanston St, Melbourne VIC", phone="+61 3 9000 3333",
         email="momo@offpeak.app", opening_hours="Mon-Sun 10:00-21:00",
         description="Family-run Nepalese kitchen famous for steamed and pan-fried momo.",
         image_url="https://images.unsplash.com/photo-1585032226651-759b368d7246"),
    dict(name="The Green Table", cuisine="Vegetarian", seating_capacity=50,
         address="45 Chapel St, Melbourne VIC", phone="+61 3 9000 4444",
         email="greentable@offpeak.app", opening_hours="Mon-Sun 08:00-20:00",
         description="Plant-forward all-day menu built around seasonal produce.",
         image_url="https://images.unsplash.com/photo-1467003909585-2f8a72700288"),
    dict(name="Northside Grill", cuisine="American", seating_capacity=70,
         address="9 Lygon St, Melbourne VIC", phone="+61 3 9000 5555",
         email="northside@offpeak.app", opening_hours="Mon-Sun 11:00-23:00",
         description="Wood-fired grill, smash burgers and a full bar.",
         image_url="https://images.unsplash.com/photo-1414235077428-338989a2e8c0"),
]

PENDING_APPLICATION = dict(
    name="Harbor & Vine", cuisine="Seafood", seating_capacity=40,
    address="17 Dock Rd, Melbourne VIC", phone="+61 3 9000 6666",
    email="harborvine@offpeak.app", opening_hours="Wed-Sun 17:00-22:00",
    description="Waterfront seafood restaurant applying to join OffPeak.",
    image_url="https://images.unsplash.com/photo-1559339352-11d035aa65de",
)


def wipe_and_create_schema():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def seed_historical_metrics(db, restaurant: Restaurant, quiet_day: int, quiet_hours: range):
    """
    quiet_day: 0=Monday ... 6=Sunday. Generates 6 weeks of hourly snapshots
    for lunch (12-14) and dinner (18-21) service, with one deliberately
    quiet day/window so the recommendation engine has something to find.
    """
    service_hours = [12, 13, 18, 19, 20, 21]
    today = date.today()
    for week in range(6):
        for day_offset in range(7):
            d = today - timedelta(days=today.weekday()) - timedelta(weeks=week) + timedelta(days=day_offset)
            if d >= today:
                continue
            dow = d.weekday()
            for hour in service_hours:
                capacity = restaurant.seating_capacity
                if dow == quiet_day and hour in quiet_hours:
                    occupancy = random.uniform(0.15, 0.35)
                else:
                    occupancy = random.uniform(0.55, 0.95)
                covers = max(0, round(capacity * occupancy))
                avg_bill_cents = random.randint(2800, 5500)
                revenue_cents = covers * avg_bill_cents
                db.add(RestaurantMetric(
                    restaurant_id=restaurant.id, date=d, day_of_week=dow, hour=hour,
                    capacity=capacity, covers=covers, revenue_cents=revenue_cents,
                    average_bill_cents=avg_bill_cents,
                    weather_condition=random.choice(["clear", "rain", "cloudy"]),
                    event_flag=False,
                ))


def seed():
    wipe_and_create_schema()
    db = SessionLocal()
    try:
        # --- Admin ---
        admin = User(email="admin@offpeak.app", hashed_password=hash_password("demo1234"),
                     full_name="OffPeak Admin", role=UserRole.ADMIN)
        db.add(admin)
        db.flush()

        # --- Demo diner (phone-based, pre-verified for convenience) ---
        diner = User(phone_number="+61400000000", email="demo@offpeak.app",
                     full_name="Demo Diner", role=UserRole.DINER, is_phone_verified=True)
        db.add(diner)
        db.flush()
        loyalty = LoyaltyAccount(diner_id=diner.id, points_balance=340, lifetime_points_earned=340)
        db.add(loyalty)
        db.flush()
        db.add(LoyaltyTransaction(loyalty_account_id=loyalty.id, type=LoyaltyTxnType.EARNED,
                                   points=340, reason="Seeded historical purchases"))

        # --- Restaurants (approved) ---
        restaurants = []
        for i, r in enumerate(RESTAURANTS):
            owner = User(email=r["email"], hashed_password=hash_password("demo1234"),
                         full_name=f"{r['name']} Owner", role=UserRole.RESTAURANT)
            db.add(owner)
            db.flush()

            application = RestaurantApplication(
                applicant_user_id=owner.id, name=r["name"], cuisine=r["cuisine"],
                address=r["address"], description=r["description"], phone=r["phone"],
                email=r["email"], opening_hours=r["opening_hours"],
                seating_capacity=r["seating_capacity"], image_url=r["image_url"],
                status=ApplicationStatus.APPROVED,
                reviewed_by_admin_id=admin.id, reviewed_at=datetime.now(timezone.utc),
            )
            db.add(application)
            db.flush()

            restaurant = Restaurant(
                application_id=application.id, owner_user_id=owner.id,
                name=r["name"], cuisine=r["cuisine"], address=r["address"],
                description=r["description"], phone=r["phone"], email=r["email"],
                opening_hours=r["opening_hours"], seating_capacity=r["seating_capacity"],
                image_url=r["image_url"], rating=round(random.uniform(4.2, 4.9), 1),
            )
            db.add(restaurant)
            db.flush()
            restaurants.append(restaurant)

            quiet_day = i  # each restaurant gets a different quiet day, Mon..Fri
            seed_historical_metrics(db, restaurant, quiet_day=quiet_day % 5, quiet_hours=range(13, 16))

        db.flush()

        # --- Pending application (Harbor & Vine) ---
        pending_owner = User(email=PENDING_APPLICATION["email"], hashed_password=hash_password("demo1234"),
                              full_name="Harbor & Vine Owner", role=UserRole.RESTAURANT)
        db.add(pending_owner)
        db.flush()
        db.add(RestaurantApplication(
            applicant_user_id=pending_owner.id, status=ApplicationStatus.PENDING,
            **PENDING_APPLICATION,
        ))

        # --- Offers: an active one on Luna Bistro (today, so the demo has
        #     something claimable immediately) + an expired one on Sakura ---
        luna = restaurants[0]
        active_offer = Offer(
            restaurant_id=luna.id, title="Luna Bistro: Afternoon Pasta Special",
            description="20% off all pasta dishes during our quiet afternoon window.",
            discount_percent=20, start_date=date.today(), end_date=date.today() + timedelta(days=7),
            start_time=time(14, 0), end_time=time(16, 30), max_redemptions=30, redemptions_used=3,
            status=OfferStatus.ACTIVE,
        )
        db.add(active_offer)

        sakura = restaurants[1]
        expired_offer = Offer(
            restaurant_id=sakura.id, title="Sakura House: Early Bird Set Menu",
            description="15% off the set menu before 6pm.",
            discount_percent=15, start_date=date.today() - timedelta(days=20),
            end_date=date.today() - timedelta(days=5),
            start_time=time(17, 0), end_time=time(18, 0), max_redemptions=15, redemptions_used=15,
            status=OfferStatus.EXPIRED,
        )
        db.add(expired_offer)
        db.flush()

        # --- Sample claim + transaction history for the demo diner ---
        past_claim = OfferClaim(
            offer_id=expired_offer.id, diner_id=diner.id, redemption_code="OFFPEAK-DEMO01",
            status=ClaimStatus.REDEEMED, redeemed_at=datetime.now(timezone.utc) - timedelta(days=6),
        )
        db.add(past_claim)
        db.flush()

        txn = Transaction(
            claim_id=past_claim.id, offer_id=expired_offer.id, diner_id=diner.id,
            restaurant_id=sakura.id, original_amount_cents=9000, discount_amount_cents=1350,
            final_amount_cents=7650, platform_commission_cents=765, restaurant_payout_cents=6885,
            currency="AUD", status=TransactionStatus.COMPLETED,
        )
        db.add(txn)

        db.commit()
        print("Seed complete.")
        print(f"  Restaurants: {len(restaurants)} approved, 1 pending (Harbor & Vine)")
        print(f"  Active offer: {active_offer.title} ({active_offer.id})")
        print(f"  Demo diner phone: +61400000000  |  static OTP: 123456")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
