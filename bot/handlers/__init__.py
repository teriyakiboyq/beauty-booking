"""Register all routers on dispatcher."""

from aiogram import Dispatcher

from bot.handlers import start


def register_handlers(dp: Dispatcher) -> None:
    dp.include_router(start.router)
