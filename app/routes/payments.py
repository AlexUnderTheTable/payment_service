"""Payment Routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.order import Order
from app.models.payment import Payment, PaymentStatus, PaymentType
from app.schemas.payment import PaymentCreate, PaymentResponse, PaymentRefund

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.get("", response_model=list[PaymentResponse])
async def list_payments(db: Session = Depends(get_db)):
    """Get all payments"""
    payments = db.query(Payment).all()
    return payments


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(payment_id: int, db: Session = Depends(get_db)):
    """Get payment by ID"""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment with id {payment_id} not found",
        )
    
    return payment


@router.post("/orders/{order_id}/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(order_id: int, payment: PaymentCreate, db: Session = Depends(get_db)):
    """Create new payment for order"""
    # Verify order exists
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {order_id} not found",
        )
    
    # Validate payment type
    valid_types = [PaymentType.CASH.value, PaymentType.ACQUIRING.value]
    if payment.payment_type.lower() not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid payment type. Must be {PaymentType.CASH.value} or {PaymentType.ACQUIRING.value}",
        )
    
    # Validate payment amount doesn't exceed remaining amount
    remaining = order.get_remaining_amount()
    if payment.amount > remaining:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment amount {payment.amount} exceeds remaining amount {remaining}",
        )
    
    # Create payment
    db_payment = Payment(
        order_id=order_id,
        amount=payment.amount,
        payment_type=payment.payment_type,
        status=PaymentStatus.PENDING,
    )
    
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    
    return db_payment


@router.post("/{payment_id}/deposit", response_model=PaymentResponse)
async def deposit_payment(payment_id: int, db: Session = Depends(get_db)):
    """Complete payment (deposit operation)"""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment with id {payment_id} not found",
        )
    
    if payment.status != PaymentStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Can only deposit pending payments. Current status: {payment.status}",
        )
    
    # Perform deposit
    success = payment.deposit()
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to deposit payment",
        )
    
    # Update order status
    payment.order.update_payment_status()
    
    db.commit()
    db.refresh(payment)
    
    return payment


@router.post("/{payment_id}/refund", response_model=PaymentResponse)
async def refund_payment(payment_id: int, refund_data: PaymentRefund, db: Session = Depends(get_db)):
    """Refund payment (return operation)"""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment with id {payment_id} not found",
        )
    
    if payment.status != PaymentStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Can only refund completed payments. Current status: {payment.status}",
        )
    
    # Perform refund
    success = payment.refund()
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to refund payment",
        )
    
    # Update order status
    payment.order.update_payment_status()
    
    db.commit()
    db.refresh(payment)
    
    return payment


@router.get("/orders/{order_id}/payments", response_model=list[PaymentResponse])
async def list_order_payments(order_id: int, db: Session = Depends(get_db)):
    """Get all payments for an order"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {order_id} not found",
        )
    
    return order.payments
