"""Create and list user appointments."""

from datetime import datetime, timedelta
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from api.deps import get_current_profile
from api.schemas.appointment import AppointmentCreate, AppointmentOut
from api.services.supabase_client import SupabaseClient, get_supabase
from shared.enums import AppointmentStatus

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.get("/my", response_model=list[AppointmentOut])
async def my_appointments(
    profile: Annotated[dict, Depends(get_current_profile)],
    db: Annotated[SupabaseClient, Depends(get_supabase)],
) -> list[dict]:
    return await db.list_user_appointments(profile["id"])


@router.post("", response_model=AppointmentOut, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    body: AppointmentCreate,
    profile: Annotated[dict, Depends(get_current_profile)],
    db: Annotated[SupabaseClient, Depends(get_supabase)],
) -> dict:
    master = await db.get_master_profile()
    service = await db.get_service(body.service_id)
    if not service or str(service["master_id"]) != str(master["id"]):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")

    settings = await db.get_master_settings(master["id"])
    end_time = body.start_time + timedelta(minutes=service["duration"])

    initial_status = (
        AppointmentStatus.PENDING
        if settings.get("require_confirmation")
        else AppointmentStatus.CONFIRMED
    )

    payload = {
        "user_id": profile["id"],
        "service_id": str(body.service_id),
        "master_id": master["id"],
        "start_time": body.start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "status": initial_status,
    }

    try:
        return await db.create_appointment(payload)
    except HTTPException as exc:
        if "overlap" in str(exc.detail).lower() or "conflict" in str(exc.detail).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This time slot is no longer available",
            ) from exc
        raise
