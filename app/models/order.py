"""Order Model"""
from enum import Enum
from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class PaymentStatus(str, Enum):
    """Order payment status"""
    UNPAID = "unpaid"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"


class Order(Base):
    """Order model for storing order information"""

    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True, nullable=False, index=True)
    total_amount = Column(Float, nullable=False)
    payment_status = Column(String, default=PaymentStatus.UNPAID, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    payments = relationship("Payment", back_populates="order", cascade="all, delete-orphan")

    def get_paid_amount(self) -> float:
        """Calculate total paid amount from all payments"""
        return sum(payment.amount for payment in self.payments if payment.status == "completed")

    def get_remaining_amount(self) -> float:
        """Calculate remaining amount to pay"""
        return self.total_amount - self.get_paid_amount()

    def update_payment_status(self) -> None:
        """Update payment status based on paid amount"""
        paid = self.get_paid_amount()

        if paid >= self.total_amount:
            self.payment_status = PaymentStatus.PAID
        elif paid > 0:
            self.payment_status = PaymentStatus.PARTIALLY_PAID
        else:
            self.payment_status = PaymentStatus.UNPAID

        self.updated_at = datetime.utcnow()

    def __repr__(self) -> str:
        return (
            f"<Order(id={self.id}, order_number={self.order_number}, "
            f"total_amount={self.total_amount}, status={self.payment_status})>"
        )
