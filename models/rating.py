from datetime import datetime
import uuid

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.database import Base


class Rating(Base):
    __tablename__ = "ratings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False)
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    reviewee_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    reviewer_role = Column(String(20), nullable=False)
    rating = Column(Numeric(2, 1), nullable=False)
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    booking = relationship("Booking")
    reviewer = relationship("User", foreign_keys=[reviewer_id])
    reviewee = relationship("User", foreign_keys=[reviewee_id])

    __table_args__ = (
        CheckConstraint("reviewer_role IN ('customer', 'cleaner')", name="chk_ratings_reviewer_role"),
        CheckConstraint("rating >= 1 AND rating <= 5", name="chk_ratings_rating_range"),
        CheckConstraint("comment IS NULL OR char_length(comment) <= 500", name="chk_ratings_comment_length"),
        CheckConstraint("reviewer_id <> reviewee_id", name="chk_ratings_not_self_review"),
        UniqueConstraint("booking_id", "reviewer_id", name="uq_ratings_booking_reviewer"),
        Index("idx_ratings_booking", "booking_id"),
        Index("idx_ratings_reviewee", "reviewee_id"),
        Index("idx_ratings_reviewer", "reviewer_id"),
        Index("idx_ratings_reviewer_role", "reviewer_role"),
        Index("idx_ratings_created_at", "created_at"),
    )
