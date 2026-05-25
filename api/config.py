"""API configuration from environment variables."""

import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

from shared.paths import ENV_FILE


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return init_settings, dotenv_settings, env_settings, file_secret_settings

    bot_token: str
    supabase_url: str
    supabase_service_role_key: str

    # Single master: Telegram user id of the beauty master
    master_telegram_id: int

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    webapp_url: str = "http://localhost:5173"

    # Comma-separated origins for CORS (Telegram WebView + your domain)
    cors_origins: str = "https://web.telegram.org,http://localhost:5173"


@lru_cache
def get_settings() -> Settings:
    return Settings()


def warn_if_publishable_key(key: str) -> None:
    """Publishable/anon keys use RLS; service_role bypasses RLS (recommended on server)."""
    if "publishable" in key.lower() or key.startswith("sb_publishable_"):
        logger.warning(
            "SUPABASE_SERVICE_ROLE_KEY is a publishable key (RLS applies). "
            "RLS policies were added for booking; for production prefer service_role secret "
            "from Dashboard → Project Settings → API.",
        )
