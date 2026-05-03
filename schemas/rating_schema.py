from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class RatingCreateRequest(BaseModel):
    booking_id: UUID
    rating: float = Field(..., ge=1, le=5)
    comment: str | None = Field(default=None, max_length=500)

    @field_validator("rating")
    @classmethod
    def rating_must_have_at_most_one_decimal(cls, value: float) -> float:
        decimal_value = Decimal(str(value))
        if decimal_value.as_tuple().exponent < -1:
            raise ValueError("Rating can have at most one decimal place")
        return value


class RatingResponse(BaseModel):
    id: UUID
    booking_id: UUID
    reviewer_role: Literal["customer", "cleaner"]
    rating: float
    comment: str | None = None
    created_at: datetime
    reviewee_name: str | None = None


class CleanerRatingSummary(BaseModel):
    average_rating: float
    total_ratings: int
    recent_reviews: list[RatingResponse]


class CustomerRatingSummary(BaseModel):
    average_rating: float
    total_ratings: int
