"""
DEPRECATED: subscription is checked in bot/utils/subscription.py
on open_booking callback only, not via global middleware.
"""

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware, Bot
from aiogram.enums import ChatMemberStatus
from aiogram.types import Message, TelegramObject

from bot.config import get_bot_settings
from bot.keyboards.inline import subscribe_channel_kb

ALLOWED_STATUSES = {
    ChatMemberStatus.MEMBER,
    ChatMemberStatus.ADMINISTRATOR,
    ChatMemberStatus.CREATOR,
}


class ChannelSubscribeMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        settings = get_bot_settings()
        channel = settings.required_channel
        if not channel:
            return await handler(event, data)

        if not isinstance(event, Message) or not event.from_user:
            return await handler(event, data)

        bot: Bot = data["bot"]
        user_id = event.from_user.id

        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
        except Exception:
            await event.answer(
                "Не удалось проверить подписку на канал. Попробуйте позже.",
            )
            return None

        if member.status not in ALLOWED_STATUSES:
            await event.answer(
                "Для записи нужно подписаться на наш канал:",
                reply_markup=subscribe_channel_kb(channel),
            )
            return None

        return await handler(event, data)
