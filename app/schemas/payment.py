"""Pydantic schema for Payment"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class PaymentCreate(BaseModel):
    """Schema for creating payment"""

    order_id: int
    amount: float = Field(gt=0, description="Payment amount must be positive")
    payment_type: str = Field(..., description="CASH or ACQUIRING")


class PaymentRefund(BaseModel):
    """Schema for refunding payment"""

    reason: Optional[str] = None


class PaymentResponse(BaseModel):
    """Schema for payment response"""

    id: int
    order_id: int
    amount: float
    payment_type: str
    status: str
    bank_payment_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BankPaymentStartRequest(BaseModel):
    """Schema for bank payment start request"""

    order_id: int
    amount: float


class BankPaymentStartResponse(BaseModel):
    """Schema for bank payment start response"""

    bank_payment_id: str


class BankPaymentCheckResponse(BaseModel):
    """Schema for bank payment check response"""

    bank_payment_id: str
    amount: float
    status: str  # pending, completed, failed
    payment_date: Optional[datetime] = None
