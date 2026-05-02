from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from core.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id", ondelete="CASCADE"), unique=True, nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)

    # Legacy admin-payment fields retained for backward compatible endpoints.
    payment_method = Column(String)
    transaction_reference = Column(String)
    amount = Column(Numeric(10, 2))
    payment_status = Column(String, default="pending")
    collected_by_cleaner = Column(Boolean, default=False)
    paid_at = Column(DateTime)

    collected_amount = Column(Numeric(10, 2))
    payment_type = Column(String)
    collected_by = Column(UUID(as_uuid=True), ForeignKey("cleaner_profiles.id", ondelete="RESTRICT"))
    collected_at = Column(DateTime)
    cleaner_share = Column(Numeric(10, 2))
    admin_share = Column(Numeric(10, 2))
    split_updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    split_updated_at = Column(DateTime)
    payout_released = Column(Boolean, default=False, nullable=False)
    cleaner_handover_status = Column(String, default="pending", nullable=False)
    status = Column(String, default="pending_collection")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    booking = relationship("Booking", back_populates="payment")
    cleaner = relationship("CleanerProfile", foreign_keys=[collected_by])
    split_admin = relationship("User", foreign_keys=[split_updated_by])
