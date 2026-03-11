"""Pydantic schema for Order"""
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, List


class OrderCreate(BaseModel):
    """Schema for creating order"""

    order_number: str
    total_amount: float = Field(gt=0, description="Total amount must be positive")


class OrderUpdate(BaseModel):
    """Schema for updating order"""

    payment_status: Optional[str] = None


class PaymentResponse(BaseModel):
    """Schema for payment response"""

    id: int
    amount: float
    payment_type: str
    status: str
    bank_payment_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    """Schema for order response"""

    id: int
    order_number: str
    total_amount: float
    payment_status: str
    paid_amount: float
    remaining_amount: float
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderDetailResponse(OrderResponse):
    """Schema for detailed order response with payments"""

    payments: List[PaymentResponse] = []
