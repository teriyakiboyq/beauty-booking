"""Generate available booking slots from master settings and existing appointments."""

from __future__ import annotations

import logging
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

logger = logging.getLogger(__name__)


def resolve_timezone(name: str) -> ZoneInfo:
    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError:
        logger.warning(
            "Timezone %r not found (install tzdata on Windows). Using UTC.",
            name,
        )
        return ZoneInfo("UTC")


def _parse_time(value: str | time) -> time:
    if isinstance(value, time):
        return value
    raw = str(value).strip()
    # Supabase TIME: "09:00:00" или "09:00"
    if "T" in raw:
        raw = raw.split("T", 1)[1][:8]
    parts = raw.split(":")
    hour = int(parts[0])
    minute = int(parts[1]) if len(parts) > 1 else 0
    return time(hour, minute)


def generate_slots(
    *,
    target_date: date,
    work_start: str | time,
    work_end: str | time,
    slot_duration_min: int,
    service_duration_min: int,
    timezone_name: str,
    busy_intervals: list[tuple[datetime, datetime]],
) -> list[dict]:
    """
    Return ISO start times where a service of given duration fits in the grid.
    busy_intervals: (start, end) aware datetimes (any TZ; compared in master TZ).
    """
    tz = resolve_timezone(timezone_name)
    start_t = _parse_time(work_start)
    end_t = _parse_time(work_end)
    day_start = datetime.combine(target_date, start_t, tzinfo=tz)
    day_end = datetime.combine(target_date, end_t, tzinfo=tz)

    if day_end <= day_start:
        logger.warning(
            "Invalid work window: work_start=%s work_end=%s → day_start=%s day_end=%s",
            work_start,
            work_end,
            day_start,
            day_end,
        )
        return []

    step = timedelta(minutes=int(slot_duration_min))
    service_delta = timedelta(minutes=int(service_duration_min))
    slots: list[dict] = []

    busy_local: list[tuple[datetime, datetime]] = []
    for busy_start, busy_end in busy_intervals:
        if busy_start.tzinfo is None:
            busy_start = busy_start.replace(tzinfo=timezone.utc)
        if busy_end.tzinfo is None:
            busy_end = busy_end.replace(tzinfo=timezone.utc)
        busy_local.append((busy_start.astimezone(tz), busy_end.astimezone(tz)))

    cursor = day_start
    iterations = 0
    while cursor + service_delta <= day_end:
        iterations += 1
        slot_end = cursor + service_delta
        overlaps = any(
            cursor < b_end and slot_end > b_start for b_start, b_end in busy_local
        )
        if not overlaps:
            slots.append(
                {
                    "start_time": cursor.astimezone(timezone.utc).isoformat(),
                    "end_time": slot_end.astimezone(timezone.utc).isoformat(),
                    "label_local": cursor.strftime("%H:%M"),
                }
            )
        cursor += step

    logger.debug(
        "generate_slots: date=%s window=%s..%s step=%s service=%s busy=%s "
        "iterations=%s slots=%s",
        target_date,
        day_start.strftime("%H:%M"),
        day_end.strftime("%H:%M"),
        slot_duration_min,
        service_duration_min,
        len(busy_local),
        iterations,
        len(slots),
    )
    return slots
