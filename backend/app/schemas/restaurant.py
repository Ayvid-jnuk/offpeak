from datetime import datetime
from pydantic import BaseModel, EmailStr


class RestaurantApplyRequest(BaseModel):
    name: str
    cuisine: str
    address: str
    description: str
    phone: str
    email: EmailStr
    opening_hours: str
    seating_capacity: int
    image_url: str | None = None
    # applicant credentials (creates the restaurant-role user)
    account_email: EmailStr
    account_password: str


class RestaurantApplicationOut(BaseModel):
    id: str
    name: str
    cuisine: str
    address: str
    description: str
    phone: str
    email: str
    opening_hours: str
    seating_capacity: int
    image_url: str | None
    status: str
    created_at: datetime
    reviewed_at: datetime | None

    class Config:
        from_attributes = True


class RestaurantOut(BaseModel):
    id: str
    name: str
    cuisine: str
    address: str
    description: str
    phone: str
    email: str
    opening_hours: str
    seating_capacity: int
    image_url: str | None
    rating: float
    is_active: bool

    class Config:
        from_attributes = True


class ApplicationReviewRequest(BaseModel):
    notes: str | None = None
