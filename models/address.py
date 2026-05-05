from sqlalchemy import Column, String, DateTime, Boolean, Numeric, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from core.database import Base

class Address(Base):
    __tablename__ = "addresses"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    address_label = Column(String(50))
    address_line1 = Column(Text, nullable=False)
    address_line2 = Column(Text)
    landmark = Column(Text)
    city = Column(String(100))
    state = Column(String(100))
    pincode = Column(String(20))
    country = Column(String(100), default="India")
    latitude = Column(Numeric(9, 6))
    longitude = Column(Numeric(9, 6))
    location_verified = Column(Boolean, default=False)
    is_default = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_addresses_user", "user_id"),
        Index("idx_addresses_user_active", "user_id", "is_deleted"),
        Index("idx_addresses_location", "latitude", "longitude"),
        Index(
            "idx_one_default_address_per_user",
            "user_id",
            unique=True,
            postgresql_where=(is_default == True) & (is_deleted == False),
        ),
    )
