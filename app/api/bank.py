"""Bank API Client"""
import httpx
import logging
from typing import Optional
from datetime import datetime
import asyncio

from config import get_settings

logger = logging.getLogger(__name__)


class BankAPIError(Exception):
    """Bank API error"""
    pass


class BankPaymentNotFound(BankAPIError):
    """Payment not found in bank"""
    pass


class BankAPIClient:
    """Client for interacting with bank API"""

    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.bank_api_base_url
        self.timeout = self.settings.bank_api_timeout
        self.max_retries = self.settings.bank_api_max_retries
        self.retry_delay = self.settings.bank_api_retry_delay

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict] = None,
        retry: int = 0,
    ) -> dict:
        """Make HTTP request with retry logic"""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if method == "POST":
                    response = await client.post(url, json=data)
                elif method == "GET":
                    response = await client.get(url)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response.raise_for_status()
                return response.json()
        
        except httpx.TimeoutException as e:
            if retry < self.max_retries:
                logger.warning(
                    f"Timeout calling {endpoint}, retrying ({retry + 1}/{self.max_retries})..."
                )
                await asyncio.sleep(self.retry_delay)
                return await self._make_request(method, endpoint, data, retry + 1)
            raise BankAPIError(f"Timeout calling bank API endpoint {endpoint}: {str(e)}")
        
        except httpx.HTTPError as e:
            if retry < self.max_retries and response.status_code >= 500:
                logger.warning(
                    f"Server error calling {endpoint}, retrying ({retry + 1}/{self.max_retries})..."
                )
                await asyncio.sleep(self.retry_delay)
                return await self._make_request(method, endpoint, data, retry + 1)
            raise BankAPIError(f"Error calling bank API endpoint {endpoint}: {str(e)}")

    async def acquiring_start(self, order_id: int, amount: float) -> str:
        """
        Start acquiring payment with bank
        
        Args:
            order_id: Order ID
            amount: Payment amount
        
        Returns:
            Bank payment ID
        
        Raises:
            BankAPIError: If payment creation failed
        """
        try:
            data = {
                "order_id": order_id,
                "amount": amount,
            }
            
            response = await self._make_request("POST", "acquiring_start", data)
            
            if "error" in response:
                raise BankAPIError(f"Bank API error: {response['error']}")
            
            if "bank_payment_id" not in response:
                raise BankAPIError("Bank API response missing bank_payment_id")
            
            logger.info(f"Payment created in bank: {response['bank_payment_id']}")
            return response["bank_payment_id"]
        
        except BankAPIError:
            raise
        except Exception as e:
            raise BankAPIError(f"Unexpected error during acquiring_start: {str(e)}")

    async def acquiring_check(self, bank_payment_id: str) -> dict:
        """
        Check acquiring payment status
        
        Args:
            bank_payment_id: Bank payment ID
        
        Returns:
            Payment info: {bank_payment_id, amount, status, payment_date}
        
        Raises:
            BankPaymentNotFound: If payment not found
            BankAPIError: If other error occurred
        """
        try:
            response = await self._make_request("GET", f"acquiring_check?id={bank_payment_id}")
            
            if "error" in response:
                if "not found" in response["error"].lower():
                    raise BankPaymentNotFound(f"Payment {bank_payment_id} not found in bank")
                raise BankAPIError(f"Bank API error: {response['error']}")
            
            return {
                "bank_payment_id": response.get("bank_payment_id"),
                "amount": response.get("amount"),
                "status": response.get("status"),  # pending, completed, failed
                "payment_date": response.get("payment_date"),
            }
        
        except BankPaymentNotFound:
            raise
        except BankAPIError:
            raise
        except Exception as e:
            raise BankAPIError(f"Unexpected error during acquiring_check: {str(e)}")


# Global client instance
_bank_client = None


def get_bank_client() -> BankAPIClient:
    """Get or create bank API client"""
    global _bank_client
    if _bank_client is None:
        _bank_client = BankAPIClient()
    return _bank_client
