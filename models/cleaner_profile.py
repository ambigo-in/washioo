from sqlalchemy import CheckConstraint, Column, String, DateTime, Numeric, Integer, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from core.database import Base


class CleanerProfile(Base):
    __tablename__ = "cleaner_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    vehicle_type = Column(String(50))
    aadhaar_number = Column(String(20))
    aadhaar_number_hash = Column(String(64))
    driving_license_number = Column(String(100))
    driving_license_number_hash = Column(String(64))
    government_id_number = Column(String(100))
    service_radius_km = Column(Numeric(8, 2))
    approval_status = Column(String(30), default="pending")
    availability_status = Column(String(30), default="offline")
    rating = Column(Numeric(3, 2), default=0)
    average_rating = Column(Numeric(3, 2), default=0, nullable=False)
    total_ratings = Column(Integer, default=0, nullable=False)
    total_jobs_completed = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="cleaner_profile")
    assignments = relationship("BookingAssignment", back_populates="cleaner")
    earnings = relationship("CleanerEarning", back_populates="cleaner", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint(
            "approval_status IN ('pending', 'approved', 'rejected', 'suspended')",
            name="chk_cleaner_approval_status",
        ),
        CheckConstraint(
            "availability_status IN ('offline', 'available', 'busy')",
            name="chk_cleaner_availability_status",
        ),
        Index("idx_cleaner_status", "approval_status", "availability_status"),
        Index(
            "idx_cleaner_aadhaar_hash",
            "aadhaar_number_hash",
            unique=True,
            postgresql_where=(aadhaar_number_hash.isnot(None)),
        ),
        Index(
            "idx_cleaner_driving_license_hash",
            "driving_license_number_hash",
            unique=True,
            postgresql_where=(driving_license_number_hash.isnot(None)),
        ),
    )
