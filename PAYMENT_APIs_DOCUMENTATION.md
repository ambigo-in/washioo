# Payment APIs - Frontend Integration Guide

This document describes the current payment flow for the car/bike service platform.

## Payment Flow

1. Cleaner completes the wash assignment.
2. Cleaner records collection from the customer:
   - collected amount
   - payment type: `upi` or `cash`
3. Admin sees collected payments in the dashboard.
4. Admin manually splits the amount:
   - cleaner share
   - admin share
5. System updates cleaner earnings.
6. Customer dashboard shows payment collection status and payment type only.
7. Cleaner dashboard shows earnings after admin split.

## Service Prices

| Service | Price |
| --- | ---: |
| Bike Wash | 59 |
| Car Wash | 199 |

## Auth

All endpoints require JWT auth.

Use:

```http
Authorization: Bearer <access_token>
```

## Payment Status Values

The new payment workflow uses:

| Status | Meaning |
| --- | --- |
| `pending_collection` | Booking is completed, but cleaner has not recorded payment collection yet |
| `collected` | Cleaner recorded payment collection; waiting for admin split |
| `split_done` | Admin split is complete; cleaner earnings are updated |

## Payment Type Values

```json
"upi" | "cash"
```

Use lowercase values in new payment APIs.

## Common Payment Object

Admin and cleaner-facing payment APIs return this shape:

```json
{
  "id": "payment_uuid",
  "booking_id": "booking_uuid",
  "customer_id": "customer_uuid",
  "collected_amount": 59.0,
  "payment_type": "upi",
  "collected_by": "cleaner_profile_uuid",
  "collected_at": "2026-05-02T18:30:00",
  "cleaner_share": 40.0,
  "admin_share": 19.0,
  "split_updated_by": "admin_user_uuid",
  "split_updated_at": "2026-05-02T18:45:00",
  "status": "split_done",
  "created_at": "2026-05-02T18:00:00",
  "updated_at": "2026-05-02T18:45:00"
}
```

Fields that are not completed yet are returned as `null`.

---

# New Payment Workflow APIs

## 1. Cleaner Collects Payment

```http
PATCH /bookings/{booking_id}/payment/collect
```

Auth: Cleaner only

Use this after the booking status is `completed`.

### Request

```json
{
  "amount": 59.0,
  "payment_type": "upi"
}
```

### Response

```json
{
  "message": "Payment collection recorded successfully",
  "payment": {
    "id": "payment_uuid",
    "booking_id": "booking_uuid",
    "customer_id": "customer_uuid",
    "collected_amount": 59.0,
    "payment_type": "upi",
    "collected_by": "cleaner_profile_uuid",
    "collected_at": "2026-05-02T18:30:00",
    "cleaner_share": null,
    "admin_share": null,
    "split_updated_by": null,
    "split_updated_at": null,
    "status": "collected",
    "created_at": "2026-05-02T18:00:00",
    "updated_at": "2026-05-02T18:30:00"
  }
}
```

### Frontend Notes

- Show this action only to cleaners.
- The booking must already be completed.
- The cleaner can collect only for their own assigned booking.
- Do not allow a second collection attempt once status is `collected` or `split_done`.

### Possible Errors

| Status | Detail |
| --- | --- |
| 400 | `Booking must be completed before payment collection` |
| 400 | `Cleaner can only collect payment for their assigned booking` |
| 400 | `Payment has already been collected` |
| 400 | `Cannot collect payment after admin split` |
| 403 | Cleaner role required |

---

## 2. Admin Lists Payments

```http
GET /admin/payments?status=collected&limit=50&offset=0
```

Auth: Admin only

### Query Params

| Param | Required | Values | Default |
| --- | --- | --- | --- |
| `status` | No | `pending_collection`, `collected`, `split_done` | all statuses |
| `limit` | No | 1 to 100 | 50 |
| `offset` | No | 0 or greater | 0 |

### Response

```json
{
  "message": "Payments fetched successfully",
  "payments": [
    {
      "id": "payment_uuid",
      "booking_id": "booking_uuid",
      "customer_id": "customer_uuid",
      "collected_amount": 59.0,
      "payment_type": "cash",
      "collected_by": "cleaner_profile_uuid",
      "collected_at": "2026-05-02T18:30:00",
      "cleaner_share": null,
      "admin_share": null,
      "split_updated_by": null,
      "split_updated_at": null,
      "status": "collected",
      "created_at": "2026-05-02T18:00:00",
      "updated_at": "2026-05-02T18:30:00"
    }
  ],
  "total": 1
}
```

### Frontend Notes

- Admin dashboard should usually filter `status=collected` for payments waiting for split.
- `pending_collection` can be used to show completed bookings where cleaner has not collected payment.
- `split_done` can be used for payment history.

---

## 3. Admin Splits Payment

```http
PATCH /admin/payments/{payment_id}/split
```

Auth: Admin only

### Request

```json
{
  "cleaner_share": 40.0,
  "admin_share": 19.0
}
```

Validation:

```text
cleaner_share + admin_share must equal collected_amount
```

Example for Bike Wash:

```text
40 + 19 = 59
```

### Response

```json
{
  "message": "Payment split applied successfully",
  "payment": {
    "id": "payment_uuid",
    "booking_id": "booking_uuid",
    "customer_id": "customer_uuid",
    "collected_amount": 59.0,
    "payment_type": "upi",
    "collected_by": "cleaner_profile_uuid",
    "collected_at": "2026-05-02T18:30:00",
    "cleaner_share": 40.0,
    "admin_share": 19.0,
    "split_updated_by": "admin_user_uuid",
    "split_updated_at": "2026-05-02T18:45:00",
    "status": "split_done",
    "created_at": "2026-05-02T18:00:00",
    "updated_at": "2026-05-02T18:45:00"
  }
}
```

### Frontend Notes

- Show split form only when payment status is `collected`.
- After success, remove the payment from the "Awaiting Split" list.
- Cleaner earnings update immediately after this endpoint succeeds.

### Possible Errors

| Status | Detail |
| --- | --- |
| 400 | `Payment must be collected before admin split` |
| 400 | `Payment split has already been applied` |
| 400 | `Cleaner share plus admin share must equal collected amount` |
| 404/400 | `Payment not found` |
| 403 | Admin role required |

---

## 4. Cleaner Earnings Summary

```http
GET /cleaner/earnings
```

Auth: Cleaner only

### Response

```json
{
  "message": "Cleaner earnings fetched successfully",
  "earnings": {
    "cleaner_id": "cleaner_profile_uuid",
    "total_earned": 400.0,
    "pending_payout": 400.0,
    "last_updated": "2026-05-02T18:45:00"
  }
}
```

### Frontend Notes

- `total_earned`: lifetime earnings recorded from admin splits.
- `pending_payout`: amount currently owed to cleaner.
- Values are `0` when the cleaner has no split payments yet.

---

## 5. Customer Payment Status

```http
GET /customer/bookings/{booking_id}/payment-status
```

Auth: Customer only

This endpoint intentionally does not expose amount details.

### Response - Not Collected

```json
{
  "message": "Payment status fetched successfully",
  "payment": {
    "booking_id": "booking_uuid",
    "status": "pending_collection",
    "payment_type": null,
    "message": "Payment not collected yet"
  }
}
```

### Response - Collected

```json
{
  "message": "Payment status fetched successfully",
  "payment": {
    "booking_id": "booking_uuid",
    "status": "collected",
    "payment_type": "cash",
    "message": "Payment collected via Cash"
  }
}
```

### Response - Split Done

```json
{
  "message": "Payment status fetched successfully",
  "payment": {
    "booking_id": "booking_uuid",
    "status": "split_done",
    "payment_type": "upi",
    "message": "Payment collected via UPI"
  }
}
```

### Frontend Notes

- Customer UI should display the `payment.message`.
- Do not show amount, cleaner share, or admin share on customer dashboard.
- Customer can only fetch payment status for their own booking.

---

# Legacy Admin Payment APIs

These endpoints still exist for backward compatibility with the old admin dashboard. New frontend work should prefer the workflow APIs above.

Legacy status values:

```json
"pending" | "paid" | "failed"
```

Legacy payment method values:

```json
"UPI" | "Cash"
```

## Get Payment Statistics

```http
GET /payments/stats
```

Auth: Admin only

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

## List Legacy Payments

```http
GET /payments/?status=pending&limit=50&offset=0
```

Auth: Admin only

```json
{
  "message": "Payments fetched successfully",
  "payments": [
    {
      "id": "payment_uuid",
      "booking_id": "booking_uuid",
      "customer_id": "customer_uuid",
      "payment_method": "UPI",
      "transaction_reference": null,
      "amount": 59.0,
      "payment_status": "pending",
      "collected_by_cleaner": true,
      "paid_at": null,
      "created_at": "2026-05-02T18:00:00",
      "updated_at": "2026-05-02T18:30:00"
    }
  ],
  "total": 15,
  "pending_count": 5,
  "paid_count": 9,
  "failed_count": 1
}
```

## Get Legacy Payment by Booking

```http
GET /payments/booking/{booking_id}
```

Auth: Admin only

## Get Legacy Payments by Customer

```http
GET /payments/customer/{customer_id}?limit=50&offset=0
```

Auth: Admin only

## Get Legacy Payment Details

```http
GET /payments/{payment_id}
```

Auth: Admin only

## Update Legacy Payment Manually

```http
PUT /payments/{payment_id}
```

Auth: Admin only

```json
{
  "payment_method": "Cash",
  "payment_status": "paid",
  "transaction_reference": "TXN789012",
  "amount": 59.0,
  "collected_by_cleaner": true,
  "paid_at": "2026-05-02T18:45:00"
}
```

All fields are optional.

## Mark Legacy Payment as Paid

```http
POST /payments/{payment_id}/mark-paid?transaction_reference=TXN123456
```

Auth: Admin only

## Mark Legacy Payment as Failed

```http
POST /payments/{payment_id}/mark-failed
```

Auth: Admin only

## Delete Legacy Payment

```http
DELETE /payments/{payment_id}
```

Auth: Admin only

Only legacy payments with `payment_status = "pending"` can be deleted.

---

# Recommended Frontend Screens

## Cleaner App

- Complete assignment using existing assignment completion API.
- After completion, show "Collect Payment" action.
- Submit:

```json
{
  "amount": 199.0,
  "payment_type": "cash"
}
```

- Show earnings card from `GET /cleaner/earnings`.

## Admin Dashboard

- Payment queue:

```http
GET /admin/payments?status=collected
```

- Split modal inputs:
  - `cleaner_share`
  - `admin_share`

- Validate on frontend that:

```text
cleaner_share + admin_share === collected_amount
```

Backend still validates this.

## Customer Dashboard

- For each booking, call:

```http
GET /customer/bookings/{booking_id}/payment-status
```

- Display only:
  - `payment.message`
  - optional status badge

---

# Error Response Shape

FastAPI validation and service errors return:

```json
{
  "detail": "Error message"
}
```

For request body validation errors, FastAPI may return:

```json
{
  "detail": [
    {
      "type": "greater_than",
      "loc": ["body", "amount"],
      "msg": "Input should be greater than 0",
      "input": 0,
      "ctx": {
        "gt": 0
      }
    }
  ]
}
```

---

# Implementation Files

- `schemas/payment_schema.py`
- `models/payment.py`
- `models/cleaner_earning.py`
- `repositories/payment_repository.py`
- `services/payment_service.py`
- `routers/payment_router.py`
- `db/migration/V6__payment_collection_and_cleaner_earnings.sql`

Status: Ready for frontend integration.
