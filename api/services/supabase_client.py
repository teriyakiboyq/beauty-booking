"""Async HTTP client for Supabase PostgREST API."""

from __future__ import annotations

from functools import lru_cache
from typing import Any
from uuid import UUID

import httpx
from fastapi import HTTPException, status

from api.config import Settings, get_settings
from shared.enums import AppointmentStatus, UserRole


class SupabaseClient:
    def __init__(self, url: str, key: str, master_telegram_id: int) -> None:
        self._base = url.rstrip("/") + "/rest/v1"
        self._key = key
        self._master_telegram_id = master_telegram_id
        self._headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict | None = None,
        json: Any = None,
    ) -> Any:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method,
                f"{self._base}{path}",
                headers=self._headers,
                params=params,
                json=json,
            )
        if response.status_code >= 400:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Supabase error: {response.text}",
            )
        if response.status_code == 204 or not response.content:
            return None
        return response.json()

    async def get_master_profile(self) -> dict:
        rows = await self._request(
            "GET",
            "/profiles",
            params={
                "telegram_id": f"eq.{self._master_telegram_id}",
                "role": f"eq.{UserRole.MASTER}",
                "limit": "1",
            },
        )
        if not rows:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Master profile not configured in database",
            )
        return rows[0]

    async def get_or_create_profile(
        self,
        *,
        telegram_id: int,
        full_name: str,
        username: str | None,
    ) -> dict:
        existing = await self._request(
            "GET",
            "/profiles",
            params={"telegram_id": f"eq.{telegram_id}", "limit": "1"},
        )
        if existing:
            return existing[0]

        created = await self._request(
            "POST",
            "/profiles",
            json={
                "telegram_id": telegram_id,
                "full_name": full_name.strip() or None,
                "username": username,
                "role": UserRole.CLIENT,
            },
        )
        return created[0]

    async def list_services(self, master_id: UUID) -> list[dict]:
        return await self._request(
            "GET",
            "/services",
            params={
                "master_id": f"eq.{master_id}",
                "is_active": "eq.true",
                "order": "sort_order.asc",
            },
        )

    async def get_service(self, service_id: UUID) -> dict | None:
        rows = await self._request(
            "GET",
            "/services",
            params={"id": f"eq.{service_id}", "limit": "1"},
        )
        return rows[0] if rows else None

    async def get_master_settings(self, master_id: UUID) -> dict:
        rows = await self._request(
            "GET",
            "/master_settings",
            params={"master_id": f"eq.{master_id}", "limit": "1"},
        )
        if not rows:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Master settings not configured",
            )
        return rows[0]

    async def list_appointments_for_day(
        self,
        master_id: UUID,
        day_start_iso: str,
        day_end_iso: str,
    ) -> list[dict]:
        # Appointments overlapping the day: start < day_end AND end > day_start
        rows = await self._request(
            "GET",
            "/appointments",
            params={
                "master_id": f"eq.{master_id}",
                "or": f"(status.eq.{AppointmentStatus.PENDING},status.eq.{AppointmentStatus.CONFIRMED})",
                "start_time": f"lt.{day_end_iso}",
                "end_time": f"gt.{day_start_iso}",
                "order": "start_time.asc",
            },
        )
        return rows if rows else []

    async def create_appointment(self, payload: dict) -> dict:
        result = await self._request("POST", "/appointments", json=payload)
        return result[0] if isinstance(result, list) else result

    async def list_user_appointments(self, user_id: UUID) -> list[dict]:
        return await self._request(
            "GET",
            "/appointments",
            params={
                "user_id": f"eq.{user_id}",
                "order": "start_time.desc",
                "limit": "20",
            },
        )


@lru_cache
def get_supabase() -> SupabaseClient:
    settings = get_settings()
    return SupabaseClient(
        settings.supabase_url,
        settings.supabase_service_role_key,
        settings.master_telegram_id,
    )
