from sqlalchemy import Column, String, DateTime, Integer, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from core.database import Base

class OTPCode(Base):
    __tablename__ = "otp_codes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone = Column(String(20), nullable=False)
    otp_code_hash = Column(String(255), nullable=False)
    purpose = Column(String(30), default="login", nullable=False)
    attempts = Column(Integer, default=0)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    consumed_at = Column(DateTime, nullable=True)
    created_ip = Column(String(64))
    user_agent = Column(Text)

    __table_args__ = (
        Index("idx_otp_phone", "phone"),
        Index("idx_otp_expiry", "expires_at"),
    )
