from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from sqlalchemy.orm import relationship
import uuid
from core.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String)
    phone = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user_roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")
    cleaner_profile = relationship("CleanerProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
