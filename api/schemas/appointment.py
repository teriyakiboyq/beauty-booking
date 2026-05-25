from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from shared.enums import AppointmentStatus


class AppointmentCreate(BaseModel):
    service_id: UUID
    start_time: datetime = Field(description="ISO 8601 UTC start time")


class AppointmentOut(BaseModel):
    id: UUID
    service_id: UUID
    start_time: datetime
    end_time: datetime
    status: AppointmentStatus
