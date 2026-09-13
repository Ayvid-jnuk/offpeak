# OffPeak

**Turn quiet tables into revenue.**

A restaurant revenue-intelligence platform and off-peak marketplace, built for
the hackathon brief. Restaurants apply and get approved by an admin, a
transparent (non-ML) recommendation engine finds each restaurant's quietest
historical window and suggests a discount, restaurants publish that
recommendation as a real offer in one click, diners discover and claim it,
restaurants redeem the claim, diners pay through a simulated checkout, and
the platform takes a 10% commission with the rest going to the restaurant —
plus loyalty points for the diner.

The marketplace is the mechanism; the revenue intelligence is the
differentiator.

## Tech stack

- **Backend:** Python 3.12, FastAPI, SQLAlchemy 2 (service-layer
  architecture), PostgreSQL, Alembic migrations, JWT auth, pytest.
- **Frontend:** Next.js 16 (App Router), TypeScript, Tailwind CSS 4, one
  responsive web app with role-based routing (no separate apps per role).

## Project structure

```
offpeak/
  backend/
    app/
      main.py                 FastAPI app + router wiring
      core/                    config, security (JWT/password hashing)
      db/                      SQLAlchemy session/base
      models/                  ORM models (users, restaurants, offers, ...)
      schemas/                 Pydantic request/response models
      services/                business logic (one file per domain)
      api/routes/               thin route handlers calling into services
      tests/                   pytest suite (SQLite in-memory, isolated)
      seed.py                  demo data generator
    migrations/                Alembic
    requirements.txt
    .env.example
    e2e_test.sh                scripted full-journey smoke test (curl)
  frontend/
    app/
      page.tsx                 landing page
      login/, signup/          auth
      diner/                   mobile-first diner app (discover, claims, wallet, profile)
      restaurant/
        application/           public application form
        (app)/                 role-gated: dashboard, offers, analytics
      admin/
        (app)/                 role-gated: dashboard, applications, restaurants, activity
    lib/                       API client, types, auth context
    components/ui.tsx          shared UI primitives
```

## Running it

### Backend

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate   # optional
pip install -r requirements.txt

# Postgres must be running and reachable at the DATABASE_URL in .env
# (see .env.example — copy it to .env and adjust if needed)
createdb offpeak   # if it doesn't exist yet

alembic upgrade head
python -m app.seed              # wipes and re-seeds demo data
uvicorn app.main:app --reload --port 8000
```

API docs: `http://localhost:8000/docs`

Run the test suite (fast, isolated, no Postgres needed):

```bash
pytest app/tests/ -v
```

Run the scripted end-to-end journey against a live server:

```bash
bash e2e_test.sh
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local   # points at http://localhost:8000/api/v1 by default
npm run dev                  # http://localhost:3000
```

## Demo accounts

| Role | Login | Password / code |
|---|---|---|
| Admin | admin@offpeak.app | demo1234 |
| Restaurant (Luna Bistro) | luna@offpeak.app | demo1234 |
| Restaurant (Sakura House) | sakura@offpeak.app | demo1234 |
| Diner | phone +61400000000 | OTP: `123456` (dev mode, shown in the UI) |

Restaurant accounts also exist for Momo Corner, The Green Table, and
Northside Grill (`momo@`, `greentable@`, `northside@offpeak.app`, same
password). A sixth restaurant, **Harbor & Vine**, is seeded as a **pending**
application for the admin-approval step of the demo.

## What's genuinely functional

- Full auth: phone + simulated OTP for diners, email + password (bcrypt
  hashed) for restaurant/admin, JWT with role-based route guards.
- Restaurant application → admin review → approval/rejection, with an audit
  log (`admin_actions`).
- The revenue intelligence engine: buckets seeded hourly occupancy data by
  day-of-week/hour, finds the quietest statistically-meaningful window, maps
  occupancy to a discount band (0/12/20/28%), and estimates additional
  covers and incremental revenue from a documented, conservative demand-lift
  assumption. Every number in the "Today's Opportunity" card comes from this
  engine, not a placeholder.
- The recommendation → **"Create recommended offer"** button creates a real
  `Offer` row pre-filled from the recommendation, and the offer's
  `source_recommendation_id` lets analytics trace the connection.
- Offer creation/validation, discovery, claiming, redemption codes (with a
  QR code), redemption, simulated checkout with exact commission math
  (`Decimal`, integer cents — never floats), and an append-only loyalty
  ledger (`loyalty_accounts` + `loyalty_transactions`), including 500-point
  → $10 credit redemption.
- Enforced rules: no claiming an exhausted/expired offer, no duplicate
  active claim, no double redemption, no redeeming another restaurant's
  claim, no negative amounts/commission/payout, discount bounded to 0–100%,
  restaurant/diner data isolation.
- Restaurant analytics and an admin operations dashboard, both computed live
  from the same transaction/claim data the diner and restaurant flows
  produce (not a separate mocked page).

## What's simulated (and clearly so)

- **SMS delivery** — OTPs are generated server-side and returned directly in
  the API response in dev mode (`OTP_DEV_MODE=true`), shown in the login UI.
  No Twilio or paid SMS provider required. Swappable behind
  `app/services/auth_service.py`.
- **Payment settlement** — checkout computes and records the real commission
  split but doesn't move real money; no Stripe/payment processor is wired
  up. Swappable behind `app/services/transaction_service.py`.
- **Historical restaurant data** — the 6 weeks of hourly occupancy/revenue
  per restaurant used by the recommendation engine is seeded, not pulled
  from a real POS. The engine's logic operates on that data exactly as it
  would on real data.

## Tests

```
23 passed in app/tests/
```

Covering: exact commission math (the $120/25%/$90/$9/$81 spec example),
commission+payout always summing to the final amount, no negative
amounts across a discount/amount sweep, loyalty earn/redeem/ledger
integrity, the 500-point redemption rule, offer validity/date bounds,
claim exhaustion, expired-offer claiming, duplicate active claims, double
redemption, cross-restaurant redemption isolation, and the recommendation
engine (no-data case, quiet-window detection, healthy-occupancy → no
discount, and a ceiling that keeps discounts non-irrational).

## The 3-minute demo flow

1. **0:00** — "Restaurants lose money when tables sit empty." Show the
   landing page.
2. **0:20** — Log in as admin, approve the pending Harbor & Vine
   application.
3. **0:40** — Log in as Luna Bistro. Dashboard shows **Today's
   Opportunity**: Monday 13:00–15:00, 27% historical occupancy, 28%
   recommended discount, estimated additional covers and revenue.
4. **1:20** — Click **Create recommended offer** — it publishes
   immediately, pre-filled from the recommendation.
5. **1:30** — Switch to the diner app (phone `+61400000000`, OTP
   `123456`). Discover shows Luna Bistro's live offer.
6. **1:45** — Claim it — get a redemption code + QR.
7. **2:00** — Back in the restaurant view, redeem the code.
8. **2:15** — Diner completes checkout: enter a $120 bill.
9. **2:25** — Show the breakdown: **-$24 discount → $96 paid → $9.60
   commission → $86.40 to the restaurant → points added to the wallet.**
10. **2:40** — Restaurant analytics: redemption rate, unused capacity,
    best-performing window.
11. **2:50** — "We don't just help restaurants discount empty tables. We
    help them turn unused capacity into predictable revenue."

## Next 3 highest-value improvements

1. **Real-time demand signals** — blend live weather/event data into the
   recommendation engine (the schema already carries `weather_condition`
   and `event_flag` per metric row; today only occupancy is used).
2. **Multi-window recommendations** — currently one quietest window per
   run; ranking the top 2–3 windows would let a restaurant run a small
   portfolio of off-peak offers instead of just one.
3. **Real payment + SMS integration** — swap the two documented seams
   (`transaction_service.checkout`, `auth_service.send_otp`) for Stripe test
   mode and a real SMS provider without touching any other business logic,
   since both are already isolated behind a single function each.

## Known limitations

- The recommendation engine requires at least 2 historical samples per
  hour-bucket to consider it meaningful (`MIN_SAMPLES` in
  `recommendation_service.py`); a brand-new restaurant with no metrics
  yet will see "not enough historical data."
- No pagination on list endpoints — fine at hackathon seed-data scale, not
  meant for production volume.
- The frontend restaurant offer detail/edit page (viewing a single offer)
  isn't built; offers can be created, listed, and activated/deactivated,
  which covers the required journey.
