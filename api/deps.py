"""FastAPI dependencies: Telegram initData validation and user resolution."""

from __future__ import annotations

import hashlib
import hmac
import json
from typing import Annotated
from urllib.parse import parse_qsl

from fastapi import Depends, Header, HTTPException, status

from api.config import Settings, get_settings
from api.services.supabase_client import SupabaseClient, get_supabase


def _validate_init_data(init_data: str, bot_token: str) -> dict:
    """
    Verify Telegram WebApp initData per official algorithm.
    https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
    """
    pairs = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = pairs.pop("hash", None)
    if not received_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing hash in init data",
        )

    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(pairs.items())
    )
    secret_key = hmac.new(
        b"WebAppData",
        bot_token.encode(),
        hashlib.sha256,
    ).digest()
    calculated = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(calculated, received_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid init data signature",
        )

    user_raw = pairs.get("user")
    if not user_raw:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing user in init data",
        )
    return json.loads(user_raw)


async def get_telegram_user(
    x_telegram_init_data: Annotated[str | None, Header()] = None,
    settings: Settings = Depends(get_settings),
) -> dict:
    if not x_telegram_init_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-Telegram-Init-Data header required",
        )
    return _validate_init_data(x_telegram_init_data, settings.bot_token)


async def get_current_profile(
    tg_user: Annotated[dict, Depends(get_telegram_user)],
    db: Annotated[SupabaseClient, Depends(get_supabase)],
) -> dict:
    """Find or create client profile by Telegram id."""
    return await db.get_or_create_profile(
        telegram_id=tg_user["id"],
        full_name=tg_user.get("first_name", "") + (
            f" {tg_user['last_name']}" if tg_user.get("last_name") else ""
        ),
        username=tg_user.get("username"),
    )
