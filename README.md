### 1. Клонировать репозиторий
git clone git@github.com:gold2201/Transaction-App.git
cd Transaction-App
### 2. Создаем .env файл
cp .env.example .env
С содержимым:
POSTGRES_USER=postgres
POSTGRES_PASSWORD=пароль
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=transactions
SECRET_KEY=ключ
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
### 3. Запускаем проект с помощью docker compose
docker compose up -d --build
Приложение будет доступно на http://localhost:8000, Swagger на http://localhost:8000/docs.
Миграции применяются автоматически при старте контейнера.
### 3.1 Запускаем проект локально
# Поднять PostgreSQL
docker compose up -d db
# Установить зависимости
uv sync
# Применить миграции
uv run alembic upgrade head
# Запустить приложение
uv run uvicorn app.main:app --reload
### Учётные данные
Пользователь - user@example.com - user123
Администратор - admin@example.com - admin123
У пользователя user@example.com создан счёт с балансом 1000.00.
### Для получения сигнатуры можете использовать следующий скрипт
import hashlib
account_id = 'UUID счета'
amount = '100'
transaction_id = 'UUID транзакции'
user_id = 'UUID пользователя которому добавляете баланс'
secret_key = 'секретный ключ из .env'
payload = f'{account_id}{amount}{transaction_id}{user_id}{secret_key}'
print(hashlib.sha256(payload.encode()).hexdigest())
