# Payment Service API

Сервис для управления платежами по заказам с поддержкой различных типов платежей (наличные, банковский эквайринг).

## 📚 Документация

- [Основная документация](docs/README.md)
- [Архитектура и ER-диаграмма](docs/ARCHITECTURE.md)
- [Примеры API запросов](docs/API_EXAMPLES.md)
- [Установка и настройка](docs/INSTALL.md)
- [Статус проекта](docs/STATUS.md)
- [Полный обзор проекта](docs/PROJECT_OVERVIEW.md)

## 🚀 Быстрый старт

```bash
# 1. Установка зависимостей
pip install -r requirements.txt

# 2. Подготовка конфигурации
cp config/.env.example config/.env
# Отредактируйте config/.env с нужными значениями

# 3. Создание БД и миграции
alembic upgrade head

# 4. Запуск сервера
python run.py
```

API будет доступен по адресу: `http://localhost:8000`

Swagger UI: `http://localhost:8000/docs`

## 📁 Структура проекта

```
payment_service/
├── docs/                       # Документация
├── config/                     # Конфигурация и переменные окружения
├── app/                        # Основной код приложения
│   ├── models/                 # SQLAlchemy модели
│   ├── schemas/                # Pydantic валидация
│   ├── routes/                 # API endpoints
│   ├── services/               # Бизнес-логика
│   ├── api/                    # Внешние API клиенты
│   ├── main.py                 # FastAPI приложение
│   ├── database.py             # БД подключение
│   └── __init__.py
├── migrations/                 # Alembic миграции
├── tests/                      # Unit и integration тесты
├── requirements.txt            # Зависимости
├── run.py                      # Точка входа
└── .gitignore
```

## 🛠 Технологический стек

- **Framework**: FastAPI
- **ORM**: SQLAlchemy
- **Database**: PostgreSQL
- **Validation**: Pydantic
- **Testing**: pytest
- **Async**: asyncio

## ✨ Основные возможности

- ✅ Управление заказами и платежами
- ✅ Поддержка наличных платежей и банковского эквайринга
- ✅ Синхронизация статуса платежей с внешним API банка
- ✅ RESTful API с полной документацией
- ✅ Обработка ошибок и валидация данных

## 📝 Лицензия

MIT
