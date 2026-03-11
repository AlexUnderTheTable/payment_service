# Payment Service API

Сервис для управления платежами по заказам с поддержкой различных типов платежей (наличные, банковский эквайринг).

## Особенности

- ✅ Управление заказами и платежами
- ✅ Поддержка наличных платежей и банковского эквайринга
- ✅ Синхронизация статуса платежей с банком
- ✅ RESTful API с FastAPI
- ✅ Реляционная БД (PostgreSQL)
- ✅ Обработка ошибок и валидация данных
- ✅ Type hints и документация

## Архитектура

```
payment_service/
├── app/
│   ├── models/          # SQLAlchemy модели (Order, Payment)
│   ├── schemas/         # Pydantic схемы
│   ├── routes/          # API маршруты
│   ├── services/        # Бизнес-логика
│   ├── api/             # Внешние API клиенты
│   ├── main.py          # FastAPI приложение
│   ├── config.py        # Конфигурация
│   └── database.py      # Database connection
├── migrations/          # Alembic миграции БД
├── tests/               # Unit и integration тесты
└── requirements.txt     # Python зависимости
```

## Технологический стек

- **Framework**: FastAPI
- **Web Server**: Uvicorn
- **ORM**: SQLAlchemy
- **Database**: PostgreSQL
- **Validation**: Pydantic
- **HTTP Client**: httpx
- **Async**: asyncio
- **Testing**: pytest

## Готовые компоненты

### 1. Models (Модели БД)
- `Order` - заказ с полями: номер, сумма, статус оплаты
- `Payment` - платеж с типом (наличные / эквайринг), суммой, статусом
- Методы: `deposit()` (пополнение), `refund()` (возврат)

### 2. API Routes (REST API)
- `GET /api/orders` - список всех заказов
- `GET /api/orders/{order_id}` - детали заказа
- `POST /api/orders` - создание заказа
- `GET /payments/{payment_id}` - детали платежа
- `POST /api/orders/{order_id}/payments` - создание платежа
- `POST /api/payments/{payment_id}/deposit` - завершение платежа
- `POST /api/payments/{payment_id}/refund` - возврат платежа
- `GET /api/orders/{order_id}/payments` - список платежей заказа

### 3. Bank API Client
- `BankAPIClient` - клиент для работы с API банка
- Методы: `acquiring_start()`, `acquiring_check()`
- Обработка ошибок и retry логика

### 4. Bank Sync Service
- `BankSyncService` - синхронизация статуса платежей с банком
- Обработка расхождений между локальной системой и банком

## Установка и запуск

### 1. Требования
- Python 3.10+
- PostgreSQL 14+
- pip

### 2. Создание виртуального окружения
```bash
cd payment_service
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 4. Конфигурация БД
```bash
# Скопировать example конфиг
cp .env.example .env

# Обновить .env с вашими параметрами БД
```

### 5. Инициализация БД (Alembic миграции)
```bash
# Инициализировать Alembic (если еще не инициализирован)
alembic init migrations

# Создать миграцию
alembic revision --autogenerate -m "Initial migration"

# Применить миграцию
alembic upgrade head
```

### 6. Запуск приложения
```bash
uvicorn app.main:app --reload

# Или используя python
python -m app.main
```

Приложение будет доступно на `http://localhost:8000`

## API Documentation

После запуска приложения откройте:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Примеры использования

### Создать заказ
```bash
curl -X POST "http://localhost:8000/api/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "order_number": "ORD-001",
    "total_amount": 1000.00
  }'
```

### Получить заказ
```bash
curl "http://localhost:8000/api/orders/1"
```

### Создать наличный платеж
```bash
curl -X POST "http://localhost:8000/api/orders/1/payments" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": 1,
    "amount": 500.00,
    "payment_type": "cash"
  }'
```

### Создать банковский платеж
```bash
curl -X POST "http://localhost:8000/api/orders/1/payments" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": 1,
    "amount": 500.00,
    "payment_type": "acquiring"
  }'
```

### Завершить платеж
```bash
curl -X POST "http://localhost:8000/api/payments/1/deposit"
```

### Вернуть платеж
```bash
curl -X POST "http://localhost:8000/api/payments/1/refund" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "Customer request"
  }'
```

## Тестирование

```bash
# Запустить все тесты
pytest

# С покрытием
pytest --cov=app

# Конкретный тест
pytest tests/test_payments.py::test_create_payment
```

## Состояния платежей

```
PENDING -> COMPLETED -> REFUNDED
       -> FAILED
```

## Состояния заказов

```
unpaid -> partially_paid -> paid
```

## Обработка ошибок

API возвращает стандартные HTTP коды:
- `200 OK` - успешный запрос
- `201 Created` - ресурс создан
- `400 Bad Request` - ошибка валидации или бизнес-логики
- `404 Not Found` - ресурс не найден
- `500 Internal Server Error` - ошибка сервера

Все ошибки содержат детальное сообщение в JSON формате.

## Архитектурные решения

### 1. Работа с внешним API банка

Для обработки платежей через банк реализована архитектура:

```
Payment Service -> Bank API Client (с retry логикой) -> Bank API
                 ↓
             Bank Sync Service (синхронизация статуса)
```

- **BankAPIClient**: Отправляет запросы и получает ID платежей
- **BankSyncService**: Периодически проверяет статус и обновляет локальное состояние
- **Retry Logic**: Автоматический retry при ошибках сети

### 2. Полиморфизм платежей

Все платежи работают через единый интерфейс `Payment`:
- `deposit()` - завершить платеж
- `refund()` - вернуть платеж

Различия между типами платежей обрабатываются на уровне создания.

### 3. Согласованность данных

- Все операции с платежами используют транзакции БД
- Статус заказа обновляется автоматически после изменения статуса платежей
- Синхронизация с банком обрабатывает расхождения состояния

## Следующие шаги

- [ ] Создать миграции Alembic для инициализации БД
- [ ] Написать unit и integration тесты
- [ ] Добавить логирование в все операции
- [ ] Реализовать webhook обработку от банка
- [ ] Добавить аутентификацию (JWT токены)
- [ ] Добавить rate limiting

## Лицензия

MIT
