# Washioo MVP - Quick Reference Card

## 🚀 QUICK START (Copy & Paste)

```bash
# 1. Setup environment
cd washioo
python -m venv venv
venv\Scripts\activate

# 2. Install & configure
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your Twilio credentials

# 3. Setup database
createdb washioo
psql -U postgres -d washioo -f schema.sql

# 4. Run server
uvicorn app.main:app --reload
```

Visit: `http://localhost:8000/docs`

---

## 📋 ENVIRONMENT VARIABLES

```
DATABASE_URL=postgresql://user:password@localhost:5432/washioo
JWT_SECRET=your-secret-key-here
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_VERIFY_SERVICE_SID=your_service_sid
TWILIO_PHONE_NUMBER=+1234567890
```

---

## 🔑 API ENDPOINTS CHEAT SHEET

### Authentication

| Method | Endpoint           | Purpose       |
| ------ | ------------------ | ------------- |
| POST   | `/auth/send-otp`   | Send OTP      |
| POST   | `/auth/verify-otp` | Verify OTP    |
| POST   | `/auth/register`   | Register user |
| POST   | `/auth/login`      | Login (JWT)   |

### Packages

| GET | `/packages` | List packages |
| GET | `/packages?vehicle_type=car` | Car packages |
| GET | `/packages/{id}` | Package details |

### Bookings

| POST | `/bookings` | Create booking |
| GET | `/bookings` | List bookings |
| GET | `/bookings/{id}` | Booking details |
| PATCH | `/bookings/{id}/status` | Update status |

### Cleaner

| GET | `/cleaner/jobs` | Get jobs |
| PATCH | `/cleaner/jobs/{id}/status` | Update status |
| PATCH | `/cleaner/location` | Update location |
| GET | `/cleaner/location/{id}` | Get location |

### Admin

| GET | `/admin/bookings` | All bookings |
| GET | `/admin/cleaners` | All cleaners |
| POST | `/admin/cleaners` | Add cleaner |
| POST | `/admin/bookings/{id}/assign` | Assign cleaner |

### WebSocket

| WS | `/ws/booking/{id}` | Real-time updates |

---

## 💻 CURL TEMPLATES

### Send OTP

```bash
curl -X POST "http://localhost:8000/auth/send-otp" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+919876543210"}'
```

### Verify OTP

```bash
curl -X POST "http://localhost:8000/auth/verify-otp" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+919876543210", "otp_code": "123456"}'
```

### Register

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+919876543210", "full_name": "John"}'
```

### Login

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+919876543210"}'
```

### Get Packages

```bash
curl -X GET "http://localhost:8000/packages"
curl -X GET "http://localhost:8000/packages?vehicle_type=car"
```

### Create Booking

```bash
curl -X POST "http://localhost:8000/bookings" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT" \
  -d '{
    "vehicle_id": "uuid",
    "package_id": "uuid",
    "address": "123 Main St",
    "latitude": 12.97,
    "longitude": 77.59,
    "payment_method": "cash"
  }'
```

### Assign Cleaner

```bash
curl -X POST "http://localhost:8000/admin/bookings/{booking_id}/assign" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ADMIN_JWT" \
  -d '{"cleaner_id": "uuid"}'
```

---

## 🗄️ DATABASE QUICK FACTS

**Tables:** users, vehicles, packages, bookings, cleaner_locations

**Booking Status Flow:**

```
pending → assigned → en_route → in_progress → completed
```

**Seed Data:**

- 5 packages (3 car + 2 bike)
- Prices: ₹79 to ₹599
- Durations: 20 to 90 minutes

---

## 🔐 JWT TOKEN HEADER

After login, include in all protected endpoints:

```bash
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 📁 FILE STRUCTURE SUMMARY

```
app/
├── main.py           ← Entry point
├── auth/             ← OTP + JWT
├── bookings/         ← Booking CRUD
├── cleaners/         ← Cleaner jobs
├── admin/            ← Admin panel
├── database/         ← DB setup
├── models/           ← ORM models
├── schemas/          ← Validation
├── services/         ← Logic
└── websocket/        ← Real-time

schema.sql           ← Database DDL
requirements.txt     ← Dependencies
.env.example         ← Config template
Dockerfile           ← Docker setup
docker-compose.yml   ← Dev environment
```

---

## 🚀 DEPLOYMENT QUICK LINKS

**Docker (Local):**

```bash
docker-compose up -d
```

**Render (MVP Recommended):**

1. Push to GitHub
2. Connect to Render
3. Add environment variables
4. Deploy

**Railway (Alternative):**

1. Connect GitHub
2. Auto-deploy on push
3. Add PostgreSQL service

---

## 🧪 TESTING QUICK COMMANDS

```bash
# All packages
curl http://localhost:8000/packages

# API docs
http://localhost:8000/docs

# Database test
psql -d washioo -c "SELECT COUNT(*) FROM packages;"

# Server health
curl http://localhost:8000/
```

---

## 🆘 COMMON ERRORS & FIXES

| Error                         | Fix                        |
| ----------------------------- | -------------------------- |
| `could not connect to server` | Start PostgreSQL service   |
| `Invalid token`               | Use correct JWT from login |
| `Twilio error`                | Check credentials in .env  |
| `Port 8000 in use`            | Change port: `--port 8001` |
| `Database not found`          | Run: `createdb washioo`    |

---

## 📞 QUICK SUPPORT RESOURCES

- **API Docs**: http://localhost:8000/docs
- **Setup**: README.md
- **Quick Start**: QUICKSTART.md
- **Deployment**: DEPLOYMENT.md
- **Testing**: TESTING.md
- **Structure**: PROJECT_STRUCTURE.md

---

## ✅ BEFORE GOING LIVE

- [ ] Update CORS origins in main.py
- [ ] Set strong JWT_SECRET
- [ ] Verify Twilio credentials
- [ ] Test all endpoints
- [ ] Setup database backups
- [ ] Enable HTTPS
- [ ] Configure environment secrets
- [ ] Test on staging first

---

## 📊 WHAT'S INCLUDED

✅ 21 API endpoints
✅ WebSocket real-time
✅ OTP authentication
✅ JWT tokens
✅ SMS notifications
✅ PostgreSQL database
✅ Docker setup
✅ 5 deployment options
✅ 49 pages documentation
✅ 30+ test scenarios
✅ Complete codebase

---

## 🎯 TYPICAL WORKFLOW

1. Customer sends OTP → Verify → Register → Login (get JWT)
2. Customer browses packages → Creates booking
3. Admin assigns cleaner (SMS sent)
4. Cleaner updates status/location via app
5. Customer sees real-time updates via WebSocket
6. Service completes → SMS confirmation sent
7. Payment collected → Booking closed

---

## 📦 ONE-LINER DEPLOYMENT

```bash
docker-compose up -d
```

Then open: http://localhost:8000/docs

---

**Everything you need to launch! 🚀**
