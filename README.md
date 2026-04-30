# Washioo - Authentication System

Production-grade OTP-based authentication system for the Washioo car washing service platform.

## Features

✅ **OTP-Based Authentication** - Secure SMS-based OTP verification using Twilio  
✅ **JWT Token Management** - Access and refresh token generation with rotation  
✅ **Rate Limiting** - Built-in rate limiting to prevent abuse  
✅ **Role-Based Access Control** - Support for customer, cleaner, and admin roles  
✅ **Audit Logging** - Complete audit trail of all authentication events  
✅ **PostgreSQL Optimized** - Designed for scalability and performance  
✅ **Production-Ready** - Security best practices, error handling, and logging

## Project Structure

```
.
├── config.py                 # Configuration and settings management
├── database.py              # Database connection and session management
├── database.sql             # PostgreSQL schema
├── main.py                  # FastAPI application entry point
├── requirements.txt         # Python dependencies
├── docker-compose.yml       # Docker Compose configuration
├── Dockerfile              # Docker image definition
├── .env.example             # Environment variables template
├── models/
│   └── __init__.py         # SQLAlchemy ORM models
├── schemas/
│   └── __init__.py         # Pydantic request/response schemas
├── repositories/
│   └── __init__.py         # Data access layer (DAL)
├── services/
│   └── __init__.py         # Business logic layer
├── routers/
│   └── __init__.py         # API endpoints
└── utils/
    ├── __init__.py         # Utility exports
    ├── security.py         # JWT, OTP, hashing utilities
    ├── rate_limiter.py     # Rate limiting implementation
    └── sms_provider.py     # SMS provider abstraction (Twilio)
```

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repo-url>
cd washioo

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your configuration
nano .env
```

Required environment variables:

- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret (generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
- `TWILIO_ACCOUNT_SID`: Twilio account ID
- `TWILIO_AUTH_TOKEN`: Twilio auth token
- `TWILIO_PHONE_NUMBER`: Your Twilio phone number

### 4. Setup Database

```bash
# Option 1: Using Docker Compose (Recommended)
docker-compose up -d postgres

# Option 2: Using existing PostgreSQL
# Ensure PostgreSQL is running and create database:
createdb -U postgres washioo_db
psql -U postgres -d washioo_db -f database.sql
```

### 5. Run Application

```bash
# Development
uvicorn main:app --reload

# Production
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

Application will be available at: `http://localhost:8000`

## API Endpoints

### 1. Send OTP

**POST** `/auth/send-otp`

Send OTP to a phone number.

**Request:**

```json
{
  "phone": "+919876543210"
}
```

**Response:**

```json
{
  "message": "OTP sent successfully",
  "user_exist": true
}
```

**Rate Limit:** 3 requests per 15 minutes per phone, 10 requests per hour per IP

---

### 2. Signup

**POST** `/auth/signup`

Create a new user account (for new users only).

**Request:**

```json
{
  "full_name": "John Doe",
  "phone": "+919876543210",
  "email": "john@example.com",
  "otp": "123456",
  "role": "customer"
}
```

**Response:**

```json
{
  "message": "User created successfully",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Rate Limit:** 5 attempts per 15 minutes

---

### 3. Signin

**POST** `/auth/signin`

Authenticate existing user (for users who already exist).

**Request:**

```json
{
  "phone": "+919876543210",
  "otp": "123456"
}
```

**Response:**

```json
{
  "message": "Login successful",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Rate Limit:** 5 attempts per 15 minutes

---

### 4. Refresh Token

**POST** `/auth/refresh-token`

Exchange refresh token for new access token (with token rotation).

**Request:**

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Rate Limit:** 20 refreshes per hour

---

### 5. Logout

**POST** `/auth/logout`

Logout user by revoking refresh token.

**Request:**

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:**

```json
{
  "message": "Logged out successfully"
}
```

---

## Authentication Flow

### Signup Flow (New User)

```
1. User enters phone number
   └─> POST /auth/send-otp
   ├─> System checks if user exists (returns user_exist: false)
   ├─> Generate OTP
   ├─> Send OTP via SMS (Twilio)
   └─> Store hashed OTP (5 min expiry)

2. User receives OTP and submits signup form
   └─> POST /auth/signup
   ├─> Validate OTP
   ├─> Create user account
   ├─> Assign role
   ├─> Generate tokens
   └─> Return access_token + refresh_token
```

### Signin Flow (Existing User)

```
1. User enters phone number
   └─> POST /auth/send-otp
   ├─> System checks if user exists (returns user_exist: true)
   ├─> Generate OTP
   ├─> Send OTP via SMS
   └─> Store hashed OTP

2. User receives OTP and submits signin form
   └─> POST /auth/signin
   ├─> Validate OTP
   ├─> Verify user
   ├─> Update last_login
   ├─> Generate tokens
   └─> Return access_token + refresh_token
```

### Token Refresh Flow

```
User's access token expires
   └─> POST /auth/refresh-token
   ├─> Validate refresh token signature
   ├─> Verify token in database (not revoked, not expired)
   ├─> Revoke old refresh token (rotation)
   ├─> Generate new tokens
   └─> Return new access_token + refresh_token
```

### Logout Flow

```
User clicks logout
   └─> POST /auth/logout
   ├─> Get refresh token
   ├─> Mark token as revoked
   ├─> Log audit entry
   └─> Return success message
```

## Security Features

### OTP Security

- ✅ 6-digit random OTP generation
- ✅ PBKDF2-SHA256 hashing (100,000 iterations)
- ✅ 5-minute expiration
- ✅ Single-use OTP enforcement
- ✅ Maximum 5 verification attempts
- ✅ Secure random number generation

### JWT Security

- ✅ Access tokens: 30 minutes (short-lived)
- ✅ Refresh tokens: 7 days (long-lived)
- ✅ Token rotation on refresh
- ✅ Hashed token storage in database
- ✅ Token revocation support
- ✅ HMAC-SHA256 algorithm

### Rate Limiting

- ✅ Send OTP: 3/15min per phone, 10/1hr per IP
- ✅ Signup/Signin: 5/15min per phone
- ✅ Refresh: 20/1hr per user
- ✅ In-memory implementation (development)
- ✅ Redis-compatible design (production)

### Additional Security

- ✅ Input validation with Pydantic
- ✅ Phone number validation
- ✅ Email validation
- ✅ CORS protection
- ✅ Comprehensive audit logging
- ✅ Request IP tracking
- ✅ Error message sanitization

## Environment Variables

See [.env.example](.env.example) for complete reference.

### Critical Variables

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/washioo_db
SECRET_KEY=your-secret-key-minimum-32-characters
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=+1234567890
```

## Development

### Using Mock SMS (Testing)

Set `DEBUG=True` or `ENVIRONMENT=development` to use mock SMS provider:

```bash
DEBUG=True
```

This will log OTPs to console instead of sending real SMS.

### Database Migrations

For production, use Alembic for migrations:

```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

## Deployment

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Scale API service
docker-compose up -d --scale api=3
```

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Set `ENVIRONMENT=production`
- [ ] Generate strong `SECRET_KEY`
- [ ] Configure `DATABASE_URL` with production database
- [ ] Setup Twilio credentials
- [ ] Configure CORS origins
- [ ] Enable HTTPS/SSL
- [ ] Setup Redis for rate limiting (optional, for scalability)
- [ ] Configure logging to file
- [ ] Setup monitoring and alerts
- [ ] Run database migrations
- [ ] Test all endpoints thoroughly

## API Documentation

Once running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Testing

### Manual API Testing

Using cURL:

```bash
# Send OTP
curl -X POST http://localhost:8000/auth/send-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919876543210"}'

# Signup
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "phone": "+919876543210",
    "email": "john@example.com",
    "otp": "123456",
    "role": "customer"
  }'
```

## Troubleshooting

### Database Connection Error

```
Error: could not translate host name "postgres" to address
```

**Solution:** Ensure PostgreSQL is running and DATABASE_URL is correct

### OTP Not Sending

```
Twilio credentials error
```

**Solution:**

- Verify TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN
- Check Twilio phone number format (+country_code...)
- Ensure Twilio account has credits

### Token Validation Error

```
Invalid token: Signature verification failed
```

**Solution:** Ensure SECRET_KEY is consistent across requests

## Performance Optimization

- Database connection pooling (default: 20 connections)
- Indexed database queries on frequently used columns
- JWT validation with cached settings
- In-memory rate limiting for development
- Async/await support for concurrent requests

## Monitoring

Logs are written to console. In production, configure:

```python
# In config.py
LOG_FILE="/var/log/washioo/auth.log"
```

Key events to monitor:

- Failed OTP verifications
- Rate limit exceeded
- Token validation failures
- User signup/signin events
- Database connection issues

## Contributing

1. Follow PEP 8 style guide
2. Add tests for new features
3. Update documentation
4. Ensure all endpoints work correctly

## License

Proprietary - Washioo Services

## Support

For issues or questions:

- Create a GitHub issue
- Contact: support@washioo.com

## Changelog

### v1.0.0 (2024)

- Initial release
- 5 core authentication APIs
- OTP-based authentication
- JWT token management
- Rate limiting
- Audit logging
