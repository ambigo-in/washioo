# Washioo Application Flow Documentation

This document explains how the current Washioo customer, cleaner, and admin flows work after automatic cleaner assignment.

## Customer

1. Customer verifies phone through OTP.
2. Customer signs in or signs up.
3. Customer chooses a service category.
4. Customer selects an existing address or adds a new address.
5. If the address is unsaved during checkout, frontend saves it before booking.
6. Customer selects Today/Tomorrow/date and Now/time.
7. Customer confirms booking.
8. Backend creates the booking and tries auto assignment.
9. If a cleaner is found, booking status becomes `assigned`.
10. If no cleaner is found, booking remains `pending`.
11. If the assigned cleaner rejects, backend immediately offers the booking to the next eligible cleaner.
12. Customer tracks booking from My Bookings.
13. Customer receives notifications for cleaner assignment, service start, and service completion.
14. Customer rates the cleaner after completion.

## Cleaner

1. Cleaner signs up with Aadhaar and optional driving license.
2. Cleaner waits for admin approval.
3. Approved cleaner sets availability to `available`.
4. Frontend captures current location and sends it to backend.
5. Cleaner remains eligible for auto assignment while approved, available, recently located, and inside service radius.
6. New auto-assigned booking appears in dashboard live services and My Assignments.
7. Cleaner opens details and accepts or rejects.
8. If cleaner rejects, the booking is automatically offered to the next eligible cleaner.
9. Cleaner can start route from assignment card/details after accepting.
10. Cleaner starts service.
11. Cleaner completes service and records collected amount/payment type.
12. Cleaner rates customer after completion.
13. Cleaner earnings update after admin payment reconciliation.

## Admin

1. Admin logs in through `/admin/login`.
2. Admin manages cleaners, users, services, bookings, payments, and ratings.
3. Admin approves cleaner profiles.
4. Admin can configure service price and extra-payment handling.
5. Admin monitors bookings.
6. If booking is pending, admin can click Auto Assign to retry system matching.
7. Admin manually assigns only when the auto pool is exhausted, cleaners are offline/busy, location is missing, or business support needs to override.
8. Admin reconciles payments after cleaner records collection.

## Auto Assignment

Auto assignment is triggered immediately after customer booking creation.

Eligibility:

- cleaner approval status is `approved`
- cleaner availability status is `available`
- cleaner has enabled auto assignment
- cleaner has current latitude/longitude
- cleaner location was updated within the freshness window
- booking address has latitude/longitude
- distance is within cleaner service radius

Scoring:

- closer cleaners score higher
- higher-rated cleaners score higher
- active assigned/accepted/in-progress jobs reduce score
- very high completed job count adds a small fairness reduction

Fallback:

- if no cleaner qualifies, booking remains `pending`
- if a cleaner rejects, the backend records the rejected attempt and tries the next eligible cleaner
- previously offered/rejected/expired cleaners are excluded for that booking
- admin can retry Auto Assign
- admin can manually assign only as the final fallback or manual override

## Important Backend Files

- `services/auto_assignment_service.py`: scoring and selection
- `repositories/assignment_attempt_repository.py`: auto-assignment attempt tracking
- `services/booking_service.py`: booking lifecycle and assignment actions
- `routers/services_router.py`: booking, cleaner location, and admin auto-assign endpoints
- `models/cleaner_profile.py`: cleaner availability/location fields
- `models/booking_assignment.py`: assignment metadata
- `models/booking_assignment_attempt.py`: dispatch attempt history
- `db/migration/V16__auto_assignment.sql`: auto-assignment fields
- `db/migration/V17__assignment_attempts.sql`: dispatch attempt history

## Important Frontend Files

- `src/pages/CheckoutPage.tsx`: creates bookings
- `src/pages/cleaner/CleanerAvailability.tsx`: captures location when going available
- `src/pages/cleaner/CleanerDashboard.tsx`: refreshes available cleaner location
- `src/pages/cleaner/CleanerAssignments.tsx`: accept/reject/start/complete flow
- `src/pages/admin/AdminBookings.tsx`: manual assignment and Auto Assign retry
