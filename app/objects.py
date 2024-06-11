from typing import Any
from fastapi import Depends, APIRouter, Query
from app.utils import get_async_client, _reverse_proxy
import httpx
from uuid import UUID
from app.models.user import User
from app.auth import get_user_info
from fastapi import Request
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
    user: User = Depends(get_user_info),
    reverse_proxy: Any = Depends(_reverse_proxy),
) -> Any:
    """Creates an object

    Forwards the file to the API with multipart form data encoding

    """

    return reverse_proxy


@router.head("")
async def check_uploaded_chunks(
    reverse_proxy: Any = Depends(_reverse_proxy),
):
    """Check the uploaded chunks"""

    return reverse_proxy


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
    # client: httpx.AsyncClient = Depends(get_async_client),
    reverse_proxy: Any = Depends(_reverse_proxy),
) -> Any:
    """Regenerates the video statistics for the object"""

    return reverse_proxy


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
