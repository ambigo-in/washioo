# Washioo API - Testing Guide

## 🧪 Testing Overview

This guide covers manual API testing using curl, Postman, or similar tools. Endpoints are organized by module.

---

## 🔑 Prerequisites

1. API running at `http://localhost:8000`
2. PostgreSQL database initialized
3. Environment variables configured (.env file)

---

## 📋 Getting Test Data

### Step 1: Get Packages (No Auth Required)

```bash
curl -X GET "http://localhost:8000/packages"
```

Keep track of package IDs for booking creation.

---

## 🔐 Authentication Testing

### Test 1: Send OTP

```bash
curl -X POST "http://localhost:8000/auth/send-otp" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+919876543210"}'
```

**Expected Response:**

```json
{
  "success": true,
  "message": "OTP sent",
  "status": "pending"
}
```

### Test 2: Verify OTP

```bash
curl -X POST "http://localhost:8000/auth/verify-otp" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+919876543210", "otp_code": "123456"}'
```

**Expected Response:**

```json
{
  "success": true,
  "message": "OTP verified"
}
```

**Note**: Get actual OTP code from Twilio console (or your SMS inbox in test account)

### Test 3: Register User (Customer)

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+919876543210",
    "full_name": "John Doe"
  }'
```

**Expected Response:**

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

**Save user ID for later use**

### Test 4: Login (Get JWT Token)

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+919876543210"}'
```

**Expected Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Save access_token for authenticated requests**

---

## 📦 Packages Testing

### Test 5: List All Packages

```bash
curl -X GET "http://localhost:8000/packages"
```

### Test 6: List Car Packages Only

```bash
curl -X GET "http://localhost:8000/packages?vehicle_type=car"
```

### Test 7: List Bike Packages Only

```bash
curl -X GET "http://localhost:8000/packages?vehicle_type=bike"
```

### Test 8: Get Specific Package

```bash
curl -X GET "http://localhost:8000/packages/{package_id}"
```

---

## 🚗 Bookings Testing

### Test 9: Create Booking

```bash
# Prerequisites: Have JWT token, vehicle_id, package_id

curl -X POST "http://localhost:8000/bookings" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "vehicle_id": "550e8400-e29b-41d4-a716-446655440000",
    "package_id": "650e8400-e29b-41d4-a716-446655440001",
    "address": "123 Main Street, Bangalore, India",
    "latitude": 12.9716,
    "longitude": 77.5946,
    "scheduled_at": "2026-04-29T14:00:00",
    "payment_method": "cash"
  }'
```

**Expected Response:**

```json
{
  "id": "750e8400-e29b-41d4-a716-446655440000",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "vehicle_id": "550e8400-e29b-41d4-a716-446655440000",
  "package_id": "650e8400-e29b-41d4-a716-446655440001",
  "cleaner_id": null,
  "address": "123 Main Street, Bangalore, India",
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

**Save booking_id for later tests**

### Test 10: List All Bookings

```bash
curl -X GET "http://localhost:8000/bookings" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Test 11: Get Booking Details

```bash
curl -X GET "http://localhost:8000/bookings/{booking_id}" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Test 12: Update Booking Status

```bash
curl -X PATCH "http://localhost:8000/bookings/{booking_id}/status" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"status": "pending"}'
```

---

## 👷 Admin Testing

### Test 13: Register Cleaner (via Admin)

```bash
# First register cleaner as customer, then promote to admin role
# Or create cleaner directly:

curl -X POST "http://localhost:8000/admin/cleaners" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN" \
  -d '{
    "phone_number": "+919876543211",
    "full_name": "Cleaner John",
    "role": "cleaner"
  }'
```

**Save cleaner_id**

### Test 14: List All Cleaners

```bash
curl -X GET "http://localhost:8000/admin/cleaners" \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN"
```

### Test 15: Assign Cleaner to Booking

```bash
curl -X POST "http://localhost:8000/admin/bookings/{booking_id}/assign" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN" \
  -d '{"cleaner_id": "{cleaner_id}"}'
```

**Expected Response:**

```json
{
  "success": true,
  "message": "Cleaner assigned",
  "booking_id": "750e8400-e29b-41d4-a716-446655440000",
  "cleaner_id": "850e8400-e29b-41d4-a716-446655440000"
}
```

**SMS automatically sent to cleaner!**

### Test 16: List All Bookings (Admin)

```bash
curl -X GET "http://localhost:8000/admin/bookings" \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN"
```

### Test 17: Get Booking Details (Admin)

```bash
curl -X GET "http://localhost:8000/admin/bookings/{booking_id}" \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN"
```

---

## 🚴 Cleaner Operations Testing

### Test 18: Get Assigned Jobs

```bash
curl -X GET "http://localhost:8000/cleaner/jobs?cleaner_id={cleaner_id}" \
  -H "Authorization: Bearer CLEANER_JWT_TOKEN"
```

### Test 19: Update Job Status (Cleaner)

```bash
curl -X PATCH "http://localhost:8000/cleaner/jobs/{booking_id}/status" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer CLEANER_JWT_TOKEN" \
  -d '{"status": "en_route"}'
```

**Status flow:**

- pending → assigned
- assigned → en_route
- en_route → in_progress
- in_progress → completed

### Test 20: Update Cleaner Location

```bash
curl -X PATCH "http://localhost:8000/cleaner/location" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer CLEANER_JWT_TOKEN" \
  -d '{
    "cleaner_id": "{cleaner_id}",
    "latitude": 12.9726,
    "longitude": 77.5956
  }'
```

### Test 21: Get Cleaner Location

```bash
curl -X GET "http://localhost:8000/cleaner/location/{cleaner_id}" \
  -H "Authorization: Bearer CLEANER_JWT_TOKEN"
```

---

## 🔌 WebSocket Testing

### Test 22: Connect to WebSocket

```bash
# Using wscat (install: npm install -g wscat)
wscat -c "ws://localhost:8000/ws/booking/{booking_id}"
```

### Test 23: Send Status Update via WebSocket

```
> {"type": "status_update", "status": "in_progress", "timestamp": "2026-04-29T14:05:00"}

< {"type":"status_update","status":"in_progress","booking_id":"{booking_id}","timestamp":"2026-04-29T14:05:00"}
```

### Test 24: Send Location Update via WebSocket

```
> {"type": "location_update", "latitude": 12.9726, "longitude": 77.5956, "timestamp": "2026-04-29T14:06:00"}

< {"type":"location_update","latitude":12.9726,"longitude":77.5956,"booking_id":"{booking_id}","timestamp":"2026-04-29T14:06:00"}
```

### Test 25: Broadcast Message via WebSocket

```
> {"type": "message", "message": "On the way!", "timestamp": "2026-04-29T14:07:00"}

< {"type":"message","message":"On the way!","booking_id":"{booking_id}","timestamp":"2026-04-29T14:07:00"}
```

---

## 🧮 Expected Seeded Data

### Packages (Pre-loaded)

**Car Packages:**

1. Basic Wash - ₹149 (30 min)
2. Deep Clean - ₹349 (60 min)
3. Premium Detail - ₹599 (90 min)

**Bike Packages:**

1. Basic Wash - ₹79 (20 min)
2. Deep Clean - ₹199 (40 min)

---

## 📊 Test Scenarios

### Scenario 1: Complete Customer Journey

1. ✅ Send OTP
2. ✅ Verify OTP
3. ✅ Register
4. ✅ Login (get JWT)
5. ✅ List packages
6. ✅ Create booking
7. ✅ Get booking status (pending)

### Scenario 2: Admin Assignment

1. ✅ Create/add cleaner
2. ✅ List cleaners
3. ✅ Assign cleaner to booking
4. ✅ Verify SMS sent
5. ✅ Check booking status (assigned)

### Scenario 3: Cleaner Service

1. ✅ Login as cleaner
2. ✅ Get assigned jobs
3. ✅ Update status (en_route)
4. ✅ Update location
5. ✅ Update status (in_progress)
6. ✅ Update status (completed)

### Scenario 4: Real-time Tracking

1. ✅ Customer connects WebSocket
2. ✅ Cleaner updates location
3. ✅ Customer sees location update
4. ✅ Cleaner updates status
5. ✅ Customer sees status update

---

## 🔍 Error Testing

### Test 26: Invalid OTP

```bash
curl -X POST "http://localhost:8000/auth/verify-otp" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+919876543210", "otp_code": "000000"}'
```

**Expected:** 400 error

### Test 27: Missing Authorization Header

```bash
curl -X GET "http://localhost:8000/bookings"
```

**Expected:** 403 error

### Test 28: Invalid JWT Token

```bash
curl -X GET "http://localhost:8000/bookings" \
  -H "Authorization: Bearer invalid_token"
```

**Expected:** 401 error

### Test 29: Booking Not Found

```bash
curl -X GET "http://localhost:8000/bookings/00000000-0000-0000-0000-000000000000" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected:** 404 error

### Test 30: Duplicate User Registration

```bash
# Try registering same phone number twice
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+919876543210", "full_name": "Duplicate User"}'
```

**Expected:** 400 error

---

## 📈 Performance Testing

### Load Test with Apache Bench

```bash
# Install: sudo apt-get install apache2-utils

# Simple 100 requests
ab -n 100 -c 10 http://localhost:8000/packages

# More intense: 1000 requests, 50 concurrent
ab -n 1000 -c 50 http://localhost:8000/packages
```

---

## ✅ Checklist

Use this checklist to verify all functionality:

- [ ] OTP authentication working
- [ ] User registration successful
- [ ] JWT token generation working
- [ ] Package listing functional
- [ ] Booking creation working
- [ ] Booking retrieval working
- [ ] Admin cleaner assignment working
- [ ] SMS notifications received
- [ ] Cleaner job retrieval working
- [ ] Location tracking working
- [ ] WebSocket connections working
- [ ] Status updates propagating
- [ ] Location updates propagating
- [ ] Error handling for invalid requests
- [ ] CORS headers correct

---

## 🐛 Debugging

### Enable verbose curl

```bash
curl -v -X GET "http://localhost:8000/packages"
```

### Check API logs

```bash
# If running with --reload
# Logs appear in terminal

# If running in background
journalctl -u washioo -f
```

### Test database connection

```bash
psql -U postgres -d washioo -c "SELECT COUNT(*) FROM packages;"
```

### Verify Twilio credentials

```bash
# Check .env file
cat .env | grep TWILIO
```

---

## 🎯 Next Steps

1. **Manual Testing**: Run through all tests above
2. **Integration Testing**: Test frontend with backend
3. **Load Testing**: Test with ab or Locust
4. **Security Testing**: Test role-based access
5. **Deployment Testing**: Test on staging environment

---

**Happy Testing! 🚀**
