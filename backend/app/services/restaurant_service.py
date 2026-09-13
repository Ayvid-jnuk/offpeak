from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.admin_action import AdminAction
from app.models.restaurant import Restaurant, RestaurantApplication, ApplicationStatus
from app.models.user import User, UserRole
from app.core.security import hash_password


def submit_application(db: Session, data: dict) -> RestaurantApplication:
    # Create (or reuse) the restaurant-role account tied to this application.
    user = db.query(User).filter(User.email == data["account_email"]).first()
    if user is None:
        user = User(
            email=data["account_email"],
            hashed_password=hash_password(data["account_password"]),
            full_name=data["name"],
            role=UserRole.RESTAURANT,
        )
        db.add(user)
        db.flush()

    application = RestaurantApplication(
        applicant_user_id=user.id,
        name=data["name"],
        cuisine=data["cuisine"],
        address=data["address"],
        description=data["description"],
        phone=data["phone"],
        email=data["email"],
        opening_hours=data["opening_hours"],
        seating_capacity=data["seating_capacity"],
        image_url=data.get("image_url"),
        status=ApplicationStatus.PENDING,
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


def approve_application(db: Session, application_id: str, admin_id: str, notes: str | None) -> Restaurant:
    application = db.get(RestaurantApplication, application_id)
    if application is None:
        raise ValueError("Application not found")
    if application.status != ApplicationStatus.PENDING:
        raise ValueError("Application already reviewed")

    application.status = ApplicationStatus.APPROVED
    application.reviewed_by_admin_id = admin_id
    application.review_notes = notes
    application.reviewed_at = datetime.now(timezone.utc)

    restaurant = Restaurant(
        application_id=application.id,
        owner_user_id=application.applicant_user_id,
        name=application.name,
        cuisine=application.cuisine,
        address=application.address,
        description=application.description,
        phone=application.phone,
        email=application.email,
        opening_hours=application.opening_hours,
        seating_capacity=application.seating_capacity,
        image_url=application.image_url,
    )
    db.add(restaurant)

    db.add(AdminAction(
        admin_id=admin_id, action="APPROVE_APPLICATION",
        target_type="restaurant_application", target_id=application.id, notes=notes,
    ))
    db.commit()
    db.refresh(restaurant)
    return restaurant


def reject_application(db: Session, application_id: str, admin_id: str, notes: str | None) -> RestaurantApplication:
    application = db.get(RestaurantApplication, application_id)
    if application is None:
        raise ValueError("Application not found")
    if application.status != ApplicationStatus.PENDING:
        raise ValueError("Application already reviewed")

    application.status = ApplicationStatus.REJECTED
    application.reviewed_by_admin_id = admin_id
    application.review_notes = notes
    application.reviewed_at = datetime.now(timezone.utc)

    db.add(AdminAction(
        admin_id=admin_id, action="REJECT_APPLICATION",
        target_type="restaurant_application", target_id=application.id, notes=notes,
    ))
    db.commit()
    db.refresh(application)
    return application


def get_restaurant_for_owner(db: Session, owner_user_id: str) -> Restaurant | None:
    return db.query(Restaurant).filter(Restaurant.owner_user_id == owner_user_id).first()
