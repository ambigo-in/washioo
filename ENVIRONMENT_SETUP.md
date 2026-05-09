# Washioo Environment Setup

This note covers the env values that matter for the latest refresh-token behavior and Web Push notifications.

## Refresh Token And Mass Logout Prevention

The current auth code signs JWTs with `SECRET_KEY`, stores refresh tokens by `jti`, and keeps only a keyed hash of the token in the database. To avoid a mass logout:

1. Keep `SECRET_KEY` unchanged across normal redeploys.
2. Set `REFRESH_TOKEN_EXPIRE_DAYS` to the intended session lifetime, currently `7`.
3. During key rotation, do not replace the key directly. Move the old key into `PREVIOUS_SECRET_KEYS`, then set the new `SECRET_KEY`.
4. Keep each old key in `PREVIOUS_SECRET_KEYS` for at least `REFRESH_TOKEN_EXPIRE_DAYS`.
5. After that window passes, remove the old key from `PREVIOUS_SECRET_KEYS`.

Example key rotation:

```env
SECRET_KEY=new-generated-secret-key-at-least-32-chars
PREVIOUS_SECRET_KEYS=old-generated-secret-key-at-least-32-chars
```

Multiple old keys are comma-separated:

```env
PREVIOUS_SECRET_KEYS=old-key-one,old-key-two
```

Generate a strong key:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Required Production Values

Set these before deployment:

```env
DEBUG=False
ENVIRONMENT=production
LOG_LEVEL=INFO

DATABASE_URL=postgresql://washioo_user:strong_password@postgres:5432/washioo_db
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=0
DATABASE_POOL_RECYCLE_SECONDS=1800

SECRET_KEY=generated-stable-secret-key
PREVIOUS_SECRET_KEYS=
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

RATE_LIMIT_ENABLED=True
SEND_OTP_RATE_LIMIT=3/15 minutes
AUTH_RATE_LIMIT=5/15 minutes
REFRESH_RATE_LIMIT=20/1 hour

SMS_COUNTRY_KEY=real_smscountry_account_key
SMS_COUNTRY_TOKEN=real_smscountry_auth_token
SMS_HEADER=AMBHPL

CORS_ORIGINS=["https://your-frontend.example.com"]
CORS_CREDENTIALS=True
CORS_METHODS=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
CORS_HEADERS=["*"]
FRONTEND_URL=https://your-frontend.example.com
```

## Web Push Notifications

Web Push is optional. Stored in-app notifications work even when `WEB_PUSH_ENABLED=False`; browser push delivery requires the values below.

```env
WEB_PUSH_ENABLED=True
WEB_PUSH_VAPID_PUBLIC_KEY=your_vapid_public_key
WEB_PUSH_VAPID_PRIVATE_KEY=your_vapid_private_key
WEB_PUSH_VAPID_SUBJECT=mailto:support@your-domain.com
```

Generate VAPID keys with pywebpush/py-vapid after installing requirements:

```bash
python -m py_vapid --gen
```

If that module entrypoint is unavailable in your local environment, generate the pair with any standard Web Push VAPID key generator and paste the public/private values into `.env`.

## Notification Enablement Process

1. Install dependencies so `pywebpush==2.0.3` is available:

```bash
pip install -r requirements.txt
```

2. Run the database migrations through `db/migration/V14__web_push_notifications.sql`. This creates `push_subscriptions` and adds the notification lookup index.
3. Set `WEB_PUSH_ENABLED=True` and configure the VAPID public/private keys.
4. Make sure the frontend origin is present in `CORS_ORIGINS`.
5. Restart the API after changing env values.
6. In the frontend, for cleaner users:
   - Register a service worker.
   - Request browser notification permission.
   - Fetch `GET /washioo-api/cleaner/push/public-key`.
   - Subscribe with the returned VAPID public key.
   - Save the subscription with `POST /washioo-api/cleaner/push/subscriptions`.
   - On logout, remove the subscription with `DELETE /washioo-api/cleaner/push/subscriptions`.

Customer and cleaner notification history can be fetched from:

```text
GET /washioo-api/customer/notifications
GET /washioo-api/cleaner/notifications
PATCH /washioo-api/customer/notifications/{notification_id}/read
PATCH /washioo-api/cleaner/notifications/{notification_id}/read
```

Currently, browser push subscription endpoints are implemented for cleaners. Customer notifications are stored and readable through the customer notification APIs.
