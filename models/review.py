from datetime import datetime
import uuid

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id", ondelete="CASCADE"), unique=True, nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    cleaner_id = Column(UUID(as_uuid=True), ForeignKey("cleaner_profiles.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer)
    review_text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    booking = relationship("Booking")
    customer = relationship("User")
    cleaner = relationship("CleanerProfile")

    __table_args__ = (
        CheckConstraint("rating BETWEEN 1 AND 5", name="chk_reviews_rating_range"),
    )
