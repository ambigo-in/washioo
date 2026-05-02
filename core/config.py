from dotenv import load_dotenv
import os
import json

load_dotenv()

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL")
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

    RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "True").lower() == "true"
    SEND_OTP_RATE_LIMIT = os.getenv("SEND_OTP_RATE_LIMIT", "3/15 minutes")
    AUTH_RATE_LIMIT = os.getenv("AUTH_RATE_LIMIT", "5/15 minutes")
    REFRESH_RATE_LIMIT = os.getenv("REFRESH_RATE_LIMIT", "20/hour")

    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_VERIFY_SERVICE_SID = os.getenv("TWILIO_VERIFY_SERVICE_SID")

    ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
    CORS_ORIGINS = json.loads(os.getenv("CORS_ORIGINS", '["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "http://127.0.0.1:3000"]'))
    CORS_CREDENTIALS = os.getenv("CORS_CREDENTIALS", "True").lower() == "true"

    def validate(self):
        missing = [
            name for name in ["DATABASE_URL", "SECRET_KEY"]
            if not getattr(self, name)
        ]
        if missing:
            raise RuntimeError(f"Missing required settings: {', '.join(missing)}")
        if len(self.SECRET_KEY) < 32:
            raise RuntimeError("SECRET_KEY must be a strong value of at least 32 characters")
        if self.ENVIRONMENT == "production" and self.SECRET_KEY == "your-secret-key-here-change-in-production":
            raise RuntimeError("SECRET_KEY cannot use the production placeholder value")
        if self.ENVIRONMENT == "production" and self.CORS_CREDENTIALS and "*" in self.CORS_ORIGINS:
            raise RuntimeError("CORS_ORIGINS cannot contain '*' when credentials are enabled")

settings = Settings()
settings.validate()
