from datetime import datetime
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Numeric, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.database import Base


class CleanerEarning(Base):
    __tablename__ = "cleaner_earnings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cleaner_id = Column(UUID(as_uuid=True), ForeignKey("cleaner_profiles.id", ondelete="CASCADE"), unique=True, nullable=False)
    total_earned = Column(Numeric(10, 2), default=0, nullable=False)
    pending_payout = Column(Numeric(10, 2), default=0, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    cleaner = relationship("CleanerProfile", back_populates="earnings")

    __table_args__ = (
        Index("idx_cleaner_earnings_cleaner", "cleaner_id"),
    )
