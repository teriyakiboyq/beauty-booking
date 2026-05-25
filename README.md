# Beauty Booking

Telegram-бот с Mini App для записи к бьюти-мастеру.

## Стек

- **bot/** — Aiogram 3 (polling, middleware подписки на канал)
- **api/** — FastAPI (слоты, услуги, записи; auth через `initData`)
- **web/** — React + Tailwind (Vite)
- **database/** — `schema.sql` для Supabase

## Быстрый старт

### 1. Supabase

1. Создайте проект на [supabase.com](https://supabase.com).
2. В SQL Editor выполните `database/schema.sql`.
3. Добавьте мастера и услуги (раскомментируйте seed в конце `schema.sql` или вручную):

```sql
INSERT INTO profiles (telegram_id, full_name, username, role)
VALUES (YOUR_MASTER_TELEGRAM_ID, 'Имя', 'username', 'master')
RETURNING id;

INSERT INTO master_settings (master_id, work_start, work_end, slot_duration, channel_username)
VALUES ('<uuid>', '09:00', '18:00', 30, 'your_channel');

INSERT INTO services (master_id, name, price, duration, description)
VALUES ('<uuid>', 'Маникюр', 2500, 60, 'Описание');
```

### 2. Переменные окружения

```bash
cp .env.example .env
# заполните BOT_TOKEN, SUPABASE_*, MASTER_TELEGRAM_ID, WEBAPP_URL
```

### 3. Python (bot + api)

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

**API:**

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**Bot:**

```bash
python -m bot.main
```

### 4. Mini App (web)

```bash
cd web
npm install
npm run dev
```

**Mini App в Telegram локально:** см. [docs/LOCAL_WEBAPP.md](docs/LOCAL_WEBAPP.md) — ngrok на порт **5173** (фронт), не на 8000 (API).

В [@BotFather](https://t.me/BotFather) укажите Menu Button / Web App URL = тот же `WEBAPP_URL` (HTTPS).

## Структура

```
beauty-booking/
├── bot/           # handlers, middlewares, keyboards
├── api/           # routers, initData auth, slot generator
├── web/           # React Mini App
├── database/      # schema.sql
├── shared/        # enums
└── requirements.txt
```

## API (для Mini App)

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/api/health` | Проверка |
| GET | `/api/services` | Список услуг |
| GET | `/api/slots?service_id=&date=` | Свободные слоты |
| POST | `/api/appointments` | Создать запись |
| GET | `/api/appointments/my` | Мои записи |

Заголовок: `X-Telegram-Init-Data` — строка `initData` из WebApp.

## Деплой (кратко)

- PostgreSQL — Supabase (hosted).
- `api` + `bot` — один VPS, один `.env`.
- `web` — `npm run build`, статика за nginx или CDN; HTTPS обязателен для Mini App.

## Следующие шаги

- Уведомления мастеру о новой записи
- Отмена / перенос из бота
- Webhook вместо polling
