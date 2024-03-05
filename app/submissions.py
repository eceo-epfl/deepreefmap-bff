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


@router.get("/{submission_id}")
async def get_submission(
    client: httpx.AsyncClient = Depends(get_async_client),
    *,
    submission_id: UUID,
    user: User = Depends(get_user_info),
) -> Any:
    """Get a submission by id"""

    res = await client.get(
        f"{config.DEEPREEFMAP_API_URL}/v1/submissions/{submission_id}",
    )

    return res.json()


@router.get("")
async def get_submissions(
    response: Response,
    *,
    filter: str = Query(None),
    sort: str = Query(None),
    range: str = Query(None),
    client: httpx.AsyncClient = Depends(get_async_client),
    user: User = Depends(get_user_info),
) -> Any:
    """Get all submissions"""

    res = await client.get(
        f"{config.DEEPREEFMAP_API_URL}/v1/submissions",
        params={"sort": sort, "range": range, "filter": filter},
    )
    response.headers["Access-Control-Expose-Headers"] = "Content-Range"
    response.headers["Content-Range"] = res.headers["Content-Range"]

    return res.json()


@router.post("")
async def create_submission(
    files: list[UploadFile] = File(...),
    *,
    client: httpx.AsyncClient = Depends(get_async_client),
    admin_user: User = Depends(require_admin),
) -> Any:
    """Creates an submission

    Forwards the file to the API with multipart form data encoding
    """

    file_streams = []
    for file in files:
        # Multiple multipart files can be sent with the same key
        # https://github.com/encode/httpx/pull/891
        file_streams.append(("files", (file.filename, file.file)))

    res = await client.post(
        f"{config.DEEPREEFMAP_API_URL}/v1/submissions",
        files=file_streams,
    )
    return res.json()


@router.put("/{submission_id}")
async def update_submission(
    submission_id: UUID,
    submission: Any = Body(...),
    client: httpx.AsyncClient = Depends(get_async_client),
    admin_user: User = Depends(require_admin),
) -> Any:
    """ "Updates an submission by id"""

    res = await client.put(
        f"{config.DEEPREEFMAP_API_URL}/v1/submissions/{submission_id}",
        json=submission,
    )

    return res.json()


@router.delete("/{submission_id}")
async def delete_submission(
    submission_id: UUID,
    client: httpx.AsyncClient = Depends(get_async_client),
    admin_user: User = Depends(require_admin),
) -> None:
    """Delete an submission by id"""

    res = await client.delete(
        f"{config.DEEPREEFMAP_API_URL}/v1/submissions/{submission_id}"
    )

    return res.json()
