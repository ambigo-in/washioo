from sqlalchemy import Column, String, DateTime, Numeric, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from core.database import Base


class CleanerProfile(Base):
    __tablename__ = "cleaner_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    vehicle_type = Column(String)
    government_id_number = Column(String)
    service_radius_km = Column(Numeric(8, 2))
    approval_status = Column(String, default="pending")
    availability_status = Column(String, default="offline")
    rating = Column(Numeric(3, 2), default=0)
    total_jobs_completed = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="cleaner_profile")
    assignments = relationship("BookingAssignment", back_populates="cleaner")
