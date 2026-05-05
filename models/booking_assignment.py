from sqlalchemy import CheckConstraint, Column, String, DateTime, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from core.database import Base


class BookingAssignment(Base):
    __tablename__ = "booking_assignments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id", ondelete="CASCADE"), unique=True, nullable=False)
    cleaner_id = Column(UUID(as_uuid=True), ForeignKey("cleaner_profiles.id", ondelete="RESTRICT"), nullable=False)
    assigned_by_admin = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    accepted_at = Column(DateTime)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    assignment_status = Column(String(30), default="assigned")
    cleaner_notes = Column(Text)

    booking = relationship("Booking", back_populates="assignment")
    cleaner = relationship("CleanerProfile", back_populates="assignments")
    admin = relationship("User", foreign_keys=[assigned_by_admin])

    __table_args__ = (
        CheckConstraint(
            "assignment_status IN ('assigned', 'accepted', 'in_progress', 'rejected', 'completed', 'cancelled')",
            name="chk_assignment_status",
        ),
        Index("idx_assignments_cleaner", "cleaner_id"),
        Index("idx_assignments_status", "assignment_status"),
        Index("idx_assignments_booking", "booking_id"),
        Index("idx_assignments_cleaner_status_assigned", "cleaner_id", "assignment_status", "assigned_at"),
        Index("idx_assignments_status_assigned", "assignment_status", "assigned_at"),
    )
