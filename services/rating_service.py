from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from models.booking import Booking
from models.booking_assignment import BookingAssignment
from models.cleaner_profile import CleanerProfile
from models.rating import Rating
from models.user import User


BLIND_REVIEW_MODE = True


class RatingService:
    @staticmethod
    def submit_rating(db: Session, booking_id: UUID, reviewer_id: UUID, reviewer_role: str, data):
        booking = _get_booking(db, booking_id)
        if booking.booking_status != "completed":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only completed bookings can be rated.",
            )

        resolved_role, reviewee_id = _resolve_reviewer_and_reviewee(booking, reviewer_id)
        reviewer_role = resolved_role
        if reviewer_id == reviewee_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Reviewer cannot rate themselves.")

        duplicate = (
            db.query(Rating)
            .filter(Rating.booking_id == booking_id, Rating.reviewer_id == reviewer_id)
            .first()
        )
        if duplicate:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You have already rated this booking.")

        rating = Rating(
            booking_id=booking_id,
            reviewer_id=reviewer_id,
            reviewee_id=reviewee_id,
            reviewer_role=reviewer_role,
            rating=Decimal(str(data.rating)),
            comment=data.comment,
        )

        try:
            db.add(rating)
            db.flush()
            _recalculate_reviewee_rating(db, reviewee_id, reviewer_role)
            db.commit()
            db.refresh(rating)
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You have already rated this booking.")
        except Exception:
            db.rollback()
            raise

        return _format_rating(rating)

    @staticmethod
    def get_booking_ratings(db: Session, booking_id: UUID, requesting_user):
        booking = _get_booking(db, booking_id)
        roles = _role_names(requesting_user)

        if "admin" not in roles:
            _assert_booking_member(booking, requesting_user.id)
            if BLIND_REVIEW_MODE:
                own_rating = (
                    db.query(Rating)
                    .filter(Rating.booking_id == booking_id, Rating.reviewer_id == requesting_user.id)
                    .first()
                )
                if not own_rating:
                    return []

        ratings = (
            db.query(Rating)
            .options(joinedload(Rating.reviewee))
            .filter(Rating.booking_id == booking_id)
            .order_by(Rating.created_at.asc())
            .all()
        )
        return [_format_rating(rating) for rating in ratings]

    @staticmethod
    def get_cleaner_summary(db: Session, cleaner_id: UUID):
        cleaner = db.query(CleanerProfile).options(joinedload(CleanerProfile.user)).filter(CleanerProfile.id == cleaner_id).first()
        if not cleaner:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cleaner profile not found")

        recent_ratings = (
            db.query(Rating)
            .options(joinedload(Rating.reviewee))
            .filter(Rating.reviewee_id == cleaner.user_id, Rating.reviewer_role == "customer")
            .order_by(Rating.created_at.desc())
            .limit(5)
            .all()
        )
        return {
            "average_rating": float(cleaner.average_rating or 0),
            "total_ratings": cleaner.total_ratings or 0,
            "recent_reviews": [_format_rating(rating) for rating in recent_ratings],
        }

    @staticmethod
    def get_customer_summary(db: Session, customer_id: UUID):
        customer = db.query(User).filter(User.id == customer_id).first()
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

        return {
            "average_rating": float(customer.average_rating or 0),
            "total_ratings": customer.total_ratings or 0,
        }

    @staticmethod
    def list_admin_ratings(
        db: Session,
        reviewer_role: str | None = None,
        booking_id: UUID | None = None,
        page: int = 1,
        limit: int = 50,
        rating: int | None = None,
    ):
        query = db.query(Rating).options(joinedload(Rating.reviewee))
        if reviewer_role:
            query = query.filter(Rating.reviewer_role == reviewer_role)
        if booking_id:
            query = query.filter(Rating.booking_id == booking_id)
        if rating:
            query = query.filter(Rating.rating == rating)

        total = query.count()
        ratings = (
            query.order_by(Rating.created_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )
        return {
            "ratings": [_format_rating(rating) for rating in ratings],
            "total": total,
            "page": page,
            "limit": limit,
        }


def _get_booking(db: Session, booking_id: UUID) -> Booking:
    booking = (
        db.query(Booking)
        .options(
            joinedload(Booking.assignment)
            .joinedload(BookingAssignment.cleaner)
            .joinedload(CleanerProfile.user)
        )
        .filter(Booking.id == booking_id)
        .first()
    )
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    return booking


def _resolve_reviewer_and_reviewee(booking: Booking, reviewer_id: UUID) -> tuple[str, UUID]:
    cleaner_user_id = _booking_cleaner_user_id(booking)

    if booking.customer_id == reviewer_id:
        if not cleaner_user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Booking does not have an assigned cleaner.")
        return "customer", cleaner_user_id

    if cleaner_user_id == reviewer_id:
        return "cleaner", booking.customer_id

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Reviewer is not part of this booking.")


def _assert_booking_member(booking: Booking, user_id: UUID) -> None:
    cleaner_user_id = _booking_cleaner_user_id(booking)
    if booking.customer_id != user_id and cleaner_user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to view ratings for this booking.")


def _booking_cleaner_user_id(booking: Booking) -> UUID | None:
    if not booking.assignment or not booking.assignment.cleaner:
        return None
    return booking.assignment.cleaner.user_id


def _recalculate_reviewee_rating(db: Session, reviewee_id: UUID, reviewer_role: str) -> None:
    rating_role_filter = "customer" if reviewer_role == "customer" else "cleaner"
    average_rating, total_ratings = (
        db.query(func.coalesce(func.avg(Rating.rating), 0), func.count(Rating.id))
        .filter(Rating.reviewee_id == reviewee_id, Rating.reviewer_role == rating_role_filter)
        .one()
    )

    rounded_average = round(float(average_rating or 0), 2)
    total_ratings = int(total_ratings or 0)

    if reviewer_role == "customer":
        cleaner = db.query(CleanerProfile).filter(CleanerProfile.user_id == reviewee_id).first()
        if cleaner:
            cleaner.average_rating = rounded_average
            cleaner.total_ratings = total_ratings
            cleaner.rating = rounded_average
    else:
        customer = db.query(User).filter(User.id == reviewee_id).first()
        if customer:
            customer.average_rating = rounded_average
            customer.total_ratings = total_ratings


def _format_rating(rating: Rating) -> dict:
    return {
        "id": rating.id,
        "booking_id": rating.booking_id,
        "reviewer_role": rating.reviewer_role,
        "rating": float(rating.rating),
        "comment": rating.comment,
        "created_at": rating.created_at,
        "reviewee_name": rating.reviewee.full_name if rating.reviewee else None,
    }


def _role_names(user) -> set[str]:
    return {user_role.role.role_name for user_role in user.user_roles if user_role.role}
