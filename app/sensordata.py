from typing import Any
from fastapi import Depends, APIRouter, Query, Response, Body
from app.config import config
from app.utils import get_async_client
import httpx
from uuid import UUID
from app.models.user import User
from app.auth import require_admin

router = APIRouter()


@router.get("/{sensordata_id}")
async def get_sensordata(
    client: httpx.AsyncClient = Depends(get_async_client),
    *,
    sensordata_id: UUID,
) -> Any:
    """Get an individual sensordata record by id"""

    res = await client.get(
        f"{config.SOIL_API_URL}/v1/sensors/data/{sensordata_id}",
    )

    return res.json()


@router.get("")
async def get_all_sensordata(
    response: Response,
    *,
    filter: str = Query(None),
    sort: str = Query(None),
    range: str = Query(None),
    client: httpx.AsyncClient = Depends(get_async_client),
) -> Any:
    """Get all sensordata"""

    res = await client.get(
        f"{config.SOIL_API_URL}/v1/sensors/data",
        params={"sort": sort, "range": range, "filter": filter},
    )
    response.headers["Access-Control-Expose-Headers"] = "Content-Range"
    response.headers["Content-Range"] = res.headers["Content-Range"]

    return res.json()


@router.post("")
async def create_sensordata(
    sensordata: Any = Body(...),
    client: httpx.AsyncClient = Depends(get_async_client),
    user: User = Depends(require_admin),
) -> Any:
    """Creates an sensordata record"""

    res = await client.post(
        f"{config.SOIL_API_URL}/v1/sensors/data",
        json=sensordata,
    )

    return res.json()


@router.put("/{sensordata_id}")
async def update_sensordata(
    sensordata_id: UUID,
    sensordata: Any = Body(...),
    client: httpx.AsyncClient = Depends(get_async_client),
    user: User = Depends(require_admin),
) -> Any:
    """Updates an individual sensordata record by id"""

    res = await client.put(
        f"{config.SOIL_API_URL}/v1/sensors/data/{sensordata_id}",
        json=sensordata,
    )

    return res.json()


@router.delete("/{sensordata_id}")
async def delete_sensor(
    sensordata_id: UUID,
    client: httpx.AsyncClient = Depends(get_async_client),
    user: User = Depends(require_admin),
) -> None:
    """Delete an individual sensordata record by id"""

    res = await client.delete(
        f"{config.SOIL_API_URL}/v1/sensors/data/{sensordata_id}"
    )

    return res.json()
