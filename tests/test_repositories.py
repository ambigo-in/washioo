from datetime import datetime
from types import SimpleNamespace

from tests.conftest import FakeDB, FakeQuery, obj, uid


def test_address_repository_crud_and_soft_delete(monkeypatch):
    import repositories.address_repository as repo

    address = obj(id=uid(), user_id=uid(), is_deleted=False, is_default=True)
    db = FakeDB()
    created = repo.create_address(db, {"user_id": address.user_id, "address_line1": "A", "is_default": True})
    assert db.added and created.address_line1 == "A" and db.commits == 1

    assert repo.get_address_by_id(FakeDB([FakeQuery(first_result=address)]), address.id) is address
    assert repo.get_user_addresses(FakeDB([FakeQuery(all_result=[address])]), address.user_id) == [address]
    assert repo.get_user_default_address(FakeDB([FakeQuery(first_result=address)]), address.user_id) is address

    update_query = FakeQuery(first_result=address)
    updated = repo.update_address(FakeDB([update_query, FakeQuery(count_result=1)]), address.id, {"address_line1": "B", "is_default": True})
    assert updated.address_line1 == "B"

    missing = repo.update_address(FakeDB([FakeQuery(first_result=None)]), address.id, {"address_line1": "C"})
    assert missing is None

    unset_query = FakeQuery(count_result=2)
    db = FakeDB([unset_query])
    repo.unset_default_addresses(db, address.user_id, exclude_address_id=address.id)
    assert unset_query.updated == {"is_default": False}
    assert db.commits == 1

    missing_deleted = repo.delete_address(FakeDB([FakeQuery(first_result=None)]), address.id)
    assert missing_deleted == (None, "not_found")

    soft = repo.delete_address(FakeDB([FakeQuery(first_result=address), FakeQuery(count_result=1)]), address.id)
    assert soft[1] == "soft_deleted"
    assert address.is_deleted is True and address.is_default is False

    hard_address = obj(id=uid(), user_id=uid(), is_deleted=False)
    hard_db = FakeDB([FakeQuery(first_result=hard_address), FakeQuery(count_result=0)])
    assert repo.delete_address(hard_db, hard_address.id)[1] == "hard_deleted"
    assert hard_db.deleted == [hard_address]


def test_booking_repository_queries_and_updates():
    import repositories.booking_repository as repo

    booking = obj(id=uid(), booking_status="pending")
    db = FakeDB()
    created = repo.create_booking(db, {"booking_reference": "BK-1"})
    assert created.booking_reference == "BK-1" and db.added

    assert repo.get_booking_by_id(FakeDB([FakeQuery(first_result=booking)]), booking.id) is booking
    assert repo.get_booking_by_reference(FakeDB([FakeQuery(first_result=booking)]), "BK-1") is booking
    assert repo.get_customer_bookings(FakeDB([FakeQuery(all_result=[booking])]), uid()) == [booking]
    assert repo.count_customer_bookings(FakeDB([FakeQuery(count_result=3)]), uid()) == 3
    assert repo.get_all_bookings(FakeDB([FakeQuery(all_result=[booking])])) == [booking]
    assert repo.count_all_bookings(FakeDB([FakeQuery(count_result=4)])) == 4
    assert repo.get_bookings_by_status(FakeDB([FakeQuery(all_result=[booking])]), "pending") == [booking]
    assert repo.count_bookings_by_status(FakeDB([FakeQuery(count_result=5)]), "pending") == 5
    assert repo.get_stale_unassigned_bookings(FakeDB([FakeQuery(all_result=[booking])]), datetime.utcnow()) == [booking]
    assert repo.get_customer_booking_by_id(FakeDB([FakeQuery(first_result=booking)]), uid(), booking.id) is booking

    updated = repo.update_booking_status(FakeDB([FakeQuery(first_result=booking)]), booking.id, "cancelled")
    assert updated.booking_status == "cancelled"
    assert repo.update_booking_status(FakeDB([FakeQuery(first_result=None)]), booking.id, "x") is None
    booking.booking_status = "pending"
    stale_cancelled = repo.cancel_stale_unassigned_booking(FakeDB([FakeQuery(first_result=booking)]), booking.id, datetime.utcnow())
    assert stale_cancelled.booking_status == "cancelled"
    assert repo.cancel_stale_unassigned_booking(FakeDB([FakeQuery(first_result=None)]), booking.id, datetime.utcnow()) is None

    updated = repo.update_booking(FakeDB([FakeQuery(first_result=booking)]), booking.id, {"final_price": 100})
    assert updated.final_price == 100
    assert repo.update_booking(FakeDB([FakeQuery(first_result=None)]), booking.id, {}) is None


def test_user_role_service_and_token_repositories():
    import repositories.role_repository as role_repo
    import repositories.service_repository as service_repo
    import repositories.token_repository as token_repo
    import repositories.user_repository as user_repo

    user = obj(id=uid(), full_name="Old", email="old@example.com", phone="9876543210")
    role = obj(id=uid(), role_name="admin")

    assert user_repo.get_user_by_phone(FakeDB([FakeQuery(first_result=user)]), user.phone) is user
    assert user_repo.get_user_by_email(FakeDB([FakeQuery(first_result=user)]), user.email) is user
    assert user_repo.get_user_by_email(FakeDB(), None) is None
    assert user_repo.create_user(FakeDB(), {"phone": "9876543211"}).phone == "9876543211"
    assert user_repo.get_user_by_id(FakeDB([FakeQuery(first_result=user)]), user.id) is user
    assert user_repo.get_all_users(FakeDB([FakeQuery(all_result=[user])])) == [user]
    assert user_repo.get_users_by_role(FakeDB([FakeQuery(all_result=[user])]), "admin") == [user]
    update_data = obj(full_name="New", email="new@example.com", phone=None)
    assert user_repo.update_user_details(FakeDB(), user, update_data).full_name == "New"
    db = FakeDB()
    assert user_repo.delete_user(db, user) is True and db.deleted == [user]
    assert user_repo.get_user_with_roles(FakeDB([FakeQuery(first_result=user)]), user.id) is user

    assert role_repo.get_role_by_name(FakeDB([FakeQuery(first_result=role)]), "ADMIN") is role
    assigned = role_repo.assign_role_to_user(FakeDB(), user.id, role.id)
    assert assigned.user_id == user.id and assigned.role_id == role.id
    user_with_roles = obj(user_roles=[obj(role=obj(role_name="admin"))])
    role_repo.get_user_with_roles = lambda db, user_id: user_with_roles
    assert role_repo.get_user_roles(FakeDB(), user.id) == ["admin"]
    assert role_repo.user_has_role(FakeDB(), user.id, "admin") is True
    role_repo.get_user_with_roles = lambda db, user_id: None
    assert role_repo.get_user_roles(FakeDB(), user.id) == []
    assert role_repo.user_has_role(FakeDB(), user.id, "admin") is False

    service = obj(id=uid(), service_name="Wash")
    assert service_repo.get_all_services(FakeDB([FakeQuery(all_result=[service])])) == [service]
    assert service_repo.get_service_by_id(FakeDB([FakeQuery(first_result=service)]), service.id) is service
    assert service_repo.get_service_by_name(FakeDB([FakeQuery(first_result=service)]), "Wash") is service
    assert service_repo.create_service(FakeDB(), {"service_name": "Wax"}).service_name == "Wax"
    assert service_repo.update_service(FakeDB([FakeQuery(first_result=service)]), service.id, {"service_name": "Detail"}).service_name == "Detail"
    assert service_repo.update_service(FakeDB([FakeQuery(first_result=None)]), service.id, {}) is None
    delete_db = FakeDB([FakeQuery(first_result=service)])
    assert service_repo.delete_service(delete_db, service.id) is service
    assert service.is_active is False
    assert service_repo.delete_service(FakeDB([FakeQuery(first_result=None)]), service.id) is None

    token = token_repo.save_refresh_token(FakeDB(), user.id, "jti", "raw", datetime.utcnow())
    assert token.user_id == user.id and token.jti == "jti"
    existing = obj(revoked_at=None)
    assert token_repo.revoke_token(FakeDB([FakeQuery(first_result=existing)]), "jti") is True
    assert existing.revoked_at is not None
    assert token_repo.revoke_token(FakeDB([FakeQuery(first_result=None)]), "missing") is False
    payload = {"type": "refresh", "jti": "jti"}
    token_obj = obj(token_hash=token_repo.hash_token("raw"), revoked_at=None, expires_at=datetime.utcnow())
    assert token_repo.get_refresh_token(FakeDB([FakeQuery(first_result=token_obj)]), "raw", payload) is token_obj
    assert token_repo.get_refresh_token(FakeDB(), "raw", {"type": "access", "jti": "jti"}) is None
    assert token_repo.get_refresh_token(FakeDB(), "raw", {"type": "refresh"}) is None


def test_cleaner_assignment_vehicle_notification_and_payment_repositories():
    import repositories.assignment_attempt_repository as attempt_repo
    import repositories.assignment_repository as assignment_repo
    import repositories.cleaner_repository as cleaner_repo
    import repositories.customer_vehicle_repository as vehicle_repo
    import repositories.notification_repository as notification_repo
    import repositories.payment_repository as payment_repo

    cleaner = obj(id=uid(), user_id=uid(), total_jobs_completed=0)
    assignment = obj(id=uid(), booking_id=uid(), cleaner_id=cleaner.id, assignment_status="assigned")
    vehicle = obj(id=uid(), customer_id=uid(), is_default=False)
    notification = obj(id=uid(), is_read=False)
    subscription = obj(endpoint="e", is_active=True)
    payment = obj(id=uid(), booking_id=uid(), customer_id=uid(), payment_status="pending")

    assert cleaner_repo.create_cleaner_profile(FakeDB(), {"user_id": cleaner.user_id}).user_id == cleaner.user_id
    assert cleaner_repo.get_cleaner_profile_by_id(FakeDB([FakeQuery(first_result=cleaner)]), cleaner.id) is cleaner
    assert cleaner_repo.get_cleaner_profile_by_user_id(FakeDB([FakeQuery(first_result=cleaner)]), cleaner.user_id) is cleaner
    assert cleaner_repo.get_all_cleaner_profiles(FakeDB([FakeQuery(all_result=[cleaner])])) == [cleaner]
    assert cleaner_repo.get_auto_assignable_cleaners(FakeDB([FakeQuery(all_result=[cleaner])])) == [cleaner]
    assert cleaner_repo.count_cleaner_active_assignments(FakeDB([FakeQuery(count_result=2)]), cleaner.id) == 2
    assert cleaner_repo.update_cleaner_profile(FakeDB([FakeQuery(first_result=cleaner)]), cleaner.id, {"vehicle_type": "bike"}).vehicle_type == "bike"
    assert cleaner_repo.update_cleaner_profile(FakeDB([FakeQuery(first_result=None)]), cleaner.id, {}) is None
    delete_db = FakeDB([FakeQuery(first_result=cleaner)])
    assert cleaner_repo.delete_cleaner_profile(delete_db, cleaner.id) is cleaner
    assert cleaner_repo.delete_cleaner_profile(FakeDB([FakeQuery(first_result=None)]), cleaner.id) is None
    user_for_role = obj(user_roles=[obj(role=obj(role_name="cleaner"))])
    assert cleaner_repo.user_has_cleaner_role(FakeDB([FakeQuery(first_result=user_for_role)]), cleaner.user_id) is True
    assert cleaner_repo.user_has_cleaner_role(FakeDB([FakeQuery(first_result=None)]), cleaner.user_id) is False

    assert assignment_repo.create_assignment(FakeDB(), {"booking_id": assignment.booking_id}).booking_id == assignment.booking_id
    assert assignment_repo.get_assignment_by_id(FakeDB([FakeQuery(first_result=assignment)]), assignment.id) is assignment
    assert assignment_repo.get_assignment_by_booking_id(FakeDB([FakeQuery(first_result=assignment)]), assignment.booking_id) is assignment
    assert assignment_repo.get_cleaner_assignments(FakeDB([FakeQuery(all_result=[assignment])]), cleaner.id) == [assignment]
    assert assignment_repo.get_all_assignments(FakeDB([FakeQuery(all_result=[assignment])])) == [assignment]
    assert assignment_repo.update_assignment(FakeDB([FakeQuery(first_result=assignment)]), assignment.id, {"assignment_status": "accepted"}).assignment_status == "accepted"
    assert assignment_repo.update_assignment(FakeDB([FakeQuery(first_result=None)]), assignment.id, {}) is None

    attempt = attempt_repo.create_assignment_attempt(FakeDB(), {"booking_id": assignment.booking_id})
    assert attempt.booking_id == assignment.booking_id
    assert attempt_repo.get_assignment_attempts_by_booking(FakeDB([FakeQuery(all_result=[attempt])]), assignment.booking_id) == [attempt]
    assert attempt_repo.get_latest_open_attempt(FakeDB([FakeQuery(first_result=attempt)]), assignment.booking_id, cleaner.id) is attempt
    assert attempt_repo.update_assignment_attempt(FakeDB(), attempt, {"status": "rejected"}).status == "rejected"
    assert attempt_repo.update_assignment_attempt(FakeDB(), None, {}) is None
    assert attempt_repo.close_latest_open_attempt(FakeDB([FakeQuery(first_result=attempt)]), assignment.booking_id, cleaner.id, "expired", "late").status == "expired"
    assert attempt_repo.close_latest_open_attempt(FakeDB([FakeQuery(first_result=None)]), assignment.booking_id, cleaner.id, "expired", None) is None

    assert vehicle_repo.create_vehicle(FakeDB(), {"customer_id": vehicle.customer_id, "is_default": True}).customer_id == vehicle.customer_id
    assert vehicle_repo.get_customer_vehicles(FakeDB([FakeQuery(all_result=[vehicle])]), vehicle.customer_id) == [vehicle]
    assert vehicle_repo.get_customer_vehicle_by_id(FakeDB([FakeQuery(first_result=vehicle)]), vehicle.customer_id, vehicle.id) is vehicle
    assert vehicle_repo.get_customer_default_vehicle(FakeDB([FakeQuery(first_result=vehicle)]), vehicle.customer_id) is vehicle
    unset_query = FakeQuery(count_result=1)
    vehicle_repo.unset_customer_default_vehicles(FakeDB([unset_query]), vehicle.customer_id)
    assert unset_query.updated == {"is_default": False}
    assert vehicle_repo.update_vehicle(FakeDB(), vehicle, {"is_default": True}).is_default is True
    db = FakeDB()
    vehicle_repo.delete_vehicle(db, vehicle)
    assert db.deleted == [vehicle]

    assert notification_repo.create_notification(FakeDB(), {"user_id": uid(), "title": "T"}).title == "T"
    assert notification_repo.get_user_notifications(FakeDB([FakeQuery(all_result=[notification])]), uid(), True) == [notification]
    assert notification_repo.get_user_notification_by_id(FakeDB([FakeQuery(first_result=notification)]), uid(), notification.id) is notification
    assert notification_repo.mark_notification_read(FakeDB(), notification).is_read is True
    assert notification_repo.upsert_push_subscription(FakeDB([FakeQuery(first_result=None)]), uid(), "e", "p", "a").endpoint == "e"
    subscription.is_active = False
    assert notification_repo.upsert_push_subscription(FakeDB([FakeQuery(first_result=subscription)]), uid(), "e", "p2", "a2").is_active is True
    assert notification_repo.get_active_push_subscriptions(FakeDB([FakeQuery(all_result=[subscription])]), uid()) == [subscription]
    notification_repo.mark_push_subscription_used(FakeDB(), subscription)
    assert subscription.last_used_at is not None
    notification_repo.deactivate_push_subscription(FakeDB(), subscription)
    assert subscription.is_active is False
    db = FakeDB([FakeQuery(first_result=subscription)])
    assert notification_repo.delete_push_subscription_by_endpoint(db, uid(), "e") is subscription
    assert notification_repo.delete_push_subscription_by_endpoint(FakeDB([FakeQuery(first_result=None)]), uid(), "e") is None

    assert payment_repo.get_payment_by_id(FakeDB([FakeQuery(first_result=payment)]), payment.id) is payment
    assert payment_repo.get_payment_by_booking_id(FakeDB([FakeQuery(first_result=payment)]), payment.booking_id) is payment
    assert payment_repo.get_payment_by_booking_id_for_update(FakeDB([FakeQuery(first_result=payment)]), payment.booking_id) is payment
    assert payment_repo.get_payment_by_id_for_update(FakeDB([FakeQuery(first_result=payment)]), payment.id) is payment
    assert payment_repo.get_all_payments(FakeDB([FakeQuery(all_result=[payment])])) == [payment]
    assert payment_repo.get_payments_by_status(FakeDB([FakeQuery(all_result=[payment])]), "pending") == [payment]
    assert payment_repo.get_admin_collection_payments(FakeDB([FakeQuery(all_result=[payment])]), "collected", "pending") == [payment]
    assert payment_repo.get_cleaner_earning_by_cleaner_id(FakeDB([FakeQuery(first_result=payment)]), cleaner.id) is payment
    assert payment_repo.get_cleaner_earning_by_cleaner_id_for_update(FakeDB([FakeQuery(first_result=payment)]), cleaner.id) is payment
    assert payment_repo.get_payments_by_customer(FakeDB([FakeQuery(all_result=[payment])]), payment.customer_id) == [payment]
    assert payment_repo.get_payment_stats(FakeDB([FakeQuery(one_result=(3, 1, 1, 1))])) == {"total": 3, "pending": 1, "paid": 1, "failed": 1}
    assert payment_repo.create_payment(FakeDB(), {"booking_id": payment.booking_id, "customer_id": payment.customer_id}).booking_id == payment.booking_id
    assert payment_repo.update_payment(FakeDB([FakeQuery(first_result=payment)]), payment.id, {"payment_status": "paid", "amount": None}).payment_status == "paid"
    assert payment_repo.update_payment(FakeDB([FakeQuery(first_result=None)]), payment.id, {}) is None
    db = FakeDB([FakeQuery(first_result=payment)])
    assert payment_repo.delete_payment(db, payment.id) is True
    assert payment_repo.delete_payment(FakeDB([FakeQuery(first_result=None)]), payment.id) is False
    assert payment_repo.get_payment_total_amount(FakeDB([FakeQuery(scalar_result=123)]), "paid") == 123.0
