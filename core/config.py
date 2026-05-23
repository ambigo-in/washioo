from dotenv import load_dotenv
import os
import json

load_dotenv()

class Settings:
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

    DATABASE_URL = os.getenv("DATABASE_URL")
    DATABASE_POOL_SIZE = int(os.getenv("DATABASE_POOL_SIZE", 20))
    DATABASE_MAX_OVERFLOW = int(os.getenv("DATABASE_MAX_OVERFLOW", 10))
    DATABASE_POOL_RECYCLE_SECONDS = int(os.getenv("DATABASE_POOL_RECYCLE_SECONDS", 1800))
    DATABASE_POOL_TIMEOUT_SECONDS = int(os.getenv("DATABASE_POOL_TIMEOUT_SECONDS", 10))

    SECRET_KEY = os.getenv("SECRET_KEY")
    PREVIOUS_SECRET_KEYS = [
        key.strip()
        for key in os.getenv("PREVIOUS_SECRET_KEYS", "").split(",")
        if key.strip()
    ]
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

    RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "True").lower() == "true"
    SEND_OTP_RATE_LIMIT = os.getenv("SEND_OTP_RATE_LIMIT", "3/15 minutes")
    AUTH_RATE_LIMIT = os.getenv("AUTH_RATE_LIMIT", "5/15 minutes")
    REFRESH_RATE_LIMIT = os.getenv("REFRESH_RATE_LIMIT", "20/hour")

    OTP_LENGTH = int(os.getenv("OTP_LENGTH", 6))
    OTP_EXPIRY_MINUTES = int(os.getenv("OTP_EXPIRY_MINUTES", 5))
    OTP_MAX_ATTEMPTS = int(os.getenv("OTP_MAX_ATTEMPTS", 5))

    SMS_COUNTRY_KEY = os.getenv("SMS_COUNTRY_KEY")
    SMS_COUNTRY_TOKEN = os.getenv("SMS_COUNTRY_TOKEN")
    SMS_HEADER = os.getenv("SMS_HEADER", "AMBHPL")

    ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
    CORS_ORIGINS = json.loads(os.getenv("CORS_ORIGINS", '["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "http://127.0.0.1:3000"]'))
    CORS_CREDENTIALS = os.getenv("CORS_CREDENTIALS", "True").lower() == "true"
    CORS_METHODS = json.loads(os.getenv("CORS_METHODS", '["*"]'))
    CORS_HEADERS = json.loads(os.getenv("CORS_HEADERS", '["*"]'))
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

    WEB_PUSH_ENABLED = os.getenv("WEB_PUSH_ENABLED", "False").lower() == "true"
    WEB_PUSH_VAPID_PRIVATE_KEY = os.getenv("WEB_PUSH_VAPID_PRIVATE_KEY")
    WEB_PUSH_VAPID_PUBLIC_KEY = os.getenv("WEB_PUSH_VAPID_PUBLIC_KEY")
    WEB_PUSH_VAPID_SUBJECT = os.getenv("WEB_PUSH_VAPID_SUBJECT", "mailto:support@washioo.local")

    def validate(self):
        missing = [
            name for name in ["DATABASE_URL", "SECRET_KEY"]
            if not getattr(self, name)
        ]
        if missing:
            raise RuntimeError(f"Missing required settings: {', '.join(missing)}")
        if len(self.SECRET_KEY) < 32:
            raise RuntimeError("SECRET_KEY must be a strong value of at least 32 characters")
        weak_previous_keys = [
            key for key in self.PREVIOUS_SECRET_KEYS if len(key) < 32
        ]
        if weak_previous_keys:
            raise RuntimeError("Each PREVIOUS_SECRET_KEYS value must be at least 32 characters")
        if self.ENVIRONMENT == "production" and self.DEBUG:
            raise RuntimeError("DEBUG must be disabled in production")
        if self.ENVIRONMENT == "production" and self.SECRET_KEY == "your-secret-key-here-change-in-production":
            raise RuntimeError("SECRET_KEY cannot use the production placeholder value")
        if self.ENVIRONMENT == "production" and self.CORS_CREDENTIALS and "*" in self.CORS_ORIGINS:
            raise RuntimeError("CORS_ORIGINS cannot contain '*' when credentials are enabled")
        if not isinstance(self.CORS_ORIGINS, list) or not all(isinstance(origin, str) for origin in self.CORS_ORIGINS):
            raise RuntimeError("CORS_ORIGINS must be a JSON array of strings")
        if not isinstance(self.CORS_METHODS, list) or not all(isinstance(method, str) for method in self.CORS_METHODS):
            raise RuntimeError("CORS_METHODS must be a JSON array of strings")
        if not isinstance(self.CORS_HEADERS, list) or not all(isinstance(header, str) for header in self.CORS_HEADERS):
            raise RuntimeError("CORS_HEADERS must be a JSON array of strings")
        if self.WEB_PUSH_ENABLED:
            web_push_missing = [
                name for name in [
                    "WEB_PUSH_VAPID_PRIVATE_KEY",
                    "WEB_PUSH_VAPID_PUBLIC_KEY",
                    "WEB_PUSH_VAPID_SUBJECT",
                ]
                if not getattr(self, name)
            ]
            if web_push_missing:
                raise RuntimeError(f"Missing required Web Push settings: {', '.join(web_push_missing)}")
            if not (
                self.WEB_PUSH_VAPID_SUBJECT.startswith("mailto:")
                or self.WEB_PUSH_VAPID_SUBJECT.startswith("https://")
            ):
                raise RuntimeError("WEB_PUSH_VAPID_SUBJECT must start with mailto: or https://")
        if self.ENVIRONMENT == "production":
            sms_missing = [
                name for name in ["SMS_COUNTRY_KEY", "SMS_COUNTRY_TOKEN"]
                if not getattr(self, name)
            ]
            if sms_missing:
                raise RuntimeError(f"Missing required SMS settings: {', '.join(sms_missing)}")
        if self.DATABASE_POOL_SIZE < 1:
            raise RuntimeError("DATABASE_POOL_SIZE must be at least 1")
        if self.DATABASE_MAX_OVERFLOW < 0:
            raise RuntimeError("DATABASE_MAX_OVERFLOW cannot be negative")
        if self.DATABASE_POOL_TIMEOUT_SECONDS < 1:
            raise RuntimeError("DATABASE_POOL_TIMEOUT_SECONDS must be at least 1")
        if self.OTP_LENGTH < 4:
            raise RuntimeError("OTP_LENGTH must be at least 4")
        if self.OTP_EXPIRY_MINUTES < 1:
            raise RuntimeError("OTP_EXPIRY_MINUTES must be at least 1")
        if self.OTP_MAX_ATTEMPTS < 1:
            raise RuntimeError("OTP_MAX_ATTEMPTS must be at least 1")

settings = Settings()
settings.validate()
