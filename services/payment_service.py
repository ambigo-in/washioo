from datetime import datetime
from repositories.payment_repository import (
    get_payment_by_id,
    get_payment_by_booking_id,
    get_all_payments,
    get_payments_by_status,
    get_payments_by_customer,
    get_payment_stats,
    create_payment,
    update_payment,
    delete_payment,
    get_payment_total_amount,
)
from repositories.user_repository import get_user_by_id
from repositories.booking_repository import get_booking_by_id


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
