"""Start command and booking entry (subscription check on open only)."""

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

from bot.keyboards.inline import open_booking_entry_kb, webapp_booking_kb
from bot.utils.subscription import require_channel_subscription

# from bot.keyboards.inline import subscribe_channel_kb
# from bot.utils.subscription import (
#     CHANNEL_SUBSCRIPTION_ENABLED,
#     channel_chat_id,
#     channel_username_display,
#     is_user_subscribed,
# )

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Greeting only — no channel check."""
    await message.answer(
        "Привет! 👋\n\n"
        "Нажмите кнопку ниже, чтобы открыть запись к мастеру.",
        reply_markup=open_booking_entry_kb(),
    )


@router.callback_query(F.data == "open_booking")
@require_channel_subscription
async def open_booking(callback: CallbackQuery) -> None:
    """Show Mini App (subscription check when CHANNEL_SUBSCRIPTION_ENABLED)."""
    if not callback.message:
        await callback.answer()
        return

    await callback.message.edit_text(
        "Откройте мини-приложение и выберите услугу и время:",
        reply_markup=webapp_booking_kb(),
    )
    await callback.answer()


# TODO: раскомментировать вместе с CHANNEL_SUBSCRIPTION_ENABLED = True в subscription.py
# @router.callback_query(F.data == "check_sub")
# async def check_subscription_after_join(callback: CallbackQuery) -> None:
#     """Re-check subscription after user tapped «Я подписался»."""
#     if not callback.from_user or not callback.message:
#         await callback.answer()
#         return
#
#     if not await is_user_subscribed(callback.bot, callback.from_user.id):
#         await callback.answer("Подписка не найдена", show_alert=True)
#         await callback.message.answer(
#             f"Для бронирования нужно быть подписанным на {channel_username_display()}",
#             reply_markup=subscribe_channel_kb(channel_chat_id()),
#         )
#         return
#
#     await callback.message.edit_text(
#         "Спасибо за подписку! Откройте запись:",
#         reply_markup=webapp_booking_kb(),
#     )
#     await callback.answer()
