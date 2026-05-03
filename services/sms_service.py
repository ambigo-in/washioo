import base64
import logging

import httpx

from core.config import settings


logger = logging.getLogger(__name__)


def generate_otp_template(otp: str) -> str:
    return f"User Admin login OTP is {otp} - SMSCNT"


async def send_otp_sms(phone_number: str, otp: str) -> bool:
    if not settings.SMS_COUNTRY_KEY or not settings.SMS_COUNTRY_TOKEN:
        logger.warning("SMSCountry credentials are not configured")
        return False

    number = phone_number.strip()
    credentials = f"{settings.SMS_COUNTRY_KEY}:{settings.SMS_COUNTRY_TOKEN}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    url = f"https://restapi.smscountry.com/v0.1/Accounts/{settings.SMS_COUNTRY_KEY}/SMSes/"

    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/json",
    }
    payload = {
        "Number": "91" + number,
        "Text": generate_otp_template(otp),
        "SenderId": settings.SMS_HEADER,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
        return True
    except httpx.HTTPError as exc:
        logger.warning("SMSCountry OTP delivery failed: %s", exc)
        return False
