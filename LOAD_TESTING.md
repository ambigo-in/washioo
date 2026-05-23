# Washioo Load Testing Guide

Use this guide to test how the Render deployment behaves when 10 or 100 users hit the API at the same time.

The included script uses `httpx`, which is already in `requirements.txt`, so you do not need to install a new load-testing package.

## 1. Start With Safe Public Endpoints

Default command:

```powershell
python scripts/load_test.py --base-url https://your-render-service.onrender.com
```

By default this hits:

```text
GET /washioo-api/health
```

Default scenarios:

```text
10-users: 10 users, 5 requests each
100-users-spike: 100 users, 1 request each at the same time
100-users-sustained: 100 users, 5 requests each
```

Avoid load testing OTP endpoints in production unless you intentionally want to test SMS/rate-limit behavior. OTP tests can send real SMS messages and may trigger provider limits.

## 2. Add More Endpoints

You can repeat `--endpoint` to test multiple read-only routes:

```powershell
python scripts/load_test.py `
  --base-url https://your-render-service.onrender.com `
  --endpoint GET:/washioo-api/health `
  --endpoint GET:/washioo-api/services/
```

For this codebase, the safest unauthenticated endpoint that reads real database data is:

```text
GET /washioo-api/services/
```

That route reads active service categories from PostgreSQL. It is a better test than `/health` when you want to measure a public API that actually needs database data.

Run only this public DB-backed API:

```powershell
python scripts/load_test.py `
  --base-url https://washioo.onrender.com `
  --endpoint GET:/washioo-api/services/
```

Run 100 users against that public DB-backed API:

```powershell
python scripts/load_test.py `
  --base-url https://washioo.onrender.com `
  --endpoint GET:/washioo-api/services/ `
  --scenario 100-users-services:100:1 `
  --timeout 60
```

Run 1000 users against that public DB-backed API:

```powershell
python scripts/load_test.py `
  --base-url https://washioo.onrender.com `
  --endpoint GET:/washioo-api/services/ `
  --scenario 1000-users-services:1000:1 `
  --timeout 120
```

Another unauthenticated DB-backed API exists, but it needs a real service ID:

```text
GET /washioo-api/services/service-categories/{service_id}
```

Example:

```powershell
python scripts/load_test.py `
  --base-url https://washioo.onrender.com `
  --endpoint GET:/washioo-api/services/service-categories/YOUR_SERVICE_ID `
  --scenario 100-users-one-service:100:1 `
  --timeout 60
```

For authenticated endpoints, set a bearer token first:

```powershell
$env:LOAD_TEST_BEARER_TOKEN="your_access_token"
python scripts/load_test.py `
  --base-url https://your-render-service.onrender.com `
  --endpoint GET:/washioo-api/auth/me
```

In this codebase, every authenticated API already hits the database during authentication because the backend loads the current user and roles from PostgreSQL. The APIs below also read business data from the database and are safer for load testing because they are `GET` requests.

Customer token examples:

```powershell
$env:LOAD_TEST_BEARER_TOKEN="customer_access_token"
python scripts/load_test.py `
  --base-url https://washioo.onrender.com `
  --endpoint GET:/washioo-api/services/addresses `
  --endpoint GET:/washioo-api/services/my-bookings `
  --endpoint GET:/washioo-api/customer/vehicles `
  --endpoint GET:/washioo-api/customer/notifications `
  --scenario 100-users-customer-read:100:1 `
  --timeout 60
```

Cleaner token examples:

```powershell
$env:LOAD_TEST_BEARER_TOKEN="cleaner_access_token"
python scripts/load_test.py `
  --base-url https://washioo.onrender.com `
  --endpoint GET:/washioo-api/services/cleaner/profile `
  --endpoint GET:/washioo-api/services/cleaner/assignments `
  --endpoint GET:/washioo-api/cleaner/notifications `
  --endpoint GET:/washioo-api/cleaner/earnings `
  --scenario 100-users-cleaner-read:100:1 `
  --timeout 60
```

Admin token examples:

```powershell
$env:LOAD_TEST_BEARER_TOKEN="admin_access_token"
python scripts/load_test.py `
  --base-url https://washioo.onrender.com `
  --endpoint GET:/washioo-api/users/ `
  --endpoint GET:/washioo-api/services/admin/all-bookings `
  --endpoint GET:/washioo-api/services/admin/cleaners `
  --endpoint GET:/washioo-api/admin/notifications `
  --endpoint GET:/washioo-api/payments/ `
  --scenario 100-users-admin-read:100:1 `
  --timeout 60
```

Avoid load testing authenticated write APIs on production unless you use staging data. That includes `POST`, `PATCH`, `PUT`, and `DELETE` routes for bookings, payments, vehicles, notification read status, cleanup, assignment accept/reject/start/complete, profile updates, and service/category admin changes.

If one token has `customer`, `cleaner`, and `admin` roles, use the built-in tri-role read preset to hit 10 authenticated read APIs at the same time:

```powershell
$env:LOAD_TEST_BEARER_TOKEN="your_three_role_access_token"
python scripts/load_test.py `
  --base-url https://washioo.onrender.com `
  --preset tri-role-read `
  --scenario 100-users-10-apis:100:10 `
  --timeout 60
```

This schedules:

```text
100 users
10 requests per user
10 authenticated read APIs
1000 total requests starting together
```

The `tri-role-read` preset includes:

```text
GET /washioo-api/users/me
GET /washioo-api/services/addresses
GET /washioo-api/services/my-bookings
GET /washioo-api/customer/vehicles
GET /washioo-api/customer/notifications
GET /washioo-api/services/cleaner/profile
GET /washioo-api/services/cleaner/assignments
GET /washioo-api/cleaner/notifications
GET /washioo-api/services/admin/all-bookings
GET /washioo-api/users/
```

## 3. Custom User Counts

Run exactly 10 users:

```powershell
python scripts/load_test.py `
  --base-url https://your-render-service.onrender.com `
  --scenario 10-users:10:1
```

Run exactly 100 users at the same time:

```powershell
python scripts/load_test.py `
  --base-url https://your-render-service.onrender.com `
  --scenario 100-users-same-time:100:1
```

Run 100 users with more pressure:

```powershell
python scripts/load_test.py `
  --base-url https://your-render-service.onrender.com `
  --scenario 100-users-sustained:100:10
```

## 4. How To Read Results

Important values:

```text
p50: normal user latency
p95: slow-user latency, usually the most useful API performance signal
p99: worst-tail latency
failed: errors, timeouts, or non-2xx/non-3xx status responses
throughput: how many requests per second the deployment handled
```

Good first target for a small API:

```text
GET health/public reads: p95 below 500-1000ms
Authenticated DB reads: p95 below 1000-2000ms
Writes/bookings/payments: p95 below 2000-3000ms
Failed requests: 0%
```

Render free web services can have cold starts because they spin down after idle time. Run the test twice: the first run shows cold-start impact, the second run shows warm behavior. See Render's free instance notes: https://render.com/free

## 5. What To Improve Based On Symptoms

If `/health` is slow:

- Render instance is cold, CPU-limited, or the database connection is slow.
- Check Render logs for worker boot time, memory usage, and database connection errors.
- Consider paid Render instance, keep-alive pings, or making `/health` optionally skip DB checks for uptime monitoring.

If public read endpoints are slow:

- Add/verify database indexes for filtered and sorted columns.
- Avoid loading unnecessary rows or relationships.
- Add pagination limits.
- Cache rarely changing public data such as service categories.

If authenticated endpoints are slow:

- Check JWT/token lookup work.
- Check database queries behind `get_current_user`.
- Avoid repeated user/role queries inside one request.

If errors start at 100 users:

- Check Render logs for timeout, memory, and worker restart messages.
- Reduce `DATABASE_POOL_SIZE` on free/small plans if PostgreSQL cannot handle many connections.
- Add more Uvicorn workers only when the instance has enough CPU and database capacity.
- Add rate limits for expensive endpoints.

If p95/p99 are much higher than p50:

- Some requests are waiting on DB connections, external services, or slow queries.
- Profile the slow endpoint locally and inspect SQL query time.
- Add indexes and remove avoidable external calls from the request path.

## 6. Important Production Safety

Start with read-only endpoints. Do not load test booking creation, payment mutation, cleanup, or admin delete endpoints on production unless you use a separate staging database.

For serious testing, create a Render staging service with a separate database and realistic test data. Production load testing should be small and controlled.
