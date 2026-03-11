# Project Structure / Структура проекта

```
payment_service/
│
├── 📄 README.md                    # Главный файл - обзор и быстрый старт
├── 📄 requirements.txt             # Python зависимости
├── 📄 run.py                       # Точка входа приложения
│
├── 📁 docs/                        # 📚 ДОКУМЕНТАЦИЯ
│   ├── README.md                   # Полная документация
│   ├── INSTALL.md                  # Подробное руководство установки
│   ├── ARCHITECTURE.md             # Архитектура + ER-диаграмма БД
│   ├── API_EXAMPLES.md             # Примеры всех API запросов
│   ├── PROJECT_OVERVIEW.md         # Полный обзор проекта
│   ├── STATUS.md                   # Статус разработки
│   └── SUMMARY.md                  # Краткое резюме
│
├── 📁 config/                      # ⚙️ КОНФИГУРАЦИЯ
│   ├── __init__.py                 # Package инициализация
│   ├── config.py                   # Основные настройки приложения
│   ├── alembic.ini                 # Конфигурация миграций БД
│   ├── .env.example                # Шаблон переменных окружения
│   └── .env                        # Переменные окружения (локально)
│
├── 📁 app/                         # 💻 КОД ПРИЛОЖЕНИЯ
│   ├── __init__.py
│   ├── main.py                     # FastAPI приложение
│   ├── database.py                 # Подключение к БД, SessionLocal
│   │
│   ├── 📁 models/                  # 📊 SQLAlchemy ORM Модели
│   │   ├── __init__.py
│   │   ├── order.py                # Order модель (заказы)
│   │   └── payment.py              # Payment модель (платежи)
│   │
│   ├── 📁 schemas/                 # ✅ Pydantic Валидация
│   │   ├── __init__.py
│   │   ├── order.py                # Order schemas
│   │   └── payment.py              # Payment schemas
│   │
│   ├── 📁 routes/                  # 🔌 REST API Endpoints
│   │   ├── __init__.py
│   │   ├── orders.py               # Order endpoints (GET, POST)
│   │   └── payments.py             # Payment endpoints (GET, POST, deposit, refund)
│   │
│   ├── 📁 services/                # 🏢 Бизнес-логика
│   │   ├── __init__.py
│   │   ├── payment.py              # PaymentService
│   │   └── bank_sync.py            # BankSyncService (синхронизация с банком)
│   │
│   └── 📁 api/                     # 🏦 Внешние API Клиенты
│       ├── __init__.py
│       └── bank.py                 # BankAPIClient (для работы с API банка)
│
├── 📁 migrations/                  # 🔄 Alembic Миграции БД
│   ├── env.py                      # Конфигурация миграций
│   ├── script.py.mako              # Шаблон миграций
│   └── 📁 versions/                # Версии миграций
│       └── 001_initial_migration.py
│
├── 📁 tests/                       # 🧪 ТЕСТИРОВАНИЕ
│   ├── __init__.py
│   ├── conftest.py                 # pytest конфигурация и fixtures
│   ├── test_order.py               # Тесты Order модели (5 тестов)
│   ├── test_payment.py             # Тесты Payment модели (6 тестов)
│   ├── test_api_endpoints.py       # Тесты API endpoints
│   ├── test_bank_api.py            # Тесты BankAPIClient
│   ├── test_bank_sync.py           # Тесты BankSyncService
│   ├── test_error_handling.py      # Тесты обработки ошибок
│   └── test_error_handling_clean.py
│
├── 📁 __pycache__/                 # (игнорируется Git)
├── 📁 .pytest_cache/               # (игнорируется Git)
│
├── .gitignore                      # Git ignore правила
├── test_functionality.py           # Скрипт функционального тестирования
├── reset_db.py                     # Скрипт сброса БД
└── reset_db_sql.py                 # SQL скрипт сброса БД
```

## 📚 Организация документации

Вся документация находится в папке **docs/**:

| Файл | Назначение |
|------|-----------|
| **docs/README.md** | Основная документация проекта |
| **docs/INSTALL.md** | Подробное руководство установки (Windows/Linux/macOS) |
| **docs/ARCHITECTURE.md** | Архитектура, паттерны, ER-диаграмма БД |
| **docs/API_EXAMPLES.md** | Примеры всех API запросов (curl, JSON) |
| **docs/PROJECT_OVERVIEW.md** | Полный обзор реализованных требований |
| **docs/STATUS.md** | Статус разработки и что реализовано |
| **docs/SUMMARY.md** | Краткое резюме функциональности |

## ⚙️ Организация конфигурации

Вся конфигурация находится в папке **config/**:

| Файл | Назначение |
|------|-----------|
| **config/config.py** | Основной файл конфигурации (Settings класс) |
| **config/__init__.py** | Package инициализация, экспорт Settings |
| **config/.env.example** | Шаблон переменных окружения (для версионирования) |
| **config/.env** | Локальные переменные окружения (в .gitignore) |
| **config/alembic.ini** | Конфигурация Alembic для миграций БД |

## 📦 Импорты конфигурации

Из любой части кода можно импортировать конфигурацию:

```python
from config import get_settings, Settings

# Получить объект настроек
settings = get_settings()

# Использовать параметры
db_url = settings.database_url
api_port = settings.api_port
```

## 🚀 Как запустить

```bash
# 1. Перейти в проект
cd payment_service

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Настроить конфигурацию
cd config
cp .env.example .env
# Отредактировать config/.env
cd ..

# 4. Применить миграции
alembic -c config/alembic.ini upgrade head

# 5. Запустить приложение
python run.py
```

API будет доступен: **http://localhost:8000**  
Swagger UI: **http://localhost:8000/docs**
