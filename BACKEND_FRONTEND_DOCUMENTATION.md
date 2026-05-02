# Backend API Documentation for Frontend

This document is the frontend integration guide for the current FastAPI backend of the Car/Bike Service platform.

It reflects the latest production-oriented backend changes:

- Role-specific auth APIs for Customer, Cleaner, and Admin.
- Generic `/auth/send-otp`, `/auth/signup`, and `/auth/signin` are disabled.
- First admin is created by Flyway SQL migration.
- Existing admins can create or update other admins through protected APIs.
- Cleaner signup requires Aadhaar number and optionally accepts driving license number.
- Aadhaar and driving license are never returned in full; responses contain masked values and boolean flags.
- Booking status changes are controlled by lifecycle APIs, not arbitrary admin status patches.
- Major list APIs support pagination with `limit` and `offset`.

## Source Files

| Area | Files |
| --- | --- |
| App entrypoint | `main.py` |
| Auth APIs | `routers/auth_router.py` |
| User APIs | `routers/user_router.py` |
| Services, address, booking, cleaner, assignment APIs | `routers/services_router.py` |
| Auth schemas | `schemas/auth_schema.py` |
| Booking/service schemas | `schemas/booking_schema.py` |
| User schemas | `schemas/user_schema.py` |
| Booking and cleaner business logic | `services/booking_service.py` |
| Auth business logic | `services/auth_service.py` |
| User business logic | `services/user_service.py` |
| Flyway migrations | `db/migration/` |

## Base URL

Local default:

```txt
http://localhost:8000
```

OpenAPI:

```txt
GET /docs
GET /redoc
GET /openapi.json
```

## Authentication

Protected APIs require:

```http
Authorization: Bearer <access_token>
```

Tokens are returned by role-specific signup/signin and refresh APIs.

Refresh tokens rotate. After calling `/auth/refresh-token`, replace both stored tokens on the frontend.

## Roles

Supported roles:

```txt
customer
cleaner
admin
```

Frontend should route by the API used for login plus the returned `account_type`.

Recommended routing:

| Auth API | Route user to |
| --- | --- |
| `/auth/customer/signin` | Customer app/dashboard |
| `/auth/cleaner/signin` | Cleaner app/dashboard |
| `/auth/admin/signin` | Admin dashboard |

You can also call:

```http
GET /auth/me
```

to get the authenticated user's roles.

## Important Production Rules

### Disabled Legacy Auth

Do not use these APIs in frontend flows:

```txt
POST /auth/send-otp
POST /auth/signup
POST /auth/signin
```

They return `410 Gone`.

Use role-specific auth APIs instead.

### Admin Creation

There is no public admin signup.

First admin:

- Created through Flyway migration `V2__create_initial_admin.sql`.

Additional admins:

- Created by an existing admin through `POST /auth/admin/create`.
- Updated by an existing admin through `PATCH /auth/admin/{admin_id}`.

### Cleaner Identity

Cleaner signup requires:

- `aadhaar_number`

Cleaner signup optionally accepts:

- `driving_license_number`

Frontend must not expect full Aadhaar or license values in responses. The API returns masked values only.

## Common Formats

| Type | Format |
| --- | --- |
| UUID | String UUID |
| Date | `YYYY-MM-DD` |
| Time | `HH:MM:SS` or `HH:MM` |
| DateTime | ISO string |
| Money | Number |

## Common Errors

Business error:

```json
{
  "detail": "Error message"
}
```

Validation error:

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

Common HTTP statuses:

| Status | Meaning |
| --- | --- |
| `400` | Business validation failed |
| `401` | Missing, invalid, or expired token |
| `403` | Role not allowed |
| `404` | Entity not found |
| `410` | Deprecated endpoint disabled |
| `422` | Request validation failed |
| `429` | Rate limit exceeded |

## Pagination

Major list APIs support:

```txt
limit=50
offset=0
```

Limits:

```txt
1 <= limit <= 100
offset >= 0
```

Example:

```http
GET /services/my-bookings?limit=20&offset=0
```

The response uses:

```json
{
  "items_or_domain_array": [],
  "total": 0
}
```

Note: `total` currently means count of returned records, not total count in database.

## Shared Response Models

### User

```json
{
  "id": "uuid",
  "full_name": "John Doe",
  "phone": "+919876543210",
  "email": "john@example.com",
  "is_verified": true,
  "is_active": true,
  "roles": ["customer"],
  "created_at": "2026-05-02T10:00:00"
}
```

### Token Response

```json
{
  "message": "Login successful",
  "access_token": "jwt",
  "refresh_token": "jwt",
  "token_type": "bearer",
  "account_type": "customer",
  "user": {}
}
```

Cleaner auth responses also include:

```json
{
  "cleaner": {}
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

```json
{
  "id": "uuid",
  "address_label": "Home",
  "address_line1": "Street address",
  "address_line2": "Apartment",
  "landmark": "Near park",
  "city": "Bengaluru",
  "state": "Karnataka",
  "pincode": "560001",
  "country": "India",
  "latitude": 12.9716,
  "longitude": 77.5946,
  "is_default": true
}
```

Some address list/create responses may omit latitude and longitude.

### Cleaner Profile

```json
{
  "id": "cleaner_profile_uuid",
  "user_id": "user_uuid",
  "full_name": "Cleaner Name",
  "phone": "+919876543210",
  "email": "cleaner@example.com",
  "vehicle_type": "bike",
  "aadhaar_number_masked": "********9012",
  "driving_license_number_masked": "******7890",
  "has_aadhaar": true,
  "has_driving_license": true,
  "service_radius_km": 10.0,
  "approval_status": "pending",
  "availability_status": "offline",
  "rating": 0.0,
  "total_jobs_completed": 0,
  "created_at": "2026-05-02T10:00:00"
}
```

Never show full identity numbers. Only masked values are returned.

### Customer Booking

```json
{
  "id": "uuid",
  "booking_reference": "BK-20260502-ABCD1234",
  "service_name": "Car Wash",
  "scheduled_date": "2026-05-10",
  "scheduled_time": "10:30:00",
  "booking_status": "pending",
  "estimated_price": 499.0,
  "final_price": null,
  "special_instructions": "Call before arriving",
  "address": {},
  "assignment": null,
  "created_at": "2026-05-02T10:00:00"
}
```

### Admin Booking

```json
{
  "id": "uuid",
  "booking_reference": "BK-20260502-ABCD1234",
  "customer_id": "uuid",
  "customer_name": "Customer Name",
  "customer_phone": "+919876543210",
  "service_name": "Car Wash",
  "service_category_id": "uuid",
  "scheduled_date": "2026-05-10",
  "scheduled_time": "10:30:00",
  "booking_status": "assigned",
  "estimated_price": 499.0,
  "final_price": null,
  "special_instructions": "Call before arriving",
  "address": {},
  "assignment": {},
  "created_at": "2026-05-02T10:00:00"
}
```

### Assignment

```json
{
  "id": "assignment_uuid",
  "cleaner_id": "cleaner_profile_uuid",
  "assignment_status": "assigned",
  "assigned_at": "2026-05-02T10:00:00",
  "accepted_at": null,
  "started_at": null,
  "completed_at": null,
  "cleaner_notes": "Assigned by admin",
  "booking_id": "booking_uuid",
  "assigned_by_admin": "admin_user_uuid",
  "cleaner": {},
  "booking": {}
}
```

## Endpoint Index

### Public

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/` | API status |
| `GET` | `/health` | API and database health |
| `GET` | `/services/?limit=50&offset=0` | List active service categories |
| `GET` | `/services/service-categories/{service_id}` | Get service category |

### Auth

| Method | Path | Auth | Purpose |
| --- | --- | --- | --- |
| `POST` | `/auth/customer/send-otp` | Public | Send customer OTP |
| `POST` | `/auth/customer/signup` | Public | Customer signup |
| `POST` | `/auth/customer/signin` | Public | Customer signin |
| `POST` | `/auth/cleaner/send-otp` | Public | Send cleaner OTP |
| `POST` | `/auth/cleaner/signup` | Public | Cleaner signup |
| `POST` | `/auth/cleaner/signin` | Public | Cleaner signin |
| `POST` | `/auth/admin/send-otp` | Public | Send admin OTP if admin exists |
| `POST` | `/auth/admin/signin` | Public | Admin signin |
| `POST` | `/auth/admin/create` | Admin | Create another admin |
| `PATCH` | `/auth/admin/{admin_id}` | Admin | Update an admin account |
| `POST` | `/auth/refresh-token` | Public | Rotate refresh token |
| `POST` | `/auth/logout` | Any authenticated role | Revoke refresh token |
| `GET` | `/auth/me` | Any authenticated role | Current profile |
| `GET` | `/auth/admin/dashboard` | Admin | Admin dashboard check |
| `GET` | `/auth/cleaner/jobs?limit=50&offset=0` | Cleaner | Cleaner jobs alias |
| `GET` | `/auth/customer/bookings?limit=50&offset=0` | Customer | Customer bookings alias |

### Users

| Method | Path | Auth | Purpose |
| --- | --- | --- | --- |
| `GET` | `/users/me` | Any authenticated role | Current profile |
| `PATCH` | `/users/me` | Any authenticated role | Update own profile |
| `GET` | `/users/?role=customer&limit=50&offset=0` | Admin | List users |
| `GET` | `/users/{user_id}` | Admin | Get user |
| `PUT` | `/users/{user_id}` | Admin | Update user |
| `DELETE` | `/users/{user_id}` | Admin | Delete user |

### Customer

| Method | Path | Auth | Purpose |
| --- | --- | --- | --- |
| `POST` | `/services/address` | Customer | Create address |
| `GET` | `/services/addresses` | Customer | List own addresses |
| `PATCH` | `/services/address/{address_id}` | Customer | Update own address |
| `DELETE` | `/services/address/{address_id}` | Customer | Delete own address |
| `POST` | `/services/book` | Customer | Create booking |
| `GET` | `/services/my-bookings?limit=50&offset=0` | Customer | List own bookings |
| `GET` | `/services/my-bookings/{booking_id}` | Customer | Get own booking |
| `PATCH` | `/services/my-bookings/{booking_id}` | Customer | Update pending own booking |
| `POST` | `/services/my-bookings/{booking_id}/cancel` | Customer | Cancel pending own booking |

### Cleaner

| Method | Path | Auth | Purpose |
| --- | --- | --- | --- |
| `GET` | `/services/cleaner/profile` | Cleaner | Get own cleaner profile |
| `PATCH` | `/services/cleaner/availability` | Cleaner | Update availability |
| `GET` | `/services/cleaner/assignments?status=assigned&limit=50&offset=0` | Cleaner | List own assignments |
| `GET` | `/services/cleaner/assignments/{assignment_id}` | Cleaner | Get own assignment |
| `POST` | `/services/cleaner/assignments/{assignment_id}/accept` | Cleaner | Accept assigned job |
| `POST` | `/services/cleaner/assignments/{assignment_id}/reject` | Cleaner | Reject assigned job |
| `POST` | `/services/cleaner/assignments/{assignment_id}/start` | Cleaner | Start accepted job |
| `POST` | `/services/cleaner/assignments/{assignment_id}/complete` | Cleaner | Complete in-progress job |

### Admin

| Method | Path | Auth | Purpose |
| --- | --- | --- | --- |
| `POST` | `/services/admin/service-categories` | Admin | Create service category |
| `PATCH` | `/services/admin/service-categories/{service_id}` | Admin | Update service category |
| `DELETE` | `/services/admin/service-categories/{service_id}` | Admin | Deactivate service category |
| `GET` | `/services/admin/all-bookings?limit=50&offset=0` | Admin | List all bookings |
| `GET` | `/services/admin/bookings/{booking_id}` | Admin | Get booking |
| `PATCH` | `/services/admin/bookings/{booking_id}` | Admin | Update booking details only |
| `GET` | `/services/admin/customers/{customer_id}/bookings?limit=50&offset=0` | Admin | Customer booking history |
| `POST` | `/services/admin/bookings/{booking_id}/assign` | Admin | Assign/reassign booking |
| `GET` | `/services/admin/bookings-by-status/{status}?limit=50&offset=0` | Admin | List bookings by status |
| `POST` | `/services/admin/cleaners` | Admin | Create cleaner profile |
| `GET` | `/services/admin/cleaners?approval_status=pending&availability_status=offline&limit=50&offset=0` | Admin | List cleaners |
| `GET` | `/services/admin/cleaners/{cleaner_id}` | Admin | Get cleaner profile |
| `PATCH` | `/services/admin/cleaners/{cleaner_id}` | Admin | Update cleaner profile/approval |
| `DELETE` | `/services/admin/cleaners/{cleaner_id}` | Admin | Delete cleaner profile |
| `GET` | `/services/admin/assignments?status=assigned&limit=50&offset=0` | Admin | List all assignments |

## Auth Flows

### Customer Signup

1. Frontend calls:

```http
POST /auth/customer/send-otp
```

Request:

```json
{
  "phone_number": "+919876543210"
}
```

Response:

```json
{
  "message": "Customer OTP sent successfully"
}
```

2. Frontend collects OTP and calls:

```http
POST /auth/customer/signup
```

Request:

```json
{
  "full_name": "Customer Name",
  "phone_number": "+919876543210",
  "email": "customer@example.com",
  "otp_code": "123456"
}
```

Response:

```json
{
  "message": "Customer signup successful",
  "access_token": "jwt",
  "refresh_token": "jwt",
  "token_type": "bearer",
  "account_type": "customer",
  "user": {}
}
```

### Customer Signin

```http
POST /auth/customer/signin
```

Request:

```json
{
  "phone_number": "+919876543210",
  "otp_code": "123456"
}
```

### Cleaner Signup

Cleaner signup requires Aadhaar.

1. Send OTP:

```http
POST /auth/cleaner/send-otp
```

2. Signup:

```http
POST /auth/cleaner/signup
```

Request:

```json
{
  "full_name": "Cleaner Name",
  "phone_number": "+919876543211",
  "email": "cleaner@example.com",
  "otp_code": "123456",
  "aadhaar_number": "123456789012",
  "driving_license_number": "DL1234567890"
}
```

Response:

```json
{
  "message": "Cleaner signup successful",
  "access_token": "jwt",
  "refresh_token": "jwt",
  "token_type": "bearer",
  "account_type": "cleaner",
  "user": {},
  "cleaner": {
    "approval_status": "pending",
    "availability_status": "offline",
    "aadhaar_number_masked": "********9012",
    "has_aadhaar": true
  }
}
```

Cleaner can sign in before approval, but cannot become `available` or `busy` until approved.

### Admin Signin

There is no public admin signup.

First admin is created by backend/database migration. Then:

```http
POST /auth/admin/send-otp
```

```http
POST /auth/admin/signin
```

Request:

```json
{
  "phone_number": "+919876543212",
  "otp_code": "123456"
}
```

## Token Refresh And Logout

### Refresh Token

```http
POST /auth/refresh-token
```

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
  "refresh_token": "new_refresh_jwt",
  "token_type": "bearer"
}
```

Frontend rule:

- Replace both tokens.
- Retry the original failed request once after a `401`.

### Logout

```http
POST /auth/logout
```

Headers:

```http
Authorization: Bearer <access_token>
```

Request:

```json
{
  "refresh_token": "jwt"
}
```

## Customer Flows

### Create Address

```http
POST /services/address
```

Request:

```json
{
  "address_label": "Home",
  "address_line1": "123 Main Road",
  "address_line2": "Flat 4B",
  "landmark": "Near metro",
  "city": "Bengaluru",
  "state": "Karnataka",
  "pincode": "560001",
  "country": "India",
  "latitude": 12.9716,
  "longitude": 77.5946,
  "is_default": true
}
```

If `is_default=true`, backend makes other addresses non-default.

### Create Booking

```http
POST /services/book
```

Request:

```json
{
  "service_category_id": "service_uuid",
  "address_id": "address_uuid",
  "scheduled_date": "2026-05-10",
  "scheduled_time": "10:30:00",
  "special_instructions": "Call before arriving"
}
```

Alternative:

- Send `address` object instead of `address_id`.
- If both `address_id` and `address` are omitted, backend uses the customer's default address.

Response:

```json
{
  "message": "Booking created successfully",
  "booking": {
    "id": "uuid",
    "booking_reference": "BK-20260502-ABCD1234",
    "service_id": "service_uuid",
    "scheduled_date": "2026-05-10",
    "scheduled_time": "10:30:00",
    "booking_status": "pending",
    "estimated_price": 499.0,
    "created_at": "2026-05-02T10:00:00"
  }
}
```

### Customer Booking Rules

Customer can update a booking only when:

```txt
booking_status = pending
```

Customer can cancel a booking only when:

```txt
booking_status = pending
```

If the booking is already `assigned`, `accepted`, `in_progress`, `completed`, or `cancelled`, frontend should hide/disable customer edit and cancel controls.

## Cleaner Flows

### Cleaner Approval

After cleaner signup:

```txt
approval_status = pending
availability_status = offline
```

Admin approves cleaner:

```http
PATCH /services/admin/cleaners/{cleaner_id}
```

Request:

```json
{
  "approval_status": "approved"
}
```

### Cleaner Availability

```http
PATCH /services/cleaner/availability
```

Request:

```json
{
  "availability_status": "available"
}
```

Rules:

- Only approved cleaners can become `available` or `busy`.
- Non-approved cleaners may set only `offline`.

### Cleaner Assignment Lifecycle

Cleaner list:

```http
GET /services/cleaner/assignments?status=assigned&limit=50&offset=0
```

Accept:

```http
POST /services/cleaner/assignments/{assignment_id}/accept
```

Start:

```http
POST /services/cleaner/assignments/{assignment_id}/start
```

Complete:

```http
POST /services/cleaner/assignments/{assignment_id}/complete
```

Complete request:

```json
{
  "cleaner_notes": "Completed successfully",
  "final_price": 499.0
}
```

Reject:

```http
POST /services/cleaner/assignments/{assignment_id}/reject
```

## Admin Flows

### Create Another Admin

```http
POST /auth/admin/create
```

Request:

```json
{
  "full_name": "Admin User",
  "phone_number": "+919876543213",
  "email": "admin2@example.com"
}
```

### Update Admin Account

```http
PATCH /auth/admin/{admin_id}
```

Request:

```json
{
  "full_name": "Updated Admin Name",
  "email": "new-admin@example.com",
  "phone": "+919876543214"
}
```

### Manage Service Categories

Create:

```http
POST /services/admin/service-categories
```

Request:

```json
{
  "service_name": "Premium Car Wash",
  "description": "Premium exterior and interior wash",
  "base_price": 899.0,
  "estimated_duration_minutes": 90,
  "is_active": true
}
```

Update:

```http
PATCH /services/admin/service-categories/{service_id}
```

Deactivate:

```http
DELETE /services/admin/service-categories/{service_id}
```

### Manage Cleaner Profiles

List pending cleaners:

```http
GET /services/admin/cleaners?approval_status=pending&limit=50&offset=0
```

Approve cleaner:

```http
PATCH /services/admin/cleaners/{cleaner_id}
```

Request:

```json
{
  "approval_status": "approved",
  "service_radius_km": 10,
  "vehicle_type": "bike"
}
```

Admin create cleaner profile manually:

```http
POST /services/admin/cleaners
```

Request:

```json
{
  "user_id": "cleaner_user_uuid",
  "vehicle_type": "bike",
  "aadhaar_number": "123456789012",
  "driving_license_number": "DL1234567890",
  "service_radius_km": 10,
  "approval_status": "pending",
  "availability_status": "offline"
}
```

### Manage Bookings

List all:

```http
GET /services/admin/all-bookings?limit=50&offset=0
```

Filter by status:

```http
GET /services/admin/bookings-by-status/pending?limit=50&offset=0
```

Get one:

```http
GET /services/admin/bookings/{booking_id}
```

Patch booking details:

```http
PATCH /services/admin/bookings/{booking_id}
```

Important:

- Do not use this endpoint to set `booking_status`.
- Backend rejects arbitrary booking status patches.
- Use assignment/lifecycle APIs for status transitions.

Assign booking:

```http
POST /services/admin/bookings/{booking_id}/assign
```

Request:

```json
{
  "cleaner_id": "cleaner_profile_uuid",
  "cleaner_notes": "Please handle this booking"
}
```

Rules:

- `cleaner_id` is `cleaner_profiles.id`, not `users.id`.
- Cleaner must be `approved`.
- Cleaner must be `available`.
- Booking must be `pending` or safely reassignable.

## Booking Status Lifecycle

```txt
pending -> assigned        admin assigns cleaner
assigned -> accepted       cleaner accepts
assigned -> pending        cleaner rejects
accepted -> in_progress    cleaner starts
in_progress -> completed   cleaner completes
pending -> cancelled       customer cancels
```

Assignment statuses:

```txt
assigned
accepted
in_progress
rejected
completed
cancelled
```

Frontend UI rules:

| Status | Customer actions | Cleaner actions | Admin actions |
| --- | --- | --- | --- |
| `pending` | edit, cancel | none | assign |
| `assigned` | view only | accept, reject | view/reassign if not active |
| `accepted` | view only | start | view |
| `in_progress` | view only | complete | view |
| `completed` | view only | view | view |
| `cancelled` | view only | view | view |

## Setup / Flyway Notes

Flyway migrations are in:

```txt
db/migration
```

Order:

```txt
V1__init_schema.sql
V2__create_initial_admin.sql
V3__add_cleaner_identity_fields.sql
V4__add_production_constraints.sql
```

Admin seed placeholders:

```properties
flyway.placeholders.admin_full_name=Admin User
flyway.placeholders.admin_phone_number=+919876543210
flyway.placeholders.admin_email=admin@example.com
```

Root `database.sql` is kept for Docker/Postgres direct initialization. Flyway should use the versioned files under `db/migration`.

## Frontend Implementation Checklist

### Auth

- Use role-specific auth endpoints only.
- Store `access_token` and `refresh_token`.
- On `401`, call refresh once and retry the failed request.
- On refresh success, replace both tokens.
- On logout, call `/auth/logout` with refresh token.

### Customer UI

- Show service categories from `/services/`.
- Manage addresses with `/services/address*`.
- Booking create requires service, schedule, and address/default address.
- Allow edit/cancel only for `pending` bookings.

### Cleaner UI

- Signup form must include Aadhaar.
- Driving license field is optional.
- Show approval pending screen until `approval_status=approved`.
- Allow availability switch to `available` only after approval.
- Show assignment actions based on `assignment_status`.

### Admin UI

- Use admin signin only.
- Add/update admins through `/auth/admin/create` and `/auth/admin/{admin_id}`.
- Approve cleaners from pending list.
- Assign pending bookings to approved available cleaners.
- Do not send `booking_status` in admin booking patch requests.

### PII

- Never ask backend for full Aadhaar/license values after signup.
- Display only returned masked values.
- Treat identity fields as sensitive client-side inputs.

