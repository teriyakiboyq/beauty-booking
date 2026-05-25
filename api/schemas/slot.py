from pydantic import BaseModel, Field


class SlotOut(BaseModel):
    start_time: str
    end_time: str
    label_local: str


class SlotsQuery(BaseModel):
    service_id: str
    date: str = Field(description="YYYY-MM-DD")
