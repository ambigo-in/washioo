from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, ForeignKey, Numeric, String, Index
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
    payment_method = Column(String(30))
    transaction_reference = Column(String(255))
    amount = Column(Numeric(10, 2))
    payment_status = Column(String(30), default="pending")
    collected_by_cleaner = Column(Boolean, default=False)
    paid_at = Column(DateTime)

    collected_amount = Column(Numeric(10, 2))
    payment_type = Column(String(20))
    collected_by = Column(UUID(as_uuid=True), ForeignKey("cleaner_profiles.id", ondelete="RESTRICT"))
    collected_at = Column(DateTime)
    cleaner_share = Column(Numeric(10, 2))
    admin_share = Column(Numeric(10, 2))
    split_updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    split_updated_at = Column(DateTime)
    payout_released = Column(Boolean, default=False, nullable=False)
    cleaner_handover_status = Column(String(30), default="pending", nullable=False)
    status = Column(String(30), default="pending_collection", nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    booking = relationship("Booking", back_populates="payment")
    cleaner = relationship("CleanerProfile", foreign_keys=[collected_by])
    split_admin = relationship("User", foreign_keys=[split_updated_by])

    __table_args__ = (
        CheckConstraint("payment_status IN ('pending', 'paid', 'failed')", name="chk_payment_status"),
        CheckConstraint("payment_type IS NULL OR payment_type IN ('cash', 'upi')", name="chk_payments_payment_type"),
        CheckConstraint("status IN ('pending_collection', 'collected', 'split_done')", name="chk_payments_collection_status"),
        CheckConstraint("cleaner_handover_status IN ('pending', 'settled')", name="chk_payments_cleaner_handover_status"),
        Index("idx_payments_status", "payment_status"),
        Index("idx_payments_method", "payment_method"),
        Index("idx_payments_collection_status", "status"),
        Index("idx_payments_collected_by", "collected_by"),
        Index("idx_payments_booking", "booking_id"),
        Index("idx_payments_customer", "customer_id"),
        Index("idx_payments_cleaner_handover_status", "cleaner_handover_status"),
        Index("idx_payments_status_created", "payment_status", "created_at"),
        Index("idx_payments_customer_created", "customer_id", "created_at"),
        Index("idx_payments_collection_status_created", "status", "created_at"),
        Index("idx_payments_handover_status_created", "cleaner_handover_status", "created_at"),
    )
