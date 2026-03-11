"""Order Routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.database import get_db
from app.models.order import Order
from app.schemas.order import OrderCreate, OrderResponse, OrderDetailResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("", response_model=list[OrderResponse])
async def list_orders(db: Session = Depends(get_db)):
    """Get all orders"""
    orders = db.query(Order).all()
    
    # Add computed fields
    result = []
    for order in orders:
        order_dict = {
            "id": order.id,
            "order_number": order.order_number,
            "total_amount": order.total_amount,
            "payment_status": order.payment_status,
            "paid_amount": order.get_paid_amount(),
            "remaining_amount": order.get_remaining_amount(),
            "created_at": order.created_at,
            "updated_at": order.updated_at,
        }
        result.append(order_dict)
    
    return result


@router.get("/{order_id}", response_model=OrderDetailResponse)
async def get_order(order_id: int, db: Session = Depends(get_db)):
    """Get order by ID with all payments"""
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {order_id} not found",
        )
    
    return {
        "id": order.id,
        "order_number": order.order_number,
        "total_amount": order.total_amount,
        "payment_status": order.payment_status,
        "paid_amount": order.get_paid_amount(),
        "remaining_amount": order.get_remaining_amount(),
        "created_at": order.created_at,
        "updated_at": order.updated_at,
        "payments": order.payments,
    }


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    """Create new order"""
    try:
        logger.info(f"Creating order: {order.order_number}")
        
        # Check if order with same number already exists
        existing = db.query(Order).filter(Order.order_number == order.order_number).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Order with number {order.order_number} already exists",
            )
        
        db_order = Order(
            order_number=order.order_number,
            total_amount=order.total_amount,
        )
        
        logger.info(f"Adding order to database")
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        logger.info(f"Order created with id: {db_order.id}")
        
        return {
            "id": db_order.id,
            "order_number": db_order.order_number,
            "total_amount": db_order.total_amount,
            "payment_status": db_order.payment_status,
            "paid_amount": db_order.get_paid_amount(),
            "remaining_amount": db_order.get_remaining_amount(),
            "created_at": db_order.created_at,
            "updated_at": db_order.updated_at,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating order: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating order: {str(e)}"
        )
