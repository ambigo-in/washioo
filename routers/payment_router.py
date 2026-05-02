from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from core.database import get_db
from core.role_dependencies import admin_only
from services.payment_service import (
    get_payment_details_service,
    get_payment_by_booking_service,
    list_all_payments_service,
    list_payments_by_status_service,
    list_payments_by_customer_service,
    update_payment_manually_service,
    mark_payment_paid_service,
    mark_payment_failed_service,
    get_payment_stats_service,
    delete_payment_service,
)
from schemas.payment_schema import PaymentUpdateRequest

PAYMENT_TAG = "Payment APIs"

router = APIRouter(prefix="/payments")


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
