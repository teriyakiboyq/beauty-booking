"""
Channel subscription check for booking / Mini App access.

Used by booking handlers only — not on /start.
"""

from collections.abc import Awaitable, Callable
from functools import wraps
from typing import ParamSpec, TypeVar

from aiogram import Bot
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message, TelegramObject

from bot.config import get_bot_settings
from bot.keyboards.inline import subscribe_channel_kb

P = ParamSpec("P")
R = TypeVar("R")

# TODO: когда появится канал — поставить True и добавить бота в канал как админа
CHANNEL_SUBSCRIPTION_ENABLED = False

ALLOWED_STATUSES = {
    ChatMemberStatus.MEMBER,
    ChatMemberStatus.ADMINISTRATOR,
    ChatMemberStatus.CREATOR,
}


def channel_username_display() -> str:
    """@username for user-facing messages."""
    channel = get_bot_settings().required_channel or "@serega_pirat2"
    if channel.startswith("@"):
        return channel
    return f"@{channel}"


def channel_chat_id() -> str:
    """Chat id / @username for get_chat_member."""
    return get_bot_settings().required_channel or "@serega_pirat2"


async def is_user_subscribed(bot: Bot, user_id: int) -> bool:
    if not CHANNEL_SUBSCRIPTION_ENABLED:
        return True

    try:
        member = await bot.get_chat_member(chat_id=channel_chat_id(), user_id=user_id)
        return member.status in ALLOWED_STATUSES
    except TelegramBadRequest:
        return False
    except Exception:
        return False


async def reply_subscription_required(event: Message | CallbackQuery) -> None:
    channel_label = channel_username_display()
    text = f"Для бронирования нужно быть подписанным на {channel_label}"

    if isinstance(event, CallbackQuery):
        if event.message:
            await event.message.answer(text, reply_markup=subscribe_channel_kb(channel_chat_id()))
        await event.answer("Нужна подписка на канал", show_alert=True)
        return

    await event.answer(text, reply_markup=subscribe_channel_kb(channel_chat_id()))


async def require_subscription(event: Message | CallbackQuery) -> bool:
    """Return True if the user may open booking / Mini App."""
    if not CHANNEL_SUBSCRIPTION_ENABLED:
        return True

    user = event.from_user
    if not user:
        return False

    # --- проверка подписки (активна при CHANNEL_SUBSCRIPTION_ENABLED = True) ---
    if await is_user_subscribed(event.bot, user.id):
        return True

    await reply_subscription_required(event)
    return False


def require_channel_subscription(
    handler: Callable[P, Awaitable[R]],
) -> Callable[P, Awaitable[R | None]]:
    """Decorator for handlers that open booking or Mini App."""

    @wraps(handler)
    async def wrapper(event: TelegramObject, *args: P.args, **kwargs: P.kwargs) -> R | None:
        if not isinstance(event, (Message, CallbackQuery)):
            return await handler(event, *args, **kwargs)

        if not await require_subscription(event):
            return None

        return await handler(event, *args, **kwargs)

    return wrapper
