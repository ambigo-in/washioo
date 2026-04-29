# Washioo - On-Demand Vehicle Wash API

A FastAPI-based backend for an on-demand doorstep vehicle washing platform.

## Features

- **OTP Authentication**: Twilio-based SMS OTP verification
- **JWT Authentication**: Secure token-based authentication
- **Booking Management**: Create, track, and manage car/bike wash bookings
- **Cleaner Management**: Assign cleaners to bookings with GPS tracking
- **Admin Dashboard**: Manage bookings and cleaners
- **Real-Time Updates**: WebSocket support for live booking tracking
- **SMS Notifications**: Twilio integration for booking and status updates
- **Multiple Payment Methods**: Support for cash and UPI payments

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **Authentication**: JWT + Twilio OTP
- **Real-Time**: WebSocket
- **ORM**: SQLAlchemy
- **SMS Service**: Twilio

## Project Structure

```
app/
├── auth/                    # Authentication module
│   ├── router.py           # Auth endpoints
│   ├── utils.py            # Auth utilities
│   └── dependencies.py      # JWT verification
├── bookings/               # Booking management
│   ├── router.py           # Booking endpoints
│   └── utils.py            # Booking logic
├── cleaners/               # Cleaner management
│   ├── router.py           # Cleaner endpoints
│   └── utils.py            # Cleaner logic
├── admin/                  # Admin operations
│   ├── router.py           # Admin endpoints
│   └── utils.py            # Admin logic
├── database/               # Database configuration
│   └── session.py          # SQLAlchemy setup
├── models/                 # SQLAlchemy models
│   └── models.py           # All DB models
├── schemas/                # Pydantic schemas
│   └── schemas.py          # Request/response schemas
├── services/               # Business logic
│   ├── twilio_service.py   # OTP verification
│   ├── jwt_service.py      # JWT token management
│   ├── notification_service.py  # SMS notifications
│   └── packages_router.py  # Package listing
├── websocket/              # Real-time updates
│   └── router.py           # WebSocket endpoints
└── main.py                 # FastAPI app entry point

schema.sql                  # PostgreSQL schema with seed data
.env.example                # Environment variables template
requirements.txt            # Python dependencies
```

## Setup Instructions

### 1. Prerequisites

- Python 3.9+
- PostgreSQL 12+
- Twilio Account (for OTP and SMS)

### 2. Environment Setup

```bash
# Clone or navigate to project directory
cd washioo

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your credentials:
# - DATABASE_URL: PostgreSQL connection string
# - JWT_SECRET: Generate a secure secret key
# - TWILIO_ACCOUNT_SID: From Twilio Console
# - TWILIO_AUTH_TOKEN: From Twilio Console
# - TWILIO_VERIFY_SERVICE_SID: From Twilio Verify Service
# - TWILIO_PHONE_NUMBER: Your Twilio phone number
```

### 4. Database Setup

```bash
# Create database in PostgreSQL
createdb washioo

# Run SQL schema
psql -U postgres -d washioo -f schema.sql
```

### 5. Run the API

```bash
# Development server with auto-reload
uvicorn app.main:app --reload

# Production server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

API documentation (Swagger UI): `http://localhost:8000/docs`

## API Endpoints

### Authentication

```
POST /auth/send-otp
  - Send OTP to phone number

POST /auth/verify-otp
  - Verify OTP code

POST /auth/register
  - Register new user

POST /auth/login
  - Login and get JWT tokens
```

### Packages

```
GET /packages?vehicle_type=car
  - List packages by vehicle type

GET /packages/{package_id}
  - Get package details
```

### Bookings

```
POST /bookings
  - Create new booking

GET /bookings
  - List all bookings

GET /bookings/{booking_id}
  - Get booking details

PATCH /bookings/{booking_id}/status
  - Update booking status
```

### Cleaner Operations

```
GET /cleaner/jobs?cleaner_id={id}
  - Get assigned jobs for cleaner

PATCH /cleaner/jobs/{booking_id}/status
  - Update job status

PATCH /cleaner/location
  - Update GPS location

GET /cleaner/location/{cleaner_id}
  - Get cleaner's current location
```

### Admin Operations

```
GET /admin/bookings
  - List all bookings

GET /admin/bookings/{booking_id}
  - Get booking details

GET /admin/cleaners
  - List all cleaners

POST /admin/cleaners
  - Add new cleaner

POST /admin/bookings/{booking_id}/assign
  - Assign cleaner to booking
```

### WebSocket

```
ws://localhost:8000/ws/booking/{booking_id}
  - Real-time booking updates
```

## API Request Examples

### 1. Send OTP

```bash
curl -X POST "http://localhost:8000/auth/send-otp" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+919876543210"}'
```

### 2. Verify OTP

```bash
curl -X POST "http://localhost:8000/auth/verify-otp" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+919876543210", "otp_code": "123456"}'
```

### 3. Register User

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+919876543210", "full_name": "John Doe"}'
```

### 4. Get Packages

```bash
curl -X GET "http://localhost:8000/packages?vehicle_type=car"
```

### 5. Create Booking

```bash
curl -X POST "http://localhost:8000/bookings" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "vehicle_id": "uuid",
    "package_id": "uuid",
    "address": "123 Main St, City",
    "latitude": 12.9716,
    "longitude": 77.5946,
    "scheduled_at": "2026-04-29T10:00:00",
    "payment_method": "cash"
  }'
```

### 6. Assign Cleaner

```bash
curl -X POST "http://localhost:8000/admin/bookings/{booking_id}/assign" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_JWT_TOKEN" \
  -d '{"cleaner_id": "uuid"}'
```

## Database Schema

### Users Table

- id (UUID, Primary Key)
- phone_number (VARCHAR, Unique)
- full_name (VARCHAR)
- role (ENUM: customer/admin/cleaner)
- is_verified (BOOLEAN)
- created_at, updated_at (TIMESTAMP)

### Vehicles Table

- id (UUID, Primary Key)
- user_id (FK to users)
- vehicle_type (ENUM: car/bike)
- vehicle_model (VARCHAR)
- vehicle_number (VARCHAR)

### Packages Table

- id (UUID, Primary Key)
- vehicle_type (ENUM: car/bike)
- package_name (VARCHAR)
- description (TEXT)
- price (DECIMAL)
- duration_minutes (INTEGER)

### Bookings Table

- id (UUID, Primary Key)
- user_id, vehicle_id, package_id, cleaner_id (FK)
- address (TEXT)
- latitude, longitude (DECIMAL)
- scheduled_at (TIMESTAMP)
- status (ENUM: pending/assigned/en_route/in_progress/completed/cancelled/failed)
- payment_status (ENUM: unpaid/paid)
- payment_method (ENUM: cash/upi)

### Cleaner Locations Table

- id (UUID, Primary Key)
- cleaner_id (FK to users)
- latitude, longitude (DECIMAL)
- updated_at (TIMESTAMP)

## Booking Status Flow

```
pending → assigned → en_route → in_progress → completed
                  ↓
            (admin assigns cleaner)
```

## Authentication Flow

1. Customer requests OTP via phone number
2. Twilio sends SMS with OTP code
3. Customer verifies OTP
4. Customer registers or logs in
5. API returns JWT access and refresh tokens
6. Customer uses JWT token in Authorization header for protected endpoints

## WebSocket Connection Example

```javascript
const ws = new WebSocket("ws://localhost:8000/ws/booking/{booking_id}");

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === "status_update") {
    console.log("Status:", data.status);
  } else if (data.type === "location_update") {
    console.log("Location:", data.latitude, data.longitude);
  }
};

// Send location update
ws.send(
  JSON.stringify({
    type: "location_update",
    latitude: 12.9716,
    longitude: 77.5946,
    timestamp: new Date().toISOString(),
  }),
);
```

## Seeded Packages

### Car Services

- Basic Wash: ₹149 (30 min)
- Deep Clean: ₹349 (60 min)
- Premium Detail: ₹599 (90 min)

### Bike Services

- Basic Wash: ₹79 (20 min)
- Deep Clean: ₹199 (40 min)

## Deployment

### Using Render/Railway

1. Push code to GitHub
2. Connect repository to Render/Railway
3. Set environment variables in deployment platform
4. Deploy

### Using Docker

```bash
docker build -t washioo .
docker run -p 8000:8000 --env-file .env washioo
```

## Security Considerations

- All credentials stored in environment variables
- JWT tokens with expiration
- HTTPS recommended for production
- Rate limiting recommended for OTP endpoints
- Database credentials never hardcoded
- CORS configured (update for production)

## Future Enhancements

- Ratings and reviews system
- Loyalty points/rewards
- Subscription plans
- AI-based cleaner auto-assignment
- Analytics dashboard
- Payment gateway integration
- Push notifications
- Advanced filtering and search

## Troubleshooting

### Database Connection Error

- Verify PostgreSQL is running
- Check DATABASE_URL in .env
- Ensure database exists

### Twilio OTP Not Received

- Verify TWILIO_ACCOUNT_SID and AUTH_TOKEN
- Check phone number format (+country_code format)
- Verify Verify Service SID is correct
- Check Twilio trial account limits

### JWT Token Errors

- Verify token is not expired
- Check Authorization header format: `Bearer {token}`
- Verify JWT_SECRET matches

## Support

For issues or questions, please check the API documentation at `/docs` endpoint or create an issue in the repository.

## License

MIT License
