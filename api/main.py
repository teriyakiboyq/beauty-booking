"""
FastAPI entrypoint for Telegram Mini App.

Run from project root:
  uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
"""

import logging

from fastapi import FastAPI

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
# Подробные логи генерации слотов
logging.getLogger("api.routers.slots").setLevel(logging.INFO)
logging.getLogger("api.services.slot_generator").setLevel(logging.DEBUG)
from fastapi.middleware.cors import CORSMiddleware

from api.config import get_settings, warn_if_publishable_key
from api.routers import appointments, services, slots

settings = get_settings()
warn_if_publishable_key(settings.supabase_service_role_key)

app = FastAPI(
    title="Beauty Booking API",
    version="0.1.0",
    description="Backend for Telegram Mini App booking flow",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(services.router, prefix="/api")
app.include_router(slots.router, prefix="/api")
app.include_router(appointments.router, prefix="/api")


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
