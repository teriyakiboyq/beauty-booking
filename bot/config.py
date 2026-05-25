"""Bot configuration from project-root .env."""

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict

from shared.paths import ENV_FILE


def _read_webapp_url_from_file() -> str | None:
    """Debug helper: raw WEBAPP_URL line from .env on disk."""
    if not ENV_FILE.is_file():
        return None
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("WEBAPP_URL="):
            return stripped.split("=", 1)[1].strip()
    return None


class BotSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    bot_token: str
    webapp_url: str = "http://localhost:5173"

    required_channel: str = "@serega_pirat2"

    supabase_url: str = ""
    supabase_service_role_key: str = ""

    @field_validator("webapp_url")
    @classmethod
    def strip_trailing_slash(cls, value: str) -> str:
        return value.rstrip("/")

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        # .env в корне проекта важнее переменных Windows/User (частая причина «старого» URL)
        return init_settings, dotenv_settings, env_settings, file_secret_settings


@lru_cache
def get_bot_settings() -> BotSettings:
    return BotSettings()


def get_env_file_webapp_url() -> str | None:
    return _read_webapp_url_from_file()
