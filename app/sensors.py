from typing import Union, Any
from fastapi import Depends, APIRouter, Query, Response
from app.config import config
from app.utils import get_async_client
import httpx
from uuid import UUID

router = APIRouter()


# @router.get("/{area_id}")
# async def get_area(
#     client: httpx.AsyncClient = Depends(get_async_client),
#     *,
#     area_id: UUID,
#     sort: list[str] | None = None,
#     range: list[int] | None = None,
#     filter: dict[str, str] | None = None,
# ) -> Any:
#     res = await client.get(
#         f"{config.SOIL_API_URL}/v1/areas/{area_id}",
#         params={"sort": sort, "range": range, "filter": filter},
#     )

#     return res.json()


@router.get("")
async def get_sensors(
    client: httpx.AsyncClient = Depends(get_async_client),
    *,
    sort: list[str] | None = None,
    range: list[int] | None = None,
    filter: str | None = None,
    response: Response,
) -> Any:
    res = await client.get(
        f"{config.SOIL_API_URL}/v1/sensors",
        params={"sort": sort, "range": range, "filter": filter},
    )
    print(res.headers["Content-Range"])
    response.headers["Access-Control-Expose-Headers"] = "Content-Range"
    response.headers["Content-Range"] = res.headers["Content-Range"]

    return res.json()
