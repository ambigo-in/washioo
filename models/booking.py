from sqlalchemy import Column, String, DateTime, Date, Time, Numeric, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from sqlalchemy.orm import relationship
import uuid
from core.database import Base

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_reference = Column(String, unique=True, nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    service_category_id = Column(UUID(as_uuid=True), ForeignKey("service_categories.id", ondelete="RESTRICT"), nullable=False)
    address_id = Column(UUID(as_uuid=True), ForeignKey("addresses.id", ondelete="RESTRICT"), nullable=False)
    scheduled_date = Column(Date)
    scheduled_time = Column(Time)
    special_instructions = Column(String)
    vehicle_make = Column(String)
    vehicle_model = Column(String)
    license_plate = Column(String)
    booking_status = Column(String, default="pending")  # pending, assigned, accepted, in_progress, completed, cancelled
    estimated_price = Column(Numeric(10, 2), nullable=False)
    final_price = Column(Numeric(10, 2))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer = relationship("User", foreign_keys=[customer_id])
    service_category = relationship("ServiceCategory", back_populates="bookings")
    address = relationship("Address")
    assignment = relationship("BookingAssignment", back_populates="booking", uselist=False, cascade="all, delete-orphan")
    payment = relationship("Payment", back_populates="booking", uselist=False, cascade="all, delete-orphan")


