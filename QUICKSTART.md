# Washioo API - Quick Start Guide

## 🚀 Quick Setup (5 minutes)

### Step 1: Clone/Navigate & Setup

```bash
cd washioo
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
```

### Step 2: Configure Environment

```bash
cp .env.example .env
# Edit .env with:
# - DATABASE_URL (PostgreSQL)
# - JWT_SECRET (any secure string)
# - TWILIO credentials
```

### Step 3: Setup Database

```bash
# Create database
createdb washioo

# Run schema
psql -U postgres -d washioo -f schema.sql
```

### Step 4: Run Server

```bash
uvicorn app.main:app --reload
```

API will be at: **http://localhost:8000**

---

## 📱 API Examples

### 1️⃣ Send OTP

```bash
curl -X POST "http://localhost:8000/auth/send-otp" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+919876543210"}'
```

**Response:**

```json
{
  "success": true,
  "message": "OTP sent",
  "status": "pending"
}
```

### 2️⃣ Verify OTP

```bash
curl -X POST "http://localhost:8000/auth/verify-otp" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+919876543210", "otp_code": "123456"}'
```

**Response:**

```json
{
  "success": true,
  "message": "OTP verified"
}
```

### 3️⃣ Register User

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+919876543210", "full_name": "John Doe"}'
```

**Response:**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "phone_number": "+919876543210",
  "full_name": "John Doe",
  "role": "customer",
  "is_verified": true,
  "created_at": "2026-04-29T10:30:00",
  "updated_at": "2026-04-29T10:30:00"
}
```

### 4️⃣ Login

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+919876543210"}'
```

**Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 5️⃣ List Packages

```bash
# All packages
curl -X GET "http://localhost:8000/packages"

# Only car packages
curl -X GET "http://localhost:8000/packages?vehicle_type=car"

# Only bike packages
curl -X GET "http://localhost:8000/packages?vehicle_type=bike"
```

**Response:**

```json
[
  {
    "id": "650e8400-e29b-41d4-a716-446655440001",
    "vehicle_type": "car",
    "package_name": "Basic Wash",
    "description": "Exterior wash and dry",
    "price": "149.00",
    "duration_minutes": 30
  },
  {
    "id": "650e8400-e29b-41d4-a716-446655440002",
    "vehicle_type": "car",
    "package_name": "Deep Clean",
    "description": "Interior + exterior deep cleaning",
    "price": "349.00",
    "duration_minutes": 60
  }
]
```

### 6️⃣ Create Vehicle (Optional - before booking)

```bash
curl -X POST "http://localhost:8000/vehicles" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "vehicle_type": "car",
    "vehicle_model": "Maruti Swift",
    "vehicle_number": "KA-01-AB-1234"
  }'
```

### 7️⃣ Create Booking

```bash
curl -X POST "http://localhost:8000/bookings" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "vehicle_id": "550e8400-e29b-41d4-a716-446655440000",
    "package_id": "650e8400-e29b-41d4-a716-446655440001",
    "address": "123 Main Street, Bangalore",
    "latitude": 12.9716,
    "longitude": 77.5946,
    "scheduled_at": "2026-04-29T14:00:00",
    "payment_method": "cash"
  }'
```

**Response:**

```json
{
  "id": "750e8400-e29b-41d4-a716-446655440000",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "vehicle_id": "550e8400-e29b-41d4-a716-446655440000",
  "package_id": "650e8400-e29b-41d4-a716-446655440001",
  "cleaner_id": null,
  "address": "123 Main Street, Bangalore",
  "latitude": 12.9716,
  "longitude": 77.5946,
  "scheduled_at": "2026-04-29T14:00:00",
  "status": "pending",
  "payment_status": "unpaid",
  "payment_method": "cash",
  "created_at": "2026-04-29T10:35:00",
  "updated_at": "2026-04-29T10:35:00"
}
```

### 8️⃣ Get Bookings

```bash
curl -X GET "http://localhost:8000/bookings" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 9️⃣ Get Booking Details

```bash
curl -X GET "http://localhost:8000/bookings/750e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 🔟 Admin: Add Cleaner

```bash
curl -X POST "http://localhost:8000/admin/cleaners" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN" \
  -d '{
    "phone_number": "+919876543211",
    "full_name": "Cleaner John",
    "role": "cleaner"
  }'
```

### 1️⃣1️⃣ Admin: Assign Cleaner to Booking

```bash
curl -X POST "http://localhost:8000/admin/bookings/750e8400-e29b-41d4-a716-446655440000/assign" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN" \
  -d '{"cleaner_id": "850e8400-e29b-41d4-a716-446655440000"}'
```

**Response:**

```json
{
  "success": true,
  "message": "Cleaner assigned",
  "booking_id": "750e8400-e29b-41d4-a716-446655440000",
  "cleaner_id": "850e8400-e29b-41d4-a716-446655440000"
}
```

SMS sent automatically to cleaner!

### 1️⃣2️⃣ Cleaner: Get Assigned Jobs

```bash
curl -X GET "http://localhost:8000/cleaner/jobs?cleaner_id=850e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer CLEANER_JWT_TOKEN"
```

### 1️⃣3️⃣ Cleaner: Update Job Status

```bash
curl -X PATCH "http://localhost:8000/cleaner/jobs/750e8400-e29b-41d4-a716-446655440000/status" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer CLEANER_JWT_TOKEN" \
  -d '{"status": "in_progress"}'
```

### 1️⃣4️⃣ Cleaner: Update Location

```bash
curl -X PATCH "http://localhost:8000/cleaner/location" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer CLEANER_JWT_TOKEN" \
  -d '{
    "cleaner_id": "850e8400-e29b-41d4-a716-446655440000",
    "latitude": 12.9716,
    "longitude": 77.5946
  }'
```

### 1️⃣5️⃣ WebSocket: Real-time Booking Updates

```bash
# Terminal 1: Connect to WebSocket
wscat -c "ws://localhost:8000/ws/booking/750e8400-e29b-41d4-a716-446655440000"

# Terminal 2: Send status update
wscat -c "ws://localhost:8000/ws/booking/750e8400-e29b-41d4-a716-446655440000"
> {"type": "status_update", "status": "in_progress", "timestamp": "2026-04-29T14:05:00"}

# Terminal 1 will receive:
< {"type":"status_update","status":"in_progress","booking_id":"750e8400-e29b-41d4-a716-446655440000","timestamp":"2026-04-29T14:05:00"}
```

---

## 🔐 Getting JWT Token

After login, use the `access_token` in Authorization header:

```bash
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## 📚 API Documentation

Visit **http://localhost:8000/docs** for interactive Swagger UI

---

## 🐛 Common Issues

### Database Connection Error

```
psycopg2.OperationalError: could not connect to server
```

**Solution**: Ensure PostgreSQL is running and DATABASE_URL is correct

### Twilio Errors

```
TwilioRestException: [403] Forbidden
```

**Solution**: Verify TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_VERIFY_SERVICE_SID

### Invalid Token Error

```
"detail": "Invalid or expired token"
```

**Solution**:

1. Ensure token is not expired
2. Check JWT_SECRET matches
3. Use correct token from login response

---

## 📝 Sample Data in Database

After running schema.sql, you'll have:

### Packages:

- **Car - Basic Wash**: ₹149 (30 min)
- **Car - Deep Clean**: ₹349 (60 min)
- **Car - Premium Detail**: ₹599 (90 min)
- **Bike - Basic Wash**: ₹79 (20 min)
- **Bike - Deep Clean**: ₹199 (40 min)

---

## 🎯 Typical User Journey

1. **Customer** → Send OTP → Verify → Register → Login (get JWT)
2. **Customer** → Get Packages → Create Booking
3. **Admin** → View Bookings → Assign Cleaner to Booking
4. **Cleaner** → Get Jobs → Update Status → Update Location
5. **Customer** → Connect WebSocket → See Real-time Updates
6. **Service Complete** → SMS Notification Sent

---

## 💾 Production Deployment

### Render

1. Push to GitHub
2. Create new Web Service on Render
3. Set environment variables
4. Deploy

### Docker

```bash
docker build -t washioo .
docker run -p 8000:8000 --env-file .env washioo
```

---

**Ready to go! 🚀**
