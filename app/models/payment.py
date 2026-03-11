"""Payment Model"""
from enum import Enum
from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class PaymentType(str, Enum):
    """Payment type"""
    CASH = "cash"
    ACQUIRING = "acquiring"


class PaymentStatus(str, Enum):
    """Payment status"""
    PENDING = "pending"
    COMPLETED = "completed"
    REFUNDED = "refunded"
    FAILED = "failed"


class Payment(Base):
    """Payment model for storing payment information"""

    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    payment_type = Column(String, nullable=False)  # CASH or ACQUIRING
    status = Column(String, default=PaymentStatus.PENDING, nullable=False)
    bank_payment_id = Column(String, nullable=True, index=True)  # ID from bank for acquiring payments
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    order = relationship("Order", back_populates="payments")

    def deposit(self) -> bool:
        """Complete the payment (deposit operation)"""
        if self.status != PaymentStatus.PENDING:
            return False

        self.status = PaymentStatus.COMPLETED
        self.updated_at = datetime.utcnow()

        # Update order status
        self.order.update_payment_status()
        return True

    def refund(self) -> bool:
        """Refund the payment (return operation)"""
        if self.status != PaymentStatus.COMPLETED:
            return False

        self.status = PaymentStatus.REFUNDED
        self.updated_at = datetime.utcnow()

        # Update order status
        self.order.update_payment_status()
        return True

    def __repr__(self) -> str:
        return (
            f"<Payment(id={self.id}, order_id={self.order_id}, "
            f"amount={self.amount}, type={self.payment_type}, status={self.status})>"
        )
