from typing import Any
from fastapi import Depends, APIRouter, Query, Response, Body
from fastapi.responses import StreamingResponse
from app.config import config
from app.utils import get_async_client, _reverse_proxy
import httpx
from uuid import UUID
from app.models.user import User
from app.auth import require_admin, get_user_info
from fastapi import (
    Header,
    HTTPException,
    Request,
    status,
)
from starlette.background import BackgroundTask
from fastapi.responses import PlainTextResponse


router = APIRouter()

MAX_FILE_SIZE = 1024 * 1024 * 1024 * 4  # = 6GB
MAX_REQUEST_BODY_SIZE = MAX_FILE_SIZE + 1024


class MaxBodySizeException(Exception):
    def __init__(self, body_len: str):
        self.body_len = body_len


class MaxBodySizeValidator:
    def __init__(self, max_size: int):
        self.body_len = 0
        self.max_size = max_size

    def __call__(self, chunk: bytes):
        self.body_len += len(chunk)
        if self.body_len > self.max_size:
            raise MaxBodySizeException(body_len=self.body_len)


@router.post("", response_class=PlainTextResponse)
async def upload_file(
    reverse_proxy: Any = Depends(_reverse_proxy),
) -> Any:
    """Creates an object"""

    return reverse_proxy


@router.patch("")
async def upload_chunk(
    request: Request,
    patch: str = Query(...),
    client: httpx.AsyncClient = Depends(get_async_client),
    admin_user: User = Depends(require_admin),
) -> Any:
    """Creates an object

    Forwards the file to the API with multipart form data encoding

    """
    try:

        URL = f"{config.DEEPREEFMAP_API_URL}/v1/objects?patch={patch}"
        req = client.build_request(
            "PATCH",
            URL,
            headers=request.headers.raw,
            timeout=None,
            content=request.stream(),
        )
        r = await client.send(req, stream=True)
        return StreamingResponse(
            r.aiter_raw(),
            status_code=r.status_code,
            headers=r.headers,
            background=BackgroundTask(r.aclose),
        )

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.response.text,
        )


@router.head("")
async def check_uploaded_chunks(
    request: Request,
    patch: str = Query(...),
    client: httpx.AsyncClient = Depends(get_async_client),
):
    try:
        URL = f"{config.DEEPREEFMAP_API_URL}/v1/objects?patch={patch}"
        req = client.build_request(
            "HEAD",
            URL,
            headers=request.headers.raw,
            content=request.stream(),
        )
        r = await client.send(req, stream=True)
        return StreamingResponse(
            r.aiter_raw(),
            status_code=r.status_code,
            headers=r.headers,
            background=BackgroundTask(r.aclose),
        )

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.response.text,
        )


@router.get("/{object_id}")
async def get_object(
    object_id: UUID,
    reverse_proxy: Any = Depends(_reverse_proxy),
) -> Any:
    """Get a object by id"""

    return reverse_proxy


@router.get("")
async def get_objects(
    reverse_proxy: Any = Depends(_reverse_proxy),
) -> Any:
    """Get all objects"""

    return reverse_proxy


@router.post("/{object_id}")
async def regenerate_statistics(
    object_id: UUID,
    client: httpx.AsyncClient = Depends(get_async_client),
    admin_user: User = Depends(require_admin),
) -> Any:
    """Regenerates the video statistics for the object"""

    res = await client.post(
        f"{config.DEEPREEFMAP_API_URL}/v1/objects/{object_id}"
    )

    return res.json()


@router.put("/{object_id}")
async def update_object(
    object_id: UUID,
    reverse_proxy: Any = Depends(_reverse_proxy),
) -> Any:
    """ "Updates an object by id"""

    return reverse_proxy


@router.delete("/{object_id}")
async def delete_object(
    object_id: UUID,
    reverse_proxy: Any = Depends(_reverse_proxy),
) -> None:
    """Delete an object by id"""

    return reverse_proxy
