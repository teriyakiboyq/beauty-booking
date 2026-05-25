"""
Aiogram bot entrypoint.

Run from project root:
  python -m bot.main
"""

import asyncio
import logging

from bot.config import get_bot_settings, get_env_file_webapp_url
from bot.handlers import register_handlers
from bot.loader import bot, dp
from shared.paths import ENV_FILE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _log_startup_config() -> None:
    settings = get_bot_settings()
    from_file = get_env_file_webapp_url()
    logger.info("Config file: %s (exists=%s)", ENV_FILE, ENV_FILE.is_file())
    logger.info("WEBAPP_URL in .env file: %s", from_file)
    logger.info("WEBAPP_URL for WebApp button: %s", settings.webapp_url)
    if from_file and from_file.rstrip("/") != settings.webapp_url.rstrip("/"):
        logger.warning(
            "WEBAPP_URL в .env и загруженный URL различаются — "
            "сохраните файл .env (Ctrl+S) или проверьте переменную WEBAPP_URL в Windows.",
        )

    url = settings.webapp_url
    if url.startswith("http://"):
        logger.warning(
            "WEBAPP_URL uses HTTP — Telegram requires HTTPS (ngrok/cloudflare).",
        )
    if ":8000" in url:
        logger.warning(
            "WEBAPP_URL points to API port 8000. Use ngrok URL of Vite (:5173).",
        )
    if "your-domain" in url or "your-ngrok" in url:
        logger.warning(
            "WEBAPP_URL looks like a placeholder — set real ngrok URL in .env",
        )


async def main() -> None:
    _log_startup_config()
    register_handlers(dp)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
