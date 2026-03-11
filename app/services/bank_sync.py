"""Bank Synchronization Service"""
import logging
from sqlalchemy.orm import Session

from app.api.bank import BankAPIClient, BankAPIError, BankPaymentNotFound
from app.models.payment import Payment, PaymentStatus

logger = logging.getLogger(__name__)


class BankSyncService:
    """Service for synchronizing payment status with bank"""

    def __init__(self, bank_client: BankAPIClient):
        self.bank_client = bank_client

    async def sync_acquiring_payment(self, payment: Payment, db: Session) -> bool:
        """
        Synchronize acquiring payment status with bank
        
        Args:
            payment: Payment object
            db: Database session
        
        Returns:
            True if synced successfully
        """
        if payment.payment_type != "acquiring" or not payment.bank_payment_id:
            logger.warning(f"Payment {payment.id} is not an acquiring payment")
            return False

        try:
            # Check status with bank
            bank_info = await self.bank_client.acquiring_check(payment.bank_payment_id)
            
            # Compare statuses
            bank_status = bank_info.get("status")
            local_status = payment.status
            
            if self._map_bank_status_to_local(bank_status) != local_status:
                logger.warning(
                    f"Status mismatch for payment {payment.id}: "
                    f"local={local_status}, bank={bank_status}"
                )
                
                # Update local status to match bank
                self._update_payment_status(payment, bank_status)
                db.commit()
                
                logger.info(f"Updated payment {payment.id} status to {payment.status}")
            
            return True
        
        except BankPaymentNotFound:
            logger.error(f"Payment {payment.id} not found in bank")
            # Don't update status - payment might be processing
            return False
        except BankAPIError as e:
            logger.error(f"Error syncing payment {payment.id} with bank: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error syncing payment {payment.id}: {str(e)}")
            return False

    @staticmethod
    def _map_bank_status_to_local(bank_status: str) -> str:
        """Map bank status to local status"""
        status_map = {
            "pending": PaymentStatus.PENDING,
            "completed": PaymentStatus.COMPLETED,
            "failed": PaymentStatus.FAILED,
        }
        return status_map.get(bank_status, PaymentStatus.PENDING)

    @staticmethod
    def _update_payment_status(payment: Payment, bank_status: str) -> None:
        """Update payment status based on bank status"""
        local_status = BankSyncService._map_bank_status_to_local(bank_status)
        payment.status = local_status
        
        # Update order status if payment completed
        if local_status == PaymentStatus.COMPLETED:
            payment.deposit()
        elif local_status == PaymentStatus.FAILED:
            payment.status = PaymentStatus.FAILED
