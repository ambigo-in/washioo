from sqlalchemy import Column, String, Boolean, DateTime, Integer, Numeric, Index
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from sqlalchemy.orm import relationship
import uuid
from core.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(150))
    phone = Column(String(20), unique=True, nullable=False)
    email = Column(String(150), unique=True)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    profile_image_url = Column(String)
    last_login = Column(DateTime)
    terms_accepted = Column(Boolean, default=False, nullable=False)
    terms_accepted_at = Column(DateTime)
    average_rating = Column(Numeric(3, 2), default=0, nullable=False)
    total_ratings = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")
    cleaner_profile = relationship("CleanerProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_users_phone", "phone"),
        Index("idx_users_email", "email"),
        Index("idx_users_active", "is_active"),
    )
