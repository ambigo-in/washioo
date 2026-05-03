from datetime import datetime
import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.database import Base


class CustomerVehicle(Base):
    __tablename__ = "customer_vehicles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    vehicle_type = Column(String(30), nullable=False)
    make = Column(String(100))
    model = Column(String(100))
    license_plate = Column(String(30))
    is_default = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer = relationship("User")
    bookings = relationship("Booking", back_populates="vehicle")

    __table_args__ = (
        Index("idx_customer_vehicles_customer", "customer_id"),
        Index("idx_customer_vehicles_default", "customer_id", "is_default"),
    )
