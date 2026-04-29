import os
from twilio.rest import Client
from app.models.models import Booking

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "+1234567890")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_booking_confirmation(customer_phone: str, booking: Booking):
    """Send booking confirmation SMS to customer"""
    try:
        message = client.messages.create(
            body=f"Your car wash booking is confirmed! Booking ID: {booking.id}. A cleaner will be assigned soon.",
            from_=TWILIO_PHONE_NUMBER,
            to=customer_phone
        )
        return {"success": True, "message_id": message.sid}
    except Exception as e:
        return {"success": False, "error": str(e)}

def send_cleaner_assigned_notification(cleaner_phone: str, booking: Booking):
    """Send notification to cleaner that a job has been assigned"""
    try:
        message = client.messages.create(
            body=f"New job assigned! Booking ID: {booking.id}. Address: {booking.address}. Please navigate to the location.",
            from_=TWILIO_PHONE_NUMBER,
            to=cleaner_phone
        )
        return {"success": True, "message_id": message.sid}
    except Exception as e:
        return {"success": False, "error": str(e)}

def send_booking_completion_notification(customer_phone: str, booking: Booking):
    """Send notification to customer that their booking is complete"""
    try:
        message = client.messages.create(
            body=f"Your car wash is complete! Booking ID: {booking.id}. Thank you for using Washioo!",
            from_=TWILIO_PHONE_NUMBER,
            to=customer_phone
        )
        return {"success": True, "message_id": message.sid}
    except Exception as e:
        return {"success": False, "error": str(e)}

def send_custom_sms(phone_number: str, message_text: str):
    """Send custom SMS to any phone number"""
    try:
        message = client.messages.create(
            body=message_text,
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        return {"success": True, "message_id": message.sid}
    except Exception as e:
        return {"success": False, "error": str(e)}
