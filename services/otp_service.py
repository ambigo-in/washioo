import random
import string
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from core.config import settings
from core.security import hash_data, verify_hash
from models.otp import OTPCode
from services.sms_service import send_otp_sms


def _generate_otp() -> str:
    return "".join(random.choices(string.digits, k=settings.OTP_LENGTH))


async def create_and_send_otp(
    db: Session,
    phone_number: str,
    purpose: str = "login",
    created_ip: str | None = None,
    user_agent: str | None = None,
) -> bool:
    otp = _generate_otp()
    otp_entry = OTPCode(
        phone=phone_number,
        otp_code_hash=hash_data(otp),
        purpose=purpose,
        expires_at=datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRY_MINUTES),
        created_ip=created_ip,
        user_agent=user_agent,
    )
    db.add(otp_entry)
    db.flush()

    if not await send_otp_sms(phone_number, otp):
        db.rollback()
        return False

    db.commit()
    return True


def verify_otp_code(db: Session, phone_number: str, otp_code: str, purpose: str = "login") -> bool:
    otp_entry = (
        db.query(OTPCode)
        .filter(
            OTPCode.phone == phone_number,
            OTPCode.purpose == purpose,
            OTPCode.consumed_at.is_(None),
            OTPCode.expires_at > datetime.utcnow(),
        )
        .order_by(OTPCode.created_at.desc())
        .first()
    )
    if not otp_entry:
        return False

    if otp_entry.attempts >= settings.OTP_MAX_ATTEMPTS:
        return False

    if not verify_hash(otp_code, otp_entry.otp_code_hash):
        otp_entry.attempts += 1
        db.commit()
        return False

    otp_entry.consumed_at = datetime.utcnow()
    db.commit()
    return True
