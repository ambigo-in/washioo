from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from core.database import Base

class OTPCode(Base):
    __tablename__ = "otp_codes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone = Column(String, nullable=False)
    purpose = Column(String, default="login")
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    consumed_at = Column(DateTime, nullable=True)