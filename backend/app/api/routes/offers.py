from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import require_restaurant
from app.db.session import get_db
from app.models.offer import Offer
from app.models.restaurant import Restaurant
from app.models.user import User
from app.schemas.offer import OfferCreateRequest, OfferUpdateRequest, OfferOut, OfferWithRestaurantOut
from app.services import offer_service, restaurant_service

router = APIRouter(prefix="/api/v1/offers", tags=["offers"])


def _to_discovery_out(offer: Offer, restaurant: Restaurant) -> OfferWithRestaurantOut:
    return OfferWithRestaurantOut(
        **OfferOut.model_validate(offer).model_dump(),
        restaurant_name=restaurant.name,
        restaurant_cuisine=restaurant.cuisine,
        restaurant_rating=float(restaurant.rating),
        restaurant_image_url=restaurant.image_url,
    )


@router.get("", response_model=list[OfferWithRestaurantOut])
def discover_offers(db: Session = Depends(get_db)):
    offers = offer_service.list_discoverable_offers(db)
    out = []
    for o in offers:
        restaurant = db.get(Restaurant, o.restaurant_id)
        if restaurant:
            out.append(_to_discovery_out(o, restaurant))
    return out


@router.get("/{offer_id}", response_model=OfferWithRestaurantOut)
def get_offer(offer_id: str, db: Session = Depends(get_db)):
    offer = db.get(Offer, offer_id)
    if offer is None:
        raise HTTPException(status_code=404, detail="Offer not found")
    restaurant = db.get(Restaurant, offer.restaurant_id)
    return _to_discovery_out(offer, restaurant)


@router.post("", response_model=OfferOut)
def create_offer(payload: OfferCreateRequest, user: User = Depends(require_restaurant), db: Session = Depends(get_db)):
    restaurant = restaurant_service.get_restaurant_for_owner(db, user.id)
    if restaurant is None:
        raise HTTPException(status_code=404, detail="No approved restaurant for this account")
    try:
        offer = offer_service.create_offer(db, restaurant.id, payload.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return offer


@router.get("/mine/list", response_model=list[OfferOut])
def my_offers(user: User = Depends(require_restaurant), db: Session = Depends(get_db)):
    restaurant = restaurant_service.get_restaurant_for_owner(db, user.id)
    if restaurant is None:
        raise HTTPException(status_code=404, detail="No approved restaurant for this account")
    return db.query(Offer).filter(Offer.restaurant_id == restaurant.id).all()


@router.patch("/{offer_id}", response_model=OfferOut)
def update_offer(offer_id: str, payload: OfferUpdateRequest, user: User = Depends(require_restaurant), db: Session = Depends(get_db)):
    restaurant = restaurant_service.get_restaurant_for_owner(db, user.id)
    offer = db.get(Offer, offer_id)
    if offer is None:
        raise HTTPException(status_code=404, detail="Offer not found")
    if restaurant is None or offer.restaurant_id != restaurant.id:
        raise HTTPException(status_code=403, detail="You can only manage your own restaurant's offers")
    try:
        offer = offer_service.update_offer(db, offer, payload.model_dump(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return offer
