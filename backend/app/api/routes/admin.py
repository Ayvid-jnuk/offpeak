from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.session import get_db
from app.models.restaurant import Restaurant, RestaurantApplication, ApplicationStatus
from app.models.claim import OfferClaim
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.restaurant import RestaurantApplicationOut, RestaurantOut, ApplicationReviewRequest
from app.services import restaurant_service, analytics_service

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.get("/applications", response_model=list[RestaurantApplicationOut])
def list_applications(status: str | None = None, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    q = db.query(RestaurantApplication)
    if status:
        try:
            q = q.filter(RestaurantApplication.status == ApplicationStatus(status))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status filter")
    return q.order_by(RestaurantApplication.created_at.desc()).all()


@router.post("/applications/{application_id}/approve", response_model=RestaurantOut)
def approve(application_id: str, payload: ApplicationReviewRequest, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    try:
        restaurant = restaurant_service.approve_application(db, application_id, admin.id, payload.notes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return restaurant


@router.post("/applications/{application_id}/reject", response_model=RestaurantApplicationOut)
def reject(application_id: str, payload: ApplicationReviewRequest, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    try:
        application = restaurant_service.reject_application(db, application_id, admin.id, payload.notes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return application


@router.get("/restaurants", response_model=list[RestaurantOut])
def list_restaurants(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    return db.query(Restaurant).all()


@router.get("/dashboard")
def dashboard(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    return analytics_service.admin_dashboard(db)


@router.get("/activity")
def activity(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    claims = db.query(OfferClaim).order_by(OfferClaim.claimed_at.desc()).limit(50).all()
    transactions = db.query(Transaction).order_by(Transaction.created_at.desc()).limit(50).all()
    return {
        "recent_claims": [
            {"id": c.id, "offer_id": c.offer_id, "status": c.status.value, "claimed_at": c.claimed_at}
            for c in claims
        ],
        "recent_transactions": [
            {
                "id": t.id, "final_amount_cents": t.final_amount_cents,
                "platform_commission_cents": t.platform_commission_cents,
                "status": t.status.value, "created_at": t.created_at,
            }
            for t in transactions
        ],
    }
