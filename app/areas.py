from typing import Any
from fastapi import Depends, APIRouter, Response, Body, Request
from app.config import config
from app.utils import get_async_client
import httpx
from uuid import UUID
from app.models.user import User
from app.auth import require_admin

router = APIRouter()


@router.get("/{area_id}")
async def get_area(
    client: httpx.AsyncClient = Depends(get_async_client),
    *,
    area_id: UUID,
) -> Any:
    """Get an area by id"""

    res = await client.get(
        f"{config.SOIL_API_URL}/v1/areas/{area_id}",
    )

    return res.json()


@router.get("")
async def get_areas(
    request: Request,
    response: Response,
    *,
    filter: str = None,
    sort: str = None,
    range: str = None,
    client: httpx.AsyncClient = Depends(get_async_client),
) -> Any:
    """Get all areas"""
    res = await client.get(
        f"{config.SOIL_API_URL}/v1/areas",
        params={"sort": sort, "range": range, "filter": filter},
    )
    response.headers["Access-Control-Expose-Headers"] = "Content-Range"
    response.headers["Content-Range"] = res.headers["Content-Range"]

    return res.json()


@router.post("")
async def create_area(
    area: Any = Body(...),
    client: httpx.AsyncClient = Depends(get_async_client),
    user: User = Depends(require_admin),
) -> Any:
    """Creates an area"""

    res = await client.post(
        f"{config.SOIL_API_URL}/v1/areas",
        json=area,
    )

    return res.json()


@router.put("/{area_id}")
async def update_area(
    area_id: UUID,
    area: Any = Body(...),
    client: httpx.AsyncClient = Depends(get_async_client),
    user: User = Depends(require_admin),
) -> Any:
    """ "Updates an area by id"""

    res = await client.put(
        f"{config.SOIL_API_URL}/v1/areas/{area_id}", json=area
    )

    return res.json()


@router.delete("/{area_id}")
async def delete_area(
    area_id: UUID,
    client: httpx.AsyncClient = Depends(get_async_client),
    user: User = Depends(require_admin),
) -> None:
    """Delete an area by id"""

    res = await client.delete(f"{config.SOIL_API_URL}/v1/areas/{area_id}")

    return res.json()
