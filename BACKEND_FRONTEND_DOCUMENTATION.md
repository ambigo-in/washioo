# Backend API Documentation for Frontend

This document describes the currently implemented FastAPI backend for the Car Wash Service Portal. It is written for frontend integration and includes authentication, roles, models, API request/response shapes, booking flows, cleaner flows, admin flows, and implementation notes.

Source of truth in code:

- App entrypoint: `main.py`
- Auth routes: `routers/auth_router.py`
- Service/address/booking/cleaner/assignment routes: `routers/services_router.py`
- Request schemas: `schemas/auth_schema.py`, `schemas/booking_schema.py`
- Response formatting and business rules: `services/booking_service.py`, `services/user_service.py`
- Database models: `models/`

## Base API

Default local API:

```text
http://localhost:8000
```

Interactive OpenAPI docs are available when the backend is running:

```text
GET /docs
GET /redoc
GET /openapi.json
```

Health/public checks:

```http
GET /
```

Response:

```json
{
  "success": true,
  "message": "Car Wash Service Portal API Running Successfully"
}
```

```http
GET /health
```

Response:

```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0"
}
```

## Global Frontend Rules

### Content Type

All request bodies are JSON:

```http
Content-Type: application/json
```

### Endpoint Index

| Method | Path | Auth | Roles | Purpose |
|---|---|---|---|---|
| `GET` | `/` | No | Public | API status message |
| `GET` | `/health` | No | Public | Health check |
| `POST` | `/auth/send-otp` | No | Public | Send OTP |
| `POST` | `/auth/signup` | No | Public | Create user or add role |
| `POST` | `/auth/signin` | No | Public | Login with OTP |
| `POST` | `/auth/refresh-token` | No | Public | Rotate refresh token |
| `POST` | `/auth/logout` | Yes | Any authenticated | Revoke refresh token |
| `GET` | `/auth/me` | Yes | customer, cleaner, admin | Current user profile |
| `GET` | `/auth/admin/dashboard` | Yes | admin | Admin dashboard check |
| `GET` | `/auth/cleaner/jobs` | Yes | cleaner | Cleaner assignments alias |
| `GET` | `/auth/customer/bookings` | Yes | customer | Customer bookings alias |
| `GET` | `/services/` | No | Public | List active service categories |
| `GET` | `/services/service-categories/{service_id}` | No | Public | Get one service category |
| `POST` | `/services/admin/service-categories` | Yes | admin | Create service category |
| `PATCH` | `/services/admin/service-categories/{service_id}` | Yes | admin | Update service category |
| `DELETE` | `/services/admin/service-categories/{service_id}` | Yes | admin | Soft-delete service category |
| `POST` | `/services/address` | Yes | customer | Create address |
| `GET` | `/services/addresses` | Yes | customer | List current user's addresses |
| `PATCH` | `/services/address/{address_id}` | Yes | customer | Update own address |
| `DELETE` | `/services/address/{address_id}` | Yes | customer | Delete own address |
| `POST` | `/services/book` | Yes | customer | Create booking |
| `GET` | `/services/my-bookings` | Yes | customer | List own bookings |
| `GET` | `/services/my-bookings/{booking_id}` | Yes | customer | Get own booking |
| `PATCH` | `/services/my-bookings/{booking_id}` | Yes | customer | Update pending own booking |
| `POST` | `/services/my-bookings/{booking_id}/cancel` | Yes | customer | Cancel own booking |
| `GET` | `/services/admin/all-bookings` | Yes | admin | List all bookings |
| `GET` | `/services/admin/bookings/{booking_id}` | Yes | admin | Get booking |
| `PATCH` | `/services/admin/bookings/{booking_id}` | Yes | admin | Update booking |
| `GET` | `/services/admin/customers/{customer_id}/bookings` | Yes | admin | Customer booking history |
| `POST` | `/services/admin/bookings/{booking_id}/assign` | Yes | admin | Assign/reassign booking |
| `GET` | `/services/admin/bookings-by-status/{status}` | Yes | admin | Filter bookings by status |
| `POST` | `/services/admin/cleaners` | Yes | admin | Create cleaner profile |
| `GET` | `/services/admin/cleaners` | Yes | admin | List cleaner profiles |
| `GET` | `/services/admin/cleaners/{cleaner_id}` | Yes | admin | Get cleaner profile |
| `PATCH` | `/services/admin/cleaners/{cleaner_id}` | Yes | admin | Update cleaner profile |
| `DELETE` | `/services/admin/cleaners/{cleaner_id}` | Yes | admin | Delete cleaner profile |
| `GET` | `/services/cleaner/profile` | Yes | cleaner | Get current cleaner profile |
| `PATCH` | `/services/cleaner/availability` | Yes | cleaner | Update availability |
| `GET` | `/services/admin/assignments` | Yes | admin | List all assignments |
| `GET` | `/services/cleaner/assignments` | Yes | cleaner | List own assignments |
| `GET` | `/services/cleaner/assignments/{assignment_id}` | Yes | cleaner | Get own assignment |
| `POST` | `/services/cleaner/assignments/{assignment_id}/accept` | Yes | cleaner | Accept assignment |
| `POST` | `/services/cleaner/assignments/{assignment_id}/reject` | Yes | cleaner | Reject assignment |
| `POST` | `/services/cleaner/assignments/{assignment_id}/start` | Yes | cleaner | Start assignment |
| `POST` | `/services/cleaner/assignments/{assignment_id}/complete` | Yes | cleaner | Complete assignment |

### Authentication

Protected endpoints use JWT bearer auth:

```http
Authorization: Bearer <access_token>
```

Tokens are returned by signup, signin, and refresh-token endpoints.

Access token expiration is controlled by `ACCESS_TOKEN_EXPIRE_MINUTES`, default `30` minutes.
Refresh token expiration is controlled by `REFRESH_TOKEN_EXPIRE_DAYS`, default `7` days.

Refresh tokens are rotating. Calling `/auth/refresh-token` revokes the submitted refresh token and returns a new access token plus a new refresh token. The frontend must replace both stored tokens after refresh.

### Roles

Supported roles:

```text
customer
cleaner
admin
```

A single user can have multiple roles. Signup with a new role can add that role to an existing phone-number account if the user does not already have it.

The frontend should call:

```http
GET /auth/me
```

after login/signup to discover the user's active roles and route them to the correct UI.

### Common Error Shapes

Business errors usually return:

```json
{
  "detail": "Error message"
}
```

Validation errors from FastAPI/Pydantic usually return HTTP `422`:

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "field_name"],
      "msg": "Field required",
      "input": {}
    }
  ]
}
```

Auth/permission errors:

```json
{
  "detail": "Invalid or expired token"
}
```

```json
{
  "detail": "Access denied. Allowed roles: admin"
}
```

Rate limit errors are handled by SlowAPI and return HTTP `429` when exceeded.

### Rate Limits

Configured defaults:

| Endpoint group | Setting | Default |
|---|---:|---:|
| Send OTP | `SEND_OTP_RATE_LIMIT` | `3/15 minutes` |
| Signup/signin | `AUTH_RATE_LIMIT` | `5/15 minutes` |
| Refresh token | `REFRESH_RATE_LIMIT` | `20/hour` |

Rate limiting can be disabled with `RATE_LIMIT_ENABLED=False`.

### Date, Time, ID, Money Formats

| Type | Format |
|---|---|
| UUID | String UUID |
| Date | `YYYY-MM-DD` |
| Time | `HH:MM:SS` or `HH:MM` request accepted by Pydantic |
| DateTime | ISO string, for example `2026-05-01T10:15:30.123456` |
| Money/Decimal | Request may send number or numeric string; response sends number |

## Shared Models

### User

Returned by `/auth/me`.

```json
{
  "id": "uuid",
  "full_name": "John Doe",
  "phone": "+919999999999",
  "email": "john@example.com",
  "is_verified": true,
  "is_active": true,
  "roles": ["customer", "cleaner"],
  "created_at": "2026-05-01T10:15:30.123456"
}
```

### Service Category

```json
{
  "id": "uuid",
  "service_name": "Car Wash",
  "description": "Exterior and interior car wash service",
  "base_price": 499.0,
  "estimated_duration_minutes": 60,
  "is_active": true
}
```

### Address

Full address shape used in booking responses:

```json
{
  "id": "uuid",
  "address_label": "Home",
  "address_line1": "123 Main Street",
  "address_line2": "Apartment 4B",
  "landmark": "Near Mall",
  "city": "Mumbai",
  "state": "Maharashtra",
  "pincode": "400001",
  "country": "India",
  "latitude": 19.076,
  "longitude": 72.8777,
  "is_default": true
}
```

Note: address create/list/update endpoints currently return the same shape without `latitude` and `longitude`. Booking responses include `latitude` and `longitude`.

### Customer Booking

Used in customer booking lists/details and nested assignment booking responses.

```json
{
  "id": "uuid",
  "booking_reference": "BK-20260501-AB12CD34",
  "service_name": "Car Wash",
  "scheduled_date": "2026-05-10",
  "scheduled_time": "10:30:00",
  "booking_status": "pending",
  "estimated_price": 499.0,
  "final_price": null,
  "special_instructions": "Please call before arriving",
  "address": {
    "id": "uuid",
    "address_label": "Home",
    "address_line1": "123 Main Street",
    "address_line2": null,
    "landmark": null,
    "city": "Mumbai",
    "state": "Maharashtra",
    "pincode": "400001",
    "country": "India",
    "latitude": null,
    "longitude": null,
    "is_default": false
  },
  "assignment": null,
  "created_at": "2026-05-01T10:15:30.123456"
}
```

### Admin Booking

Admin booking includes customer and service IDs.

```json
{
  "id": "uuid",
  "booking_reference": "BK-20260501-AB12CD34",
  "customer_id": "uuid",
  "customer_name": "John Doe",
  "customer_phone": "+919999999999",
  "service_name": "Car Wash",
  "service_category_id": "uuid",
  "scheduled_date": "2026-05-10",
  "scheduled_time": "10:30:00",
  "booking_status": "assigned",
  "estimated_price": 499.0,
  "final_price": null,
  "special_instructions": "Please call before arriving",
  "address": {
    "id": "uuid",
    "address_label": "Home",
    "address_line1": "123 Main Street",
    "address_line2": null,
    "landmark": null,
    "city": "Mumbai",
    "state": "Maharashtra",
    "pincode": "400001",
    "country": "India",
    "latitude": null,
    "longitude": null,
    "is_default": false
  },
  "assignment": {
    "id": "uuid",
    "cleaner_id": "uuid",
    "assignment_status": "assigned",
    "assigned_at": "2026-05-01T10:30:00.123456",
    "accepted_at": null,
    "started_at": null,
    "completed_at": null,
    "cleaner_notes": "Assigned by dispatch"
  },
  "created_at": "2026-05-01T10:15:30.123456"
}
```

### Cleaner Profile

```json
{
  "id": "uuid",
  "user_id": "uuid",
  "full_name": "Cleaner Name",
  "phone": "+919999999998",
  "email": "cleaner@example.com",
  "vehicle_type": "bike",
  "government_id_number": "ID123",
  "service_radius_km": 10.0,
  "approval_status": "approved",
  "availability_status": "available",
  "rating": 0.0,
  "total_jobs_completed": 0,
  "created_at": "2026-05-01T10:15:30.123456"
}
```

Cleaner approval statuses:

```text
pending
approved
rejected
suspended
```

Cleaner availability statuses:

```text
offline
available
busy
```

### Assignment Summary

Nested inside booking responses.

```json
{
  "id": "uuid",
  "cleaner_id": "uuid",
  "assignment_status": "assigned",
  "assigned_at": "2026-05-01T10:30:00.123456",
  "accepted_at": null,
  "started_at": null,
  "completed_at": null,
  "cleaner_notes": "Assigned by dispatch"
}
```

### Full Assignment

Used by admin assignment APIs and cleaner assignment APIs.

```json
{
  "id": "uuid",
  "cleaner_id": "uuid",
  "assignment_status": "assigned",
  "assigned_at": "2026-05-01T10:30:00.123456",
  "accepted_at": null,
  "started_at": null,
  "completed_at": null,
  "cleaner_notes": "Assigned by dispatch",
  "booking_id": "uuid",
  "assigned_by_admin": "uuid",
  "cleaner": {
    "id": "uuid",
    "user_id": "uuid",
    "full_name": "Cleaner Name",
    "phone": "+919999999998",
    "email": "cleaner@example.com",
    "vehicle_type": "bike",
    "government_id_number": "ID123",
    "service_radius_km": 10.0,
    "approval_status": "approved",
    "availability_status": "available",
    "rating": 0.0,
    "total_jobs_completed": 0,
    "created_at": "2026-05-01T10:15:30.123456"
  },
  "booking": {
    "id": "uuid",
    "booking_reference": "BK-20260501-AB12CD34",
    "customer_id": "uuid",
    "customer_name": "John Doe",
    "customer_phone": "+919999999999",
    "service_name": "Car Wash",
    "service_category_id": "uuid",
    "scheduled_date": "2026-05-10",
    "scheduled_time": "10:30:00",
    "booking_status": "assigned",
    "estimated_price": 499.0,
    "final_price": null,
    "special_instructions": "Please call before arriving",
    "address": {},
    "assignment": {},
    "created_at": "2026-05-01T10:15:30.123456"
  }
}
```

Assignment statuses:

```text
assigned
accepted
rejected
completed
```

Booking statuses:

```text
pending
assigned
accepted
in_progress
completed
cancelled
```

## Auth APIs

Base prefix:

```text
/auth
```

### Send OTP

```http
POST /auth/send-otp
```

Public. Sends SMS OTP through Twilio Verify.

Request:

```json
{
  "phone_number": "+919999999999"
}
```

Response:

```json
{
  "message": "OTP sent successfully",
  "user_exist": true
}
```

Notes:

- `user_exist` tells the frontend whether this phone number already exists.
- OTP is verified only during signup/signin.

### Signup

```http
POST /auth/signup
```

Public. Creates a new user or adds a role to an existing user after OTP verification.

Request:

```json
{
  "full_name": "John Doe",
  "phone_number": "+919999999999",
  "email": "john@example.com",
  "otp_code": "123456",
  "role": "customer"
}
```

`role` must be one of:

```text
customer
cleaner
admin
```

Response for new user:

```json
{
  "message": "User created successfully",
  "access_token": "jwt",
  "refresh_token": "jwt",
  "token_type": "bearer",
  "is_new_user": true
}
```

Response for existing user adding a new role:

```json
{
  "message": "Role 'cleaner' added successfully to existing account",
  "access_token": "jwt",
  "refresh_token": "jwt",
  "token_type": "bearer",
  "is_new_user": false
}
```

Important validation/errors:

- Invalid OTP: `400 {"detail": "Invalid OTP"}`
- Invalid role: `400 {"detail": "Invalid role selected"}`
- Existing inactive account: `400 {"detail": "User account is inactive"}`
- Existing user already has role: `400 {"detail": "You already have the customer role"}`
- If role is `cleaner`, a cleaner profile is auto-created with default `approval_status=pending` and `availability_status=offline`.

### Signin

```http
POST /auth/signin
```

Public. Logs in an existing user after OTP verification.

Request:

```json
{
  "phone_number": "+919999999999",
  "otp_code": "123456"
}
```

Response:

```json
{
  "message": "Login successful",
  "access_token": "jwt",
  "refresh_token": "jwt",
  "token_type": "bearer"
}
```

Important validation/errors:

- Unknown phone: `400 {"detail": "User not found"}`
- Inactive user: `400 {"detail": "User account is inactive"}`
- Invalid OTP: `400 {"detail": "Invalid OTP"}`

### Refresh Token

```http
POST /auth/refresh-token
```

Public. Uses refresh token rotation.

Request:

```json
{
  "refresh_token": "jwt"
}
```

Response:

```json
{
  "access_token": "new_jwt",
  "refresh_token": "new_jwt",
  "token_type": "bearer"
}
```

Important validation/errors:

- Invalid/expired token: `401 {"detail": "Invalid refresh token"}`
- Revoked or unknown token: `401 {"detail": "Refresh token revoked or invalid"}`
- Token/user mismatch: `401 {"detail": "Refresh token does not belong to this user"}`

### Logout

```http
POST /auth/logout
Authorization: Bearer <access_token>
```

Requires any authenticated user. Revokes the submitted refresh token.

Request:

```json
{
  "refresh_token": "jwt"
}
```

Response:

```json
{
  "message": "Logged out successfully"
}
```

Error:

```json
{
  "detail": "Invalid token"
}
```

### Current User Profile

```http
GET /auth/me
Authorization: Bearer <access_token>
```

Allowed roles: `customer`, `cleaner`, `admin`.

Response:

```json
{
  "message": "User details fetched successfully",
  "user": {
    "id": "uuid",
    "full_name": "John Doe",
    "phone": "+919999999999",
    "email": "john@example.com",
    "is_verified": true,
    "is_active": true,
    "roles": ["customer"],
    "created_at": "2026-05-01T10:15:30.123456"
  }
}
```

### Admin Dashboard

```http
GET /auth/admin/dashboard
Authorization: Bearer <access_token>
```

Allowed role: `admin`.

Response:

```json
{
  "message": "Welcome Admin",
  "admin_id": "uuid",
  "roles": ["admin"]
}
```

### Cleaner Jobs Alias

```http
GET /auth/cleaner/jobs
Authorization: Bearer <access_token>
```

Allowed role: `cleaner`.

Response:

```json
{
  "message": "Cleaner jobs fetched successfully",
  "assignments": [],
  "total": 0
}
```

This is an alias-like endpoint for cleaner assignments, but it has no `status` filter. Prefer `/services/cleaner/assignments` for the fuller cleaner jobs screen.

### Customer Bookings Alias

```http
GET /auth/customer/bookings
Authorization: Bearer <access_token>
```

Allowed role: `customer`.

Response:

```json
{
  "message": "Customer bookings fetched successfully",
  "bookings": [],
  "total": 0
}
```

This is similar to `/services/my-bookings`. Prefer `/services/my-bookings` for customer booking screens.

## Public Service APIs

Base prefix:

```text
/services
```

### List Active Services

```http
GET /services/
```

Public. Returns active service categories only.

Response:

```json
{
  "message": "Services fetched successfully",
  "services": [
    {
      "id": "uuid",
      "service_name": "Car Wash",
      "description": "Exterior and interior car wash service",
      "base_price": 499.0,
      "estimated_duration_minutes": 60,
      "is_active": true
    }
  ],
  "total": 1
}
```

### Get Service Category

```http
GET /services/service-categories/{service_id}
```

Public.

Response:

```json
{
  "message": "Service fetched successfully",
  "service": {
    "id": "uuid",
    "service_name": "Car Wash",
    "description": "Exterior and interior car wash service",
    "base_price": 499.0,
    "estimated_duration_minutes": 60,
    "is_active": true
  }
}
```

Error:

```json
{
  "detail": "Service not found"
}
```

## Customer Address APIs

All address APIs require role `customer`.

### Create Address

```http
POST /services/address
Authorization: Bearer <access_token>
```

Request:

```json
{
  "address_label": "Home",
  "address_line1": "123 Main Street",
  "address_line2": "Apartment 4B",
  "landmark": "Near Mall",
  "city": "Mumbai",
  "state": "Maharashtra",
  "pincode": "400001",
  "country": "India",
  "latitude": 19.076,
  "longitude": 72.8777,
  "is_default": true
}
```

Required:

- `address_line1`

Defaults:

- `country`: `India`
- `is_default`: `false`

Response:

```json
{
  "message": "Address created successfully",
  "address": {
    "id": "uuid",
    "address_label": "Home",
    "address_line1": "123 Main Street",
    "address_line2": "Apartment 4B",
    "landmark": "Near Mall",
    "city": "Mumbai",
    "state": "Maharashtra",
    "pincode": "400001",
    "country": "India",
    "is_default": true
  }
}
```

Important frontend note:

- Latitude and longitude are accepted and stored, but not returned by this endpoint.
- The backend does not currently enforce only one default address per user.

### List My Addresses

```http
GET /services/addresses
Authorization: Bearer <access_token>
```

Response:

```json
{
  "message": "Addresses fetched successfully",
  "addresses": [
    {
      "id": "uuid",
      "address_label": "Home",
      "address_line1": "123 Main Street",
      "address_line2": null,
      "landmark": null,
      "city": "Mumbai",
      "state": "Maharashtra",
      "pincode": "400001",
      "country": "India",
      "is_default": false
    }
  ],
  "total": 1
}
```

### Update Address

```http
PATCH /services/address/{address_id}
Authorization: Bearer <access_token>
```

Only the address owner can update it.

Request accepts any subset:

```json
{
  "address_label": "Office",
  "address_line1": "New Address",
  "address_line2": null,
  "landmark": "Near Metro",
  "city": "Pune",
  "state": "Maharashtra",
  "pincode": "411001",
  "country": "India",
  "latitude": 18.5204,
  "longitude": 73.8567,
  "is_default": false
}
```

Response:

```json
{
  "message": "Address updated successfully",
  "address": {
    "id": "uuid",
    "address_label": "Office",
    "address_line1": "New Address",
    "address_line2": null,
    "landmark": "Near Metro",
    "city": "Pune",
    "state": "Maharashtra",
    "pincode": "411001",
    "country": "India",
    "is_default": false
  }
}
```

Error:

```json
{
  "detail": "Address not found"
}
```

### Delete Address

```http
DELETE /services/address/{address_id}
Authorization: Bearer <access_token>
```

Only the address owner can delete it.

Response:

```json
{
  "message": "Address deleted successfully",
  "address_id": "uuid"
}
```

## Customer Booking APIs

All customer booking APIs require role `customer`.

### Create Booking

```http
POST /services/book
Authorization: Bearer <access_token>
```

Request using an existing address:

```json
{
  "service_category_id": "uuid",
  "address_id": "uuid",
  "scheduled_date": "2026-05-10",
  "scheduled_time": "10:30:00",
  "special_instructions": "Please call before arriving"
}
```

Request creating a new address inline:

```json
{
  "service_category_id": "uuid",
  "address": {
    "address_label": "Home",
    "address_line1": "123 Main Street",
    "address_line2": null,
    "landmark": "Near Mall",
    "city": "Mumbai",
    "state": "Maharashtra",
    "pincode": "400001",
    "country": "India",
    "latitude": 19.076,
    "longitude": 72.8777,
    "is_default": false
  },
  "scheduled_date": "2026-05-10",
  "scheduled_time": "10:30:00",
  "special_instructions": "Please call before arriving"
}
```

Required:

- `service_category_id`
- `scheduled_date`
- `scheduled_time`
- either `address_id` or `address`

Response:

```json
{
  "message": "Booking created successfully",
  "booking": {
    "id": "uuid",
    "booking_reference": "BK-20260501-AB12CD34",
    "service_id": "uuid",
    "scheduled_date": "2026-05-10",
    "scheduled_time": "10:30:00",
    "booking_status": "pending",
    "estimated_price": 499.0,
    "created_at": "2026-05-01T10:15:30.123456"
  }
}
```

Important business rules:

- Service must exist and be active.
- Address must belong to the current customer.
- New bookings always start as `pending`.
- `estimated_price` is copied from the service category `base_price`.
- Booking reference format is `BK-YYYYMMDD-XXXXXXXX`.

Errors:

```json
{"detail": "Service not found or inactive"}
{"detail": "Please provide an address or address_id"}
{"detail": "Invalid address"}
```

### List My Bookings

```http
GET /services/my-bookings
Authorization: Bearer <access_token>
```

Response:

```json
{
  "message": "Bookings fetched successfully",
  "bookings": [],
  "total": 0
}
```

Bookings are ordered by newest first.

### Get My Booking Details

```http
GET /services/my-bookings/{booking_id}
Authorization: Bearer <access_token>
```

Only the booking owner can access it.

Response:

```json
{
  "message": "Booking fetched successfully",
  "booking": {
    "id": "uuid",
    "booking_reference": "BK-20260501-AB12CD34",
    "service_name": "Car Wash",
    "scheduled_date": "2026-05-10",
    "scheduled_time": "10:30:00",
    "booking_status": "pending",
    "estimated_price": 499.0,
    "final_price": null,
    "special_instructions": "Please call before arriving",
    "address": {},
    "assignment": null,
    "created_at": "2026-05-01T10:15:30.123456"
  }
}
```

Error:

```json
{
  "detail": "Booking not found"
}
```

### Update My Booking

```http
PATCH /services/my-bookings/{booking_id}
Authorization: Bearer <access_token>
```

Only the booking owner can update it. Customer can update only while `booking_status` is `pending`.

Request accepts any subset:

```json
{
  "service_category_id": "uuid",
  "address_id": "uuid",
  "scheduled_date": "2026-05-11",
  "scheduled_time": "12:00:00",
  "special_instructions": "Updated instructions"
}
```

Response:

```json
{
  "message": "Booking updated successfully",
  "booking": {}
}
```

Business rules:

- Only pending bookings can be updated by customer.
- If service is changed, `estimated_price` is recalculated from the new service.
- If address is changed, address must belong to customer.
- This endpoint does not accept inline address creation.

Errors:

```json
{"detail": "Booking not found"}
{"detail": "Only pending bookings can be updated by customer"}
{"detail": "Service not found or inactive"}
{"detail": "Invalid address"}
```

### Cancel My Booking

```http
POST /services/my-bookings/{booking_id}/cancel
Authorization: Bearer <access_token>
```

Request:

```json
{
  "reason": "Plans changed"
}
```

Response:

```json
{
  "message": "Booking cancelled successfully",
  "booking": {}
}
```

Important frontend note:

- `reason` is accepted by the request schema but is not currently stored.

Business rules:

- Completed and already cancelled bookings cannot be cancelled.
- In-progress bookings cannot be cancelled.
- Assigned or accepted bookings can currently be cancelled by customer.

Errors:

```json
{"detail": "Booking not found"}
{"detail": "Booking cannot be cancelled"}
{"detail": "Booking is already in progress"}
```

## Admin Service Category APIs

All admin APIs require role `admin`.

### Create Service Category

```http
POST /services/admin/service-categories
Authorization: Bearer <access_token>
```

Request:

```json
{
  "service_name": "Premium Car Wash",
  "description": "Exterior, interior, wax polish",
  "base_price": 999.0,
  "estimated_duration_minutes": 90,
  "is_active": true
}
```

Required:

- `service_name`
- `base_price`

Response:

```json
{
  "message": "Service created successfully",
  "service": {
    "id": "uuid",
    "service_name": "Premium Car Wash",
    "description": "Exterior, interior, wax polish",
    "base_price": 999.0,
    "estimated_duration_minutes": 90,
    "is_active": true
  }
}
```

### Update Service Category

```http
PATCH /services/admin/service-categories/{service_id}
Authorization: Bearer <access_token>
```

Request accepts any subset:

```json
{
  "service_name": "Premium Car Wash",
  "description": "Updated description",
  "base_price": 1099.0,
  "estimated_duration_minutes": 100,
  "is_active": true
}
```

Response:

```json
{
  "message": "Service updated successfully",
  "service": {}
}
```

### Delete Service Category

```http
DELETE /services/admin/service-categories/{service_id}
Authorization: Bearer <access_token>
```

This is a soft delete. It sets `is_active=false`.

Response:

```json
{
  "message": "Service deactivated successfully",
  "service_id": "uuid"
}
```

## Admin Booking APIs

All admin booking APIs require role `admin`.

### List All Bookings

```http
GET /services/admin/all-bookings
Authorization: Bearer <access_token>
```

Response:

```json
{
  "message": "All bookings fetched successfully",
  "bookings": [],
  "total": 0
}
```

Bookings are ordered by newest first.

### Get Booking

```http
GET /services/admin/bookings/{booking_id}
Authorization: Bearer <access_token>
```

Response:

```json
{
  "message": "Booking fetched successfully",
  "booking": {}
}
```

### Update Booking

```http
PATCH /services/admin/bookings/{booking_id}
Authorization: Bearer <access_token>
```

Request accepts any subset:

```json
{
  "service_category_id": "uuid",
  "address_id": "uuid",
  "scheduled_date": "2026-05-11",
  "scheduled_time": "12:00:00",
  "special_instructions": "Admin note",
  "booking_status": "assigned",
  "estimated_price": 499.0,
  "final_price": 599.0
}
```

`booking_status` must be one of:

```text
pending
assigned
accepted
in_progress
completed
cancelled
```

Response:

```json
{
  "message": "Booking updated successfully",
  "booking": {}
}
```

Errors:

```json
{"detail": "Booking not found"}
{"detail": "Invalid booking status"}
{"detail": "Service not found"}
{"detail": "Address not found"}
```

### Get Customer Bookings

```http
GET /services/admin/customers/{customer_id}/bookings
Authorization: Bearer <access_token>
```

Response:

```json
{
  "message": "Customer bookings fetched successfully",
  "customer_id": "uuid",
  "bookings": [],
  "total": 0
}
```

### Assign Booking To Cleaner

```http
POST /services/admin/bookings/{booking_id}/assign
Authorization: Bearer <access_token>
```

Request:

```json
{
  "cleaner_id": "cleaner_profile_uuid",
  "cleaner_notes": "Please handle this booking"
}
```

Response:

```json
{
  "message": "Booking assigned successfully",
  "assignment": {}
}
```

Important frontend note:

- `cleaner_id` is the `cleaner_profiles.id`, not `users.id`.
- If the booking already has an assignment, this endpoint reassigns it by updating the existing assignment.

Business rules:

- Booking must exist.
- Booking cannot be assigned if current status is `completed`, `cancelled`, or `in_progress`.
- Cleaner profile must exist.
- Cleaner must have `approval_status=approved`.
- Cleaner must have `availability_status=available`.
- Booking status becomes `assigned`.
- Assignment status becomes `assigned`.

Errors:

```json
{"detail": "Booking not found"}
{"detail": "Booking cannot be assigned in its current status"}
{"detail": "Cleaner profile not found"}
{"detail": "Cleaner is not approved"}
{"detail": "Cleaner is not available"}
```

### Get Bookings By Status

```http
GET /services/admin/bookings-by-status/{status}
Authorization: Bearer <access_token>
```

Allowed `status` values:

```text
pending
assigned
accepted
in_progress
completed
cancelled
```

Response:

```json
{
  "message": "Bookings with status 'pending' fetched successfully",
  "status": "pending",
  "bookings": [],
  "total": 0
}
```

Error:

```json
{
  "detail": "Invalid status. Valid statuses: pending, assigned, accepted, in_progress, completed, cancelled"
}
```

## Admin Cleaner Profile APIs

All admin cleaner APIs require role `admin`.

### Create Cleaner Profile

```http
POST /services/admin/cleaners
Authorization: Bearer <access_token>
```

Creates a cleaner profile for an existing user who already has the `cleaner` role.

Request:

```json
{
  "user_id": "user_uuid",
  "vehicle_type": "bike",
  "government_id_number": "GOV123",
  "service_radius_km": 10.0,
  "approval_status": "pending",
  "availability_status": "offline"
}
```

Required:

- `user_id`

Defaults:

- `approval_status`: `pending`
- `availability_status`: `offline`

Response:

```json
{
  "message": "Cleaner profile created successfully",
  "cleaner": {}
}
```

Errors:

```json
{"detail": "User not found"}
{"detail": "User does not have cleaner role"}
{"detail": "Cleaner profile already exists for this user"}
```

### List Cleaners

```http
GET /services/admin/cleaners
Authorization: Bearer <access_token>
```

Optional query params:

```text
approval_status=pending|approved|rejected|suspended
availability_status=offline|available|busy
```

Example:

```http
GET /services/admin/cleaners?approval_status=approved&availability_status=available
```

Response:

```json
{
  "message": "Cleaners fetched successfully",
  "cleaners": [],
  "total": 0
}
```

Cleaners are ordered by newest first.

### Get Cleaner

```http
GET /services/admin/cleaners/{cleaner_id}
Authorization: Bearer <access_token>
```

`cleaner_id` is `cleaner_profiles.id`.

Response:

```json
{
  "message": "Cleaner fetched successfully",
  "cleaner": {}
}
```

### Update Cleaner

```http
PATCH /services/admin/cleaners/{cleaner_id}
Authorization: Bearer <access_token>
```

Request accepts any subset:

```json
{
  "vehicle_type": "bike",
  "government_id_number": "GOV123",
  "service_radius_km": 12.5,
  "approval_status": "approved",
  "availability_status": "available"
}
```

Response:

```json
{
  "message": "Cleaner updated successfully",
  "cleaner": {}
}
```

### Delete Cleaner Profile

```http
DELETE /services/admin/cleaners/{cleaner_id}
Authorization: Bearer <access_token>
```

Response:

```json
{
  "message": "Cleaner profile deleted successfully",
  "cleaner_id": "uuid"
}
```

## Cleaner APIs

Cleaner APIs require role `cleaner`.

### Get My Cleaner Profile

```http
GET /services/cleaner/profile
Authorization: Bearer <access_token>
```

Returns the current user's cleaner profile. If the user has cleaner role but no profile, the backend creates one automatically.

Response:

```json
{
  "message": "Cleaner profile fetched successfully",
  "cleaner": {}
}
```

### Update My Availability

```http
PATCH /services/cleaner/availability
Authorization: Bearer <access_token>
```

Request:

```json
{
  "availability_status": "available"
}
```

Allowed values:

```text
offline
available
busy
```

Response:

```json
{
  "message": "Availability updated successfully",
  "cleaner": {}
}
```

Business rules:

- Cleaner must be approved before setting availability to `available` or `busy`.
- A non-approved cleaner can set availability to `offline`.

Error:

```json
{
  "detail": "Cleaner must be approved before becoming available or busy"
}
```

## Assignment APIs

### Admin List Assignments

```http
GET /services/admin/assignments
Authorization: Bearer <access_token>
```

Allowed role: `admin`.

Optional query param:

```text
status=assigned|accepted|rejected|completed
```

Response:

```json
{
  "message": "Assignments fetched successfully",
  "assignments": [],
  "total": 0
}
```

### Cleaner List My Assignments

```http
GET /services/cleaner/assignments
Authorization: Bearer <access_token>
```

Allowed role: `cleaner`.

Optional query param:

```text
status=assigned|accepted|rejected|completed
```

Response:

```json
{
  "message": "Cleaner assignments fetched successfully",
  "assignments": [],
  "total": 0
}
```

Error for invalid status:

```json
{
  "detail": "Invalid assignment status"
}
```

### Cleaner Get Assignment

```http
GET /services/cleaner/assignments/{assignment_id}
Authorization: Bearer <access_token>
```

Cleaner can only access their own assignment.

Response:

```json
{
  "message": "Assignment fetched successfully",
  "assignment": {}
}
```

### Cleaner Accept Assignment

```http
POST /services/cleaner/assignments/{assignment_id}/accept
Authorization: Bearer <access_token>
```

Request:

```json
{
  "cleaner_notes": "Accepted, will arrive on time"
}
```

Response:

```json
{
  "message": "Assignment accepted successfully",
  "assignment": {}
}
```

Business rules:

- Assignment must be `assigned`.
- Booking must be `assigned`.
- Assignment becomes `accepted`.
- Booking becomes `accepted`.
- Cleaner availability becomes `busy`.
- `accepted_at` is set.

Errors:

```json
{"detail": "Assignment not found"}
{"detail": "Only assigned bookings can be accepted"}
{"detail": "Booking is not available for acceptance"}
```

### Cleaner Reject Assignment

```http
POST /services/cleaner/assignments/{assignment_id}/reject
Authorization: Bearer <access_token>
```

Request:

```json
{
  "cleaner_notes": "Cannot take this job"
}
```

Response:

```json
{
  "message": "Assignment rejected successfully",
  "assignment": {}
}
```

Business rules:

- Assignment must be `assigned`.
- Assignment becomes `rejected`.
- Booking returns to `pending`.
- Cleaner availability becomes `available`.

Error:

```json
{
  "detail": "Assignment cannot be rejected"
}
```

### Cleaner Start Assignment

```http
POST /services/cleaner/assignments/{assignment_id}/start
Authorization: Bearer <access_token>
```

Request:

```json
{
  "cleaner_notes": "Reached customer location"
}
```

Response:

```json
{
  "message": "Assignment started successfully",
  "assignment": {}
}
```

Business rules:

- Assignment must be `accepted`.
- Assignment must not already have `started_at`.
- Booking must be `accepted`.
- `started_at` is set.
- Booking becomes `in_progress`.
- Assignment status remains `accepted` until completion.

Errors:

```json
{"detail": "Only accepted assignments can be started"}
{"detail": "Assignment has already been started"}
{"detail": "Booking is not ready to start"}
```

### Cleaner Complete Assignment

```http
POST /services/cleaner/assignments/{assignment_id}/complete
Authorization: Bearer <access_token>
```

Request:

```json
{
  "cleaner_notes": "Completed successfully",
  "final_price": 599.0
}
```

Response:

```json
{
  "message": "Assignment completed successfully",
  "assignment": {}
}
```

Business rules:

- Assignment must have been started.
- Assignment status must still be `accepted`.
- Booking must be `in_progress`.
- Assignment becomes `completed`.
- `completed_at` is set.
- Booking becomes `completed`.
- If provided, `final_price` is saved on booking.
- Cleaner availability becomes `available`.
- Cleaner `total_jobs_completed` increments by 1.

Errors:

```json
{"detail": "Assignment must be started before completion"}
{"detail": "Assignment cannot be completed"}
{"detail": "Booking is not in progress"}
```

## End-to-End Flows

### Customer Signup/Login Flow

1. Customer enters phone number.
2. Frontend calls `POST /auth/send-otp`.
3. Customer enters OTP.
4. For new customer, frontend calls `POST /auth/signup` with role `customer`.
5. For existing customer, frontend calls `POST /auth/signin`.
6. Store `access_token` and `refresh_token`.
7. Call `GET /auth/me`.
8. Route user based on `user.roles`.

### Customer Booking Flow

1. Fetch services with `GET /services/`.
2. Fetch addresses with `GET /services/addresses`.
3. If needed, create address with `POST /services/address`.
4. Create booking with `POST /services/book`.
5. Show booking status as `pending`.
6. Customer can edit booking with `PATCH /services/my-bookings/{booking_id}` while status is `pending`.
7. Customer can cancel with `POST /services/my-bookings/{booking_id}/cancel` unless booking is `in_progress`, `completed`, or `cancelled`.
8. Track booking through `GET /services/my-bookings` or `GET /services/my-bookings/{booking_id}`.

### Cleaner Onboarding Flow

1. Cleaner signs up with role `cleaner`.
2. Backend auto-creates cleaner profile in `pending/offline` state.
3. Admin views cleaners with `GET /services/admin/cleaners?approval_status=pending`.
4. Admin approves cleaner with `PATCH /services/admin/cleaners/{cleaner_id}` and `approval_status=approved`.
5. Cleaner sets availability with `PATCH /services/cleaner/availability` and `availability_status=available`.

### Admin Assignment Flow

1. Admin views pending bookings with `GET /services/admin/bookings-by-status/pending`.
2. Admin views available approved cleaners with `GET /services/admin/cleaners?approval_status=approved&availability_status=available`.
3. Admin assigns booking with `POST /services/admin/bookings/{booking_id}/assign`.
4. Booking becomes `assigned`.
5. Assignment becomes `assigned`.
6. Cleaner receives assignment in `GET /services/cleaner/assignments?status=assigned`.

### Cleaner Job Execution Flow

1. Cleaner lists assignments with `GET /services/cleaner/assignments`.
2. Cleaner accepts with `POST /services/cleaner/assignments/{assignment_id}/accept`.
3. Booking status becomes `accepted`; cleaner availability becomes `busy`.
4. Cleaner starts job with `POST /services/cleaner/assignments/{assignment_id}/start`.
5. Booking status becomes `in_progress`.
6. Cleaner completes job with `POST /services/cleaner/assignments/{assignment_id}/complete`.
7. Assignment becomes `completed`; booking becomes `completed`; cleaner availability becomes `available`.

### Rejection/Reassignment Flow

1. Cleaner rejects an assigned job with `POST /services/cleaner/assignments/{assignment_id}/reject`.
2. Assignment becomes `rejected`.
3. Booking returns to `pending`.
4. Cleaner availability becomes `available`.
5. Admin assigns the booking again with `POST /services/admin/bookings/{booking_id}/assign`.

## State Machines

### Booking Status Transitions

Implemented transitions:

```text
pending -> assigned        admin assigns cleaner
assigned -> accepted       cleaner accepts assignment
assigned -> pending        cleaner rejects assignment
accepted -> in_progress    cleaner starts assignment
in_progress -> completed   cleaner completes assignment
any allowed -> cancelled   customer/admin cancellation/update rules vary
```

Customer update is allowed only when:

```text
booking_status == pending
```

Customer cancellation is blocked when:

```text
booking_status in completed, cancelled, in_progress
```

Admin can directly update `booking_status` to any valid booking status through the admin update booking endpoint.

### Assignment Status Transitions

Implemented transitions:

```text
assigned -> accepted
assigned -> rejected
accepted -> completed
```

Starting a job does not change assignment status. It sets `started_at` and changes booking status to `in_progress`.

## Database Models Implemented in SQLAlchemy

These are the models currently imported by `main.py` and created by `Base.metadata.create_all`.

### `users`

| Field | Type | Notes |
|---|---|---|
| `id` | UUID | Primary key |
| `full_name` | string | Nullable |
| `phone` | string | Unique, required |
| `email` | string | Unique |
| `is_verified` | boolean | Default `false` |
| `is_active` | boolean | Default `true` |
| `created_at` | datetime | UTC default |

### `roles`

| Field | Type | Notes |
|---|---|---|
| `id` | UUID | Primary key |
| `role_name` | string | Unique, required |
| `description` | text | Optional |
| `created_at` | datetime | UTC default |

Default roles from `database.sql`:

```text
customer
cleaner
admin
```

### `user_roles`

| Field | Type | Notes |
|---|---|---|
| `id` | UUID | Primary key |
| `user_id` | UUID | FK users.id |
| `role_id` | UUID | FK roles.id |
| `assigned_at` | datetime | UTC default |

### `refresh_tokens`

| Field | Type | Notes |
|---|---|---|
| `id` | UUID | Primary key |
| `user_id` | UUID | FK users.id |
| `token_hash` | string | Unique; stores raw JWT despite the field name |
| `created_at` | datetime | UTC default |
| `expires_at` | datetime | Expiration |
| `revoked_at` | datetime/null | Set on logout/rotation |

### `otp_codes`

SQLAlchemy model exists, but current OTP sending/verification uses Twilio Verify directly. The implemented code does not store OTP code rows locally.

| Field | Type | Notes |
|---|---|---|
| `id` | UUID | Primary key |
| `phone` | string | Required |
| `purpose` | string | Default `login` |
| `created_at` | datetime | UTC default |
| `expires_at` | datetime | Expiration |
| `consumed_at` | datetime/null | Not used by current Twilio flow |

### `addresses`

| Field | Type | Notes |
|---|---|---|
| `id` | UUID | Primary key |
| `user_id` | UUID | FK users.id |
| `address_label` | string | Home/Office/Other |
| `address_line1` | string | Required |
| `address_line2` | string | Optional |
| `landmark` | string | Optional |
| `city` | string | Optional |
| `state` | string | Optional |
| `pincode` | string | Optional |
| `country` | string | Default `India` |
| `latitude` | numeric | Optional |
| `longitude` | numeric | Optional |
| `is_default` | boolean | Default `false` |
| `created_at` | datetime | UTC default |
| `updated_at` | datetime | UTC on update |

### `service_categories`

| Field | Type | Notes |
|---|---|---|
| `id` | UUID | Primary key |
| `service_name` | string | Unique, required |
| `description` | string | Optional |
| `base_price` | numeric | Required |
| `estimated_duration_minutes` | integer | Optional |
| `is_active` | boolean | Default `true` |
| `created_at` | datetime | UTC default |

Default rows from `database.sql`:

```text
Car Wash - 499.00 - 60 minutes
Bike Wash - 199.00 - 30 minutes
```

### `bookings`

| Field | Type | Notes |
|---|---|---|
| `id` | UUID | Primary key |
| `booking_reference` | string | Unique, generated |
| `customer_id` | UUID | FK users.id |
| `service_category_id` | UUID | FK service_categories.id |
| `address_id` | UUID | FK addresses.id |
| `scheduled_date` | date | Optional at DB level, required in create request |
| `scheduled_time` | time | Optional at DB level, required in create request |
| `special_instructions` | string | Optional |
| `booking_status` | string | Default `pending` |
| `estimated_price` | numeric | Required |
| `final_price` | numeric | Optional |
| `created_at` | datetime | UTC default |
| `updated_at` | datetime | UTC on update |

### `cleaner_profiles`

| Field | Type | Notes |
|---|---|---|
| `id` | UUID | Primary key |
| `user_id` | UUID | Unique FK users.id |
| `vehicle_type` | string | Optional |
| `government_id_number` | string | Optional |
| `service_radius_km` | numeric | Optional |
| `approval_status` | string | Default `pending` |
| `availability_status` | string | Default `offline` |
| `rating` | numeric | Default `0` |
| `total_jobs_completed` | integer | Default `0` |
| `created_at` | datetime | UTC default |
| `updated_at` | datetime | UTC on update |

### `booking_assignments`

| Field | Type | Notes |
|---|---|---|
| `id` | UUID | Primary key |
| `booking_id` | UUID | Unique FK bookings.id |
| `cleaner_id` | UUID | FK cleaner_profiles.id |
| `assigned_by_admin` | UUID | FK users.id |
| `assigned_at` | datetime | UTC |
| `accepted_at` | datetime/null | Set on accept |
| `started_at` | datetime/null | Set on start |
| `completed_at` | datetime/null | Set on complete |
| `assignment_status` | string | Default `assigned` |
| `cleaner_notes` | string | Optional |

## Database-Only/Future Tables in `database.sql`

`database.sql` also defines these tables, but there are no implemented SQLAlchemy models/routes/services for them in the current backend:

- `payments`
- `cleaner_settlements`
- `notifications`
- `reviews`
- `audit_logs`

Frontend should not build production UI screens that require these APIs until backend endpoints are added. They can be planned as future modules.

## Frontend Implementation Checklist

Auth:

- Store access token and refresh token securely.
- Attach bearer token to all protected endpoints.
- On `401`, try `/auth/refresh-token` once, replace both tokens, then retry original request.
- After signin/signup, call `/auth/me` to get roles.
- Support multi-role users.

Customer UI:

- Service list from `GET /services/`.
- Address list/create/update/delete.
- Booking create with either existing `address_id` or inline `address`.
- Booking detail/list with status badges.
- Edit booking only while `pending`.
- Disable cancel for `in_progress`, `completed`, and `cancelled`.

Admin UI:

- Service category CRUD.
- Booking list/detail/status filters.
- Cleaner list filters by approval and availability.
- Cleaner approval/suspension/update.
- Assignment list filter by status.
- Assign/reassign bookings using `cleaner_profiles.id`.

Cleaner UI:

- Profile screen using `GET /services/cleaner/profile`.
- Availability control.
- Block or explain `available/busy` until approved.
- Assignment list/detail.
- Actions by state:
  - `assigned`: accept or reject
  - `accepted` with no `started_at`: start
  - `accepted` with `started_at`: complete
  - `completed`/`rejected`: read-only

## Important Current Gaps/Notes

- No payment APIs are currently implemented.
- No notification APIs are currently implemented.
- No reviews/rating submission APIs are currently implemented.
- No pagination is implemented on list endpoints.
- No search is implemented on list endpoints.
- No file upload/profile image APIs are implemented.
- Address default uniqueness is not enforced.
- Cancellation reason is accepted but not persisted.
- Address latitude/longitude are accepted but not returned by direct address endpoints.
- Admin can create/update service categories but public list returns only active services.
- Cleaner assignment uses `cleaner_profiles.id`, not user ID.
