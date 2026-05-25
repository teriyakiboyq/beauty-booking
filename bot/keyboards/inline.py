"""Inline keyboards for bot messages."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from bot.config import get_bot_settings


def _webapp_url() -> str:
    """URL for WebAppInfo — always from WEBAPP_URL in project .env."""
    return get_bot_settings().webapp_url


def open_booking_entry_kb() -> InlineKeyboardMarkup:
    """First step after /start — opens booking flow (then WebApp button)."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Открыть запись",
                    callback_data="open_booking",
                ),
            ],
        ],
    )


def webapp_booking_kb() -> InlineKeyboardMarkup:
    settings = get_bot_settings()
    url = settings.webapp_url
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Открыть запись",
                    web_app=WebAppInfo(url=url),
                ),
            ],
        ],
    )


def subscribe_channel_kb(channel: str) -> InlineKeyboardMarkup:
    username = channel.lstrip("@")
    url = f"https://t.me/{username}"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Подписаться на канал", url=url)],
            [InlineKeyboardButton(text="✅ Я подписался", callback_data="check_sub")],
        ],
    )
