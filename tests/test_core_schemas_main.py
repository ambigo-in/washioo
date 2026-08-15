import importlib
import pkgutil
from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest
from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.security import HTTPAuthorizationCredentials
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.exc import TimeoutError as SQLAlchemyTimeoutError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import Response

from tests.conftest import FakeDB, obj, uid


def test_imports_all_backend_modules():
    packages = ["core", "models", "repositories", "routers", "schemas", "services", "utils"]
    imported = []
    for package_name in packages:
        package = importlib.import_module(package_name)
        for module in pkgutil.walk_packages(package.__path__, f"{package_name}."):
            imported.append(importlib.import_module(module.name))
    assert imported


def test_settings_validate_accepts_and_rejects_required_cases(monkeypatch):
    import core.config as config

    settings = config.Settings()
    settings.DATABASE_URL = "postgresql://example"
    settings.SECRET_KEY = "x" * 32
    settings.PREVIOUS_SECRET_KEYS = ["y" * 32]
    settings.ENVIRONMENT = "development"
    settings.CORS_ORIGINS = ["http://localhost"]
    settings.CORS_METHODS = ["GET"]
    settings.CORS_HEADERS = ["Authorization"]
    settings.WEB_PUSH_ENABLED = False
    settings.DATABASE_POOL_SIZE = 1
    settings.DATABASE_MAX_OVERFLOW = 0
    settings.DATABASE_POOL_TIMEOUT_SECONDS = 1
    settings.OTP_LENGTH = 4
    settings.OTP_EXPIRY_MINUTES = 1
    settings.OTP_MAX_ATTEMPTS = 1
    settings.validate()

    settings.SECRET_KEY = "short"
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        settings.validate()

    settings.SECRET_KEY = "x" * 32
    settings.PREVIOUS_SECRET_KEYS = ["weak"]
    with pytest.raises(RuntimeError, match="PREVIOUS_SECRET_KEYS"):
        settings.validate()

    settings.PREVIOUS_SECRET_KEYS = []
    settings.ENVIRONMENT = "production"
    settings.DEBUG = True
    with pytest.raises(RuntimeError, match="DEBUG"):
        settings.validate()

    settings.DEBUG = False
    settings.CORS_CREDENTIALS = True
    settings.CORS_ORIGINS = ["*"]
    with pytest.raises(RuntimeError, match="CORS_ORIGINS"):
        settings.validate()

    settings.CORS_ORIGINS = [1]
    with pytest.raises(RuntimeError, match="CORS_ORIGINS"):
        settings.validate()

    settings.CORS_ORIGINS = ["https://app.example"]
    settings.WEB_PUSH_ENABLED = True
    settings.WEB_PUSH_VAPID_PRIVATE_KEY = None
    with pytest.raises(RuntimeError, match="Web Push"):
        settings.validate()

    settings.WEB_PUSH_VAPID_PRIVATE_KEY = "private"
    settings.WEB_PUSH_VAPID_PUBLIC_KEY = "public"
    settings.WEB_PUSH_VAPID_SUBJECT = "ftp://bad"
    with pytest.raises(RuntimeError, match="WEB_PUSH_VAPID_SUBJECT"):
        settings.validate()


def test_security_hashing_token_rotation_and_decode_errors(monkeypatch):
    import core.security as security
    from core.config import settings

    monkeypatch.setattr(settings, "SECRET_KEY", "primary-secret-key-value-1234567890")
    monkeypatch.setattr(settings, "PREVIOUS_SECRET_KEYS", ["old-secret-key-value-123456789012"])
    monkeypatch.setattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES", 5)
    monkeypatch.setattr(settings, "REFRESH_TOKEN_EXPIRE_DAYS", 7)

    hashed = security.hash_data("123456")
    assert security.verify_hash("123456", hashed)
    assert not security.verify_hash("000000", hashed)

    token_hash = security.hash_token("refresh")
    assert security.verify_token_hash("refresh", token_hash)
    assert not security.verify_token_hash("other", token_hash)
    old_hash = jwt.get_unverified_header if False else None
    old_hash = __import__("hmac").new(
        settings.PREVIOUS_SECRET_KEYS[0].encode(), b"refresh", __import__("hashlib").sha256
    ).hexdigest()
    assert security.verify_token_hash("refresh", old_hash)

    assert security.hash_identifier(" ab 12 ") == security.hash_identifier("AB12")
    assert security.mask_identifier("123456789012") == "********9012"
    assert security.mask_identifier("123") == "***"

    access = security.create_access_token({"sub": "user-1"})
    decoded = security.decode_token_or_raise(access)
    assert decoded["sub"] == "user-1"
    assert decoded["type"] == "access"
    assert security.decode_token(access)["jti"]

    refresh, jti = security.create_refresh_token({"sub": "user-1"})
    assert security.decode_token_or_raise(refresh)["jti"] == jti

    expired = jwt.encode(
        {"sub": "x", "exp": datetime.utcnow() - timedelta(seconds=1)},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    with pytest.raises(security.TokenExpired):
        security.decode_token_or_raise(expired)
    with pytest.raises(security.TokenInvalid):
        security.decode_token_or_raise("not-a-token")
    assert security.decode_token("not-a-token") is None


def test_get_current_user_success_and_error_branches(monkeypatch):
    import core.dependencies as dependencies
    import core.security as security

    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="token")
    user = obj(id="u1", is_active=True)
    monkeypatch.setattr(dependencies, "decode_token_or_raise", lambda token: {"type": "access", "sub": "u1"})
    monkeypatch.setattr(dependencies, "get_user_with_roles", lambda db, user_id: user)
    assert dependencies.get_current_user(credentials, FakeDB()) is user

    for exc, detail in [
        (security.TokenExpired(), "Token expired"),
        (security.TokenInvalid(), "Invalid token"),
    ]:
        monkeypatch.setattr(dependencies, "decode_token_or_raise", lambda token, exc=exc: (_ for _ in ()).throw(exc))
        with pytest.raises(HTTPException) as raised:
            dependencies.get_current_user(credentials, FakeDB())
        assert raised.value.status_code == 401
        assert raised.value.detail == detail

    monkeypatch.setattr(dependencies, "decode_token_or_raise", lambda token: {"type": "refresh", "sub": "u1"})
    with pytest.raises(HTTPException) as raised:
        dependencies.get_current_user(credentials, FakeDB())
    assert raised.value.detail == "Invalid token type"

    monkeypatch.setattr(dependencies, "decode_token_or_raise", lambda token: {"type": "access"})
    with pytest.raises(HTTPException) as raised:
        dependencies.get_current_user(credentials, FakeDB())
    assert raised.value.detail == "Invalid token subject"

    monkeypatch.setattr(dependencies, "decode_token_or_raise", lambda token: {"type": "access", "sub": "u1"})
    monkeypatch.setattr(dependencies, "get_user_with_roles", lambda db, user_id: obj(is_active=False))
    with pytest.raises(HTTPException) as raised:
        dependencies.get_current_user(credentials, FakeDB())
    assert raised.value.detail == "User not found or inactive"


def test_require_roles_accepts_matching_role_and_rejects_missing_roles():
    from core.role_dependencies import require_roles

    checker = require_roles(["admin", "cleaner"])
    user = obj(terms_accepted=True, user_roles=[obj(role=obj(role_name="cleaner"))])
    assert checker(user) is user

    with pytest.raises(HTTPException) as raised:
        checker(obj(terms_accepted=True, user_roles=[obj(role=obj(role_name="customer"))]))
    assert raised.value.status_code == 403

    with pytest.raises(HTTPException) as raised:
        checker(obj(terms_accepted=False, user_roles=[obj(role=obj(role_name="admin"))]))
    assert raised.value.detail["error_code"] == "terms_not_accepted"


def test_database_get_db_closes_session(monkeypatch):
    import core.database as database

    db = FakeDB()
    monkeypatch.setattr(database, "SessionLocal", lambda: db)
    gen = database.get_db()
    assert next(gen) is db
    with pytest.raises(StopIteration):
        next(gen)
    assert db.closed


def test_schema_validation_positive_and_negative_cases():
    from schemas.auth_schema import CleanerSignupRequest, RoleSignupRequest, SendOTPRequest
    from schemas.booking_schema import (
        CleanerDrivingLicenseUploadRequest,
        CreateAddressRequest,
        CreateBookingRequest,
        CreateCustomerVehicleRequest,
        CreateServiceRequest,
        UpdateAddressRequest,
        UpdateCleanerLocationRequest,
    )
    from schemas.payment_schema import AdminPaymentSplitRequest, CleanerPaymentUpdateRequest
    from schemas.rating_schema import RatingCreateRequest

    assert SendOTPRequest(phone_number=" 9876543210 ").phone_number == "9876543210"
    with pytest.raises(ValidationError):
        SendOTPRequest(phone_number="12345")
    assert RoleSignupRequest(
        full_name="A", phone_number="9876543210", email="", otp_code="111111"
    ).email is None
    assert CleanerSignupRequest(
        full_name="A",
        phone_number="9876543210",
        otp_code="111111",
        aadhaar_number="123456789012",
        driving_license_number=" abcd12345678901 ",
    ).driving_license_number == "ABCD12345678901"
    with pytest.raises(ValidationError):
        CleanerSignupRequest(
            full_name="A", phone_number="9876543210", otp_code="1", aadhaar_number="123"
        )

    assert CreateAddressRequest(address_line1="X", latitude=12.1234567, longitude=77.9999999).latitude == 12.123457
    with pytest.raises(ValidationError):
        UpdateAddressRequest(latitude=12.0)
    assert UpdateAddressRequest(latitude=12.1234567, longitude=77.7654321).longitude == 77.765432
    assert CreateServiceRequest(service_name="Wash", base_price=100).base_price == 100
    with pytest.raises(ValidationError):
        CreateServiceRequest(service_name="Wash", base_price=0)
    assert CreateCustomerVehicleRequest(vehicle_type="car").vehicle_type == "car"
    with pytest.raises(ValidationError):
        CreateCustomerVehicleRequest(vehicle_type="truck")
    assert UpdateCleanerLocationRequest(latitude=1.1234567, longitude=2.1234567).latitude == 1.123457
    assert CleanerDrivingLicenseUploadRequest(driving_license_number=" abcd12345678901 ").driving_license_number == "ABCD12345678901"
    with pytest.raises(ValidationError):
        CreateBookingRequest(service_category_id="svc", scheduled_date="bad", scheduled_time="10:00")
    assert CleanerPaymentUpdateRequest(amount=10, payment_type="cash").payment_type == "cash"
    with pytest.raises(ValidationError):
        AdminPaymentSplitRequest(cleaner_share=-1, admin_share=1)
    assert RatingCreateRequest(booking_id=uid(), rating=4.5).rating == 4.5
    with pytest.raises(ValidationError):
        RatingCreateRequest(booking_id=uid(), rating=4.55)


@pytest.mark.anyio
async def test_main_cache_middleware_and_exception_handlers(monkeypatch):
    import main

    assert main.root()["success"] is True
    request = SimpleNamespace(
        method="GET",
        headers={},
        url=SimpleNamespace(path=f"{main.API_PREFIX}/services"),
    )

    async def call_next(_request):
        return Response("ok", status_code=200)

    response = await main.api_cache_control_middleware(request, call_next)
    assert response.headers["Cache-Control"].startswith("public")
    assert response.headers["Vary"] == "Accept-Encoding"

    authed = SimpleNamespace(
        method="GET",
        headers={"authorization": "Bearer token"},
        url=SimpleNamespace(path=f"{main.API_PREFIX}/services"),
    )
    response = await main.api_cache_control_middleware(authed, call_next)
    assert response.headers["Cache-Control"] == "no-store"

    non_api = SimpleNamespace(method="GET", headers={}, url=SimpleNamespace(path="/"))
    response = await main.api_cache_control_middleware(non_api, call_next)
    assert "Cache-Control" not in response.headers

    req = SimpleNamespace(method="POST", url=SimpleNamespace(path="/x"))
    monkeypatch.setattr(main.settings, "DEBUG", False)
    validation_response = await main.validation_exception_handler(req, RequestValidationError([]))
    assert validation_response.status_code == 422
    assert b"Invalid request payload" in validation_response.body

    http_response = await main.http_exception_handler(req, StarletteHTTPException(404, "missing"))
    assert http_response.status_code == 404
    assert b"missing" in http_response.body

    timeout_response = await main.database_timeout_exception_handler(req, SQLAlchemyTimeoutError("busy", None, None))
    assert timeout_response.status_code == 503
    assert timeout_response.headers["Retry-After"] == "5"

    monkeypatch.setattr(main.settings, "DEBUG", True)
    unhandled = await main.unhandled_exception_handler(req, RuntimeError("boom"))
    assert unhandled.status_code == 500
    assert b"boom" in unhandled.body


def test_health_check_uses_database_connection(monkeypatch):
    import main

    class Conn:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def execute(self, statement):
            self.statement = statement

    conn = Conn()
    monkeypatch.setattr(main.engine, "connect", lambda: conn)
    result = main.health_check()
    assert result["status"] == "healthy"
    assert result["database"] == "connected"
