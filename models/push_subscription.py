from datetime import datetime
import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.database import Base


class PushSubscription(Base):
    __tablename__ = "push_subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    endpoint = Column(Text, nullable=False)
    p256dh = Column(Text, nullable=False)
    auth = Column(Text, nullable=False)
    user_agent = Column(Text)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_used_at = Column(DateTime)

    user = relationship("User")

    __table_args__ = (
        UniqueConstraint("endpoint", name="uq_push_subscriptions_endpoint"),
        Index("idx_push_subscriptions_user_active", "user_id", "is_active"),
    )
