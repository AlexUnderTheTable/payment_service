# API Examples / Примеры использования API

## Overview

Примеры запросов и ответов для всех endpoint'ов Payment Service API.

---

## Orders API

### 1. List All Orders

**Request:**
```bash
curl -X GET "http://localhost:8000/api/orders" \
  -H "accept: application/json"
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "order_number": "ORD-001",
    "total_amount": 1000.0,
    "payment_status": "partially_paid",
    "paid_amount": 500.0,
    "remaining_amount": 500.0,
    "created_at": "2024-03-11T10:00:00",
    "updated_at": "2024-03-11T10:15:00"
  },
  {
    "id": 2,
    "order_number": "ORD-002",
    "total_amount": 2500.0,
    "payment_status": "unpaid",
    "paid_amount": 0.0,
    "remaining_amount": 2500.0,
    "created_at": "2024-03-11T10:30:00",
    "updated_at": "2024-03-11T10:30:00"
  }
]
```

---

### 2. Get Order Details

**Request:**
```bash
curl -X GET "http://localhost:8000/api/orders/1" \
  -H "accept: application/json"
```

**Response (200 OK):**
```json
{
  "id": 1,
  "order_number": "ORD-001",
  "total_amount": 1000.0,
  "payment_status": "partially_paid",
  "paid_amount": 500.0,
  "remaining_amount": 500.0,
  "created_at": "2024-03-11T10:00:00",
  "updated_at": "2024-03-11T10:15:00",
  "payments": [
    {
      "id": 1,
      "amount": 500.0,
      "payment_type": "cash",
      "status": "completed",
      "bank_payment_id": null,
      "created_at": "2024-03-11T10:10:00",
      "updated_at": "2024-03-11T10:10:00"
    }
  ]
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Order with id 999 not found"
}
```

---

### 3. Create Order

**Request:**
```bash
curl -X POST "http://localhost:8000/api/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "order_number": "ORD-001",
    "total_amount": 1000.0
  }'
```

**Response (201 Created):**
```json
{
  "id": 1,
  "order_number": "ORD-001",
  "total_amount": 1000.0,
  "payment_status": "unpaid",
  "paid_amount": 0.0,
  "remaining_amount": 1000.0,
  "created_at": "2024-03-11T10:00:00",
  "updated_at": "2024-03-11T10:00:00"
}
```

**Request with duplicate order_number (400 Bad Request):**
```bash
curl -X POST "http://localhost:8000/api/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "order_number": "ORD-001",
    "total_amount": 2000.0
  }'
```

**Response (400 Bad Request):**
```json
{
  "detail": "Order with number ORD-001 already exists"
}
```

---

## Payments API

### 4. Create Cash Payment

**Request:**
```bash
curl -X POST "http://localhost:8000/api/orders/1/payments" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": 1,
    "amount": 500.0,
    "payment_type": "cash"
  }'
```

**Response (201 Created):**
```json
{
  "id": 1,
  "order_id": 1,
  "amount": 500.0,
  "payment_type": "cash",
  "status": "pending",
  "bank_payment_id": null,
  "created_at": "2024-03-11T10:10:00",
  "updated_at": "2024-03-11T10:10:00"
}
```

---

### 5. Create Acquiring Payment (Bank Payment)

**Request:**
```bash
curl -X POST "http://localhost:8000/api/orders/1/payments" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": 1,
    "amount": 500.0,
    "payment_type": "acquiring"
  }'
```

**Response (201 Created):**
```json
{
  "id": 2,
  "order_id": 1,
  "amount": 500.0,
  "payment_type": "acquiring",
  "status": "pending",
  "bank_payment_id": "BANK-12345-67890",
  "created_at": "2024-03-11T10:20:00",
  "updated_at": "2024-03-11T10:20:00"
}
```

**Error: Amount exceeds remaining (400 Bad Request):**
```bash
curl -X POST "http://localhost:8000/api/orders/1/payments" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": 1,
    "amount": 600.0,
    "payment_type": "cash"
  }'
```

**Response (400 Bad Request):**
```json
{
  "detail": "Payment amount 600.0 exceeds remaining amount 500.0"
}
```

---

### 6. Complete Payment (Deposit)

**Request:**
```bash
curl -X POST "http://localhost:8000/api/payments/1/deposit" \
  -H "accept: application/json"
```

**Response (200 OK):**
```json
{
  "id": 1,
  "order_id": 1,
  "amount": 500.0,
  "payment_type": "cash",
  "status": "completed",
  "bank_payment_id": null,
  "created_at": "2024-03-11T10:10:00",
  "updated_at": "2024-03-11T10:15:00"
}
```

**Error: Payment already completed (400 Bad Request):**
```bash
curl -X POST "http://localhost:8000/api/payments/1/deposit"
```

**Response (400 Bad Request):**
```json
{
  "detail": "Can only deposit pending payments. Current status: completed"
}
```

---

### 7. Refund Payment

**Request:**
```bash
curl -X POST "http://localhost:8000/api/payments/1/refund" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "Customer request"
  }'
```

**Response (200 OK):**
```json
{
  "id": 1,
  "order_id": 1,
  "amount": 500.0,
  "payment_type": "cash",
  "status": "refunded",
  "bank_payment_id": null,
  "created_at": "2024-03-11T10:10:00",
  "updated_at": "2024-03-11T10:20:00"
}
```

**Error: Can only refund completed payments (400 Bad Request):**
```bash
curl -X POST "http://localhost:8000/api/payments/2/refund" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Test"}'
```

**Response (400 Bad Request):**
```json
{
  "detail": "Can only refund completed payments. Current status: pending"
}
```

---

### 8. Get Payment Details

**Request:**
```bash
curl -X GET "http://localhost:8000/api/payments/1" \
  -H "accept: application/json"
```

**Response (200 OK):**
```json
{
  "id": 1,
  "order_id": 1,
  "amount": 500.0,
  "payment_type": "cash",
  "status": "completed",
  "bank_payment_id": null,
  "created_at": "2024-03-11T10:10:00",
  "updated_at": "2024-03-11T10:15:00"
}
```

---

### 9. List Order Payments

**Request:**
```bash
curl -X GET "http://localhost:8000/api/orders/1/payments" \
  -H "accept: application/json"
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "order_id": 1,
    "amount": 500.0,
    "payment_type": "cash",
    "status": "completed",
    "bank_payment_id": null,
    "created_at": "2024-03-11T10:10:00",
    "updated_at": "2024-03-11T10:15:00"
  },
  {
    "id": 2,
    "order_id": 1,
    "amount": 300.0,
    "payment_type": "acquiring",
    "status": "pending",
    "bank_payment_id": "BANK-98765-43210",
    "created_at": "2024-03-11T10:20:00",
    "updated_at": "2024-03-11T10:20:00"
  }
]
```

---

## HTTP Status Codes

| Code | Meaning | Use Cases |
|------|---------|-----------|
| 200 | OK | GET, successful POST (deposit/refund) |
| 201 | Created | POST /orders, POST /payments |
| 400 | Bad Request | Validation error, business logic error |
| 404 | Not Found | Order/payment not found |
| 500 | Internal Server Error | Unhandled server error |

---

## Common Error Scenarios

### Scenario 1: Try to overpay order

```bash
# Create order for 1000
curl -X POST "http://localhost:8000/api/orders" \
  -H "Content-Type: application/json" \
  -d '{"order_number": "ORD-001", "total_amount": 1000.0}'

# Try to create payment for 1500
curl -X POST "http://localhost:8000/api/orders/1/payments" \
  -H "Content-Type: application/json" \
  -d '{"order_id": 1, "amount": 1500.0, "payment_type": "cash"}'

# Response: 400 Bad Request - "Payment amount 1500.0 exceeds remaining amount 1000.0"
```

### Scenario 2: Complete partial payment, then full order

```bash
# Create order for 1000
curl -X POST "http://localhost:8000/api/orders" \
  -H "Content-Type: application/json" \
  -d '{"order_number": "ORD-002", "total_amount": 1000.0}'

# Create first payment 400
curl -X POST "http://localhost:8000/api/orders/1/payments" \
  -H "Content-Type: application/json" \
  -d '{"order_id": 1, "amount": 400.0, "payment_type": "cash"}'

# Complete it
curl -X POST "http://localhost:8000/api/payments/1/deposit"

# Check order status - should be "partially_paid"
curl -X GET "http://localhost:8000/api/orders/1"

# Create second payment 600 (remaining amount)
curl -X POST "http://localhost:8000/api/orders/1/payments" \
  -H "Content-Type: application/json" \
  -d '{"order_id": 1, "amount": 600.0, "payment_type": "cash"}'

# Complete it
curl -X POST "http://localhost:8000/api/payments/2/deposit"

# Check order status - should be "paid"
curl -X GET "http://localhost:8000/api/orders/1"
```

### Scenario 3: Refund and repay

```bash
# Complete payment for order
curl -X POST "http://localhost:8000/api/payments/1/deposit"

# Refund it
curl -X POST "http://localhost:8000/api/payments/1/refund" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Wrong payment"}'

# Check order status - should be back to "unpaid"
curl -X GET "http://localhost:8000/api/orders/1"

# Create new payment
curl -X POST "http://localhost:8000/api/orders/1/payments" \
  -H "Content-Type: application/json" \
  -d '{"order_id": 1, "amount": 500.0, "payment_type": "cash"}'
```

---

## Using Swagger UI

After starting the application, you can test all endpoints interactively:

**URL**: http://localhost:8000/docs

Features:
- Interactive request/response testing
- Auto-generated documentation
- Schema validation
- Easy parameter input

---

## Python Client Example

```python
import httpx
import asyncio

async def test_payment_api():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # Create order
        order_response = await client.post(
            "/api/orders",
            json={"order_number": "ORD-001", "total_amount": 1000.0}
        )
        order = order_response.json()
        print(f"Created order: {order}")
        
        # Create payment
        payment_response = await client.post(
            f"/api/orders/{order['id']}/payments",
            json={
                "order_id": order['id'],
                "amount": 500.0,
                "payment_type": "cash"
            }
        )
        payment = payment_response.json()
        print(f"Created payment: {payment}")
        
        # Complete payment
        deposit_response = await client.post(
            f"/api/payments/{payment['id']}/deposit"
        )
        completed = deposit_response.json()
        print(f"Completed payment: {completed}")

# Run example
asyncio.run(test_payment_api())
```

---

**Last Updated**: 2024-03-11
