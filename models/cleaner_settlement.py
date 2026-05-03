from datetime import datetime
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Numeric, String, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.database import Base


class CleanerSettlement(Base):
    __tablename__ = "cleaner_settlements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cleaner_id = Column(UUID(as_uuid=True), ForeignKey("cleaner_profiles.id", ondelete="RESTRICT"), nullable=False)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id", ondelete="CASCADE"), unique=True, nullable=False)
    payment_id = Column(UUID(as_uuid=True), ForeignKey("payments.id", ondelete="CASCADE"), nullable=False)
    collected_amount = Column(Numeric(10, 2), nullable=False)
    admin_received_amount = Column(Numeric(10, 2))
    settlement_status = Column(String(30), default="pending")
    submitted_at = Column(DateTime)
    verified_at = Column(DateTime)
    verified_by_admin = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    cleaner = relationship("CleanerProfile")
    booking = relationship("Booking")
    payment = relationship("Payment")
    verifier = relationship("User", foreign_keys=[verified_by_admin])

    __table_args__ = (
        Index("idx_settlements_status", "settlement_status"),
    )
