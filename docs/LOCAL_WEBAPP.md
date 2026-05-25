# Mini App локально (Telegram + ngrok)

## Почему пустое окно

| Ошибка | Что происходит |
|--------|----------------|
| `WEBAPP_URL=http://127.0.0.1:8000` | Открывается **API**, а не React — нет HTML |
| `http://` вместо `https://` | Telegram **не открывает** HTTP WebApp |
| Vite не запущен | ngrok отдаёт 502 / пустую страницу |
| Неверный ngrok URL | 404 или чужой туннель |

**WebAppInfo** → только **фронтенд** (`npm run dev`, порт **5173**).  
**FastAPI** (:8000) → только JSON API, Mini App ходит туда через `/api`.

## Быстрая настройка (один ngrok)

### 1. Запустите три процесса

```powershell
# Терминал 1 — API
cd C:\Users\glass\Projects\beauty-booking
.venv\Scripts\activate
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Терминал 2 — фронт
cd C:\Users\glass\Projects\beauty-booking\web
npm run dev

# Терминал 3 — туннель на ФРОНТ (5173, не 8000!)
ngrok http 5173
```

### 2. Скопируйте HTTPS URL из ngrok

Пример: `https://abc123.ngrok-free.app`

### 3. Корневой `.env`

```env
WEBAPP_URL=https://abc123.ngrok-free.app
CORS_ORIGINS=https://web.telegram.org,https://abc123.ngrok-free.app,http://localhost:5173
```

### 4. `web/.env`

```env
VITE_API_URL=/api
```

Vite проксирует `https://abc123.ngrok-free.app/api/*` → `http://127.0.0.1:8000/api/*`.

### 5. Перезапустите бота

```powershell
cd C:\Users\glass\Projects\beauty-booking
python -m bot.main
```

В логе должно быть: `WEBAPP_URL for WebApp button: https://ваш-ngrok...`

### 5.1. Обновите кнопку в чате

URL WebApp **запекается** в уже отправленное сообщение. После смены `.env` снова нажмите **/start** → «Открыть запись», чтобы получить кнопку с новым URL.

### 6. Проверка в браузере

Откройте `https://abc123.ngrok-free.app` — должна быть страница «Выберите услугу», не JSON.

### 7. BotFather (опционально)

`/mybots` → ваш бот → **Menu Button** → URL = тот же `WEBAPP_URL`.

## Альтернатива: два туннеля

- ngrok `5173` → `WEBAPP_URL`
- ngrok `8000` → `VITE_API_URL=https://xyz.ngrok.app/api` и добавить URL в `CORS_ORIGINS`

Один туннель проще (см. `vite.config.ts` proxy).

## Cloudflare Tunnel

Вместо ngrok:

```powershell
cloudflared tunnel --url http://localhost:5173
```

Дальше те же шаги с выданным `https://....trycloudflare.com` URL.
