from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler

from core.database import Base, engine
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
    booking_assignment,
)

from routers.auth_router import router as auth_router
from routers.services_router import router as services_router
from routers.user_router import router as user_router

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
]

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Car Wash Service Portal API",
    description="Car Wash Service Backend",
    version="1.0.0",
    openapi_tags=openapi_tags,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS Configuration
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "*"   # REMOVE in production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Routers
app.include_router(auth_router)
app.include_router(services_router)
app.include_router(user_router)

@app.get("/", tags=["Public APIs"])
def root():
    return {
        "success": True,
        "message": "Car Wash Service Portal API Running Successfully"
    }

@app.get("/health", tags=["Public APIs"])
def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "version": "1.0.0"
    }
