"""Public service catalog for Mini App."""

from typing import Annotated

from fastapi import APIRouter, Depends

from api.schemas.service import ServiceOut
from api.services.supabase_client import SupabaseClient, get_supabase

router = APIRouter(prefix="/services", tags=["services"])


@router.get("", response_model=list[ServiceOut])
async def list_services(
    db: Annotated[SupabaseClient, Depends(get_supabase)],
) -> list[dict]:
    master = await db.get_master_profile()
    return await db.list_services(master["id"])
