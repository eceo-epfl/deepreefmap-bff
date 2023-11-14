from typing import Union, Any
from fastapi import Depends, APIRouter, Query, Response, Body
from app.config import config
from app.utils import get_async_client
import httpx
from uuid import UUID
from pydantic.types import Json

router = APIRouter()


@router.get("/{area_id}")
async def get_area(
    client: httpx.AsyncClient = Depends(get_async_client),
    *,
    area_id: UUID,
) -> Any:
    res = await client.get(
        f"{config.SOIL_API_URL}/v1/areas/{area_id}",
    )

    return res.json()


@router.get("")
async def get_areas(
    response: Response,
    *,
    filter: str = None,
    sort: str = None,
    range: str = None,
    client: httpx.AsyncClient = Depends(get_async_client),
) -> Any:
    # Fetch data from config.SOIL_API_URL/v1/areas/ and relay back to client

    res = await client.get(
        f"{config.SOIL_API_URL}/v1/areas",
        params={"sort": sort, "range": range, "filter": filter},
    )
    response.headers["Access-Control-Expose-Headers"] = "Content-Range"
    response.headers["Content-Range"] = res.headers["Content-Range"]
    print(res)
    return res.json()


@router.post("")
async def create_area(
    area: Any = Body(...),
    client: httpx.AsyncClient = Depends(get_async_client),
) -> Any:
    """Creates an area"""
    print(area)
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
) -> Any:
    res = await client.put(
        f"{config.SOIL_API_URL}/v1/areas/{area_id}", json=area
    )

    return res.json()


@router.delete("/{area_id}")
async def delete_area(
    area_id: UUID,
    client: httpx.AsyncClient = Depends(get_async_client),
) -> None:
    """Delete an area by id"""
    res = await client.delete(f"{config.SOIL_API_URL}/v1/areas/{area_id}")

    return res.json()
