from typing import Union, Any
from fastapi import Depends, APIRouter, Query, Response
from app.config import config
from app.utils import get_async_client
import httpx
from uuid import UUID

router = APIRouter()


@router.get("/{sensor_id}")
async def get_sensor(
    client: httpx.AsyncClient = Depends(get_async_client),
    *,
    sensor_id: UUID,
) -> Any:
    res = await client.get(
        f"{config.SOIL_API_URL}/v1/sensors/{sensor_id}",
    )

    return res.json()


@router.get("")
async def get_sensors(
    response: Response,
    *,
    filter: str = Query(None),
    sort: str = Query(None),
    range: str = Query(None),
    client: httpx.AsyncClient = Depends(get_async_client),
) -> Any:
    print("sort", sort, "range", range, "filter", filter)
    res = await client.get(
        f"{config.SOIL_API_URL}/v1/sensors",
        params={"sort": sort, "range": range, "filter": filter},
    )
    response.headers["Access-Control-Expose-Headers"] = "Content-Range"
    response.headers["Content-Range"] = res.headers["Content-Range"]

    return res.json()
