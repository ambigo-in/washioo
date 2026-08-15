import asyncio
import logging

from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler
from sqlalchemy import text
from sqlalchemy.exc import TimeoutError as SQLAlchemyTimeoutError
from starlette.exceptions import HTTPException as StarletteHTTPException

from core.config import settings
from core.database import engine
from core.rate_limiter import limiter
from services.booking_auto_cancel_service import run_booking_auto_cancel_loop

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
    push_subscription,
    booking_assignment,
    booking_assignment_attempt,
    payment,
    rating,
    review,
)

from routers.auth_router import router as auth_router
from routers.admin_router import router as admin_router
from routers.services_router import router as services_router
from routers.user_router import router as user_router
from routers.cleaner_router import router as cleaner_router
from routers.customer_router import router as customer_router
from routers.payment_router import router as payment_router
from routers.payment_router import workflow_router as payment_workflow_router
from routers.rating_router import router as rating_router
from routers.websocket_router import router as websocket_router

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


def _is_public_cacheable_api_request(request: Request) -> bool:
    # Service endpoints must always return fresh data for frontend admin and public screens.
    return False

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


@app.middleware("http")
async def api_cache_control_middleware(request: Request, call_next):
    response = await call_next(request)

    if not request.url.path.startswith(API_PREFIX):
        return response

    if _is_public_cacheable_api_request(request) and response.status_code < 400:
        response.headers["Cache-Control"] = (
            "public, max-age=300, s-maxage=600, stale-while-revalidate=60"
        )
        response.headers["Vary"] = "Accept-Encoding"
        return response

    response.headers["Cache-Control"] = "no-store"
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.info("Validation failed for %s %s", request.method, request.url.path)
    detail = exc.errors() if settings.DEBUG else "Invalid request payload"
    return JSONResponse(status_code=422, content={"detail": detail})


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(SQLAlchemyTimeoutError)
async def database_timeout_exception_handler(request: Request, exc: SQLAlchemyTimeoutError):
    logger.warning("Database pool exhausted for %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=503,
        content={"detail": "Database is busy. Please retry shortly."},
        headers={"Retry-After": "5"},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error for %s %s", request.method, request.url.path)
    detail = str(exc) if settings.DEBUG else "Internal server error"
    return JSONResponse(status_code=500, content={"detail": detail})

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
    expose_headers=["*"]
)


@app.on_event("startup")
async def start_booking_auto_cancel_task():
    stop_event = asyncio.Event()
    app.state.booking_auto_cancel_stop_event = stop_event
    app.state.booking_auto_cancel_task = asyncio.create_task(
        run_booking_auto_cancel_loop(stop_event)
    )


@app.on_event("shutdown")
async def stop_booking_auto_cancel_task():
    task = getattr(app.state, "booking_auto_cancel_task", None)
    stop_event = getattr(app.state, "booking_auto_cancel_stop_event", None)
    if stop_event:
        stop_event.set()
    if task:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

# Routers
api_router.include_router(auth_router)
api_router.include_router(admin_router)
api_router.include_router(services_router)
api_router.include_router(user_router)
api_router.include_router(cleaner_router)
api_router.include_router(customer_router)
api_router.include_router(payment_router)
api_router.include_router(payment_workflow_router)
api_router.include_router(rating_router)
api_router.include_router(websocket_router)

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
