### 1. Клонирование репозитория
```bash
git clone git@github.com:gold2201/Transaction-App.git
cd Transaction-App
```

### 2. Настройка окружения
Создайте файл конфигурации `.env`:
```bash
touch .env
```

Заполните `.env` следующими переменными:
```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=transactions
SECRET_KEY=gfdmhghif38yrf9ew0jkf32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 3. Запуск контейнеров
```bash
docker compose up -d --build
```
> *Миграции базы данных применяются автоматически при старте контейнера.*

### Ссылки для доступа:
* **Приложение:** [http://localhost:8000](http://localhost:8000)
* **Интерактивная документация (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Локальная разработка (База в Docker)

Если вы хотите запускать и дебажить код локально, используя `uv`.

### 1. Запуск базы данных
```bash
docker compose up -d db
```

### 2. Установка зависимостей и окружения
```bash
uv sync
```

### 3. Миграции и запуск
```bash
uv run alembic upgrade head

uv run uvicorn app.main:app --reload
```

---

## Учётные данные по умолчанию

Для тестирования функционала вы можете использовать следующие аккаунты:

| Роль | Email | Пароль | Дополнительно |
| :--- | :--- | :--- | :--- |
| **Пользователь** | `user@example.com` | `user123` | Создан счёт с балансом **1000.00** |
| **Администратор**| `admin@example.com` | `admin123` | Полный доступ |

---

## Генерация подписи для вебхука

Для верификации входящих вебхуков используется хэширование SHA-256. Пример генерации подписи на Python:

```python
import hashlib

# Исходные данные для подписи
account_id = 'UUID счета'
amount = '100'
transaction_id = 'UUID транзакции'
user_id = 'UUID пользователя которому добавляете баланс'
secret_key = 'секретный ключ из .env'

# Формирование строки и генерация хэша
payload = f'{account_id}{amount}{transaction_id}{user_id}{secret_key}'
signature = hashlib.sha256(payload.encode()).hexdigest()

print(f"Сгенерированная подпись: {signature}")
```
