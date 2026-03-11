# Архитектура платежного сервиса

## Диаграмма компонентов

```
┌─────────────────────────────────────────────────────────────────┐
│                         REST API (FastAPI)                      │
├─────────────────────────────────────────────────────────────────┤
│  GET /orders                     POST /orders                    │
│  GET /orders/{id}                GET /orders/{id}/payments       │
│  POST /orders/{id}/payments      GET /payments/{id}              │
│  POST /payments/{id}/deposit     POST /payments/{id}/refund      │
└────────────┬────────────────────────────────────┬────────────────┘
             │                                    │
       ┌─────▼─────────────────────┬──────────────▼─────┐
       │   Routes (Routers)        │   Request Validation│
       │  - orders.py              │   (Pydantic Schemas)│
       │  - payments.py            │                     │
       └─────┬─────────────────────┴──────────────┬──────┘
             │                                    │
       ┌─────▼──────────────────────────────────▼──────────────┐
       │         Business Logic Services                        │
       │  - PaymentService                                      │
       │  - BankSyncService                                     │
       │  - Order & Payment models with business methods        │
       └────────────┬─────────────────────┬────────────────────┘
                    │                     │
        ┌───────────▼───────────┐  ┌──────▼──────────────────┐
        │   Database Layer      │  │  External API Client    │
        │  (SQLAlchemy ORM)     │  │  - BankAPIClient        │
        │                       │  │  - Retry logic          │
        │  - Order model        │  │  - Error handling       │
        │  - Payment model      │  │                         │
        └────────────┬──────────┘  └──────┬──────────────────┘
                     │                    │
        ┌────────────▼────────┐  ┌────────▼──────────────────┐
        │  PostgreSQL DB      │  │  Bank API                 │
        │                     │  │  - acquiring_start        │
        │  - orders table     │  │  - acquiring_check        │
        │  - payments table   │  │                           │
        └─────────────────────┘  └───────────────────────────┘
```

## Иерархия слоёв

### 1. Presentation Layer (REST API)
- **Компоненты**: FastAPI приложение, маршруты (routes)
- **Ответственность**: Обработка HTTP запросов, валидация входных данных
- **Файлы**: `app/main.py`, `app/routes/`

### 2. Business Logic Layer
- **Компоненты**: Services, Models с методами deposit/refund
- **Ответственность**: Реализация бизнес-правил, логика платежей
- **Файлы**: `app/services/`, `app/models/`

### 3. Data Access Layer
- **Компоненты**: SQLAlchemy ORM, Database connection
- **Ответственность**: Работа с БД, транзакции
- **Файлы**: `app/database.py`, `app/models/`

### 4. External Integration Layer
- **Компоненты**: BankAPIClient, BankSyncService
- **Ответственность**: Взаимодействие с внешним API банка
- **Файлы**: `app/api/bank.py`, `app/services/bank_sync.py`

## Диаграмма Сущности-Отношения (БД)

```
┌──────────────────────────┐
│        ORDERS            │
├──────────────────────────┤
│ id (PK)                  │
│ order_number (UNIQUE)    │
│ total_amount             │
│ payment_status           │
│ created_at               │
│ updated_at               │
└────────────┬─────────────┘
             │ (1:N)
             │
┌────────────▼─────────────┐
│       PAYMENTS           │
├──────────────────────────┤
│ id (PK)                  │
│ order_id (FK)            │
│ amount                   │
│ payment_type             │
│ status                   │
│ bank_payment_id          │
│ created_at               │
│ updated_at               │
└──────────────────────────┘
```

### Таблица orders

| Поле | Тип | Описание |
|------|-----|---------|
| id | INTEGER | Primary Key |
| order_number | VARCHAR | Уникальный номер заказа |
| total_amount | FLOAT | Сумма заказа |
| payment_status | VARCHAR | Статус: unpaid, partially_paid, paid |
| created_at | DATETIME | Дата создания |
| updated_at | DATETIME | Дата последнего обновления |

### Таблица payments

| Поле | Тип | Описание |
|------|-----|---------|
| id | INTEGER | Primary Key |
| order_id | INTEGER | Foreign Key на orders.id |
| amount | FLOAT | Сумма платежа |
| payment_type | VARCHAR | Тип: cash, acquiring |
| status | VARCHAR | Статус: pending, completed, refunded, failed |
| bank_payment_id | VARCHAR (nullable) | ID платежа в банке для acquiring платежей |
| created_at | DATETIME | Дата создания |
| updated_at | DATETIME | Дата последнего обновления |

## Потоки данных

### Создание платежа наличными

```
HTTP POST /api/orders/{order_id}/payments
    ↓
Валидация (Pydantic schema)
    ↓ (order_id существует? сумма не превышает остаток?)
Payment model создана в БД
    ↓
Ответ: 201 Created с деталями платежа
```

### Создание платежа через банк

```
HTTP POST /api/orders/{order_id}/payments {payment_type: "acquiring"}
    ↓
Валидация входных данных
    ↓
BankAPIClient.acquiring_start(order_id, amount)
    ↓ (с retry логикой при ошибках)
Bank API возвращает bank_payment_id
    ↓
Payment model создана в БД с bank_payment_id
    ↓
Ответ: 201 Created
```

### Завершение платежа (deposit)

```
HTTP POST /api/payments/{payment_id}/deposit
    ↓
Получить Payment из БД
    ↓ (status == PENDING?)
payment.deposit() → status = COMPLETED
    ↓
order.update_payment_status() → проверить и обновить статус заказа
    ↓
Коммит транзакции в БД
    ↓
Ответ: 200 OK с деталями платежа
```

### Возврат платежа (refund)

```
HTTP POST /api/payments/{payment_id}/refund
    ↓
Получить Payment из БД
    ↓ (status == COMPLETED?)
payment.refund() → status = REFUNDED
    ↓
order.update_payment_status() → пересчитать статус
    ↓
Коммит транзакции в БД
    ↓
Ответ: 200 OK
```

### Синхронизация с банком

```
BankSyncService.sync_acquiring_payment(payment)
    ↓
BankAPIClient.acquiring_check(bank_payment_id)
    ↓ (с обработкой ошибок и retry)
Получить статус платежа from Bank API
    ↓
Сравнить с локальным статусом
    ↓ (если отличаются)
Логировать расхождение
    ↓
Обновить локальный статус
    ↓
Обновить статус заказа
    ↓
Коммит изменений
```

## Использованные паттерны проектирования

### 1. Service Layer Pattern
- **Что**: Слой бизнес-логики отделен от REST контроллеров
- **Где**: `PaymentService`, `BankSyncService`
- **Преимущества**: Бизнес-логика переиспользуется, тестируется отдельно

### 2. Repository Pattern
- **Что**: Работа с БД через ORM, а не прямые SQL запросы
- **Где**: SQLAlchemy models как repositories
- **Преимущества**: Абстрагирование от БД, легко заменить БД

### 3. Dependency Injection
- **Что**: Зависимости передаются через параметры
- **Где**: FastAPI Depends(), services инициализируются с зависимостями
- **Преимущества**: Легко тестировать, мокировать зависимости

### 4. Retry Pattern (Exponential Backoff)
- **Что**: Автоматический retry при ошибках сети/timeout
- **Где**: BankAPIClient._make_request()
- **Преимущества**: Надежность при работе с нестабильным внешним API

### 5. Strategy Pattern для типов платежей
- **Что**: Разные типы платежей работают через единый интерфейс
- **Где**: payment.deposit(), payment.refund() работают для всех типов
- **Преимущества**: Легко добавлять новые типы платежей

### 6. Polymorphic Model Pattern
- **Что**: Все платежи (cash и acquiring) используют одну таблицу
- **Где**: Payment model с payment_type enum
- **Преимущества**: Простая структура БД, единая логика обработки

## Обработка ошибок

### Типы ошибок

1. **Validation Errors** (400 Bad Request)
   - Некорректный payment_type
   - Сумма платежа больше остатка
   - Отрицательная или нулевая сумма

2. **Not Found Errors** (404 Not Found)
   - Order не существует
   - Payment не существует
   - Bank payment не найден в базе

3. **State Errors** (400 Bad Request)
   - Попытка завершить уже завершенный платеж
   - Попытка вернуть не завершенный платеж
   - Попытка создать платеж для оплаченного заказа

4. **External API Errors**
   - BankAPIError при ошибке банка
   - BankPaymentNotFound при платеж не найден в банке
   - Timeout при долгом ответе банка

### Стратегия обработки

- Все ошибки логируются с контекстом
- Клиентам возвращается понятное сообщение об ошибке
- HTTP коды выбраны согласно REST стандартам
- Recovery стратегии применяются где возможно (retry при network errors)

## Асинхронность

- BankAPIClient использует `async/await` для HTTP запросов
- Горячей точки остальных операций остаются синхронными (БД транзакции)
- Можно добавить асинхронность в маршруты при необходимости

---

**Дата создания**: 11 Марта 2024
**Версия архитектуры**: 1.0
