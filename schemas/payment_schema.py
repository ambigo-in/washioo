from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from decimal import Decimal


class PaymentUpdateRequest(BaseModel):
    payment_method: Optional[Literal["UPI", "Cash"]] = None
    payment_status: Optional[Literal["pending", "paid", "failed"]] = None
    transaction_reference: Optional[str] = None
    amount: Optional[float] = None
    collected_by_cleaner: Optional[bool] = None
    paid_at: Optional[datetime] = None


class PaymentResponse(BaseModel):
    id: str
    booking_id: str
    customer_id: str
    payment_method: str
    transaction_reference: Optional[str]
    amount: float
    payment_status: str
    collected_by_cleaner: bool
    paid_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class PaymentListResponse(BaseModel):
    payments: list[PaymentResponse]
    total: int
    pending_count: int
    paid_count: int
    failed_count: int


class CleanerPaymentUpdateRequest(BaseModel):
    amount: Decimal = Field(..., gt=0)
    payment_type: Literal["upi", "cash"]


class AdminPaymentSplitRequest(BaseModel):
    cleaner_share: Decimal = Field(..., ge=0)
    admin_share: Decimal = Field(..., ge=0)


class PaymentCollectionResponse(BaseModel):
    id: str
    booking_id: str
    customer_id: str
    collected_amount: Optional[Decimal] = None
    payment_type: Optional[Literal["cash", "upi"]] = None
    collected_by: Optional[str] = None
    collected_at: Optional[datetime] = None
    cleaner_share: Optional[Decimal] = None
    admin_share: Optional[Decimal] = None
    split_updated_by: Optional[str] = None
    split_updated_at: Optional[datetime] = None
    payout_released: bool = False
    cleaner_handover_status: Literal["pending", "settled"] = "pending"
    status: Literal["pending_collection", "collected", "split_done"]
    created_at: datetime
    updated_at: datetime


class CleanerEarningsSummary(BaseModel):
    cleaner_id: str
    total_earned: Decimal
    admin_due: Decimal
    settled: Decimal
    admin_total: Decimal
    pending_payout: Optional[Decimal] = None
    last_updated: Optional[datetime] = None


class CustomerPaymentStatusResponse(BaseModel):
    booking_id: str
    status: Literal["pending_collection", "collected", "split_done"]
    payment_type: Optional[Literal["cash", "upi"]] = None
    message: str
