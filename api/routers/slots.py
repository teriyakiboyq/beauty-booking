"""Available time slots for booking calendar."""

import logging
from datetime import date, datetime, time, timedelta, timezone
from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.schemas.slot import SlotOut
from api.services.slot_generator import generate_slots, resolve_timezone
from api.services.supabase_client import SupabaseClient, get_supabase

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/slots", tags=["slots"])


def _parse_appointment_dt(raw: str) -> datetime:
    value = raw.replace("Z", "+00:00")
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


@router.get("", response_model=list[SlotOut])
async def get_slots(
    service_id: Annotated[UUID, Query()],
    day: Annotated[date, Query(alias="date", description="YYYY-MM-DD")],
    db: Annotated[SupabaseClient, Depends(get_supabase)],
) -> list[dict]:
    logger.info(
        "GET /slots service_id=%s date=%s",
        service_id,
        day.isoformat(),
    )

    master = await db.get_master_profile()
    logger.info("Master profile id=%s telegram_id=%s", master["id"], master.get("telegram_id"))

    service = await db.get_service(service_id)
    if not service or str(service["master_id"]) != str(master["id"]):
        logger.warning("Service %s not found for master %s", service_id, master["id"])
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")

    logger.info(
        "Service: name=%s duration=%s min price=%s",
        service.get("name"),
        service.get("duration"),
        service.get("price"),
    )

    settings = await db.get_master_settings(master["id"])
    tz_name = settings.get("timezone", "UTC")
    tz = resolve_timezone(tz_name)

    logger.info(
        "Master settings: work_start=%s work_end=%s slot_duration=%s timezone=%s",
        settings.get("work_start"),
        settings.get("work_end"),
        settings.get("slot_duration"),
        tz_name,
    )

    day_start = datetime.combine(day, time.min, tzinfo=tz)
    day_end = day_start + timedelta(days=1)
    day_start_utc = day_start.astimezone(timezone.utc).isoformat()
    day_end_utc = day_end.astimezone(timezone.utc).isoformat()

    logger.info("Day bounds (UTC): %s .. %s", day_start_utc, day_end_utc)

    appointments = await db.list_appointments_for_day(
        master["id"],
        day_start_utc,
        day_end_utc,
    )
    appointments = appointments or []

    logger.info("Appointments overlapping day: count=%s", len(appointments))
    for row in appointments:
        logger.info(
            "  busy: %s — %s status=%s",
            row.get("start_time"),
            row.get("end_time"),
            row.get("status"),
        )

    busy: list[tuple[datetime, datetime]] = []
    for row in appointments:
        busy.append(
            (
                _parse_appointment_dt(row["start_time"]),
                _parse_appointment_dt(row["end_time"]),
            )
        )

    slots = generate_slots(
        target_date=day,
        work_start=settings["work_start"],
        work_end=settings["work_end"],
        slot_duration_min=int(settings["slot_duration"]),
        service_duration_min=int(service["duration"]),
        timezone_name=tz_name,
        busy_intervals=busy,
    )

    logger.info("Returning %s slot(s)", len(slots))
    if slots:
        logger.info("  first=%s last=%s", slots[0]["label_local"], slots[-1]["label_local"])
    else:
        logger.warning(
            "No slots generated. Check work_start/work_end, service duration (%s min), "
            "and whether all times are blocked by appointments.",
            service.get("duration"),
        )

    return slots
