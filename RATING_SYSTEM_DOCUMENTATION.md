# Rating System APIs - Frontend Integration Guide

This document describes the bidirectional rating system for completed car/bike service bookings.

Base URL:

```txt
http://localhost:8000
```

All protected endpoints require JWT auth:

```http
Authorization: Bearer <access_token>
```

## Overview

After a booking is completed:

1. Customer can rate the assigned cleaner.
2. Cleaner can rate the customer.
3. Each side can submit only one rating per booking.
4. Ratings cannot be edited or submitted again.
5. Admin can view all ratings.

Ratings are tied to a specific booking.

## Important UI Rules

| Rule | Frontend Behavior |
| --- | --- |
| Booking must be `completed` | Show rating form only after booking completion |
| One rating per user per booking | After successful submit, disable/hide rating form |
| Rating range is `1` to `5` | Use star/rating input with min `1`, max `5` |
| One decimal allowed | Allow values like `4`, `4.0`, `4.5`; do not allow `4.25` |
| Comment is optional | Textarea can be empty |
| Comment max length is `500` | Add character counter and client validation |
| Blind review is enabled | Do not show the other party's rating until current user has submitted |

## Blind Review Behavior

Blind review mode is currently enabled in backend.

For customer/cleaner users:

- Before current user submits their own rating, `GET /bookings/{booking_id}/ratings` returns an empty list.
- After current user submits, the same endpoint returns submitted ratings for that booking.
- Admin always sees all submitted ratings.

Frontend suggestion:

- If booking is completed and `GET /bookings/{booking_id}/ratings` returns `[]`, show the rating form.
- After submit succeeds, call `GET /bookings/{booking_id}/ratings` again to show available ratings.
- If submit returns `409`, treat it as already rated and hide the form.

## Roles

Supported roles:

```txt
customer
cleaner
admin
```

The backend resolves reviewer role from booking membership:

- If logged-in user is `booking.customer_id`, rating is submitted as `customer`.
- If logged-in user is the assigned cleaner's user account, rating is submitted as `cleaner`.
- Other users receive `403 Forbidden`.

This works with multi-role users because the booking relationship decides which side they represent.

## Data Shapes

### RatingCreateRequest

Used when submitting a rating.

```json
{
  "booking_id": "booking_uuid",
  "rating": 4.5,
  "comment": "Good service"
}
```

Fields:

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `booking_id` | UUID | Yes | Must match the `{booking_id}` path value |
| `rating` | number | Yes | `1` to `5`, max one decimal place |
| `comment` | string or null | No | Max `500` characters |

### RatingResponse

Returned by rating list and submit APIs.

```json
{
  "id": "rating_uuid",
  "booking_id": "booking_uuid",
  "reviewer_role": "customer",
  "rating": 4.5,
  "comment": "Good service",
  "created_at": "2026-05-02T18:30:00",
  "reviewee_name": "Cleaner Name"
}
```

Fields:

| Field | Type | Notes |
| --- | --- | --- |
| `id` | UUID | Rating ID |
| `booking_id` | UUID | Booking being rated |
| `reviewer_role` | `customer` or `cleaner` | Side that submitted this rating |
| `rating` | number | Rating value |
| `comment` | string or null | Optional review text |
| `created_at` | datetime | Rating submission time |
| `reviewee_name` | string or null | Name of the user who was rated |

## Endpoints

## 1. Submit Booking Rating

```http
POST /bookings/{booking_id}/ratings
```

Auth:

```txt
customer or cleaner
```

When to call:

- Booking status is `completed`
- Current user is either the booking customer or assigned cleaner
- Current user has not already rated this booking

Request:

```json
{
  "booking_id": "booking_uuid",
  "rating": 5,
  "comment": "Excellent work"
}
```

Success response: `201 Created`

```json
{
  "id": "rating_uuid",
  "booking_id": "booking_uuid",
  "reviewer_role": "customer",
  "rating": 5.0,
  "comment": "Excellent work",
  "created_at": "2026-05-02T18:30:00",
  "reviewee_name": "Cleaner Name"
}
```

Common errors:

| Status | Meaning | UI Action |
| --- | --- | --- |
| `400` | Path `booking_id` and body `booking_id` do not match | Fix request payload |
| `403` | Booking is not completed, user is not part of booking, or invalid rating side | Hide form or show permission message |
| `404` | Booking not found | Show not found state |
| `409` | User already rated this booking | Hide form and refresh ratings |
| `422` | Invalid rating or comment too long | Show field validation errors |

Duplicate rating message:

```json
{
  "detail": "You have already rated this booking."
}
```

## 2. Get Ratings For A Booking

```http
GET /bookings/{booking_id}/ratings
```

Auth:

```txt
customer, cleaner, or admin
```

Access rules:

- Customer can view ratings for own booking.
- Cleaner can view ratings for assigned booking.
- Admin can view ratings for any booking.

Success response: `200 OK`

```json
[
  {
    "id": "rating_uuid_1",
    "booking_id": "booking_uuid",
    "reviewer_role": "customer",
    "rating": 5.0,
    "comment": "Excellent work",
    "created_at": "2026-05-02T18:30:00",
    "reviewee_name": "Cleaner Name"
  },
  {
    "id": "rating_uuid_2",
    "booking_id": "booking_uuid",
    "reviewer_role": "cleaner",
    "rating": 4.5,
    "comment": "Polite customer",
    "created_at": "2026-05-02T18:35:00",
    "reviewee_name": "Customer Name"
  }
]
```

Blind review empty response:

```json
[]
```

Frontend note:

For customer/cleaner users, an empty list can mean either no ratings exist yet or the current user has not submitted their own rating yet.

## 3. Get Cleaner Rating Summary

```http
GET /cleaners/{cleaner_id}/ratings
```

Auth:

```txt
admin or customer
```

Path parameter:

| Field | Meaning |
| --- | --- |
| `cleaner_id` | ID from `cleaner_profiles.id`, not `users.id` |

Success response: `200 OK`

```json
{
  "average_rating": 4.75,
  "total_ratings": 12,
  "recent_reviews": [
    {
      "id": "rating_uuid",
      "booking_id": "booking_uuid",
      "reviewer_role": "customer",
      "rating": 5.0,
      "comment": "Great cleaning",
      "created_at": "2026-05-02T18:30:00",
      "reviewee_name": "Cleaner Name"
    }
  ]
}
```

Frontend use:

- Show cleaner's average rating on cleaner profile cards.
- Show `total_ratings` beside stars.
- Show latest 5 customer reviews from `recent_reviews`.

## 4. Get Customer Rating Summary

```http
GET /customers/{customer_id}/ratings
```

Auth:

```txt
admin or cleaner
```

Path parameter:

| Field | Meaning |
| --- | --- |
| `customer_id` | Customer's `users.id` |

Success response: `200 OK`

```json
{
  "average_rating": 4.3,
  "total_ratings": 8
}
```

Frontend use:

- Cleaner app can show customer reputation before/after assignment if product allows it.
- Admin dashboard can show customer quality/reliability.

## 5. Admin List Ratings

```http
GET /admin/ratings
```

Auth:

```txt
admin only
```

Query parameters:

| Parameter | Type | Required | Notes |
| --- | --- | --- | --- |
| `reviewer_role` | `customer` or `cleaner` | No | Filter by who submitted the rating |
| `booking_id` | UUID | No | Filter by booking |
| `page` | integer | No | Default `1` |
| `limit` | integer | No | Default `50`, max `100` |

Example:

```http
GET /admin/ratings?reviewer_role=customer&page=1&limit=20
```

Success response: `200 OK`

```json
{
  "ratings": [
    {
      "id": "rating_uuid",
      "booking_id": "booking_uuid",
      "reviewer_role": "customer",
      "rating": 5.0,
      "comment": "Excellent work",
      "created_at": "2026-05-02T18:30:00",
      "reviewee_name": "Cleaner Name"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 20
}
```

## Recommended Frontend Flows

### Customer Completed Booking Screen

1. Check booking status.
2. If `booking_status !== "completed"`, do not show rating form.
3. If completed, call:

```http
GET /bookings/{booking_id}/ratings
```

4. If response is empty, show "Rate cleaner" form.
5. Submit with:

```http
POST /bookings/{booking_id}/ratings
```

6. On success, hide form and refresh booking ratings.
7. On `409`, hide form and refresh booking ratings.

### Cleaner Completed Assignment Screen

1. Check linked booking status.
2. If completed, allow cleaner to rate customer.
3. Use the same submit endpoint:

```http
POST /bookings/{booking_id}/ratings
```

4. Backend automatically submits as cleaner if the logged-in cleaner is assigned to that booking.

### Admin Ratings Dashboard

Use:

```http
GET /admin/ratings?page=1&limit=50
```

Recommended filters:

- reviewer role
- booking ID
- date range can be added later if needed

## Validation Details

### Valid Ratings

```txt
1
1.0
2.5
4.5
5
5.0
```

### Invalid Ratings

```txt
0
5.5
4.25
```

Invalid values return `422 Unprocessable Entity`.

## Error Response Format

Most errors use this shape:

```json
{
  "detail": "Error message"
}
```

Pydantic validation errors use FastAPI's standard validation response:

```json
{
  "detail": [
    {
      "type": "less_than_equal",
      "loc": ["body", "rating"],
      "msg": "Input should be less than or equal to 5",
      "input": 6,
      "ctx": {
        "le": 5
      }
    }
  ]
}
```

## Database Notes For Frontend

Frontend usually does not need these details, but they explain IDs:

- Cleaner summary uses `cleaner_profiles.id`.
- Customer summary uses `users.id`.
- Ratings store both reviewer and reviewee as `users.id`.
- Cleaner average rating is stored on `cleaner_profiles.average_rating`.
- Customer average rating is stored on `users.average_rating`.
- Legacy `reviews` table exists in old schema but new UI should use `ratings`.

## Display Suggestions

Recommended UI components:

- Star input with half-star support.
- Optional review textarea with `500` character counter.
- Disabled submit button until rating is selected.
- Show backend validation errors near the form.
- For completed bookings, show "Rating submitted" state after success.
- For blind review, show a neutral message after submit if the other side has not rated yet.

Suggested blind-review message:

```txt
Your rating has been submitted. The other rating will appear here once available.
```

## Current Limitations

- Ratings cannot be edited.
- Ratings cannot be deleted from public APIs.
- Customer rating summary does not include recent reviews yet.
- Admin date filters are not implemented yet.
- Frontend cannot directly know "current user already rated" except by submit `409` or by ratings becoming visible after submission.
