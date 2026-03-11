"""Payment Service"""
import logging
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.payment import Payment, PaymentStatus, PaymentType
from app.api.bank import BankAPIClient, BankAPIError
from app.services.bank_sync import BankSyncService

logger = logging.getLogger(__name__)


class PaymentService:
    """Service for managing payments"""

    def __init__(self, bank_client: BankAPIClient):
        self.bank_client = bank_client
        self.sync_service = BankSyncService(bank_client)

    async def create_acquiring_payment(
        self,
        order: Order,
        amount: float,
        db: Session,
    ) -> Payment:
        """
        Create acquiring payment with bank
        
        Args:
            order: Order object
            amount: Payment amount
            db: Database session
        
        Returns:
            Created payment
        
        Raises:
            ValueError: If validation fails
            BankAPIError: If bank API error
        """
        # Validate amount
        remaining = order.get_remaining_amount()
        if amount > remaining:
            raise ValueError(f"Payment amount {amount} exceeds remaining amount {remaining}")

        # Call bank API
        try:
            bank_payment_id = await self.bank_client.acquiring_start(order.id, amount)
        except BankAPIError as e:
            logger.error(f"Failed to create acquiring payment: {str(e)}")
            raise

        # Create payment in database
        payment = Payment(
            order_id=order.id,
            amount=amount,
            payment_type=PaymentType.ACQUIRING,
            status=PaymentStatus.PENDING,
            bank_payment_id=bank_payment_id,
        )

        db.add(payment)
        db.commit()
        db.refresh(payment)

        logger.info(f"Created acquiring payment {payment.id} with bank_id {bank_payment_id}")
        return payment

    async def sync_acquiring_payment(self, payment: Payment, db: Session) -> None:
        """
        Synchronize acquiring payment with bank
        
        Args:
            payment: Payment object
            db: Database session
        """
        await self.sync_service.sync_acquiring_payment(payment, db)

    def create_cash_payment(
        self,
        order: Order,
        amount: float,
        db: Session,
    ) -> Payment:
        """
        Create cash payment
        
        Args:
            order: Order object
            amount: Payment amount
            db: Database session
        
        Returns:
            Created payment
        
        Raises:
            ValueError: If validation fails
        """
        # Validate amount
        remaining = order.get_remaining_amount()
        if amount > remaining:
            raise ValueError(f"Payment amount {amount} exceeds remaining amount {remaining}")

        # Create payment in database
        payment = Payment(
            order_id=order.id,
            amount=amount,
            payment_type=PaymentType.CASH,
            status=PaymentStatus.PENDING,
        )

        db.add(payment)
        db.commit()
        db.refresh(payment)

        logger.info(f"Created cash payment {payment.id}")
        return payment
