# Washioo - Deployment Guide

## Deployment Options

Choose one of the following deployment methods:

---

## 1. 🐳 Docker Compose (Local/Self-Hosted)

### Prerequisites

- Docker & Docker Compose installed

### Steps

```bash
# 1. Clone repository
cd washioo

# 2. Create .env file
cp .env.example .env
# Edit .env with your credentials

# 3. Start services
docker-compose up -d

# 4. Check logs
docker-compose logs -f api
```

### Access

- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Database: localhost:5432

### Useful Commands

```bash
# Stop services
docker-compose down

# View logs
docker-compose logs -f api

# Rebuild after code changes
docker-compose up -d --build

# Connect to database
docker-compose exec db psql -U postgres -d washioo
```

---

## 2. ☁️ Render (Recommended for MVP)

### Prerequisites

- GitHub account (push code to GitHub)
- Render account (https://render.com)

### Steps

#### A. Push Code to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git push -u origin main
```

#### B. Create PostgreSQL on Render

1. Go to Render Dashboard
2. Click "New +" → "PostgreSQL"
3. Set name: `washioo-db`
4. Note the connection string

#### C. Create Web Service

1. Click "New +" → "Web Service"
2. Connect GitHub repository
3. Set configuration:
   - **Name**: washioo-api
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 8000`

#### D. Add Environment Variables

In Web Service settings, add:

```
DATABASE_URL=<PostgreSQL connection string from Render>
JWT_SECRET=<generate secure secret>
TWILIO_ACCOUNT_SID=<your value>
TWILIO_AUTH_TOKEN=<your value>
TWILIO_VERIFY_SERVICE_SID=<your value>
TWILIO_PHONE_NUMBER=<your value>
```

#### E. Deploy

Click "Deploy" button and wait for deployment to complete.

### Access

- API: https://washioo-api.onrender.com
- Docs: https://washioo-api.onrender.com/docs

---

## 3. 🚂 Railway (Alternative)

### Prerequisites

- GitHub account
- Railway account (https://railway.app)

### Steps

#### A. Connect GitHub

1. Go to Railway Dashboard
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Connect your GitHub account and select washioo repo

#### B. Create PostgreSQL

1. Click "Add Services" → "Database" → "PostgreSQL"
2. Set database name as `washioo`

#### C. Configure Environment

1. Go to Variables
2. Add all from .env.example
3. Set DATABASE_URL to PostgreSQL connection string

#### D. Deploy

Railway automatically deploys on push to main branch.

### Access

- API: https://washioo-<random>.up.railway.app
- Docs: https://washioo-<random>.up.railway.app/docs

---

## 4. 🌐 AWS EC2 (DIY)

### Prerequisites

- AWS EC2 instance (Ubuntu 20.04 or later)
- SSH access to instance

### Steps

```bash
# 1. SSH into instance
ssh -i your-key.pem ubuntu@your-instance-ip

# 2. Install dependencies
sudo apt-get update
sudo apt-get install -y python3.9 python3-pip postgresql postgresql-contrib nginx

# 3. Clone repository
git clone https://github.com/your-username/washioo.git
cd washioo

# 4. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 5. Install Python packages
pip install -r requirements.txt

# 6. Configure environment
cp .env.example .env
nano .env  # Edit with your credentials

# 7. Setup PostgreSQL
sudo -u postgres createdb washioo
sudo -u postgres psql -d washioo -f schema.sql

# 8. Run with Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app.main:app

# 9. Configure Nginx (reverse proxy)
# Create /etc/nginx/sites-available/washioo
```

---

## 5. 🔧 Heroku (Legacy)

### Note: Heroku free tier ended in Nov 2022

If using Heroku:

```bash
# 1. Install Heroku CLI
# 2. Login
heroku login

# 3. Create app
heroku create washioo-api

# 4. Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# 5. Set environment variables
heroku config:set JWT_SECRET=your-secret
heroku config:set TWILIO_ACCOUNT_SID=your-sid
# ... etc

# 6. Deploy
git push heroku main
```

---

## 📊 Production Checklist

- [ ] Database backed up regularly
- [ ] Environment variables secured
- [ ] HTTPS/SSL enabled
- [ ] CORS properly configured for frontend domains
- [ ] Rate limiting enabled on auth endpoints
- [ ] Error logging and monitoring setup
- [ ] Database connection pooling enabled
- [ ] Secrets not committed to git
- [ ] API documentation accessible
- [ ] Health check endpoint working

---

## 🔐 Security for Production

### Update CORS

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com", "https://www.yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Add Rate Limiting

```bash
pip install slowapi
```

### Use HTTPS

All production deployments should use HTTPS. Render and Railway do this automatically.

### Keep Secrets Safe

- Never commit .env file
- Use platform-specific secret management
- Rotate JWT_SECRET periodically

---

## 🧪 Testing After Deployment

```bash
# Test health check
curl https://your-api-domain.com/

# Test docs
https://your-api-domain.com/docs

# Test auth endpoint
curl -X POST https://your-api-domain.com/auth/send-otp \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+919876543210"}'
```

---

## 📈 Monitoring & Logs

### Render

Dashboard → Logs tab

### Railway

Dashboard → Logs

### Docker

```bash
docker-compose logs -f api
```

### AWS EC2

```bash
sudo journalctl -u gunicorn -f
```

---

## 🐛 Troubleshooting

### API not responding

1. Check if service is running
2. Check logs for errors
3. Verify environment variables
4. Check database connection

### Database connection issues

1. Verify DATABASE_URL
2. Check if database is accessible
3. Run schema.sql again if needed
4. Check network/firewall settings

### Twilio SMS not working

1. Verify TWILIO credentials
2. Check Twilio account balance
3. Verify phone number format
4. Check Twilio logs

### CORS errors

1. Update CORS origins in main.py
2. Test with Postman/curl (no CORS restriction)
3. Check frontend domain matches

---

## 💡 Performance Tuning

### Database Connection Pooling

```python
# In database/session.py
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True
)
```

### Gunicorn Workers

```bash
gunicorn -w 4 -b 0.0.0.0:8000 app.main:app
# Adjust workers based on CPU cores
```

### Cache Headers

Add to main.py for better performance.

---

## 📞 Support

For deployment issues:

1. Check platform-specific documentation
2. Review logs carefully
3. Test locally first with Docker
4. Verify all environment variables are set

---

**Choose Render or Railway for easiest MVP deployment! 🚀**
