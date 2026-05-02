from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime


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
