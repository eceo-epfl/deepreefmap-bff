from typing import Any
from fastapi import Depends, APIRouter, Query, Response, Body
from fastapi.responses import StreamingResponse
from app.config import config
from app.utils import get_async_client
import httpx
from uuid import UUID
from app.models.user import User
from app.auth import require_admin, get_user_info
from fastapi import (
    UploadFile,
    Header,
    HTTPException,
    Request,
    File,
    status,
)
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import FileTarget, ValueTarget
from streaming_form_data.validators import MaxSizeValidator
from starlette.requests import ClientDisconnect
from starlette.background import BackgroundTask
import streaming_form_data
import os


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


@router.post("/upload")
async def upload_file(
    upload_length: str = Header(..., alias="Upload-Length"),
    content_type: str = Header(..., alias="Content-Type"),
    *,
    client: httpx.AsyncClient = Depends(get_async_client),
    user: User = Depends(get_user_info),
) -> Any:
    try:
        res = await client.post(
            f"{config.DEEPREEFMAP_API_URL}/v1/objects/upload",
            headers={
                "Upload-Length": upload_length,
                "Content-Type": content_type,
            },
        )
        res.raise_for_status()

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.response.text,
        )
    return res.json()


@router.patch("/upload")
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

        URL = f"{config.DEEPREEFMAP_API_URL}/v1/objects/upload?patch={patch}"
        req = client.build_request(
            "PATCH",
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


@router.head("/upload")
async def check_uploaded_chunks(
    request: Request,
    patch: str = Query(...),
    client: httpx.AsyncClient = Depends(get_async_client),
):
    try:
        URL = f"{config.DEEPREEFMAP_API_URL}/v1/objects/upload?patch={patch}"
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


@router.delete("/upload")
async def delete_upload(
    request: Request,
    client: httpx.AsyncClient = Depends(get_async_client),
):
    try:
        URL = f"{config.DEEPREEFMAP_API_URL}/v1/objects/upload"
        req = client.build_request(
            "DELETE",
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
