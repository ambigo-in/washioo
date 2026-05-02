# API Documentation

Base URL: `http://localhost:8000`

Authorization uses JWT bearer tokens for protected routes:

```http
Authorization: Bearer <access_token>
```

Roles used by the API: `customer`, `cleaner`, `admin`.

Flyway migrations live in `db/migration` and should run in order:

```txt
V1__init_schema.sql
V2__create_initial_admin.sql
V3__add_cleaner_identity_fields.sql
V4__add_production_constraints.sql
```

## Common Error Response

```json
{
  "detail": "Error message"
}
```

Common status codes:

| Status | Meaning |
| --- | --- |
| `400` | Invalid request or business validation failed |
| `401` | Missing, invalid, or expired bearer token |
| `403` | Authenticated user does not have the required role |
| `404` | Requested entity was not found |
| `429` | Rate limit exceeded |

## Request Entities

### SendOTPRequest

```json
{
  "phone_number": "string"
}
```

### SigninRequest

```json
{
  "phone_number": "string",
  "otp_code": "string"
}
```

### RoleSignupRequest

Used by customer signup APIs. The role is taken from the endpoint path.

```json
{
  "full_name": "string",
  "phone_number": "string",
  "email": "user@example.com",
  "otp_code": "string"
}
```

### CleanerSignupRequest

Used by cleaner signup APIs. Aadhaar number is required; driving license number is optional.

```json
{
  "full_name": "string",
  "phone_number": "string",
  "email": "user@example.com",
  "otp_code": "string",
  "aadhaar_number": "string",
  "driving_license_number": "string"
}
```

### CreateAdminRequest

```json
{
  "full_name": "string",
  "phone_number": "string",
  "email": "admin@example.com"
}
```

### RefreshTokenRequest

```json
{
  "refresh_token": "string"
}
```

### LogoutRequest

```json
{
  "refresh_token": "string"
}
```

### UpdateUserRequest

All fields are optional.

```json
{
  "full_name": "string",
  "email": "user@example.com",
  "phone": "string"
}
```

### CreateAddressRequest

```json
{
  "address_label": "string",
  "address_line1": "string",
  "address_line2": "string",
  "landmark": "string",
  "city": "string",
  "state": "string",
  "pincode": "string",
  "country": "India",
  "latitude": 0,
  "longitude": 0,
  "is_default": false
}
```

Required field: `address_line1`.

### UpdateAddressRequest

Same fields as `CreateAddressRequest`, but all fields are optional.

### CreateServiceRequest

```json
{
  "service_name": "string",
  "description": "string",
  "base_price": 0,
  "estimated_duration_minutes": 0,
  "is_active": true
}
```

Required fields: `service_name`, `base_price`.

### UpdateServiceRequest

Same fields as `CreateServiceRequest`, but all fields are optional.

### CreateBookingRequest

```json
{
  "service_category_id": "string",
  "address_id": "string",
  "address": "CreateAddressRequest",
  "scheduled_date": "YYYY-MM-DD",
  "scheduled_time": "HH:MM:SS",
  "special_instructions": "string"
}
```

Required fields: `service_category_id`, `scheduled_date`, `scheduled_time`.

Use either `address_id`, `address`, or omit both to use the customer's default address.

### UpdateBookingRequest

All fields are optional.

```json
{
  "service_category_id": "string",
  "address_id": "string",
  "scheduled_date": "YYYY-MM-DD",
  "scheduled_time": "HH:MM:SS",
  "special_instructions": "string"
}
```

### AdminUpdateBookingRequest

All fields are optional.

```json
{
  "service_category_id": "string",
  "address_id": "string",
  "scheduled_date": "YYYY-MM-DD",
  "scheduled_time": "HH:MM:SS",
  "special_instructions": "string",
  "booking_status": "pending | assigned | accepted | in_progress | completed | cancelled",
  "estimated_price": 0,
  "final_price": 0
}
```

### CancelBookingRequest

```json
{
  "reason": "string"
}
```

### CreateCleanerProfileRequest

```json
{
  "user_id": "string",
  "vehicle_type": "string",
  "aadhaar_number": "string",
  "driving_license_number": "string",
  "service_radius_km": 0,
  "approval_status": "pending | approved | rejected | suspended",
  "availability_status": "offline | available | busy"
}
```

Required fields: `user_id`, `aadhaar_number`.

Defaults: `approval_status = pending`, `availability_status = offline`.

### UpdateCleanerProfileRequest

Same fields as `CreateCleanerProfileRequest` except `user_id`, and all fields are optional.

### UpdateCleanerAvailabilityRequest

```json
{
  "availability_status": "offline | available | busy"
}
```

### AssignBookingRequest

```json
{
  "cleaner_id": "string",
  "cleaner_notes": "string"
}
```

Required field: `cleaner_id`.

### CleanerAssignmentActionRequest

```json
{
  "cleaner_notes": "string"
}
```

### CompleteAssignmentRequest

```json
{
  "cleaner_notes": "string",
  "final_price": 0
}
```

## Response Entities

### TokenResponse

```json
{
  "message": "string",
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer"
}
```

`/auth/signup` also returns `is_new_user`.

### User

```json
{
  "id": "string",
  "full_name": "string",
  "phone": "string",
  "email": "user@example.com",
  "is_verified": true,
  "is_active": true,
  "roles": ["customer"],
  "created_at": "datetime"
}
```

### ServiceCategory

```json
{
  "id": "string",
  "service_name": "string",
  "description": "string",
  "base_price": 0,
  "estimated_duration_minutes": 0,
  "is_active": true
}
```

### Address

Some address endpoints omit `latitude` and `longitude`; booking response entities include them.

```json
{
  "id": "string",
  "address_label": "string",
  "address_line1": "string",
  "address_line2": "string",
  "landmark": "string",
  "city": "string",
  "state": "string",
  "pincode": "string",
  "country": "India",
  "latitude": 0,
  "longitude": 0,
  "is_default": false
}
```

### CustomerBooking

```json
{
  "id": "string",
  "booking_reference": "string",
  "service_name": "string",
  "scheduled_date": "YYYY-MM-DD",
  "scheduled_time": "HH:MM:SS",
  "booking_status": "string",
  "estimated_price": 0,
  "final_price": 0,
  "special_instructions": "string",
  "address": "Address",
  "assignment": "AssignmentSummary | null",
  "created_at": "datetime"
}
```

### CreatedBooking

Returned when a customer creates a new booking.

```json
{
  "id": "string",
  "booking_reference": "string",
  "service_id": "string",
  "scheduled_date": "YYYY-MM-DD",
  "scheduled_time": "HH:MM:SS",
  "booking_status": "string",
  "estimated_price": 0,
  "created_at": "datetime"
}
```

### AdminBooking

```json
{
  "id": "string",
  "booking_reference": "string",
  "customer_id": "string",
  "customer_name": "string",
  "customer_phone": "string",
  "service_name": "string",
  "service_category_id": "string",
  "scheduled_date": "YYYY-MM-DD",
  "scheduled_time": "HH:MM:SS",
  "booking_status": "string",
  "estimated_price": 0,
  "final_price": 0,
  "special_instructions": "string",
  "address": "Address",
  "assignment": "AssignmentSummary | null",
  "created_at": "datetime"
}
```

### CleanerProfile

```json
{
  "id": "string",
  "user_id": "string",
  "full_name": "string",
  "phone": "string",
  "email": "user@example.com",
  "vehicle_type": "string",
  "aadhaar_number_masked": "********9012",
  "driving_license_number_masked": "******7890",
  "has_aadhaar": true,
  "has_driving_license": true,
  "service_radius_km": 0,
  "approval_status": "string",
  "availability_status": "string",
  "rating": 0,
  "total_jobs_completed": 0,
  "created_at": "datetime"
}
```

### AssignmentSummary

```json
{
  "id": "string",
  "cleaner_id": "string",
  "assignment_status": "string",
  "assigned_at": "datetime",
  "accepted_at": "datetime",
  "started_at": "datetime",
  "completed_at": "datetime",
  "cleaner_notes": "string"
}
```

### Assignment

```json
{
  "id": "string",
  "cleaner_id": "string",
  "assignment_status": "string",
  "assigned_at": "datetime",
  "accepted_at": "datetime",
  "started_at": "datetime",
  "completed_at": "datetime",
  "cleaner_notes": "string",
  "booking_id": "string",
  "assigned_by_admin": "string",
  "cleaner": "CleanerProfile",
  "booking": "AdminBooking"
}
```

## Public APIs

| Method | Endpoint | Request | Success Response | Authorization |
| --- | --- | --- | --- | --- |
| `GET` | `/` | None | `{ "success": true, "message": "Car Wash Service Portal API Running Successfully" }` | Public |
| `GET` | `/health` | None | `{ "status": "healthy", "database": "connected", "version": "1.0.0" }` | Public |
| `GET` | `/services/` | None | `{ "message": "Services fetched successfully", "services": [ServiceCategory], "total": 0 }` | Public |
| `GET` | `/services/service-categories/{service_id}` | Path: `service_id` | `{ "message": "Service fetched successfully", "service": ServiceCategory }` | Public |

## Auth APIs

| Method | Endpoint | Request | Success Response | Authorization |
| --- | --- | --- | --- | --- |
| `POST` | `/auth/send-otp` | None | `410 Gone` | Deprecated; use role-specific OTP endpoints |
| `POST` | `/auth/signup` | None | `410 Gone` | Deprecated; use role-specific signup endpoints |
| `POST` | `/auth/signin` | None | `410 Gone` | Deprecated; use role-specific signin endpoints |
| `POST` | `/auth/customer/send-otp` | `SendOTPRequest` | `{ "message": "Customer OTP sent successfully" }` | Public |
| `POST` | `/auth/customer/signup` | `RoleSignupRequest` | `TokenResponse` plus `account_type` and `user` | Public |
| `POST` | `/auth/customer/signin` | `SigninRequest` | `TokenResponse` plus `account_type` and `user` | Public |
| `POST` | `/auth/cleaner/send-otp` | `SendOTPRequest` | `{ "message": "Cleaner OTP sent successfully" }` | Public |
| `POST` | `/auth/cleaner/signup` | `CleanerSignupRequest` | `TokenResponse` plus `account_type`, `user`, and `cleaner` | Public |
| `POST` | `/auth/cleaner/signin` | `SigninRequest` | `TokenResponse` plus `account_type`, `user`, and `cleaner` | Public |
| `POST` | `/auth/admin/send-otp` | `SendOTPRequest` | `{ "message": "Admin OTP sent successfully" }` | Public, only existing admin phones receive OTP |
| `POST` | `/auth/admin/signin` | `SigninRequest` | `TokenResponse` plus `account_type` and `user` | Public, only existing admin accounts |
| `POST` | `/auth/admin/create` | `CreateAdminRequest` | `{ "message": "Admin account created successfully", "admin": User }` | Bearer token, role: `admin` |
| `PATCH` | `/auth/admin/{admin_id}` | `UpdateUserRequest` | `{ "message": "Admin account updated successfully", "admin": User }` | Bearer token, role: `admin` |
| `POST` | `/auth/refresh-token` | `RefreshTokenRequest` | `{ "access_token": "string", "refresh_token": "string", "token_type": "bearer" }` | Public |
| `POST` | `/auth/logout` | `LogoutRequest` | `{ "message": "Logged out successfully" }` | Bearer token, roles: `customer`, `cleaner`, `admin` |
| `GET` | `/auth/me` | None | `{ "message": "User details fetched successfully", "user": User }` | Bearer token, roles: `customer`, `cleaner`, `admin` |
| `GET` | `/auth/admin/dashboard` | None | `{ "message": "Welcome Admin", "admin_id": "string", "roles": ["admin"] }` | Bearer token, role: `admin` |
| `GET` | `/auth/cleaner/jobs` | None | `{ "message": "Cleaner jobs fetched successfully", "assignments": [Assignment], "total": 0 }` | Bearer token, role: `cleaner` |
| `GET` | `/auth/customer/bookings` | None | `{ "message": "Customer bookings fetched successfully", "bookings": [CustomerBooking], "total": 0 }` | Bearer token, role: `customer` |

The generic `/auth/send-otp`, `/auth/signup`, and `/auth/signin` APIs are disabled in production-facing flows.

## Admin Seed Migration

Use this Flyway migration to create the first admin directly in the database:

```txt
db/migration/V2__create_initial_admin.sql
```

Configure these Flyway placeholders before running it:

```properties
flyway.placeholders.admin_full_name=Admin User
flyway.placeholders.admin_phone_number=+919876543210
flyway.placeholders.admin_email=admin@example.com
```

If the phone number already belongs to an existing non-admin user, the migration adds the `admin` role to that account. If you run the SQL manually, replace the placeholders in the file with real values first.

## Cleaner Identity Migration

Cleaner signup stores required Aadhaar and optional driving license details on `cleaner_profiles`.

```txt
db/migration/V3__add_cleaner_identity_fields.sql
```

The API stores masked identity numbers plus deterministic hashes for uniqueness checks. Full Aadhaar and driving license values are not returned by normal API responses.

## User APIs

| Method | Endpoint | Request | Success Response | Authorization |
| --- | --- | --- | --- | --- |
| `GET` | `/users/me` | None | `{ "message": "Current user profile fetched successfully", "user": User }` | Bearer token, roles: `customer`, `cleaner`, `admin` |
| `PATCH` | `/users/me` | `UpdateUserRequest` | `{ "message": "Profile updated successfully", "user": User }` | Bearer token, roles: `customer`, `cleaner`, `admin` |
| `GET` | `/users/?role={role}` | Optional query: `role` | `{ "message": "Users fetched successfully", "users": [User], "total": 0 }` | Bearer token, role: `admin` |
| `GET` | `/users/{user_id}` | Path: `user_id` | `{ "message": "User fetched successfully", "user": User }` | Bearer token, role: `admin` |
| `PUT` | `/users/{user_id}` | Path: `user_id`, body: `UpdateUserRequest` | `{ "message": "User updated successfully", "user": User }` | Bearer token, role: `admin` |
| `DELETE` | `/users/{user_id}` | Path: `user_id` | `{ "message": "User deleted successfully" }` | Bearer token, role: `admin` |

## Service Category Admin APIs

| Method | Endpoint | Request | Success Response | Authorization |
| --- | --- | --- | --- | --- |
| `POST` | `/services/admin/service-categories` | `CreateServiceRequest` | `{ "message": "Service created successfully", "service": ServiceCategory }` | Bearer token, role: `admin` |
| `PATCH` | `/services/admin/service-categories/{service_id}` | Path: `service_id`, body: `UpdateServiceRequest` | `{ "message": "Service updated successfully", "service": ServiceCategory }` | Bearer token, role: `admin` |
| `DELETE` | `/services/admin/service-categories/{service_id}` | Path: `service_id` | `{ "message": "Service deactivated successfully", "service_id": "string" }` | Bearer token, role: `admin` |

## Address APIs

| Method | Endpoint | Request | Success Response | Authorization |
| --- | --- | --- | --- | --- |
| `POST` | `/services/address` | `CreateAddressRequest` | `{ "message": "Address created successfully", "address": Address }` | Bearer token, role: `customer` |
| `GET` | `/services/addresses` | None | `{ "message": "Addresses fetched successfully", "addresses": [Address], "total": 0 }` | Bearer token, role: `customer` |
| `PATCH` | `/services/address/{address_id}` | Path: `address_id`, body: `UpdateAddressRequest` | `{ "message": "Address updated successfully", "address": Address }` | Bearer token, role: `customer` |
| `DELETE` | `/services/address/{address_id}` | Path: `address_id` | `{ "message": "Address deleted successfully", "address_id": "string" }` | Bearer token, role: `customer` |

## Customer Booking APIs

| Method | Endpoint | Request | Success Response | Authorization |
| --- | --- | --- | --- | --- |
| `POST` | `/services/book` | `CreateBookingRequest` | `{ "message": "Booking created successfully", "booking": CreatedBooking }` | Bearer token, role: `customer` |
| `GET` | `/services/my-bookings` | None | `{ "message": "Bookings fetched successfully", "bookings": [CustomerBooking], "total": 0 }` | Bearer token, role: `customer` |
| `GET` | `/services/my-bookings/{booking_id}` | Path: `booking_id` | `{ "message": "Booking fetched successfully", "booking": CustomerBooking }` | Bearer token, role: `customer` |
| `PATCH` | `/services/my-bookings/{booking_id}` | Path: `booking_id`, body: `UpdateBookingRequest` | `{ "message": "Booking updated successfully", "booking": CustomerBooking }` | Bearer token, role: `customer` |
| `POST` | `/services/my-bookings/{booking_id}/cancel` | Path: `booking_id`, body: `CancelBookingRequest` | `{ "message": "Booking cancelled successfully", "booking": CustomerBooking }` | Bearer token, role: `customer` |

## Admin Booking APIs

| Method | Endpoint | Request | Success Response | Authorization |
| --- | --- | --- | --- | --- |
| `GET` | `/services/admin/all-bookings` | None | `{ "message": "All bookings fetched successfully", "bookings": [AdminBooking], "total": 0 }` | Bearer token, role: `admin` |
| `GET` | `/services/admin/bookings/{booking_id}` | Path: `booking_id` | `{ "message": "Booking fetched successfully", "booking": AdminBooking }` | Bearer token, role: `admin` |
| `PATCH` | `/services/admin/bookings/{booking_id}` | Path: `booking_id`, body: `AdminUpdateBookingRequest` | `{ "message": "Booking updated successfully", "booking": AdminBooking }` | Bearer token, role: `admin` |
| `GET` | `/services/admin/customers/{customer_id}/bookings` | Path: `customer_id` | `{ "message": "Customer bookings fetched successfully", "customer_id": "string", "bookings": [CustomerBooking], "total": 0 }` | Bearer token, role: `admin` |
| `POST` | `/services/admin/bookings/{booking_id}/assign` | Path: `booking_id`, body: `AssignBookingRequest` | `{ "message": "Booking assigned successfully", "assignment": Assignment }` | Bearer token, role: `admin` |
| `GET` | `/services/admin/bookings-by-status/{status}` | Path: `status` | `{ "message": "Bookings with status '<status>' fetched successfully", "status": "string", "bookings": [AdminBooking], "total": 0 }` | Bearer token, role: `admin` |

Valid `status` values: `pending`, `assigned`, `accepted`, `in_progress`, `completed`, `cancelled`.

## Cleaner Profile APIs

| Method | Endpoint | Request | Success Response | Authorization |
| --- | --- | --- | --- | --- |
| `POST` | `/services/admin/cleaners` | `CreateCleanerProfileRequest` | `{ "message": "Cleaner profile created successfully", "cleaner": CleanerProfile }` | Bearer token, role: `admin` |
| `GET` | `/services/admin/cleaners` | Optional query: `approval_status`, `availability_status` | `{ "message": "Cleaners fetched successfully", "cleaners": [CleanerProfile], "total": 0 }` | Bearer token, role: `admin` |
| `GET` | `/services/admin/cleaners/{cleaner_id}` | Path: `cleaner_id` | `{ "message": "Cleaner fetched successfully", "cleaner": CleanerProfile }` | Bearer token, role: `admin` |
| `PATCH` | `/services/admin/cleaners/{cleaner_id}` | Path: `cleaner_id`, body: `UpdateCleanerProfileRequest` | `{ "message": "Cleaner updated successfully", "cleaner": CleanerProfile }` | Bearer token, role: `admin` |
| `DELETE` | `/services/admin/cleaners/{cleaner_id}` | Path: `cleaner_id` | `{ "message": "Cleaner profile deleted successfully", "cleaner_id": "string" }` | Bearer token, role: `admin` |
| `GET` | `/services/cleaner/profile` | None | `{ "message": "Cleaner profile fetched successfully", "cleaner": CleanerProfile }` | Bearer token, role: `cleaner` |
| `PATCH` | `/services/cleaner/availability` | `UpdateCleanerAvailabilityRequest` | `{ "message": "Availability updated successfully", "cleaner": CleanerProfile }` | Bearer token, role: `cleaner` |

## Assignment APIs

| Method | Endpoint | Request | Success Response | Authorization |
| --- | --- | --- | --- | --- |
| `GET` | `/services/admin/assignments` | Optional query: `status` | `{ "message": "Assignments fetched successfully", "assignments": [Assignment], "total": 0 }` | Bearer token, role: `admin` |
| `GET` | `/services/cleaner/assignments` | Optional query: `status` | `{ "message": "Cleaner assignments fetched successfully", "assignments": [Assignment], "total": 0 }` | Bearer token, role: `cleaner` |
| `GET` | `/services/cleaner/assignments/{assignment_id}` | Path: `assignment_id` | `{ "message": "Assignment fetched successfully", "assignment": Assignment }` | Bearer token, role: `cleaner` |
| `POST` | `/services/cleaner/assignments/{assignment_id}/accept` | Path: `assignment_id`, body: `CleanerAssignmentActionRequest` | `{ "message": "Assignment accepted successfully", "assignment": Assignment }` | Bearer token, role: `cleaner` |
| `POST` | `/services/cleaner/assignments/{assignment_id}/reject` | Path: `assignment_id`, body: `CleanerAssignmentActionRequest` | `{ "message": "Assignment rejected successfully", "assignment": Assignment }` | Bearer token, role: `cleaner` |
| `POST` | `/services/cleaner/assignments/{assignment_id}/start` | Path: `assignment_id`, body: `CleanerAssignmentActionRequest` | `{ "message": "Assignment started successfully", "assignment": Assignment }` | Bearer token, role: `cleaner` |
| `POST` | `/services/cleaner/assignments/{assignment_id}/complete` | Path: `assignment_id`, body: `CompleteAssignmentRequest` | `{ "message": "Assignment completed successfully", "assignment": Assignment }` | Bearer token, role: `cleaner` |
