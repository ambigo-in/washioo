from sqlalchemy import Column, String, DateTime, Boolean, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from core.database import Base

class Address(Base):
    __tablename__ = "addresses"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    address_label = Column(String)  # Home/Office/Other
    address_line1 = Column(String, nullable=False)
    address_line2 = Column(String)
    landmark = Column(String)
    city = Column(String)
    state = Column(String)
    pincode = Column(String)
    country = Column(String, default="India")
    latitude = Column(Numeric(9, 6))
    longitude = Column(Numeric(9, 6))
    location_verified = Column(Boolean, default=False)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

