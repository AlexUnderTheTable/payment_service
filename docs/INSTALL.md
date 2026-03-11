# Installation Guide / Руководство по установке

## Требования к системе

- **Python**: 3.10 или выше
- **PostgreSQL**: 14 или выше
- **pip**: Latest version
- **Операционная система**: Windows, Linux, macOS

---

## Шаг 1: Установка PostgreSQL

### Windows
1. Скачайте инсталлер с https://www.postgresql.org/download/windows/
2. Запустите инсталлер
3. Выберите путь установки
4. Установите пароль для пользователя `postgres`
5. Порт оставьте по умолчанию (5432)
6. Завершите установку

Проверка установки:
```bash
psql --version
```

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib

# Проверка
psql --version
sudo systemctl status postgresql
```

### macOS (используя Homebrew)
```bash
brew install postgresql

# Запустить сервис
brew services start postgresql

# Проверка
psql --version
```

---

## Шаг 2: Создание базы данных

### Windows (используя pgAdmin или командную строку)

Откройте Command Prompt или PowerShell:
```bash
# Подключитесь к PostgreSQL
psql -U postgres

# Введите пароль, который задали при установке

# В psql консоли выполните:
CREATE DATABASE payment_service;
\q
```

### Linux/macOS
```bash
# Создать БД
sudo -u postgres createdb payment_service

# Проверить создание
sudo -u postgres psql -l
```

---

## Шаг 3: Установка проекта

### 3.1 Клонирование/скачивание проекта
```bash
# Перейти в папку проекта
cd c:\Users\user\Desktop\Projects\Test_task\payment_service

# Или на Linux/Mac
cd ~/Projects/Test_task/payment_service
```

### 3.2 Создание виртуального окружения

**Windows**
```bash
# Создать виртуальное окружение
python -m venv venv

# Активировать
venv\Scripts\activate
```

**Linux/macOS**
```bash
# Создать виртуальное окружение
python3 -m venv venv

# Активировать
source venv/bin/activate
```

### 3.3 Установка зависимостей
```bash
# Убедитесь, что виртуальное окружение активировано
# Ваша командная строка должна начинаться с (venv)

# Обновить pip
pip install --upgrade pip

# Установить зависимости
pip install -r requirements.txt
```

Проверка установки:
```bash
pip list
# Должны видеть: fastapi, sqlalchemy, psycopg2-binary, alembic, pydantic и др.
```

---

## Шаг 4: Конфигурация приложения

### 4.1 Создать .env файл
```bash
# Перейди в папку config
cd config

# Скопировать шаблон
cp .env.example .env

# Или на Windows
copy .env.example .env
```

### 4.2 Отредактировать .env файл

Откройте `config/.env` в текстовом редакторе и обновите параметры:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:ВАШ_ПАРОЛЬ@localhost:5432/payment_service

# API Server
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=True

# Bank API Configuration
BANK_API_BASE_URL=https://bank.api
BANK_API_TIMEOUT=30
BANK_API_MAX_RETRIES=3
BANK_API_RETRY_DELAY=1

# Logging
LOG_LEVEL=INFO
```

**Важные параметры**:
- `DATABASE_URL`: Замените `ВАШ_ПАРОЛЬ` на пароль пользователя `postgres`
- Если PostgreSQL запущен локально на порту 5432 - остальное менять не нужно

---

## Шаг 5: Инициализация БД (Миграции)

### 5.1 Применить миграции

Убедитесь, что находитесь в корне проекта (payment_service):

```bash
# Убедитесь виртуальное окружение активировано
# Выполните миграцию (конфиг находится в папке config/)
alembic -c config/alembic.ini upgrade head
```

**Ожидаемый вывод**:
```
...
Running upgrade  -> 001, initial migration
Done!
```

### 5.2 Проверка БД

Проверьте, что таблицы созданы:
```bash
# Подключитесь к БД
psql -U postgres -d payment_service

# В psql консоли:
\dt
# Должны видеть таблицы: orders, payments

# Выход
\q
```

---

## Шаг 6: Запуск приложения

### Опция 1: Используя run.py
```bash
python run.py
```

### Опция 2: Используя uvicorn напрямую
```bash
uvicorn app.main:app --reload
```

### Опция 3: Используя специфичный хост/порт
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Ожидаемый вывод**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started server process [PID]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

## Шаг 7: Тестирование приложения

### 7.1 Swagger UI
Откройте в браузере: **http://localhost:8000/docs**

Здесь можно:
- Видеть все API endpoints
- Читать документацию
- Тестировать запросы
- Видеть примеры ответов

### 7.2 Curl команды

**Проверка здоровья**:
```bash
curl http://localhost:8000/health
```

**Создание заказа**:
```bash
curl -X POST http://localhost:8000/api/orders \
  -H "Content-Type: application/json" \
  -d '{"order_number": "ORD-001", "total_amount": 1000.0}'
```

**Получение заказа**:
```bash
curl http://localhost:8000/api/orders/1
```

Полный список примеров в `API_EXAMPLES.md`

### 7.3 Запуск тестов
```bash
# Все тесты
pytest

# С выводом подробностей
pytest -v

# С покрытием кода
pytest --cov=app

# Конкретный тест файл
pytest tests/test_order.py -v
```

---

## Шаг 8: Остановка приложения

```bash
# Нажмите в консоли
Ctrl+C
```

Приложение должно gracefully завершить работу.

---

## Troubleshooting / Решение проблем

### Ошибка: "ModuleNotFoundError: No module named 'fastapi'"
**Решение**: Виртуальное окружение не активировано или зависимости не установлены
```bash
# Активировать окружение
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Переустановить зависимости
pip install -r requirements.txt
```

### Ошибка: "Could not connect to PostgreSQL"
**Решение**: PostgreSQL не запущен или неправильные параметры подключения
```bash
# Проверить подключение
psql -U postgres -d payment_service

# Проверить, что БД существует
psql -U postgres -l | grep payment_service

# Проверить DATABASE_URL в .env файле
```

### Ошибка: "relation 'orders' does not exist"
**Решение**: Миграции не применены
```bash
# Применить миграции
alembic upgrade head

# Проверить статус миграций
alembic current
```

### Ошибка: "Port 8000 is already in use"
**Решение**: Другое приложение занимает порт
```bash
# Используйте другой порт
uvicorn app.main:app --port 8001 --reload
```

---

## Development Mode

### Автоматическая перезагрузка
Флаг `--reload` в uvicorn обеспечивает автоматическую перезагрузку при изменениях:
```bash
# Уже включен в run.py и примерах выше
```

### Отключение Debug режима
Для продакшена обновите `.env`:
```env
API_DEBUG=False
```

### Подробное логирование
```env
LOG_LEVEL=DEBUG
```

---

## Production Deployment

Для развёртывания на продакшене:

### 1. Обновить конфиг
```env
API_DEBUG=False
LOG_LEVEL=INFO
DATABASE_URL=postgresql://prod_user:secure_password@prod.server:5432/payment_service
```

### 2. Использовать production ASGI server
```bash
# Gunicorn + Uvicorn
pip install gunicorn

gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### 3. Использовать Nginx как reverse proxy
Конфиг Nginx:
```nginx
server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 4. Использовать Docker (опционально)
```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

---

## Полезные команды

```bash
# Проверить версию Python
python --version

# Список установленных пакетов
pip list

# Переустановить зависимости
pip install -r requirements.txt --upgrade

# Создать список зависимостей
pip freeze > requirements.txt

# Удалить виртуальное окружение (если нужно переустановить)
# Windows
rmdir /s venv

# Linux/Mac
rm -rf venv

# Проверить синтаксис Python файлов
python -m py_compile app/main.py
```

---

## Успешная установка ✅

Если вы видите:
1. Приложение запущено на http://localhost:8000
2. Swagger UI доступен на http://localhost:8000/docs
3. Эндпоинты отвечают (вы можете создать заказ)
4. Тесты проходят (pytest показывает все тесты успешными)

**...то установка успешна! 🎉**

---

## Следующие шаги

1. Читайте `API_EXAMPLES.md` для примеров использования API
2. Изучите `ARCHITECTURE.md` для понимания архитектуры
3. Смотрите `README.md` для быстрого старта
4. Запустите тесты для проверки: `pytest -v`
5. Используйте Swagger UI для интерактивного тестирования

---

**Дата создания**: 11 Марта 2024  
**Последнее обновление**: 11 Марта 2024
