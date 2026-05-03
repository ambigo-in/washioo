import logging

from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler
from sqlalchemy import text
from starlette.exceptions import HTTPException as StarletteHTTPException

from core.config import settings
from core.database import engine
from core.rate_limiter import limiter

from models import (
    audit_log,
    user,
    role,
    user_role,
    refresh_token,
    address,
    service_category,
    booking,
    cleaner_profile,
    customer_vehicle,
    cleaner_earning,
    cleaner_settlement,
    notification,
    booking_assignment,
    payment,
    rating,
    review,
)

from routers.auth_router import router as auth_router
from routers.services_router import router as services_router
from routers.user_router import router as user_router
from routers.cleaner_router import router as cleaner_router
from routers.customer_router import router as customer_router
from routers.payment_router import router as payment_router
from routers.payment_router import workflow_router as payment_workflow_router
from routers.rating_router import router as rating_router

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
    {
    "name": "Rating APIs",
        "description": "Bidirectional customer and cleaner booking ratings.",
    },
]

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)
API_PREFIX = "/washioo-api"

app = FastAPI(
    title="Car Wash Service Portal API",
    description="Car Wash Service Backend",
    version="1.0.0",
    openapi_tags=openapi_tags,
)
api_router = APIRouter(prefix=API_PREFIX)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.info("Validation failed for %s %s", request.method, request.url.path)
    detail = exc.errors() if settings.DEBUG else "Invalid request payload"
    return JSONResponse(status_code=422, content={"detail": detail})


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error for %s %s", request.method, request.url.path)
    detail = str(exc) if settings.DEBUG else "Internal server error"
    return JSONResponse(status_code=500, content={"detail": detail})

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Routers
api_router.include_router(auth_router)
api_router.include_router(services_router)
api_router.include_router(user_router)
api_router.include_router(cleaner_router)
api_router.include_router(customer_router)
api_router.include_router(payment_router)
api_router.include_router(payment_workflow_router)
api_router.include_router(rating_router)

@api_router.get("/", tags=["Public APIs"])
def root():
    return {
        "success": True,
        "message": "Car Wash Service Portal API Running Successfully"
    }

@api_router.get("/health", tags=["Public APIs"])
def health_check():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {
        "status": "healthy",
        "database": "connected",
        "version": "1.0.0"
    }


app.include_router(api_router)
