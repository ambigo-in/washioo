from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.role_dependencies import all_authenticated_users, require_roles
from schemas.rating_schema import (
    CleanerRatingSummary,
    CustomerRatingSummary,
    RatingCreateRequest,
    RatingResponse,
)
from services.rating_service import RatingService


router = APIRouter(tags=["Rating APIs"])


@router.post("/bookings/{booking_id}/ratings", response_model=RatingResponse, status_code=status.HTTP_201_CREATED)
def submit_booking_rating(
    booking_id: UUID,
    payload: RatingCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["customer", "cleaner"])),
):
    if payload.booking_id != booking_id:
        raise HTTPException(status_code=400, detail="Path booking_id and body booking_id must match.")

    reviewer_role = _current_booking_role_hint(current_user)
    return RatingService.submit_rating(db, booking_id, current_user.id, reviewer_role, payload)


@router.get("/bookings/{booking_id}/ratings", response_model=list[RatingResponse])
def get_booking_ratings(
    booking_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(all_authenticated_users),
):
    return RatingService.get_booking_ratings(db, booking_id, current_user)


@router.get("/cleaners/{cleaner_id}/ratings", response_model=CleanerRatingSummary)
def get_cleaner_ratings(
    cleaner_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin", "customer"])),
):
    return RatingService.get_cleaner_summary(db, cleaner_id)


@router.get("/customers/{customer_id}/ratings", response_model=CustomerRatingSummary)
def get_customer_ratings(
    customer_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin", "cleaner"])),
):
    return RatingService.get_customer_summary(db, customer_id)


@router.get("/admin/ratings")
def list_ratings_admin(
    reviewer_role: Literal["customer", "cleaner"] | None = Query(default=None),
    rating: int | None = Query(default=None, ge=1, le=5),
    booking_id: UUID | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_admin=Depends(require_roles(["admin"])),
):
    return RatingService.list_admin_ratings(db, reviewer_role, booking_id, page, limit, rating)


def _current_booking_role_hint(current_user) -> str:
    roles = {user_role.role.role_name for user_role in current_user.user_roles if user_role.role}
    if "customer" in roles:
        return "customer"
    return "cleaner"
