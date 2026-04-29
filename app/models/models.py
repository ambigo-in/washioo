from sqlalchemy import Column, String, Boolean, Enum, Text, DECIMAL, Integer, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
import uuid
from app.database.session import Base

class UserRole(enum.Enum):
    customer = "customer"
    admin = "admin"
    cleaner = "cleaner"

class VehicleType(enum.Enum):
    car = "car"
    bike = "bike"

class BookingStatus(enum.Enum):
    pending = "pending"
    assigned = "assigned"
    en_route = "en_route"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"
    failed = "failed"

class PaymentStatus(enum.Enum):
    unpaid = "unpaid"
    paid = "paid"

class PaymentMethod(enum.Enum):
    cash = "cash"
    upi = "upi"

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone_number = Column(String(20), unique=True, nullable=False)
    full_name = Column(String(100))
    role = Column(Enum(UserRole), nullable=False)
    is_verified = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default="now()")
    updated_at = Column(TIMESTAMP, server_default="now()")
    vehicles = relationship("Vehicle", back_populates="user")
    bookings = relationship("Booking", back_populates="user", foreign_keys='Booking.user_id')
    cleaner_bookings = relationship("Booking", back_populates="cleaner", foreign_keys='Booking.cleaner_id')

class Vehicle(Base):
    __tablename__ = "vehicles"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    vehicle_type = Column(Enum(VehicleType), nullable=False)
    vehicle_model = Column(String(100), nullable=False)
    vehicle_number = Column(String(30), nullable=False)
    created_at = Column(TIMESTAMP, server_default="now()")
    user = relationship("User", back_populates="vehicles")
    bookings = relationship("Booking", back_populates="vehicle")

class Package(Base):
    __tablename__ = "packages"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_type = Column(Enum(VehicleType), nullable=False)
    package_name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(DECIMAL(10,2), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    bookings = relationship("Booking", back_populates="package")

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"))
    package_id = Column(UUID(as_uuid=True), ForeignKey("packages.id"))
    cleaner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    address = Column(Text, nullable=False)
    latitude = Column(DECIMAL(9,6))
    longitude = Column(DECIMAL(9,6))
    scheduled_at = Column(TIMESTAMP)
    status = Column(Enum(BookingStatus), default=BookingStatus.pending)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.unpaid)
    payment_method = Column(Enum(PaymentMethod))
    created_at = Column(TIMESTAMP, server_default="now()")
    updated_at = Column(TIMESTAMP, server_default="now()")
    user = relationship("User", back_populates="bookings", foreign_keys=[user_id])
    cleaner = relationship("User", back_populates="cleaner_bookings", foreign_keys=[cleaner_id])
    vehicle = relationship("Vehicle", back_populates="bookings")
    package = relationship("Package", back_populates="bookings")

class CleanerLocation(Base):
    __tablename__ = "cleaner_locations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cleaner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    latitude = Column(DECIMAL(9,6))
    longitude = Column(DECIMAL(9,6))
    updated_at = Column(TIMESTAMP, server_default="now()")
