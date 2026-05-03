from sqlalchemy import CheckConstraint, Column, String, DateTime, Date, Time, Numeric, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from sqlalchemy.orm import relationship
import uuid
from core.database import Base

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_reference = Column(String(30), unique=True, nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    service_category_id = Column(UUID(as_uuid=True), ForeignKey("service_categories.id", ondelete="RESTRICT"), nullable=False)
    address_id = Column(UUID(as_uuid=True), ForeignKey("addresses.id", ondelete="RESTRICT"), nullable=False)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("customer_vehicles.id", ondelete="SET NULL"))
    scheduled_date = Column(Date)
    scheduled_time = Column(Time)
    special_instructions = Column(Text)
    vehicle_make = Column(String(100))
    vehicle_model = Column(String(100))
    license_plate = Column(String(30))
    booking_status = Column(String(30), default="pending")
    estimated_price = Column(Numeric(10, 2), nullable=False)
    final_price = Column(Numeric(10, 2))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer = relationship("User", foreign_keys=[customer_id])
    service_category = relationship("ServiceCategory", back_populates="bookings")
    address = relationship("Address")
    vehicle = relationship("CustomerVehicle", back_populates="bookings")
    assignment = relationship("BookingAssignment", back_populates="booking", uselist=False, cascade="all, delete-orphan")
    payment = relationship("Payment", back_populates="booking", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint(
            "booking_status IN ('pending', 'assigned', 'accepted', 'in_progress', 'completed', 'cancelled')",
            name="chk_bookings_status",
        ),
        Index("idx_bookings_customer", "customer_id"),
        Index("idx_bookings_status", "booking_status"),
        Index("idx_bookings_date", "scheduled_date"),
        Index("idx_bookings_service_category", "service_category_id"),
        Index("idx_bookings_address", "address_id"),
        Index("idx_bookings_vehicle", "vehicle_id"),
    )

