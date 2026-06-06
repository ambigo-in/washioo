from sqlalchemy import Column, String, DateTime, Boolean, Numeric, Integer
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from sqlalchemy.orm import relationship
import uuid
from core.database import Base

class ServiceCategory(Base):
    __tablename__ = "service_categories"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_name = Column(String(50), unique=True, nullable=False)
    description = Column(String)
    base_price = Column(Numeric(10, 2), nullable=False)
    estimated_duration_minutes = Column(Integer)
    allow_extra_payment = Column(Boolean, default=False, nullable=False)
    max_extra_amount = Column(Numeric(10, 2))
    extra_payment_instructions = Column(String)
    image_url = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    bookings = relationship("Booking", back_populates="service_category")
