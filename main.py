from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler
from sqlalchemy import text

from core.config import settings
from core.database import engine
from core.rate_limiter import limiter

from models import (
    user,
    role,
    user_role,
    refresh_token,
    address,
    service_category,
    booking,
    cleaner_profile,
    cleaner_earning,
    booking_assignment,
    payment,
)

from routers.auth_router import router as auth_router
from routers.services_router import router as services_router
from routers.user_router import router as user_router
from routers.cleaner_router import router as cleaner_router
from routers.customer_router import router as customer_router
from routers.payment_router import router as payment_router
from routers.payment_router import workflow_router as payment_workflow_router

openapi_tags = [
    {
        "name": "Auth APIs",
        "description": "OTP, signup, signin, refresh token, and logout endpoints.",
    },
    {
        "name": "Profile APIs",
        "description": "Authenticated user profile endpoints shared by all roles.",
    },
    {
        "name": "Public APIs",
        "description": "Endpoints available without authentication.",
    },
    {
        "name": "Customer APIs",
        "description": "Customer-only address and booking endpoints.",
    },
    {
        "name": "Cleaner APIs",
        "description": "Cleaner-only profile, availability, and assignment endpoints.",
    },
    {
        "name": "Admin APIs",
        "description": "Admin-only service, booking, cleaner, and assignment management endpoints.",
    },
    {
        "name": "Address APIs",
        "description": "Authenticated address management endpoints.",
    },
    {
        "name": "Payment APIs",
        "description": "Payment collection, admin split, cleaner earnings, and legacy admin payment endpoints.",
    },
]

app = FastAPI(
    title="Car Wash Service Portal API",
    description="Car Wash Service Backend",
    version="1.0.0",
    openapi_tags=openapi_tags,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Routers
app.include_router(auth_router)
app.include_router(services_router)
app.include_router(user_router)
app.include_router(cleaner_router)
app.include_router(customer_router)
app.include_router(payment_router)
app.include_router(payment_workflow_router)

@app.get("/", tags=["Public APIs"])
def root():
    return {
        "success": True,
        "message": "Car Wash Service Portal API Running Successfully"
    }

@app.get("/health", tags=["Public APIs"])
def health_check():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {
        "status": "healthy",
        "database": "connected",
        "version": "1.0.0"
    }

