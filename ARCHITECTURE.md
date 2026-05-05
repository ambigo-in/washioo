# Washioo Authentication System - Architecture Documentation

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENT APPLICATION                   │
│              (Web / Mobile / Desktop App)               │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTPS
                       ▼
┌─────────────────────────────────────────────────────────┐
│                   FASTAPI APPLICATION                   │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │          API ROUTERS (/routers)                  │  │
│  │  • Send OTP      • Signup                        │  │
│  │  • Signin        • Refresh Token                 │  │
│  │  • Logout                                        │  │
│  └──────────────────────────────────────────────────┘  │
│                       │                                 │
│  ┌──────────────────────────────────────────────────┐  │
│  │   SERVICES LAYER (/services)                    │  │
│  │  • AuthenticationService                         │  │
│  │    - send_otp()                                  │  │
│  │    - signup()                                    │  │
│  │    - signin()                                    │  │
│  │    - refresh_token()                             │  │
│  │    - logout()                                    │  │
│  │    - _generate_tokens()                          │  │
│  └──────────────────────────────────────────────────┘  │
│                       │                                 │
│  ┌──────────────────────────────────────────────────┐  │
│  │    REPOSITORIES LAYER (/repositories)            │  │
│  │  • UserRepository                                │  │
│  │  • OTPCodeRepository                             │  │
│  │  • RefreshTokenRepository                        │  │
│  │  • UserRoleRepository                            │  │
│  │  • AuditLogRepository                            │  │
│  │  • RoleRepository                                │  │
│  └──────────────────────────────────────────────────┘  │
│                       │                                 │
│  ┌──────────────────────────────────────────────────┐  │
│  │     UTILITIES & HELPERS (/utils)                 │  │
│  │  • TokenManager (JWT)                            │  │
│  │  • OTPManager (OTP Generation & Hashing)        │  │
│  │  • PasswordManager (Password Hashing)            │  │
│  │  • HashManager (Token Hashing)                   │  │
│  │  • rate_limiter (Rate Limiting)                  │  │
│  │  • sms_provider (SMSCountry Integration)             │  │
│  └──────────────────────────────────────────────────┘  │
│                       │                                 │
└───────────────────────┼─────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
   ┌─────────┐    ┌──────────┐   ┌──────────┐
   │PostgreSQL    │  SMSCountry  │   │  File    │
   │  Database    │   SMS    │   │  Logging │
   └─────────┘    └──────────┘   └──────────┘
```

## Layered Architecture

### 1. API Layer (Routers)

**File:** `routers/__init__.py`

Handles HTTP requests and responses.

**Responsibilities:**

- Parse incoming requests
- Validate input with Pydantic schemas
- Call service methods
- Handle exceptions
- Return formatted responses
- Rate limit checks

**Endpoints:**

```
POST /auth/send-otp      → send_otp()
POST /auth/signup        → signup()
POST /auth/signin        → signin()
POST /auth/refresh-token → refresh_token()
POST /auth/logout        → logout()
```

---

### 2. Service Layer (Business Logic)

**File:** `services/__init__.py`

Contains all business logic and orchestration.

**Class:** `AuthenticationService`

**Methods:**

```python
def send_otp(phone, ip)
def signup(phone, full_name, email, otp, role, ip)
def signin(phone, otp, ip)
def refresh_token(refresh_token, ip)
def logout(refresh_token, user_id)
def _generate_tokens(user_id, phone, ip)
```

**Responsibilities:**

- OTP generation and verification
- User creation and authentication
- Token generation and rotation
- Rate limit enforcement
- Business rule validation
- Audit logging

---

### 3. Repository Layer (Data Access)

**File:** `repositories/__init__.py`

Abstracts database operations.

**Classes:**

- `UserRepository` - User CRUD operations
- `OTPCodeRepository` - OTP management
- `RefreshTokenRepository` - Token management
- `UserRoleRepository` - Role assignment
- `AuditLogRepository` - Audit logging
- `RoleRepository` - Role queries

**Database Operations:**

```python
# User operations
UserRepository.get_by_phone(db, phone)
UserRepository.create(db, phone, full_name, email)
UserRepository.update(db, user_id, **kwargs)
UserRepository.update_last_login(db, user_id)

# OTP operations
OTPCodeRepository.create(db, phone, otp_hash, ...)
OTPCodeRepository.get_latest_for_phone(db, phone)
OTPCodeRepository.mark_consumed(db, otp_id)
OTPCodeRepository.increment_attempts(db, otp_id)

# Token operations
RefreshTokenRepository.create(db, user_id, token_hash, ...)
RefreshTokenRepository.get_by_hash(db, token_hash)
RefreshTokenRepository.revoke(db, token_id)
RefreshTokenRepository.revoke_by_hash(db, token_hash)
```

---

### 4. Utilities Layer

**Files:** `utils/*.py`

Provides reusable utilities.

#### JWT Management (`utils/security.py`)

```python
class TokenManager:
    def create_access_token(data, expires_delta)
    def create_refresh_token(data, expires_delta)
    def verify_token(token)
```

#### OTP Management (`utils/security.py`)

```python
class OTPManager:
    def generate_otp(length)
    def hash_otp(otp)
    def verify_otp(otp, hashed)
```

#### Password Hashing (`utils/security.py`)

```python
class PasswordManager:
    def hash_password(password)
    def verify_password(password, hashed)
```

#### Rate Limiting (`utils/rate_limiter.py`)

```python
class InMemoryRateLimiter:
    def is_allowed(key, max_requests, window_seconds)
    def reset(key)

def check_send_otp_rate_limit(phone, ip)
def check_auth_rate_limit(phone)
def check_refresh_rate_limit(user_id)
```

#### SMS Provider (`utils/sms_provider.py`)

```python
class SMSProvider (ABC):
    def send_otp(phone, otp)

class SMSCountrySMSProvider(SMSProvider):
    def send_otp(phone, otp)

class MockSMSProvider(SMSProvider):
    def send_otp(phone, otp)

class SMSProviderFactory:
    def create(provider_type)
```

---

### 5. Models Layer (Database Schema)

**File:** `models/__init__.py`

SQLAlchemy ORM models.

**Classes:**

```python
class User           # users table
class Role           # roles table
class UserRole       # user_roles table (many-to-many)
class OTPCode        # otp_codes table
class RefreshToken   # refresh_tokens table
class AuditLog       # audit_logs table
```

**Relationships:**

```
User
  ├─ user_roles (UserRole) → many-to-many with Role
  ├─ otp_codes (OTPCode)
  ├─ refresh_tokens (RefreshToken)
  └─ audit_logs (AuditLog)

Role
  └─ user_roles (UserRole) → many-to-many with User

UserRole
  ├─ user (User)
  └─ role (Role)

OTPCode
  └─ user (User)

RefreshToken
  └─ user (User)

AuditLog
  └─ user (User)
```

---

### 6. Schemas Layer (Validation)

**File:** `schemas/__init__.py`

Pydantic models for request/response validation.

**Request Schemas:**

- `SendOTPRequest` - Phone number
- `SignupRequest` - Full name, phone, email, OTP, role
- `SigninRequest` - Phone, OTP
- `RefreshTokenRequest` - Refresh token
- `LogoutRequest` - Refresh token

**Response Schemas:**

- `SendOTPResponse` - Message, user_exist
- `TokenResponse` - Access token, refresh token, token type
- `LogoutResponse` - Message
- `UserResponse` - User data
- `OTPErrorResponse` - Error details
- `TokenErrorResponse` - Error details

---

### 7. Configuration Layer

**File:** `config.py`

Environment configuration management.

```python
class Settings:
    # Application
    APP_NAME, APP_VERSION, DEBUG, ENVIRONMENT

    # Database
    DATABASE_URL, DATABASE_POOL_SIZE, DATABASE_MAX_OVERFLOW

    # JWT
    SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
    REFRESH_TOKEN_EXPIRE_DAYS

    # OTP
    OTP_LENGTH, OTP_EXPIRY_MINUTES, OTP_MAX_ATTEMPTS

    # Rate Limiting
    RATE_LIMIT_ENABLED, SEND_OTP_RATE_LIMIT
    SEND_OTP_IP_RATE_LIMIT, AUTH_RATE_LIMIT, REFRESH_RATE_LIMIT

    # SMSCountry
    SMS_COUNTRY_KEY, SMS_COUNTRY_TOKEN, SMS_HEADER

    # CORS
    CORS_ORIGINS, CORS_CREDENTIALS, CORS_METHODS, CORS_HEADERS

    # Logging
    LOG_LEVEL, LOG_FILE

    # Security
    PASSWORD_MIN_LENGTH, MAX_LOGIN_ATTEMPTS, LOCKOUT_DURATION_MINUTES

    # Frontend
    FRONTEND_URL
```

---

### 8. Database Layer

**File:** `database.py`

Database connection and session management.

```python
# Connection
engine = create_engine(DATABASE_URL, ...)
SessionLocal = sessionmaker(bind=engine)

# Dependency injection
def get_db_session() -> Session:
    # Used in FastAPI routes
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Context manager
@contextmanager
def get_db():
    # Used outside FastAPI routes
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialization
def init_db():
    Base.metadata.create_all(bind=engine)
```

---

## Data Flow Diagrams

### Send OTP Flow

```
Client
  │
  ├─ POST /auth/send-otp {phone}
  │
  ▼
Router
  ├─ Validate phone format (Pydantic)
  ├─ Extract client IP
  │
  ▼
Service (AuthenticationService)
  ├─ Check rate limit (IP + phone)
  ├─ Check if user exists (UserRepository)
  │
  ├─ Generate OTP
  │   └─ OTPManager.generate_otp()
  │
  ├─ Hash OTP
  │   └─ OTPManager.hash_otp()
  │
  ├─ Store OTP in DB
  │   └─ OTPCodeRepository.create()
  │
  ├─ Send OTP via SMS
  │   └─ sms_provider.send_otp() → SMSCountry API
  │
  ├─ Create audit log
  │   └─ AuditLogRepository.create()
  │
  ▼
Response
  └─ {message, user_exist}
```

### Signup Flow

```
Client
  │
  ├─ POST /auth/signup {full_name, phone, email, otp, role}
  │
  ▼
Router
  ├─ Validate inputs (Pydantic)
  │
  ▼
Service (AuthenticationService)
  ├─ Check rate limit
  ├─ Verify user doesn't exist
  │
  ├─ Get OTP from DB
  │   └─ OTPCodeRepository.get_latest_for_phone()
  │
  ├─ Validate OTP
  │   ├─ Check expiry
  │   ├─ Check not consumed
  │   └─ Verify OTP hash
  │       └─ OTPManager.verify_otp()
  │
  ├─ Mark OTP consumed
  │   └─ OTPCodeRepository.mark_consumed()
  │
  ├─ Create user
  │   └─ UserRepository.create()
  │
  ├─ Get role from DB
  │   └─ RoleRepository.get_by_name()
  │
  ├─ Assign role to user
  │   └─ UserRoleRepository.assign_role()
  │
  ├─ Generate tokens
  │   ├─ Create access token
  │   │   └─ TokenManager.create_access_token()
  │   │
  │   ├─ Create refresh token
  │   │   └─ TokenManager.create_refresh_token()
  │   │
  │   ├─ Hash refresh token
  │   │   └─ HashManager.hash_token()
  │   │
  │   └─ Store refresh token hash
  │       └─ RefreshTokenRepository.create()
  │
  ├─ Create audit log
  │   └─ AuditLogRepository.create()
  │
  ▼
Response
  └─ {message, access_token, refresh_token, token_type}
```

### Signin Flow

```
Client
  │
  ├─ POST /auth/signin {phone, otp}
  │
  ▼
Router → Service (similar to Signup but):
  ├─ Verify user EXISTS (not new signup)
  │
  ├─ Update last_login
  │   └─ UserRepository.update_last_login()
  │
  └─ Return tokens
```

### Refresh Token Flow

```
Client
  │
  ├─ POST /auth/refresh-token {refresh_token}
  │
  ▼
Service (AuthenticationService)
  ├─ Verify token signature
  │   └─ TokenManager.verify_token()
  │
  ├─ Check rate limit
  │   └─ check_refresh_rate_limit()
  │
  ├─ Hash refresh token
  │   └─ HashManager.hash_token()
  │
  ├─ Get token from DB
  │   └─ RefreshTokenRepository.get_by_hash()
  │
  ├─ Validate token
  │   ├─ Check not expired
  │   └─ Check not revoked
  │
  ├─ Revoke old token (rotation)
  │   └─ RefreshTokenRepository.revoke()
  │
  ├─ Generate new tokens
  │   ├─ TokenManager.create_access_token()
  │   ├─ TokenManager.create_refresh_token()
  │   └─ RefreshTokenRepository.create()
  │
  └─ Create audit log
```

---

## Security Architecture

### OTP Security

```
User Phone
    │
    ├─ Generate 6-digit OTP (cryptographically secure)
    │
    ├─ Hash with PBKDF2-SHA256 (100,000 iterations)
    │
    ├─ Store hash in database (not plain OTP)
    │
    ├─ Send OTP via SMS (not stored)
    │
    ├─ On verification: hash input and compare
    │
    └─ Mark as consumed (single-use)
```

### JWT Security

```
User ID + Phone
    │
    ├─ Create payload
    │   └─ {sub, active_role, roles, type: "access/refresh", exp, iat, jti}
    │
    ├─ Sign with HMAC-SHA256 using SECRET_KEY
    │
    ├─ Return to client (only client has it)
    │
    ├─ For refresh token: also store hash in DB
    │
    └─ On refresh: verify signature, validate DB hash, rotate
```

### Token Rotation

```
Initial Login
    │
    ├─ access_token (15 min)
    └─ refresh_token (7 days) → hash stored in DB

Access Token Expires
    │
    ├─ Client sends refresh_token
    │
    └─ Server:
        ├─ Verify signature
        ├─ Check DB hash
        ├─ Revoke old token (mark revoked_at)
        ├─ Generate new tokens
        └─ Return new access + new refresh_token
```

---

## Rate Limiting Architecture

### In-Memory Rate Limiter (Development)

```
Endpoint Request
    │
    ├─ Get client identifier (IP/Phone/User)
    │
    ├─ Check requests in time window
    │   ├─ Remove expired requests
    │   └─ Count current requests
    │
    ├─ Allow/Block decision
    │   └─ If count < limit: ALLOW
    │       Else: BLOCK (429)
    │
    └─ Return {is_allowed, stats}
```

### Rate Limit Strategies

```
Send OTP:
  ├─ Per phone: 3 requests / 15 minutes
  └─ Per IP: 10 requests / 1 hour

Signup/Signin:
  └─ Per phone: 5 attempts / 15 minutes

Refresh Token:
  └─ Per user: 20 attempts / 1 hour
```

---

## Database Schema Integration

### Key Tables

```
users
  ├─ id (UUID, PK)
  ├─ phone (unique)
  ├─ email (unique)
  ├─ full_name
  ├─ is_verified
  ├─ is_active
  └─ last_login

roles
  ├─ id (UUID, PK)
  └─ role_name (customer, cleaner, admin)

user_roles (M2M)
  ├─ user_id (FK → users)
  └─ role_id (FK → roles)

otp_codes
  ├─ id (UUID, PK)
  ├─ phone
  ├─ otp_code_hash
  ├─ expires_at (index)
  ├─ consumed_at
  └─ attempts

refresh_tokens
  ├─ id (UUID, PK)
  ├─ user_id (FK → users, index)
  ├─ token_hash (unique)
  ├─ expires_at
  ├─ revoked_at
  └─ created_at

audit_logs
  ├─ id (UUID, PK)
  ├─ user_id (FK → users, index)
  ├─ action
  ├─ entity_type (index)
  ├─ entity_id
  └─ metadata (JSON)
```

---

## Error Handling Architecture

### Exception Hierarchy

```
Exception
  │
  ├─ RateLimitExceeded (429)
  │   └─ "Too many requests"
  │
  ├─ ValueError (400)
  │   ├─ "User already exists"
  │   ├─ "Invalid OTP"
  │   ├─ "OTP expired"
  │   └─ "Token not found"
  │
  ├─ HTTPException (401)
  │   ├─ "Invalid token"
  │   ├─ "Token revoked"
  │   └─ "Unauthorized"
  │
  └─ HTTPException (500)
      └─ "Internal server error"
```

### Error Response Format

```json
{
  "message": "Human-readable error message",
  "error_code": "ERROR_CODE (optional)",
  "retry_after": 900 (for rate limit)
}
```

---

## Performance Considerations

### Database Optimizations

- Connection pooling (default: 20)
- Indexed columns:
  - users: phone, email, is_active
  - otp_codes: phone, expires_at
  - refresh_tokens: user_id
  - audit_logs: user_id, entity_type, entity_id

### Caching

- Settings cached with `@lru_cache()`
- JWT verification cached per request
- No database-level caching (for simplicity)

### Scalability

- Async request handling (FastAPI)
- Connection pooling
- Rate limiting ready for Redis
- Stateless service design
- Database queries optimized with indexes

---

## Monitoring & Observability

### Logging Points

```
INFO: OTP generated, OTP sent, User created, Token generated
WARNING: Invalid OTP, Rate limit exceeded, Token revoked
ERROR: Database errors, SMS failures, Validation errors
DEBUG: Query details, Token verification
```

### Key Metrics to Monitor

- OTP send success/failure rate
- User signup/signin success rate
- Token refresh rate
- Rate limit violations
- Database connection pool usage
- API response times
- Error rates by endpoint

---

## Deployment Architecture

### Development

```
Developer Machine
  └─ .venv (virtual environment)
      └─ Python 3.9+
          └─ Uvicorn (reload enabled)
              └─ SQLite or Local PostgreSQL
                  └─ Mock SMS (development)
```

### Production

```
Load Balancer (NGINX)
  │
  ├─ API Server 1 (Gunicorn + Uvicorn)
  ├─ API Server 2
  └─ API Server 3 (scaled)
      │
      ├─ PostgreSQL (production)
      │   └─ Backups
      │
      ├─ Redis (rate limiting, caching)
      │   └─ Persistence
      │
      ├─ SMSCountry (SMS)
      │
      └─ Monitoring
          ├─ Sentry (error tracking)
          ├─ Prometheus (metrics)
          └─ ELK Stack (logging)
```

---

This architecture provides:

- ✅ Clean separation of concerns
- ✅ Easy testing (dependency injection)
- ✅ Scalability (stateless design)
- ✅ Security (proper hashing, token rotation)
- ✅ Maintainability (layered approach)
- ✅ Performance (indexing, pooling)

