from twilio.rest import Client
from core.config import settings

client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

def send_otp(phone_number: str):
    return client.verify.v2.services(
        settings.TWILIO_VERIFY_SERVICE_SID
    ).verifications.create(
        to=phone_number,
        channel="sms"
    )

def verify_otp(phone_number: str, otp_code: str):
    return client.verify.v2.services(
        settings.TWILIO_VERIFY_SERVICE_SID
    ).verification_checks.create(
        to=phone_number,
        code=otp_code
    )