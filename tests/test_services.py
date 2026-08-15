from datetime import date, datetime, time, timedelta
from decimal import Decimal
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from httpx import Response

from tests.conftest import FakeDB, FakeQuery, obj, uid


def payment_obj(**overrides):
    base = dict(
        id=uid(),
        booking_id=uid(),
        customer_id=uid(),
        payment_method="Cash",
        transaction_reference=None,
        amount=Decimal("100"),
        payment_status="pending",
        collected_by_cleaner=False,
        paid_at=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        collected_amount=None,
        payment_type=None,
        collected_by=None,
        collected_at=None,
        cleaner_share=None,
        admin_share=None,
        split_updated_by=None,
        split_updated_at=None,
        payout_released=False,
        cleaner_handover_status="pending",
        status="pending_collection",
    )
    base.update(overrides)
    return obj(**base)


@pytest.mark.anyio
async def test_otp_service_create_send_and_verify(monkeypatch):
    import services.otp_service as otp

    sent = []
    monkeypatch.setattr(otp, "_generate_otp", lambda: "123456")
    monkeypatch.setattr(otp, "hash_data", lambda value: f"hash:{value}")

    async def send_ok(phone, code):
        sent.append((phone, code))
        return True

    monkeypatch.setattr(otp, "send_otp_sms", send_ok)
    db = FakeDB()
    assert await otp.create_and_send_otp(db, "9876543210", "signup", "ip", "agent") is True
    assert sent == [("9876543210", "123456")]
    assert db.added[0].otp_code_hash == "hash:123456"
    assert db.commits == 1

    async def send_fail(phone, code):
        return False

    monkeypatch.setattr(otp, "send_otp_sms", send_fail)
    db = FakeDB()
    assert await otp.create_and_send_otp(db, "9876543210") is False
    assert db.rollbacks == 1

    entry = obj(otp_code_hash="hash:123456", attempts=0, consumed_at=None)
    monkeypatch.setattr(otp, "verify_hash", lambda plain, hashed: plain == "123456")
    db = FakeDB([FakeQuery(first_result=entry)])
    assert otp.verify_otp_code(db, "9876543210", "123456") is True
    assert entry.consumed_at is not None

    entry = obj(otp_code_hash="hash:123456", attempts=0, consumed_at=None)
    db = FakeDB([FakeQuery(first_result=entry)])
    assert otp.verify_otp_code(db, "9876543210", "000000") is False
    assert entry.attempts == 1

    assert otp.verify_otp_code(FakeDB([FakeQuery(first_result=None)]), "9876543210", "123456") is False
    entry = obj(otp_code_hash="hash", attempts=999)
    assert otp.verify_otp_code(FakeDB([FakeQuery(first_result=entry)]), "9876543210", "123456") is False


@pytest.mark.anyio
async def test_sms_service_generates_template_and_handles_disabled_config(monkeypatch):
    import services.sms_service as sms

    template = sms.generate_otp_template("123456")
    assert "123456" in template and "SMSCNT" in template
    monkeypatch.setattr(sms.settings, "SMS_COUNTRY_KEY", None)
    assert await sms.send_otp_sms("9876543210", "123456") is False


@pytest.mark.anyio
async def test_storage_service_validation_upload_sign_and_delete(monkeypatch):
    import services.storage_service as storage

    class Upload:
        def __init__(self, filename="a.png", content_type="image/png", content=b"abc"):
            self.filename = filename
            self.content_type = content_type
            self._content = content

        async def read(self):
            return self._content

    content, extension = await storage.validate_image_upload(Upload())
    assert content == b"abc" and extension == "png"

    for file in [
        Upload(filename=None),
        Upload(filename="a.gif"),
        Upload(content_type="text/plain"),
        Upload(content=b""),
    ]:
        with pytest.raises(Exception):
            await storage.validate_image_upload(file)

    monkeypatch.setattr(storage.settings, "MAX_UPLOAD_SIZE_BYTES", 1)
    with pytest.raises(Exception, match="smaller"):
        await storage.validate_image_upload(Upload(content=b"ab"))

    monkeypatch.setattr(storage.settings, "MAX_UPLOAD_SIZE_BYTES", 1024)
    monkeypatch.setattr(storage.settings, "SUPABASE_URL", "https://proj.storage.supabase.co/storage/v1/s3")
    monkeypatch.setattr(storage.settings, "SUPABASE_SERVICE_ROLE_KEY", "key")
    assert storage._clean_supabase_url() == "https://proj.supabase.co"
    monkeypatch.setattr(storage.settings, "SUPABASE_URL", "https://proj.supabase.co/storage/v1")
    assert storage._clean_supabase_url() == "https://proj.supabase.co"
    monkeypatch.setattr(storage.settings, "SUPABASE_URL", None)
    with pytest.raises(Exception, match="not configured"):
        storage._clean_supabase_url()

    assert storage._supabase_error_message(Response(400, json={"message": "bad"})) == "bad"
    assert "raw" in storage._supabase_error_message(Response(400, content=b"raw"))

    monkeypatch.setattr(storage.settings, "SUPABASE_URL", "https://proj.supabase.co")
    paths = [
        "https://proj.supabase.co/storage/v1/object/public/test-bucket/a%20b.png",
        "https://proj.supabase.co/storage/v1/object/sign/test-bucket/a.png",
        "https://proj.supabase.co/object/sign/test-bucket/a.png",
        "https://proj.supabase.co/storage/v1/object/test-bucket/a.png",
    ]
    assert [storage._object_path_from_storage_url(path) for path in paths] == ["a b.png", "a.png", "a.png", "a.png"]
    assert storage._object_path_from_storage_url("https://elsewhere/nope") is None
    assert storage._absolute_supabase_storage_url("https://proj.supabase.co", "/object/sign/bucket/x").endswith("/storage/v1/object/sign/bucket/x")

    class AsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        async def post(self, *args, **kwargs):
            return Response(201, json={})

    monkeypatch.setattr(storage.httpx, "AsyncClient", AsyncClient)
    url = await storage.upload_service_image(Upload(), "svc")
    assert "/storage/v1/object/public/test-bucket/services/svc/" in url

    class Client:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def post(self, *args, **kwargs):
            return Response(200, json={"signedURL": "/object/sign/test-bucket/a.png?token=1"})

        def request(self, *args, **kwargs):
            return Response(200, json={})

    monkeypatch.setattr(storage.httpx, "Client", Client)
    public_url = "https://proj.supabase.co/storage/v1/object/public/test-bucket/a.png"
    signed = storage.create_signed_image_url(public_url, expires_in=120)
    assert signed.endswith("/storage/v1/object/sign/test-bucket/a.png?token=1")
    assert storage.create_signed_image_url(public_url, expires_in=120) == signed
    assert storage.delete_storage_file(public_url) is True
    assert storage.delete_storage_file(None) is False
    assert storage.create_signed_cleaner_image_url(None) is None


def test_cleanup_service_preview_and_deletes():
    import services.cleanup_service as cleanup

    queries = [FakeQuery(count_result=i) for i in range(1, 7)]
    preview = cleanup.get_cleanup_preview(FakeDB(queries), {"otp_codes_hours": 1})
    assert [item["eligible_records"] for item in preview] == [1, 2, 3, 4, 5, 6]
    assert cleanup._cleanup_item("x", "X", None)["eligible_records"] == 0

    for func in [
        cleanup.cleanup_otp_codes,
        cleanup.cleanup_refresh_tokens,
        cleanup.cleanup_notifications,
        cleanup.cleanup_assignment_attempts,
        cleanup.cleanup_push_subscriptions,
        cleanup.cleanup_audit_logs,
    ]:
        assert func(FakeDB([FakeQuery(delete_result=2)])) == 2
    result = cleanup.run_all_cleanups(FakeDB([FakeQuery(delete_result=1) for _ in range(6)]))
    assert set(result) == {"otp_codes", "refresh_tokens", "notifications", "assignment_attempts", "push_subscriptions", "audit_logs"}


def test_notification_service_branches(monkeypatch):
    import services.notification_service as notifications

    made = []

    def create(_db, data):
        notification = obj(id=uid(), is_read=False, created_at=datetime.utcnow(), **data)
        made.append(notification)
        return notification

    monkeypatch.setattr(notifications, "create_notification", create)
    monkeypatch.setattr(notifications, "emit_user_event", lambda *args, **kwargs: None)
    monkeypatch.setattr(notifications, "send_web_push_to_user", lambda *args, **kwargs: {"sent": 0})

    assert notifications.get_web_push_public_config()["enabled"] is False
    payload = obj(endpoint="e", keys=obj(p256dh="p", auth="a"))
    monkeypatch.setattr(notifications, "upsert_push_subscription", lambda *args, **kwargs: "saved")
    assert notifications.save_web_push_subscription_service(FakeDB(), uid(), payload, "ua") == "saved"
    monkeypatch.setattr(notifications, "delete_push_subscription_by_endpoint", lambda *args, **kwargs: True)
    assert notifications.delete_web_push_subscription_service(FakeDB(), uid(), obj(endpoint="e")) is True
    monkeypatch.setattr(notifications, "get_user_notifications", lambda *args: ["n"])
    assert notifications.list_user_notifications_service(FakeDB(), uid()) == ["n"]
    monkeypatch.setattr(notifications, "get_user_notification_by_id", lambda *args: None)
    with pytest.raises(Exception, match="Notification not found"):
        notifications.mark_user_notification_read_service(FakeDB(), uid(), uid())
    monkeypatch.setattr(notifications, "get_user_notification_by_id", lambda *args: obj(id=uid()))
    monkeypatch.setattr(notifications, "mark_notification_read", lambda db, n: "read")
    assert notifications.mark_user_notification_read_service(FakeDB(), uid(), uid()) == "read"

    assert notifications.notify_user_booking_status_change(FakeDB(), None, "T", "M", "type") is None
    booking = obj(id=uid(), customer_id=uid(), booking_reference="BK-1")
    assert notifications.notify_customer_booking_accepted(FakeDB(), booking).notification_type == "booking_accepted"
    assert notifications.notify_customer_service_started(FakeDB(), booking).notification_type == "service_started"
    assert notifications.notify_customer_service_completed(FakeDB(), booking).notification_type == "service_completed"
    assert notifications.notify_customer_booking_rejected(FakeDB(), booking).notification_type == "booking_rejected"
    auto_cancelled = notifications.notify_customer_booking_auto_cancelled(FakeDB(), booking)
    assert auto_cancelled.notification_type == "booking_auto_cancelled"
    assert "Please book again" in auto_cancelled.message
    cleaner = obj(user_id=uid())
    assert notifications.notify_cleaner_verification_approved(FakeDB(), cleaner).notification_type == "cleaner_verification_approved"
    assert "Reason" in notifications.notify_cleaner_verification_rejected(FakeDB(), cleaner, "bad docs").message
    assert "Reason" in notifications.notify_cleaner_document_resubmission_requested(FakeDB(), cleaner, "blurred").message
    assert notifications.notify_cleaner_verification_approved(FakeDB(), None) is None

    service = obj(service_name="Wash")
    assignment = obj(id=uid(), booking_id=uid(), booking=obj(service_category=service, scheduled_date=date.today(), scheduled_time=time(10)), cleaner=None)
    assert notifications.notify_cleaner_booking_assigned(FakeDB(), uid(), assignment).notification_type == "booking_assigned"

    assignment.cleaner = obj(user=obj(full_name="A"))
    assignment.assigned_by_admin = uid()
    assignment.booking.id = uid()
    assignment.booking.booking_reference = "BK-2"
    assert notifications.notify_admin_booking_assignment_accepted(FakeDB(), assignment).notification_type == "booking_assignment_accepted"
    assert notifications.notify_admin_booking_assignment_rejected(FakeDB(), assignment).notification_type == "booking_assignment_rejected"

    formatted = notifications.format_notification(made[-1])
    assert formatted["id"] == str(made[-1].id)

    assert notifications.send_web_push_to_user(FakeDB(), uid(), "T", "B")["sent"] == 0


def test_booking_auto_cancel_service_notifies_customer(monkeypatch):
    import services.booking_auto_cancel_service as auto_cancel

    stale = obj(id=uid(), customer_id=uid(), booking_status="pending")
    skipped = obj(id=uid(), customer_id=uid(), booking_status="pending")
    cancelled = obj(
        id=stale.id,
        customer_id=stale.customer_id,
        booking_status="cancelled",
    )
    notified = []
    events = []

    monkeypatch.setattr(auto_cancel.settings, "BOOKING_AUTO_CANCEL_UNASSIGNED_HOURS", 6)
    monkeypatch.setattr(auto_cancel.settings, "BOOKING_AUTO_CANCEL_BATCH_SIZE", 100)
    monkeypatch.setattr(
        auto_cancel,
        "get_stale_unassigned_bookings",
        lambda db, cutoff, limit: [stale, skipped],
    )
    monkeypatch.setattr(
        auto_cancel,
        "cancel_stale_unassigned_booking",
        lambda db, booking_id, cutoff: cancelled if booking_id == stale.id else None,
    )
    monkeypatch.setattr(
        auto_cancel,
        "notify_customer_booking_auto_cancelled",
        lambda db, booking: notified.append(booking),
    )
    monkeypatch.setattr(
        auto_cancel,
        "emit_user_event",
        lambda user_id, event_type, data: events.append(("user", user_id, event_type, data)),
    )
    monkeypatch.setattr(
        auto_cancel,
        "emit_role_event",
        lambda role, event_type, data: events.append(("role", role, event_type, data)),
    )

    assert auto_cancel.auto_cancel_stale_unassigned_bookings(FakeDB()) == 1
    assert notified == [cancelled]
    assert ("user", cancelled.customer_id, "booking_auto_cancelled", {
        "booking_id": str(cancelled.id),
        "booking_status": "cancelled",
    }) in events
    assert any(event[:3] == ("role", "admin", "booking_auto_cancelled") for event in events)


def test_payment_service_success_and_error_branches(monkeypatch):
    import services.payment_service as payments

    payment = payment_obj()
    assert payments.format_payment(payment)["amount"] == 100.0
    assert payments.format_collection_payment(payment)["status"] == "pending_collection"

    booking = obj(id=uid(), customer_id=uid())
    monkeypatch.setattr(payments, "get_payment_by_booking_id", lambda db, booking_id: payment)
    assert payments.ensure_pending_collection_payment(FakeDB(), booking) is payment
    monkeypatch.setattr(payments, "get_payment_by_booking_id", lambda db, booking_id: None)
    db = FakeDB()
    created = payments.ensure_pending_collection_payment(db, booking)
    assert created.booking_id == booking.id and db.added

    cleaner = obj(id=uid())
    booking = obj(id=uid(), customer_id=uid(), booking_status="completed")
    assignment = obj(cleaner_id=cleaner.id)
    monkeypatch.setattr(payments, "get_cleaner_profile_by_user_id", lambda db, user_id: cleaner)
    monkeypatch.setattr(payments, "get_booking_by_id", lambda db, booking_id: booking)
    monkeypatch.setattr(payments, "get_assignment_by_booking_id", lambda db, booking_id: assignment)
    monkeypatch.setattr(payments, "get_payment_by_booking_id_for_update", lambda db, booking_id: None)
    result = payments.record_collection(FakeDB(), uid(), booking.id, obj(amount=Decimal("120"), payment_type="upi"))
    assert result["status"] == "collected" and result["payment_type"] == "upi"

    monkeypatch.setattr(payments, "get_cleaner_profile_by_user_id", lambda db, user_id: None)
    with pytest.raises(Exception, match="Cleaner profile"):
        payments.record_collection(FakeDB(), uid(), booking.id, obj(amount=1, payment_type="cash"))

    monkeypatch.setattr(payments, "get_cleaner_profile_by_user_id", lambda db, user_id: cleaner)
    monkeypatch.setattr(payments, "get_booking_by_id", lambda db, booking_id: obj(booking_status="pending"))
    with pytest.raises(Exception, match="completed"):
        payments.record_collection(FakeDB(), uid(), booking.id, obj(amount=1, payment_type="cash"))

    monkeypatch.setattr(payments, "get_booking_by_id", lambda db, booking_id: booking)
    monkeypatch.setattr(payments, "get_assignment_by_booking_id", lambda db, booking_id: obj(cleaner_id=uid()))
    with pytest.raises(Exception, match="assigned booking"):
        payments.record_collection(FakeDB(), uid(), booking.id, obj(amount=1, payment_type="cash"))

    monkeypatch.setattr(payments, "get_assignment_by_booking_id", lambda db, booking_id: assignment)
    monkeypatch.setattr(payments, "get_payment_by_booking_id_for_update", lambda db, booking_id: payment_obj(status="split_done"))
    with pytest.raises(Exception, match="after admin split"):
        payments.record_collection(FakeDB(), uid(), booking.id, obj(amount=1, payment_type="cash"))
    monkeypatch.setattr(payments, "get_payment_by_booking_id_for_update", lambda db, booking_id: payment_obj(status="collected"))
    with pytest.raises(Exception, match="already been collected"):
        payments.record_collection(FakeDB(), uid(), booking.id, obj(amount=1, payment_type="cash"))

    collected = payment_obj(status="collected", collected_by=cleaner.id, collected_amount=Decimal("100"))
    monkeypatch.setattr(payments, "get_payment_by_id_for_update", lambda db, payment_id: collected)
    monkeypatch.setattr(payments, "get_cleaner_earning_by_cleaner_id_for_update", lambda db, cleaner_id: None)
    split = payments.apply_admin_split(FakeDB(), uid(), collected.id, obj(cleaner_share=Decimal("70"), admin_share=Decimal("30")))
    assert split["status"] == "split_done"
    for bad_payment, message in [
        (None, "Payment not found"),
        (payment_obj(status="split_done"), "already"),
        (payment_obj(status="pending_collection"), "must be collected"),
        (payment_obj(status="collected", collected_by=None), "missing"),
    ]:
        monkeypatch.setattr(payments, "get_payment_by_id_for_update", lambda db, pid, bad_payment=bad_payment: bad_payment)
        with pytest.raises(Exception, match=message):
            payments.apply_admin_split(FakeDB(), uid(), uid(), obj(cleaner_share=1, admin_share=1))

    monkeypatch.setattr(payments, "get_payment_by_id_for_update", lambda db, pid: payment_obj(status="collected", collected_by=uid(), collected_amount=Decimal("10")))
    with pytest.raises(Exception, match="must equal"):
        payments.apply_admin_split(FakeDB(), uid(), uid(), obj(cleaner_share=Decimal("6"), admin_share=Decimal("5")))

    split_done = payment_obj(status="split_done", cleaner_handover_status="pending")
    monkeypatch.setattr(payments, "get_payment_by_id_for_update", lambda db, pid: split_done)
    assert payments.mark_admin_share_collected(FakeDB(), split_done.id)["cleaner_handover_status"] == "settled"
    with pytest.raises(Exception, match="already"):
        payments.mark_admin_share_collected(FakeDB(), split_done.id)

    monkeypatch.setattr(payments, "get_admin_collection_payments", lambda *args: [payment])
    assert len(payments.get_admin_payments(FakeDB(), status="collected")) == 1
    with pytest.raises(Exception, match="Invalid status"):
        payments.get_admin_payments(FakeDB(), status="bad")
    with pytest.raises(Exception, match="Invalid handover"):
        payments.get_admin_payments(FakeDB(), cleaner_handover_status="bad")

    monkeypatch.setattr(payments, "get_user_by_id", lambda db, cid: obj(id=cid))
    monkeypatch.setattr(payments, "get_payments_by_customer", lambda *args: [payment])
    assert payments.list_payments_by_customer_service(FakeDB(), uid()) == [payments.format_payment(payment)]
    monkeypatch.setattr(payments, "get_user_by_id", lambda db, cid: None)
    with pytest.raises(Exception, match="Customer not found"):
        payments.list_payments_by_customer_service(FakeDB(), uid())

    monkeypatch.setattr(payments, "get_payment_by_id", lambda db, pid: payment)
    monkeypatch.setattr(payments, "update_payment", lambda db, pid, data: payment_obj(**{**payment.__dict__, **data}))
    updated = payments.update_payment_manually_service(FakeDB(), payment.id, obj(payment_method="UPI", payment_status="paid", transaction_reference="tx", amount=20, collected_by_cleaner=True, paid_at=None))
    assert updated["payment_status"] == "paid"
    with pytest.raises(Exception, match="Invalid payment method"):
        payments.update_payment_manually_service(FakeDB(), payment.id, obj(payment_method="Card", payment_status=None, transaction_reference=None, amount=None, collected_by_cleaner=None, paid_at=None))
    with pytest.raises(Exception, match="Amount"):
        payments.update_payment_manually_service(FakeDB(), payment.id, obj(payment_method=None, payment_status=None, transaction_reference=None, amount=0, collected_by_cleaner=None, paid_at=None))

    assert payments.mark_payment_paid_service(FakeDB(), payment.id, "tx")["payment_status"] == "paid"
    assert payments.mark_payment_failed_service(FakeDB(), payment.id)["payment_status"] == "failed"
    monkeypatch.setattr(payments, "get_payment_stats", lambda db: {"total": 3, "pending": 1, "paid": 1, "failed": 1})
    monkeypatch.setattr(payments, "get_payment_total_amount", lambda db, status: 10 if status == "paid" else 5)
    assert payments.get_payment_stats_service(FakeDB())["total_amount_paid"] == 10.0
    monkeypatch.setattr(payments, "delete_payment", lambda db, pid: True)
    assert payments.delete_payment_service(FakeDB(), payment.id) is True
    payment.payment_status = "paid"
    with pytest.raises(Exception, match="Only pending"):
        payments.delete_payment_service(FakeDB(), payment.id)


def test_booking_service_formatters_and_lifecycle_branches(monkeypatch):
    import services.booking_service as booking_service

    monkeypatch.setattr(booking_service, "create_signed_cleaner_image_url", lambda url: f"signed:{url}" if url else None)
    user = obj(full_name="Customer", phone="9876543210", email="c@example.com", profile_image_url="profile.png")
    cleaner_user = obj(full_name="Cleaner", phone="9876543211", email="cl@example.com", profile_image_url="cleaner.png")
    cleaner = obj(
        id=uid(),
        user_id=uid(),
        user=cleaner_user,
        vehicle_type="bike",
        profile_photo_url=None,
        aadhaar_number="123456789012",
        aadhaar_number_hash=None,
        aadhaar_image_url="aadhaar.png",
        driving_license_number="DL1234567890123",
        driving_license_number_hash=None,
        driving_license_image_url="license.png",
        verification_status="approved",
        document_review_status="approved",
        document_resubmission_required=False,
        document_rejection_reason=None,
        documents_submitted_at=datetime.utcnow(),
        documents_verified_at=datetime.utcnow(),
        pending_aadhaar_image_url=None,
        pending_driving_license_image_url=None,
        service_radius_km=Decimal("8"),
        approval_status="approved",
        availability_status="available",
        current_latitude=Decimal("12.1"),
        current_longitude=Decimal("77.1"),
        last_location_at=datetime.utcnow(),
        last_available_at=datetime.utcnow(),
        auto_assign_enabled=True,
        rating=Decimal("4.2"),
        average_rating=Decimal("4.3"),
        total_ratings=2,
        total_jobs_completed=5,
        created_at=datetime.utcnow(),
    )
    assignment = obj(
        id=uid(),
        booking_id=uid(),
        cleaner_id=cleaner.id,
        cleaner=cleaner,
        assignment_status="assigned",
        assigned_by_admin=uid(),
        assigned_at=datetime.utcnow(),
        accepted_at=None,
        started_at=None,
        completed_at=None,
        cleaner_notes="note",
        expires_at=datetime.utcnow(),
        auto_assigned=True,
        assignment_rank=1,
        assignment_score=Decimal("90.2"),
        distance_km=Decimal("1.2"),
    )
    address = obj(
        id=uid(),
        address_label="Home",
        address_line1="A",
        address_line2=None,
        landmark=None,
        city="City",
        state="State",
        pincode="123456",
        country="India",
        latitude=Decimal("12.1"),
        longitude=Decimal("77.1"),
        location_verified=True,
        is_default=True,
        is_deleted=False,
    )
    payment = payment_obj(status="collected", payment_status="pending", payment_type="cash", collected_amount=Decimal("150"))
    booking = obj(
        id=assignment.booking_id,
        booking_reference="BK-1",
        customer_id=uid(),
        customer=user,
        service_category=obj(service_name="Wash"),
        service_category_id=uid(),
        scheduled_date=date.today(),
        scheduled_time=time(10, 30),
        booking_status="assigned",
        estimated_price=Decimal("120"),
        final_price=None,
        special_instructions="Careful",
        address=address,
        assignment=assignment,
        vehicle_id=uid(),
        vehicle_make="Honda",
        vehicle_model="City",
        license_plate="KA01AB1234",
        payment=payment,
        created_at=datetime.utcnow(),
    )
    assignment.booking = booking

    assert booking_service.cleaner_can_view_customer_contact(assignment) is False
    assert booking_service.format_cleaner_booking_detail(booking)["customer_phone"] is None
    assignment.assignment_status = "accepted"
    assert booking_service.cleaner_can_view_customer_contact(assignment) is True
    assert booking_service.format_admin_booking(booking)["payment"]["amount"] == 150.0
    assert booking_service.format_customer_booking(booking)["payment"]["payment_status"] == "done"
    assert booking_service.format_address(None) is None
    assert booking_service.format_vehicle_details(obj(vehicle_id=None))["id"] is None
    assert booking_service.format_customer_vehicle(obj(id=uid(), customer_id=uid(), vehicle_type="car", make="M", model="N", license_plate="L", is_default=True, created_at=None, updated_at=None))["is_default"] is True
    assert booking_service.format_cleaner_profile(cleaner, include_sensitive_identity=True)["identity_data_status"] == "full_available"
    assert booking_service.format_assignment(assignment)["booking"]["booking_reference"] == "BK-1"
    assignment.assignment_status = "assigned"
    assert booking_service.format_cleaner_assignment(assignment)["booking"]["customer_name"] is None

    with pytest.raises(Exception, match="past"):
        booking_service.validate_future_schedule(date.today() - timedelta(days=1), time(1))
    assert booking_service.generate_booking_reference().startswith("BK-")

    monkeypatch.setattr(booking_service, "get_customer_booking_by_id", lambda *args: None)
    with pytest.raises(Exception, match="Booking not found"):
        booking_service.get_customer_booking_service(FakeDB(), "c", "b")
    monkeypatch.setattr(booking_service, "get_customer_booking_by_id", lambda *args: booking)
    assert booking_service.get_customer_booking_service(FakeDB(), "c", "b") is booking

    vehicle = obj(id=uid(), make="M", model="N", license_plate="L")
    payload = obj(
        scheduled_date=date.today() + timedelta(days=1),
        scheduled_time=time(12),
        service_category_id=uid(),
        address_id=None,
        address=None,
        vehicle_id=None,
        special_instructions=None,
    )
    monkeypatch.setattr(booking_service, "get_service_by_id", lambda db, sid: obj(is_active=True, base_price=Decimal("99")))
    monkeypatch.setattr(booking_service, "get_user_default_address", lambda db, cid: obj(id=address.id))
    monkeypatch.setattr(booking_service, "get_address_by_id", lambda db, aid: obj(id=aid, user_id="customer"))
    monkeypatch.setattr(booking_service, "get_customer_default_vehicle", lambda db, cid: vehicle)
    monkeypatch.setattr(booking_service, "create_booking", lambda db, data: obj(id=uid(), **data))
    monkeypatch.setattr(booking_service, "auto_assign_booking", lambda db, bid: {"assigned": False})
    monkeypatch.setattr(booking_service, "get_booking_by_id", lambda db, bid: obj(id=bid, customer_id="customer", booking_status="pending"))
    monkeypatch.setattr(booking_service, "emit_role_event", lambda *args, **kwargs: None)
    created = booking_service.create_new_booking(FakeDB(), "customer", payload)
    assert created.booking_status == "pending"

    monkeypatch.setattr(booking_service, "get_service_by_id", lambda db, sid: obj(is_active=False))
    with pytest.raises(Exception, match="inactive"):
        booking_service.create_new_booking(FakeDB(), "customer", payload)

    monkeypatch.setattr(booking_service, "get_service_by_id", lambda db, sid: obj(is_active=True, base_price=1))
    monkeypatch.setattr(booking_service, "get_user_default_address", lambda db, cid: None)
    with pytest.raises(Exception, match="address"):
        booking_service.create_new_booking(FakeDB(), "customer", payload)


def test_auto_assignment_service_scores_and_paths(monkeypatch):
    import services.auto_assignment_service as auto

    address = obj(latitude=Decimal("12.0"), longitude=Decimal("77.0"))
    booking = obj(id=uid(), customer_id=uid(), booking_status="pending", address=address)
    cleaner = obj(
        id=uid(),
        user_id=uid(),
        last_location_at=datetime.utcnow(),
        current_latitude=Decimal("12.01"),
        current_longitude=Decimal("77.01"),
        service_radius_km=Decimal("8"),
        average_rating=Decimal("4"),
        rating=Decimal("4"),
        total_jobs_completed=10,
    )
    monkeypatch.setattr(auto, "count_cleaner_active_assignments", lambda db, cid: 1)
    score = auto._score_cleaner(FakeDB(), cleaner, booking)
    assert score["score"] > 0
    assert auto._score_cleaner(FakeDB(), cleaner, obj(address=None)) is None
    cleaner.last_location_at = datetime.utcnow() - timedelta(hours=1)
    assert auto._score_cleaner(FakeDB(), cleaner, booking) is None
    cleaner.last_location_at = datetime.utcnow()
    cleaner.service_radius_km = Decimal("0.1")
    assert auto._score_cleaner(FakeDB(), cleaner, booking) is None

    monkeypatch.setattr(auto, "get_assignment_attempts_by_booking", lambda db, bid: [])
    monkeypatch.setattr(auto, "get_booking_by_id", lambda db, bid: None)
    with pytest.raises(Exception, match="Booking not found"):
        auto.auto_assign_booking(FakeDB(), uid())

    monkeypatch.setattr(auto, "get_booking_by_id", lambda db, bid: obj(booking_status="completed"))
    result = auto.auto_assign_booking(FakeDB(), uid())
    assert result["reason"] == "booking_not_assignable"

    monkeypatch.setattr(auto, "get_booking_by_id", lambda db, bid: booking)
    monkeypatch.setattr(auto, "get_assignment_by_booking_id", lambda db, bid: None)
    monkeypatch.setattr(auto, "get_auto_assignable_cleaners", lambda db: [])
    monkeypatch.setattr(auto, "update_booking", lambda *args, **kwargs: None)
    monkeypatch.setattr(auto, "emit_role_event", lambda *args, **kwargs: None)
    result = auto.auto_assign_booking(FakeDB(), booking.id)
    assert result["reason"] == "no_available_cleaner"

    cleaner.service_radius_km = Decimal("8")
    monkeypatch.setattr(auto, "get_auto_assignable_cleaners", lambda db: [cleaner])
    assignment = obj(id=uid(), cleaner=cleaner)
    monkeypatch.setattr(auto, "create_assignment", lambda db, data: obj(id=uid(), **data))
    monkeypatch.setattr(auto, "get_assignment_by_id", lambda db, aid: assignment)
    monkeypatch.setattr(auto, "create_assignment_attempt", lambda *args, **kwargs: None)
    monkeypatch.setattr(auto, "notify_cleaner_booking_assigned", lambda *args, **kwargs: None)
    monkeypatch.setattr(auto, "emit_user_event", lambda *args, **kwargs: None)
    result = auto.auto_assign_booking(FakeDB(), booking.id)
    assert result["assigned"] is True


def test_rating_service_helpers_and_errors(monkeypatch):
    import services.rating_service as ratings

    customer_id = uid()
    cleaner_user_id = uid()
    booking = obj(
        id=uid(),
        customer_id=customer_id,
        booking_status="completed",
        assignment=obj(cleaner=obj(user_id=cleaner_user_id)),
    )
    assert ratings._resolve_reviewer_and_reviewee(booking, customer_id) == ("customer", cleaner_user_id)
    assert ratings._resolve_reviewer_and_reviewee(booking, cleaner_user_id) == ("cleaner", customer_id)
    with pytest.raises(HTTPException):
        ratings._resolve_reviewer_and_reviewee(booking, uid())
    ratings._assert_booking_member(booking, customer_id)
    with pytest.raises(HTTPException):
        ratings._assert_booking_member(booking, uid())
    assert ratings._booking_cleaner_user_id(obj(assignment=None)) is None
    assert ratings._role_names(obj(user_roles=[obj(role=obj(role_name="admin")), obj(role=None)])) == {"admin"}
    rating = obj(id=uid(), booking_id=booking.id, reviewer_role="customer", rating=Decimal("4.5"), comment="good", created_at=datetime.utcnow(), reviewee=obj(full_name="Cleaner"))
    assert ratings._format_rating(rating)["reviewee_name"] == "Cleaner"

    monkeypatch.setattr(ratings, "_get_booking", lambda db, bid: obj(booking_status="pending"))
    with pytest.raises(HTTPException):
        ratings.RatingService.submit_rating(FakeDB(), booking.id, customer_id, "customer", obj(rating=5, comment=None))


def test_admin_export_datetime_user_and_realtime_helpers(monkeypatch):
    import services.admin_export_service as export
    import services.realtime_service as realtime
    import services.user_service as users
    from utils.datetime_utils import utc_isoformat

    assert utc_isoformat(None) is None
    assert utc_isoformat(datetime(2026, 1, 1, 1, 2, 3)).endswith("Z")
    assert export.export_filename("admin").startswith("washioo-admin-export-")
    assert export._excel_value(Decimal("1.50")) == 1.5
    assert export._excel_value(uid())
    assert export._role_names(obj(user_roles=[obj(role=obj(role_name="admin")), obj(role=None)])) == "admin"
    db = FakeDB([
        FakeQuery(all_result=[obj(id=uid(), full_name="A", phone="9", email=None, is_active=True, is_verified=True, terms_accepted=False, average_rating=0, total_ratings=0, last_login=None, created_at=None, updated_at=None, user_roles=[])]),
        FakeQuery(all_result=[]),
        FakeQuery(all_result=[]),
        FakeQuery(all_result=[]),
        FakeQuery(all_result=[]),
    ])
    workbook_bytes = export.build_admin_export_workbook(db, "all")
    assert workbook_bytes.getbuffer().nbytes > 0
    with pytest.raises(ValueError):
        export.build_admin_export_workbook(FakeDB(), "unknown")

    calls = []
    monkeypatch.setattr(realtime.websocket_manager, "emit_to_user", lambda *args: calls.append(args))
    monkeypatch.setattr(realtime.websocket_manager, "emit_to_role", lambda *args: calls.append(args))
    realtime.emit_user_event(uid(), "event", {"x": 1})
    realtime.emit_role_event("admin", "event", {"x": 1})
    assert len(calls) == 2

    user = obj(id=uid(), full_name="A", email=None, phone="9", is_verified=True, is_active=True, user_roles=[obj(role=obj(role_name="admin"))], terms_accepted=False, terms_accepted_at=None, profile_image_url=None, average_rating=0, total_ratings=0, created_at=None)
    assert users.get_user_profile(user)["roles"] == ["admin"]
    monkeypatch.setattr(users, "get_user_by_id", lambda db, uid: user)
    assert users.get_user_details_service(FakeDB(), user.id)["id"] == str(user.id)
    monkeypatch.setattr(users, "get_user_by_id", lambda db, uid: None)
    with pytest.raises(Exception, match="User not found"):
        users.get_user_details_service(FakeDB(), user.id)
