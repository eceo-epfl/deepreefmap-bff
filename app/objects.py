from typing import Any
from fastapi import Depends, APIRouter, Query, Response, Body
from app.config import config
from app.utils import get_async_client
import httpx
from uuid import UUID
from app.models.user import User
from app.auth import require_admin, get_user_info
from fastapi import File, UploadFile

router = APIRouter()


@router.get("/{object_id}")
async def get_object(
    client: httpx.AsyncClient = Depends(get_async_client),
    *,
    object_id: UUID,
    user: User = Depends(get_user_info),
) -> Any:
    """Get a object by id"""

    res = await client.get(
        f"{config.DEEPREEFMAP_API_URL}/v1/objects/{object_id}",
    )

    return res.json()


@router.get("")
async def get_objects(
    response: Response,
    *,
    filter: str = Query(None),
    sort: str = Query(None),
    range: str = Query(None),
    client: httpx.AsyncClient = Depends(get_async_client),
    user: User = Depends(get_user_info),
) -> Any:
    """Get all objects"""

    res = await client.get(
        f"{config.DEEPREEFMAP_API_URL}/v1/objects",
        params={"sort": sort, "range": range, "filter": filter},
    )
    response.headers["Access-Control-Expose-Headers"] = "Content-Range"
    response.headers["Content-Range"] = res.headers["Content-Range"]

    return res.json()


@router.post("")
async def create_object(
    file: UploadFile = File(...),
    *,
    client: httpx.AsyncClient = Depends(get_async_client),
    admin_user: User = Depends(require_admin),
) -> Any:
    """Creates an object

    Forwards the file to the API with multipart form data encoding
    """

    file_streams = []
    file_streams.append(("file", (file.filename, file.file)))

    res = await client.post(
        f"{config.DEEPREEFMAP_API_URL}/v1/objects/inputs",
        files=file_streams,
        timeout=None,
    )
    return res.json()


@router.put("/{object_id}")
async def update_object(
    object_id: UUID,
    object: Any = Body(...),
    client: httpx.AsyncClient = Depends(get_async_client),
    admin_user: User = Depends(require_admin),
) -> Any:
    """ "Updates an object by id"""

    res = await client.put(
        f"{config.DEEPREEFMAP_API_URL}/v1/objects/{object_id}",
        json=object,
    )

    return res.json()


@router.delete("/{object_id}")
async def delete_object(
    object_id: UUID,
    client: httpx.AsyncClient = Depends(get_async_client),
    admin_user: User = Depends(require_admin),
) -> None:
    """Delete an object by id"""

    res = await client.delete(
        f"{config.DEEPREEFMAP_API_URL}/v1/objects/{object_id}"
    )

    return res.json()
