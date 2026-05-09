from datetime import datetime
import uuid

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.database import Base


class BookingAssignmentAttempt(Base):
    __tablename__ = "booking_assignment_attempts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False)
    cleaner_id = Column(UUID(as_uuid=True), ForeignKey("cleaner_profiles.id", ondelete="RESTRICT"), nullable=False)
    assignment_id = Column(UUID(as_uuid=True), ForeignKey("booking_assignments.id", ondelete="SET NULL"))
    status = Column(String(30), nullable=False, default="offered")
    score = Column(Numeric(8, 2))
    distance_km = Column(Numeric(8, 2))
    reason = Column(Text)
    offered_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime)
    responded_at = Column(DateTime)

    booking = relationship("Booking")
    cleaner = relationship("CleanerProfile")
    assignment = relationship("BookingAssignment")

    __table_args__ = (
        CheckConstraint(
            "status IN ('offered', 'accepted', 'rejected', 'expired', 'skipped')",
            name="chk_assignment_attempt_status",
        ),
        Index("idx_assignment_attempts_booking", "booking_id"),
        Index("idx_assignment_attempts_cleaner", "cleaner_id"),
        Index("idx_assignment_attempts_status", "status"),
        Index("idx_assignment_attempts_booking_cleaner", "booking_id", "cleaner_id"),
    )
