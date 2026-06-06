# Cleaner Verification Workflow

## Migration

Run `db/migration/V19__cleaner_document_verification.sql` in pgAdmin before deploying the code. The migration is additive and keeps all new columns nullable where existing cleaner accounts may not yet have documents.

## Storage

Cleaner profile photos and document images are uploaded to Supabase Storage. PostgreSQL stores only URL strings.

Required environment variables:

- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `SUPABASE_STORAGE_BUCKET`
- `MAX_UPLOAD_SIZE_BYTES`
- `DRIVING_LICENSE_REQUIRED`

Allowed upload formats are `jpg`, `jpeg`, `png`, and `webp`. The default maximum size is 3 MB.

## Cleaner Workflow

Cleaner signup still uses the existing JSON auth endpoint for backward compatibility. New frontend clients require a profile photo and Aadhaar image during signup, then upload those images immediately through authenticated document endpoints.

Existing cleaners can use Profile to upload missing documents:

- Profile photo can be updated any time.
- Aadhaar image and number are submitted for admin review.
- Driving license is optional unless `DRIVING_LICENSE_REQUIRED=True`.

If an already submitted Aadhaar or driving license is changed, the new document is stored in pending fields and the cleaner moves to `pending_reverification`. Admin approval is required before it replaces the active document.

## Admin Workflow

Admin cleaner details now show personal information, identity numbers, current document previews, pending replacement document previews, and review actions.

Review actions:

- `PUT /services/admin/cleaners/{cleaner_id}/approve`
- `PUT /services/admin/cleaners/{cleaner_id}/reject`
- `PUT /services/admin/cleaners/{cleaner_id}/request-resubmission`

Reject and request-resubmission require a reason. The cleaner sees this reason in Profile.

## Cleaner APIs

- `GET /services/cleaner/profile`
- `POST /services/cleaner/profile/photo`
- `POST /services/cleaner/profile/aadhaar`
- `POST /services/cleaner/profile/driving-license`

The upload APIs accept multipart form data with a `file` field. Aadhaar and driving license endpoints also accept optional number fields:

- `aadhaar_number`
- `driving_license_number`

## Booking Visibility

Customer booking responses now include `assignment.cleaner_details` with:

- Cleaner name
- Profile photo URL
- Rating
- Experience count
- Verification badge

The frontend displays cleaner details after a booking is accepted, in progress, or completed.

## Security Notes

- Aadhaar and driving license formats are validated server-side.
- Aadhaar and driving license duplicate checks use existing HMAC hashes.
- Uploaded files are validated by extension, MIME type, and size before storage.
- Image binaries are never stored in PostgreSQL.
- Cleaner availability and booking acceptance remain blocked unless the cleaner is approved.

## Assumptions

- The Supabase bucket serves public URLs for cleaner/customer/admin previews.
- Existing cleaners without document images remain able to sign in and complete their profile.
- Existing clients that only call JSON signup continue to work, but those cleaners remain pending until documents are uploaded and approved.
