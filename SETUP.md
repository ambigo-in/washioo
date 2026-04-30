# Washioo Authentication System - Setup Guide

A complete step-by-step guide to set up and run the authentication system.

## Prerequisites

- Python 3.9+
- PostgreSQL 12+ (or use Docker)
- pip (Python package manager)
- Git
- Twilio Account (for SMS)

## Step 1: Initial Setup

### Clone Repository

```bash
cd /path/to/your/project
git clone <repository-url>
cd washioo
```

### Create Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Database Setup

### Option A: Docker (Recommended)

```bash
# Start PostgreSQL with Docker Compose
docker-compose up -d postgres

# Wait for PostgreSQL to be ready
docker-compose exec postgres psql -U washioo_user -d washioo_db -f /docker-entrypoint-initdb.d/schema.sql
```

### Option B: Manual PostgreSQL Setup

```bash
# Create database
createdb -U postgres washioo_db

# Run schema
psql -U postgres -d washioo_db -f database.sql

# Verify
psql -U postgres -d washioo_db -c "\dt"
```

### Option C: PostgreSQL with Homebrew (macOS)

```bash
# Install PostgreSQL
brew install postgresql

# Start service
brew services start postgresql

# Create database
createdb washioo_db

# Run schema
psql -d washioo_db -f database.sql
```

## Step 3: Configuration

### Copy Environment Template

```bash
cp .env.example .env
```

### Edit .env File

#### On Windows (use Notepad or VSCode):

```
notepad .env
```

#### On macOS/Linux:

```bash
nano .env
```

### Configure Required Variables

#### 1. Database Configuration

```env
# For Docker setup:
DATABASE_URL=postgresql://washioo_user:washioo_password@localhost:5432/washioo_db

# For manual PostgreSQL setup:
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/washioo_db

# For production:
DATABASE_URL=postgresql://prod_user:prod_password@prod_host.com:5432/washioo_prod
```

#### 2. JWT Secret Key

Generate a secure key:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Add to .env:

```env
SECRET_KEY=<generated-key-here>
```

#### 3. Twilio Configuration

Get from [Twilio Console](https://www.twilio.com/console):

```env
TWILIO_ACCOUNT_SID=AC... (your Account SID)
TWILIO_AUTH_TOKEN=... (your Auth Token)
TWILIO_PHONE_NUMBER=+1234567890 (your Twilio number)
```

#### 4. Optional: Development Settings

For development/testing, use mock SMS:

```env
DEBUG=True
ENVIRONMENT=development
```

This will log OTPs to console instead of sending SMS.

### Full .env Example (Development)

```env
# Application
APP_NAME="Washioo - Car Washing Service"
DEBUG=True
ENVIRONMENT=development

# Database
DATABASE_URL=postgresql://washioo_user:washioo_password@localhost:5432/washioo_db

# JWT
SECRET_KEY=your-generated-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# OTP
OTP_LENGTH=6
OTP_EXPIRY_MINUTES=5
OTP_MAX_ATTEMPTS=5

# Twilio
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
```

## Step 4: Verify Installation

### Check Python

```bash
python --version
# Should be 3.9+
```

### Check Virtual Environment

```bash
which python
# Should show path to venv
```

### Check Dependencies

```bash
pip list
# Should show FastAPI, SQLAlchemy, etc.
```

## Step 5: Run Application

### Development Mode

```bash
uvicorn main:app --reload
```

Output should show:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### Production Mode

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

## Step 6: Verify Setup

### Health Check

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "healthy",
  "service": "Washioo - Car Washing Service",
  "version": "1.0.0"
}
```

### API Documentation

Visit: http://localhost:8000/docs

## Step 7: Test Endpoints

### Test 1: Send OTP

```bash
curl -X POST http://localhost:8000/auth/send-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919876543210"}'
```

Expected response:

```json
{
  "message": "OTP sent successfully",
  "user_exist": false
}
```

**Note:** If DEBUG=True, check console for the OTP code (e.g., "123456")

### Test 2: Signup

```bash
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

Expected response:

```json
{
  "message": "User created successfully",
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer"
}
```

### Test 3: Signin

```bash
# First, get OTP again
curl -X POST http://localhost:8000/auth/send-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919876543210"}'

# Then signin
curl -X POST http://localhost:8000/auth/signin \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+919876543210",
    "otp": "123456"
  }'
```

### Test 4: Refresh Token

```bash
curl -X POST http://localhost:8000/auth/refresh-token \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "your_refresh_token_here"}'
```

### Test 5: Logout

```bash
curl -X POST http://localhost:8000/auth/logout \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "your_refresh_token_here"}'
```

## Troubleshooting

### Issue: "ModuleNotFoundError"

**Solution:** Activate virtual environment

```bash
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### Issue: "Database connection refused"

**Cause:** PostgreSQL not running
**Solution:**

```bash
# Check if PostgreSQL is running
# Windows: Check Services
# macOS: brew services list
# Linux: systemctl status postgresql

# Or use Docker:
docker-compose up -d postgres
```

### Issue: "Could not translate host name"

**Cause:** PostgreSQL hostname incorrect
**Solution:** Update DATABASE_URL in .env to correct host

### Issue: "OTP not being sent"

**Cause:** Debug mode enabled or Twilio credentials incorrect
**Solution:**

- Check console logs for OTP (if DEBUG=True)
- Verify Twilio credentials in .env
- Check Twilio account has credits

### Issue: "CORS error in frontend"

**Cause:** Frontend origin not in CORS_ORIGINS
**Solution:** Update CORS_ORIGINS in .env

```env
CORS_ORIGINS=["http://localhost:3000", "http://yourfrontend.com"]
```

### Issue: "Invalid token signature"

**Cause:** SECRET_KEY changed or mismatch
**Solution:** Ensure all instances use same SECRET_KEY

## Docker Deployment

### Using Docker Compose (All-in-One)

```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f api

# Stop services
docker-compose down
```

### Manual Docker Build

```bash
# Build image
docker build -t washioo-api .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  -e SECRET_KEY=your-secret-key \
  -e TWILIO_ACCOUNT_SID=... \
  -e TWILIO_AUTH_TOKEN=... \
  -e TWILIO_PHONE_NUMBER=... \
  washioo-api
```

## Production Deployment

### Before Deploying

1. **Security Checklist**
   - [ ] DEBUG=False
   - [ ] ENVIRONMENT=production
   - [ ] SECRET_KEY is strong and random
   - [ ] Database has backups
   - [ ] CORS_ORIGINS whitelist only trusted domains
   - [ ] HTTPS/SSL enabled
   - [ ] Rate limiting configured

2. **Database**
   - [ ] Run migrations: `alembic upgrade head`
   - [ ] Setup indexes: Check database.sql
   - [ ] Configure backups
   - [ ] Test restore process

3. **Environment**
   - [ ] Copy .env.example to .env
   - [ ] Update all production values
   - [ ] Never commit .env to git
   - [ ] Add .env to .gitignore

4. **Monitoring**
   - [ ] Setup logging to files
   - [ ] Configure alerting
   - [ ] Monitor database performance
   - [ ] Setup error tracking (Sentry)

### Deploy with Gunicorn + Nginx

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 \
  -k uvicorn.workers.UvicornWorker \
  -b 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile - \
  main:app
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name api.washioo.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Monitoring & Logs

### View Logs

```bash
# Live logs (Docker)
docker-compose logs -f api

# Logs from file
tail -f /var/log/washioo/auth.log
```

### Monitor Performance

```bash
# Database connections
psql -d washioo_db -c "SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname;"

# API metrics
curl http://localhost:8000/health
```

## Support & Documentation

- **API Docs:** http://localhost:8000/docs
- **README:** See README.md
- **Testing:** See TESTING.md
- **Issues:** Check error logs and stdout

## Next Steps

1. Customize configuration for your environment
2. Setup CI/CD pipeline
3. Configure monitoring and alerting
4. Test with real Twilio account
5. Deploy to production
6. Setup backups and disaster recovery

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Twilio Documentation](https://www.twilio.com/docs)
- [Docker Documentation](https://docs.docker.com/)
