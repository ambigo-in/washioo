from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from core.database import get_db
from core.role_dependencies import admin_only
from core.role_dependencies import require_roles
from services.payment_service import (
    apply_admin_split,
    get_admin_payments,
    get_cleaner_earnings,
    get_customer_payment_status,
    mark_admin_share_collected,
    get_payment_details_service,
    get_payment_by_booking_service,
    list_all_payments_service,
    list_payments_by_status_service,
    list_payments_by_customer_service,
    record_collection,
    update_payment_manually_service,
    mark_payment_paid_service,
    mark_payment_failed_service,
    get_payment_stats_service,
    delete_payment_service,
)
from schemas.payment_schema import (
    AdminPaymentSplitRequest,
    CleanerPaymentUpdateRequest,
    PaymentUpdateRequest,
)

PAYMENT_TAG = "Payment APIs"

router = APIRouter(prefix="/payments")
workflow_router = APIRouter()


@workflow_router.patch("/bookings/{booking_id}/payment/collect", tags=[PAYMENT_TAG])
def collect_booking_payment(
    booking_id: str,
    payload: CleanerPaymentUpdateRequest,
    db: Session = Depends(get_db),
    current_cleaner=Depends(require_roles(["cleaner"])),
):
    """Cleaner records cash/UPI collection after completing their assigned booking."""
    try:
        payment = record_collection(db, current_cleaner.id, booking_id, payload)
        return {
            "message": "Payment collection recorded successfully",
            "payment": payment,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@workflow_router.patch("/admin/payments/{payment_id}/split", tags=[PAYMENT_TAG])
def split_collected_payment(
    payment_id: str,
    payload: AdminPaymentSplitRequest,
    db: Session = Depends(get_db),
    current_admin=Depends(require_roles(["admin"])),
):
    """Admin splits a collected payment and updates cleaner earnings."""
    try:
        payment = apply_admin_split(db, current_admin.id, payment_id, payload)
        return {
            "message": "Payment split applied successfully",
            "payment": payment,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@workflow_router.patch("/admin/payments/{payment_id}/handover/collect", tags=[PAYMENT_TAG])
def collect_admin_share_from_cleaner(
    payment_id: str,
    db: Session = Depends(get_db),
    current_admin=Depends(require_roles(["admin"])),
):
    """Admin marks the cleaner's handover of admin share as collected."""
    try:
        payment = mark_admin_share_collected(db, payment_id)
        return {
            "message": "Admin share marked as collected successfully",
            "payment": payment,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@workflow_router.get("/admin/payments", tags=[PAYMENT_TAG])
def list_admin_collection_payments(
    status: str = Query(None),
    cleaner_handover_status: str = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_admin=Depends(require_roles(["admin"])),
):
    """Admin lists payment collection/split records."""
    try:
        payments = get_admin_payments(db, status, cleaner_handover_status, limit, offset)
        return {
            "message": "Payments fetched successfully",
            "payments": payments,
            "total": len(payments),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@workflow_router.get("/cleaner/earnings", tags=[PAYMENT_TAG])
def get_current_cleaner_earnings(
    db: Session = Depends(get_db),
    current_cleaner=Depends(require_roles(["cleaner"])),
):
    """Cleaner views updated earnings after admin splits."""
    try:
        earnings = get_cleaner_earnings(db, current_cleaner.id)
        return {
            "message": "Cleaner earnings fetched successfully",
            "earnings": earnings,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@workflow_router.get("/customer/bookings/{booking_id}/payment-status", tags=[PAYMENT_TAG])
def get_customer_booking_payment_status(
    booking_id: str,
    db: Session = Depends(get_db),
    current_customer=Depends(require_roles(["customer"])),
):
    """Customer sees collection status and payment type without amount details."""
    try:
        payment_status = get_customer_payment_status(db, current_customer.id, booking_id)
        return {
            "message": "Payment status fetched successfully",
            "payment": payment_status,
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/stats", tags=[PAYMENT_TAG])
def get_payment_statistics(
    db: Session = Depends(get_db),
    current_admin=Depends(admin_only)
):
    """Get payment statistics and aggregates"""
    try:
        stats = get_payment_stats_service(db)
        return {
            "message": "Payment statistics fetched successfully",
            "statistics": stats
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", tags=[PAYMENT_TAG])
def list_payments(
    db: Session = Depends(get_db),
    status: str = Query(None),
    limit: int = Query(50),
    offset: int = Query(0),
    current_admin=Depends(admin_only)
):
    """List all payments with optional status filter"""
    try:
        if status:
            result = list_payments_by_status_service(db, status, limit, offset)
        else:
            result = list_all_payments_service(db, limit, offset)
        
        return {
            "message": "Payments fetched successfully",
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/customer/{customer_id}", tags=[PAYMENT_TAG])
def get_customer_payments(
    customer_id: str,
    db: Session = Depends(get_db),
    limit: int = Query(50),
    offset: int = Query(0),
    current_admin=Depends(admin_only)
):
    """Get payments for a specific customer"""
    try:
        payments = list_payments_by_customer_service(db, customer_id, limit, offset)
        return {
            "message": "Customer payments fetched successfully",
            "customer_id": customer_id,
            "payments": payments,
            "total": len(payments)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/booking/{booking_id}", tags=[PAYMENT_TAG])
def get_booking_payment(
    booking_id: str,
    db: Session = Depends(get_db),
    current_admin=Depends(admin_only)
):
    """Get payment for a specific booking"""
    try:
        payment = get_payment_by_booking_service(db, booking_id)
        return {
            "message": "Booking payment fetched successfully",
            "payment": payment
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{payment_id}", tags=[PAYMENT_TAG])
def get_payment_details(
    payment_id: str,
    db: Session = Depends(get_db),
    current_admin=Depends(admin_only)
):
    """Get details for a specific payment"""
    try:
        payment = get_payment_details_service(db, payment_id)
        return {
            "message": "Payment details fetched successfully",
            "payment": payment
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{payment_id}", tags=[PAYMENT_TAG])
def update_payment_manual(
    payment_id: str,
    payload: PaymentUpdateRequest,
    db: Session = Depends(get_db),
    current_admin=Depends(admin_only)
):
    """Admin: Manually update payment details"""
    try:
        updated_payment = update_payment_manually_service(db, payment_id, payload)
        return {
            "message": "Payment updated successfully",
            "payment": updated_payment
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{payment_id}/mark-paid", tags=[PAYMENT_TAG])
def mark_payment_as_paid(
    payment_id: str,
    transaction_reference: str = Query(None),
    db: Session = Depends(get_db),
    current_admin=Depends(admin_only)
):
    """Admin: Quick action to mark payment as paid"""
    try:
        updated_payment = mark_payment_paid_service(db, payment_id, transaction_reference)
        return {
            "message": "Payment marked as paid successfully",
            "payment": updated_payment
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{payment_id}/mark-failed", tags=[PAYMENT_TAG])
def mark_payment_as_failed(
    payment_id: str,
    db: Session = Depends(get_db),
    current_admin=Depends(admin_only)
):
    """Admin: Mark payment as failed"""
    try:
        updated_payment = mark_payment_failed_service(db, payment_id)
        return {
            "message": "Payment marked as failed successfully",
            "payment": updated_payment
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{payment_id}", tags=[PAYMENT_TAG])
def delete_payment(
    payment_id: str,
    db: Session = Depends(get_db),
    current_admin=Depends(admin_only)
):
    """Admin: Delete payment (only pending payments)"""
    try:
        result = delete_payment_service(db, payment_id)
        if result:
            return {"message": "Payment deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Payment not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
