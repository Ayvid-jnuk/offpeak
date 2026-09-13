from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_restaurant
from app.db.session import get_db
from app.models.restaurant import Restaurant
from app.models.user import User
from app.schemas.restaurant import RestaurantApplyRequest, RestaurantApplicationOut, RestaurantOut
from app.services import restaurant_service, analytics_service

router = APIRouter(prefix="/api/v1/restaurants", tags=["restaurants"])


@router.get("", response_model=list[RestaurantOut])
def list_restaurants(db: Session = Depends(get_db)):
    return db.query(Restaurant).filter(Restaurant.is_active == True).all()  # noqa: E712


@router.get("/{restaurant_id}", response_model=RestaurantOut)
def get_restaurant(restaurant_id: str, db: Session = Depends(get_db)):
    restaurant = db.get(Restaurant, restaurant_id)
    if restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant


@router.post("/apply", response_model=RestaurantApplicationOut)
def apply(payload: RestaurantApplyRequest, db: Session = Depends(get_db)):
    application = restaurant_service.submit_application(db, payload.model_dump())
    return application


@router.get("/me/profile", response_model=RestaurantOut)
def my_restaurant(user: User = Depends(require_restaurant), db: Session = Depends(get_db)):
    restaurant = restaurant_service.get_restaurant_for_owner(db, user.id)
    if restaurant is None:
        raise HTTPException(status_code=404, detail="No approved restaurant for this account yet")
    return restaurant


@router.get("/me/analytics")
def my_analytics(user: User = Depends(require_restaurant), db: Session = Depends(get_db)):
    restaurant = restaurant_service.get_restaurant_for_owner(db, user.id)
    if restaurant is None:
        raise HTTPException(status_code=404, detail="No approved restaurant for this account yet")
    return analytics_service.restaurant_analytics(db, restaurant.id)
