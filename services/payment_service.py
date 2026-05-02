from datetime import datetime
from decimal import Decimal
from sqlalchemy import case, func
from models.cleaner_earning import CleanerEarning
from models.payment import Payment
from repositories.cleaner_repository import get_cleaner_profile_by_user_id
from repositories.assignment_repository import get_assignment_by_booking_id
from repositories.payment_repository import (
    get_payment_by_id,
    get_payment_by_id_for_update,
    get_payment_by_booking_id,
    get_payment_by_booking_id_for_update,
    get_all_payments,
    get_payments_by_status,
    get_admin_collection_payments,
    get_cleaner_earning_by_cleaner_id,
    get_cleaner_earning_by_cleaner_id_for_update,
    get_payments_by_customer,
    get_payment_stats,
    create_payment,
    update_payment,
    delete_payment,
    get_payment_total_amount,
)
from repositories.user_repository import get_user_by_id
from repositories.booking_repository import get_booking_by_id, get_customer_booking_by_id


COLLECTION_STATUSES = ["pending_collection", "collected", "split_done"]
HANDOVER_STATUSES = ["pending", "settled"]


def format_payment(payment):
    return {
        "id": str(payment.id),
        "booking_id": str(payment.booking_id),
        "customer_id": str(payment.customer_id),
        "payment_method": payment.payment_method,
        "transaction_reference": payment.transaction_reference,
        "amount": float(payment.amount) if payment.amount else 0,
        "payment_status": payment.payment_status,
        "collected_by_cleaner": payment.collected_by_cleaner,
        "paid_at": payment.paid_at.isoformat() if payment.paid_at else None,
        "created_at": payment.created_at.isoformat(),
        "updated_at": payment.updated_at.isoformat()
    }


def format_collection_payment(payment):
    return {
        "id": str(payment.id),
        "booking_id": str(payment.booking_id),
        "customer_id": str(payment.customer_id),
        "collected_amount": float(payment.collected_amount) if payment.collected_amount is not None else None,
        "payment_type": payment.payment_type,
        "collected_by": str(payment.collected_by) if payment.collected_by else None,
        "collected_at": payment.collected_at.isoformat() if payment.collected_at else None,
        "cleaner_share": float(payment.cleaner_share) if payment.cleaner_share is not None else None,
        "admin_share": float(payment.admin_share) if payment.admin_share is not None else None,
        "split_updated_by": str(payment.split_updated_by) if payment.split_updated_by else None,
        "split_updated_at": payment.split_updated_at.isoformat() if payment.split_updated_at else None,
        "payout_released": bool(getattr(payment, "payout_released", False)),
        "cleaner_handover_status": getattr(payment, "cleaner_handover_status", "pending"),
        "status": payment.status or "pending_collection",
        "created_at": payment.created_at.isoformat(),
        "updated_at": payment.updated_at.isoformat(),
    }


def ensure_pending_collection_payment(db, booking):
    payment = get_payment_by_booking_id(db, booking.id)
    if payment:
        return payment

    payment = Payment(
        booking_id=booking.id,
        customer_id=booking.customer_id,
        status="pending_collection",
        payment_status="pending",
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


def record_collection(db, cleaner_user_id, booking_id, payload):
    cleaner = get_cleaner_profile_by_user_id(db, cleaner_user_id)
    if not cleaner:
        raise Exception("Cleaner profile not found")

    booking = get_booking_by_id(db, booking_id)
    if not booking:
        raise Exception("Booking not found")
    if booking.booking_status != "completed":
        raise Exception("Booking must be completed before payment collection")

    assignment = get_assignment_by_booking_id(db, booking_id)
    if not assignment or assignment.cleaner_id != cleaner.id:
        raise Exception("Cleaner can only collect payment for their assigned booking")

    payment = get_payment_by_booking_id_for_update(db, booking_id)
    if not payment:
        payment = Payment(
            booking_id=booking.id,
            customer_id=booking.customer_id,
            status="pending_collection",
            payment_status="pending",
        )
        db.add(payment)
        db.flush()

    if payment.status == "split_done":
        raise Exception("Cannot collect payment after admin split")
    if payment.status == "collected":
        raise Exception("Payment has already been collected")

    payment.collected_amount = payload.amount
    payment.payment_type = payload.payment_type
    payment.collected_by = cleaner.id
    payment.collected_at = datetime.utcnow()
    payment.status = "collected"

    # Keep legacy fields populated for older dashboard endpoints.
    payment.amount = payload.amount
    payment.payment_method = payload.payment_type.upper() if payload.payment_type == "upi" else "Cash"
    payment.payment_status = "pending"
    payment.collected_by_cleaner = True

    db.commit()
    db.refresh(payment)
    return format_collection_payment(payment)


def apply_admin_split(db, admin_user_id, payment_id, payload):
    payment = get_payment_by_id_for_update(db, payment_id)
    if not payment:
        raise Exception("Payment not found")
    if payment.status == "split_done":
        raise Exception("Payment split has already been applied")
    if payment.status != "collected":
        raise Exception("Payment must be collected before admin split")
    if not payment.collected_by:
        raise Exception("Collected cleaner is missing for this payment")

    cleaner_share = Decimal(payload.cleaner_share)
    admin_share = Decimal(payload.admin_share)
    collected_amount = Decimal(payment.collected_amount)
    if cleaner_share + admin_share != collected_amount:
        raise Exception("Cleaner share plus admin share must equal collected amount")

    earning = get_cleaner_earning_by_cleaner_id_for_update(db, payment.collected_by)
    if not earning:
        earning = CleanerEarning(
            cleaner_id=payment.collected_by,
            total_earned=Decimal("0"),
            pending_payout=Decimal("0"),
        )
        db.add(earning)
        db.flush()

    earning.total_earned = Decimal(earning.total_earned or 0) + cleaner_share
    earning.pending_payout = Decimal(earning.pending_payout or 0) + cleaner_share
    earning.last_updated = datetime.utcnow()

    payment.cleaner_share = cleaner_share
    payment.admin_share = admin_share
    payment.split_updated_by = admin_user_id
    payment.split_updated_at = datetime.utcnow()
    payment.cleaner_handover_status = "pending"
    payment.status = "split_done"
    payment.payment_status = "paid"
    payment.paid_at = payment.paid_at or datetime.utcnow()

    db.commit()
    db.refresh(payment)
    return format_collection_payment(payment)


def mark_admin_share_collected(db, payment_id):
    payment = get_payment_by_id_for_update(db, payment_id)
    if not payment:
        raise Exception("Payment not found")
    if payment.status != "split_done":
        raise Exception("Admin share can be collected only after payment split")
    if payment.cleaner_handover_status == "settled":
        raise Exception("Admin share has already been collected")

    payment.cleaner_handover_status = "settled"
    db.commit()
    db.refresh(payment)
    return format_collection_payment(payment)


def get_admin_payments(db, status=None, cleaner_handover_status=None, limit=50, offset=0):
    if status and status not in COLLECTION_STATUSES:
        raise Exception(f"Invalid status. Must be one of: {', '.join(COLLECTION_STATUSES)}")
    if cleaner_handover_status and cleaner_handover_status not in HANDOVER_STATUSES:
        raise Exception(f"Invalid handover status. Must be one of: {', '.join(HANDOVER_STATUSES)}")
    payments = get_admin_collection_payments(db, status, cleaner_handover_status, limit, offset)
    return [format_collection_payment(payment) for payment in payments]


def get_cleaner_earnings(db, cleaner_user_id):
    cleaner = get_cleaner_profile_by_user_id(db, cleaner_user_id)
    if not cleaner:
        raise Exception("Cleaner profile not found")

    totals = (
        db.query(
            func.coalesce(func.sum(Payment.cleaner_share), 0),
            func.coalesce(func.sum(Payment.admin_share), 0),
            func.coalesce(
                func.sum(
                    case(
                        (Payment.cleaner_handover_status == "pending", Payment.admin_share),
                        else_=0,
                    )
                ),
                0,
            ),
            func.coalesce(
                func.sum(
                    case(
                        (Payment.cleaner_handover_status == "settled", Payment.admin_share),
                        else_=0,
                    )
                ),
                0,
            ),
            func.max(Payment.split_updated_at),
        )
        .filter(
            Payment.collected_by == cleaner.id,
            Payment.status == "split_done",
            Payment.cleaner_share.isnot(None),
        )
        .one()
    )
    total_earned = Decimal(totals[0] or 0)
    admin_total = Decimal(totals[1] or 0)
    admin_due = Decimal(totals[2] or 0)
    settled = Decimal(totals[3] or 0)
    last_updated = totals[4]

    earning = get_cleaner_earning_by_cleaner_id(db, cleaner.id)
    if earning:
        earning.total_earned = total_earned
        earning.pending_payout = admin_due
        if last_updated:
            earning.last_updated = last_updated
        db.commit()
    elif total_earned or admin_due:
        earning = CleanerEarning(
            cleaner_id=cleaner.id,
            total_earned=total_earned,
            pending_payout=admin_due,
            last_updated=last_updated or datetime.utcnow(),
        )
        db.add(earning)
        db.commit()

    return {
        "cleaner_id": str(cleaner.id),
        "total_earned": float(total_earned),
        "admin_due": float(admin_due),
        "settled": float(settled),
        "admin_total": float(admin_total),
        "pending_payout": float(admin_due),
        "last_updated": last_updated.isoformat() if last_updated else None,
    }


def get_customer_payment_status(db, customer_user_id, booking_id):
    booking = get_customer_booking_by_id(db, customer_user_id, booking_id)
    if not booking:
        raise Exception("Booking not found")

    payment = get_payment_by_booking_id(db, booking_id)
    status = payment.status if payment and payment.status else "pending_collection"
    payment_type = payment.payment_type if payment else None
    method_label = payment_type.upper() if payment_type == "upi" else "Cash" if payment_type == "cash" else None
    message = f"Payment collected via {method_label}" if method_label else "Payment not collected yet"
    return {
        "booking_id": str(booking.id),
        "status": status,
        "payment_type": payment_type,
        "message": message,
    }


class PaymentService:
    record_collection = staticmethod(record_collection)
    apply_admin_split = staticmethod(apply_admin_split)
    get_admin_payments = staticmethod(get_admin_payments)
    get_cleaner_earnings = staticmethod(get_cleaner_earnings)


def get_payment_details_service(db, payment_id):
    payment = get_payment_by_id(db, payment_id)
    if not payment:
        raise Exception("Payment not found")
    return format_payment(payment)


def get_payment_by_booking_service(db, booking_id):
    payment = get_payment_by_booking_id(db, booking_id)
    if not payment:
        raise Exception("Payment not found for this booking")
    return format_payment(payment)


def list_all_payments_service(db, limit=50, offset=0):
    payments = get_all_payments(db, limit, offset)
    stats = get_payment_stats(db)
    return {
        "payments": [format_payment(p) for p in payments],
        "total": stats["total"],
        "pending_count": stats["pending"],
        "paid_count": stats["paid"],
        "failed_count": stats["failed"]
    }


def list_payments_by_status_service(db, status, limit=50, offset=0):
    valid_statuses = ["pending", "paid", "failed"]
    if status not in valid_statuses:
        raise Exception(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
    
    payments = get_payments_by_status(db, status, limit, offset)
    stats = get_payment_stats(db)
    return {
        "payments": [format_payment(p) for p in payments],
        "total": stats["total"],
        "pending_count": stats["pending"],
        "paid_count": stats["paid"],
        "failed_count": stats["failed"],
        "filtered_count": len(payments)
    }


def list_payments_by_customer_service(db, customer_id, limit=50, offset=0):
    customer = get_user_by_id(db, customer_id)
    if not customer:
        raise Exception("Customer not found")
    
    payments = get_payments_by_customer(db, customer_id, limit, offset)
    return [format_payment(p) for p in payments]


def update_payment_manually_service(db, payment_id, payload):
    """Admin manual payment update"""
    payment = get_payment_by_id(db, payment_id)
    if not payment:
        raise Exception("Payment not found")
    
    update_data = {}
    
    if payload.payment_method:
        valid_methods = ["Cash", "UPI"]
        if payload.payment_method not in valid_methods:
            raise Exception(f"Invalid payment method. Must be one of: {', '.join(valid_methods)}")
        update_data["payment_method"] = payload.payment_method
    
    if payload.payment_status:
        valid_statuses = ["pending", "paid", "failed"]
        if payload.payment_status not in valid_statuses:
            raise Exception(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        update_data["payment_status"] = payload.payment_status
        
        # Auto-set paid_at when marking as paid
        if payload.payment_status == "paid" and not payment.paid_at:
            update_data["paid_at"] = datetime.utcnow()
    
    if payload.transaction_reference is not None:
        update_data["transaction_reference"] = payload.transaction_reference
    
    if payload.amount is not None:
        if payload.amount <= 0:
            raise Exception("Amount must be greater than 0")
        update_data["amount"] = payload.amount
    
    if payload.collected_by_cleaner is not None:
        update_data["collected_by_cleaner"] = payload.collected_by_cleaner
    
    if payload.paid_at is not None:
        update_data["paid_at"] = payload.paid_at
    
    updated_payment = update_payment(db, payment_id, update_data)
    return format_payment(updated_payment)


def mark_payment_paid_service(db, payment_id, transaction_reference=None):
    """Quick action to mark payment as paid"""
    payment = get_payment_by_id(db, payment_id)
    if not payment:
        raise Exception("Payment not found")
    
    update_data = {
        "payment_status": "paid",
        "paid_at": datetime.utcnow()
    }
    
    if transaction_reference:
        update_data["transaction_reference"] = transaction_reference
    
    updated_payment = update_payment(db, payment_id, update_data)
    return format_payment(updated_payment)


def mark_payment_failed_service(db, payment_id):
    """Mark payment as failed"""
    payment = get_payment_by_id(db, payment_id)
    if not payment:
        raise Exception("Payment not found")
    
    update_data = {"payment_status": "failed"}
    updated_payment = update_payment(db, payment_id, update_data)
    return format_payment(updated_payment)


def get_payment_stats_service(db):
    """Get payment statistics"""
    stats = get_payment_stats(db)
    
    total_paid = get_payment_total_amount(db, "paid")
    total_pending = get_payment_total_amount(db, "pending")
    
    return {
        "total_payments": stats["total"],
        "pending_count": stats["pending"],
        "paid_count": stats["paid"],
        "failed_count": stats["failed"],
        "total_amount_paid": float(total_paid),
        "total_amount_pending": float(total_pending)
    }


def delete_payment_service(db, payment_id):
    """Delete payment (use with caution - usually for data cleanup only)"""
    payment = get_payment_by_id(db, payment_id)
    if not payment:
        raise Exception("Payment not found")
    
    # Safety check: only allow deletion if payment is still pending
    if payment.payment_status != "pending":
        raise Exception("Only pending payments can be deleted")
    
    result = delete_payment(db, payment_id)
    return result
