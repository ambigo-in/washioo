# Payment Management APIs - Complete Overview

## Current Payment System Architecture

### Database Structure

- **payments** table tracks:
  - `id` (UUID primary key)
  - `booking_id` (FK to bookings)
  - `customer_id` (FK to users)
  - `payment_method` (Cash/UPI)
  - `transaction_reference` (for external tracking)
  - `amount` (decimal 10,2)
  - `payment_status` (pending, paid, failed)
  - `collected_by_cleaner` (boolean)
  - `paid_at` (timestamp)
  - `created_at`, `updated_at`

---

## New Admin Payment Management APIs

All payment endpoints are **admin-only** and use the `/payments` prefix.

### 1. **Get Payment Statistics**

```
GET /payments/stats
```

**Response:**

```json
{
  "message": "Payment statistics fetched successfully",
  "statistics": {
    "total_payments": 15,
    "pending_count": 5,
    "paid_count": 9,
    "failed_count": 1,
    "total_amount_paid": 4500.5,
    "total_amount_pending": 2200.0
  }
}
```

---

### 2. **List All Payments (with optional filters)**

```
GET /payments/?limit=50&offset=0&status=paid
```

**Query Parameters:**

- `status` (optional): Filter by status (pending, paid, failed)
- `limit` (default: 50): Number of records
- `offset` (default: 0): Pagination offset

**Response:**

```json
{
  "message": "Payments fetched successfully",
  "payments": [
    {
      "id": "uuid",
      "booking_id": "uuid",
      "customer_id": "uuid",
      "payment_method": "UPI",
      "transaction_reference": "TXN123456",
      "amount": 499.0,
      "payment_status": "paid",
      "collected_by_cleaner": false,
      "paid_at": "2026-05-02T14:30:00",
      "created_at": "2026-05-02T10:00:00",
      "updated_at": "2026-05-02T14:30:00"
    }
  ],
  "total": 15,
  "pending_count": 5,
  "paid_count": 9,
  "failed_count": 1
}
```

---

### 3. **Get Payment by Booking**

```
GET /payments/booking/{booking_id}
```

**Response:**

```json
{
  "message": "Booking payment fetched successfully",
  "payment": {
    "id": "uuid",
    "booking_id": "uuid",
    "payment_method": "Cash",
    "amount": 499.00,
    "payment_status": "pending",
    ...
  }
}
```

---

### 4. **Get Payments by Customer**

```
GET /payments/customer/{customer_id}?limit=50&offset=0
```

**Response:**

```json
{
  "message": "Customer payments fetched successfully",
  "customer_id": "uuid",
  "payments": [...],
  "total": 5
}
```

---

### 5. **Get Payment Details**

```
GET /payments/{payment_id}
```

**Response:**

```json
{
  "message": "Payment details fetched successfully",
  "payment": {
    "id": "uuid",
    "booking_id": "uuid",
    "customer_id": "uuid",
    "payment_method": "UPI",
    "transaction_reference": "TXN123456",
    "amount": 499.0,
    "payment_status": "paid",
    "collected_by_cleaner": false,
    "paid_at": "2026-05-02T14:30:00",
    "created_at": "2026-05-02T10:00:00",
    "updated_at": "2026-05-02T14:30:00"
  }
}
```

---

### 6. **Update Payment Manually (Admin)**

```
PUT /payments/{payment_id}
```

**Request Body:**

```json
{
  "payment_method": "Cash",
  "payment_status": "paid",
  "transaction_reference": "TXN789012",
  "amount": 550.0,
  "collected_by_cleaner": true,
  "paid_at": "2026-05-02T15:00:00"
}
```

**All fields are optional** - only provide fields you want to update.

**Response:**

```json
{
  "message": "Payment updated successfully",
  "payment": {
    "id": "uuid",
    "payment_method": "Cash",
    "payment_status": "paid",
    ...
  }
}
```

---

### 7. **Quick Action: Mark Payment as Paid**

```
POST /payments/{payment_id}/mark-paid?transaction_reference=TXN123456
```

**Query Parameters:**

- `transaction_reference` (optional): Add transaction ID while marking paid

**Response:**

```json
{
  "message": "Payment marked as paid successfully",
  "payment": {
    "id": "uuid",
    "payment_status": "paid",
    "paid_at": "2026-05-02T14:30:00",
    ...
  }
}
```

---

### 8. **Quick Action: Mark Payment as Failed**

```
POST /payments/{payment_id}/mark-failed
```

**Response:**

```json
{
  "message": "Payment marked as failed successfully",
  "payment": {
    "id": "uuid",
    "payment_status": "failed",
    ...
  }
}
```

---

### 9. **Delete Payment (Pending Only)**

```
DELETE /payments/{payment_id}
```

**Restrictions:**

- Only pending payments can be deleted
- Use for data cleanup only

**Response:**

```json
{
  "message": "Payment deleted successfully"
}
```

---

## Use Cases

### Scenario 1: Customer Pays via UPI

1. Payment record created with `status: pending`
2. Admin receives notification or manual entry
3. Admin calls: `POST /payments/{id}/mark-paid?transaction_reference=UPI_TXN_XYZ`
4. Payment status changes to `paid`, `paid_at` auto-set

### Scenario 2: Manual Cash Payment Collection

1. Cleaner collects cash from customer
2. Admin updates payment:
   ```
   PUT /payments/{id}
   {
     "payment_method": "Cash",
     "payment_status": "paid",
     "collected_by_cleaner": true,
     "amount": 499.00
   }
   ```

### Scenario 3: Payment Failed - Update Amount

1. Payment initially for 499
2. Customer negotiates, needs to be 450
3. Admin updates:
   ```
   PUT /payments/{id}
   {
     "amount": 450.00
   }
   ```

### Scenario 4: View Payment Dashboard

1. Admin calls: `GET /payments/stats`
2. Get real-time: total pending, total paid, revenue
3. Track cash flow and outstanding amounts

### Scenario 5: Track Customer Payment History

1. Admin calls: `GET /payments/customer/{cust_id}`
2. See all payments made by that customer
3. Identify payment patterns or issues

---

## Database Integration

### Automatic Fields

- `created_at`: Set automatically on creation
- `updated_at`: Updated automatically on any change
- `paid_at`: Set automatically when marking as paid
- `id`: UUID generated automatically

### Manual Entry Points (Admin Controlled)

- `payment_method` (Cash/UPI)
- `payment_status` (pending/paid/failed)
- `transaction_reference` (for tracking)
- `amount`
- `collected_by_cleaner`

---

## Authorization

✅ **Admin only** - All payment endpoints require admin role
❌ Customers cannot view other customers' payments
❌ Cleaners cannot modify payments directly

---

## Error Handling

| Error                                  | Status | Cause                                 |
| -------------------------------------- | ------ | ------------------------------------- |
| "Payment not found"                    | 404    | Invalid payment ID                    |
| "Invalid status"                       | 400    | Status not in (pending, paid, failed) |
| "Amount must be > 0"                   | 400    | Invalid amount value                  |
| "Only pending payments can be deleted" | 400    | Trying to delete paid/failed          |
| "Customer not found"                   | 400    | Invalid customer ID                   |

---

## Files Created/Modified

✅ `schemas/payment_schema.py` - PaymentUpdateRequest, PaymentResponse
✅ `repositories/payment_repository.py` - DB operations
✅ `services/payment_service.py` - Business logic
✅ `routers/payment_router.py` - API endpoints
✅ `main.py` - Router registration + OpenAPI tags

---

## Next Steps (Optional)

1. **Webhook Notifications**: Notify admin/cleaner when payment status changes
2. **Payment Reconciliation**: Generate reports for accounting
3. **Refund System**: Add refund endpoints for paid payments
4. **Settlement**: Connect cleaner_settlements table for payouts
5. **Audit Logs**: Track all payment changes with admin who made them

---

**Status**: ✅ **Ready for Production**
