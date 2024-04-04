from typing import Any
from fastapi import Depends, APIRouter, Query, Response, Body, HTTPException
from app.config import config
from app.utils import get_async_client
import httpx
from uuid import UUID
from app.models.user import User
from app.models.token import DownloadToken
from app.auth import require_admin, get_user_info
from fastapi import File, UploadFile, BackgroundTasks
from fastapi.responses import StreamingResponse
from itsdangerous import URLSafeSerializer
import jwt
import datetime

router = APIRouter()


@router.get("/kubernetes/jobs")
async def get_jobs(
    client: httpx.AsyncClient = Depends(get_async_client),
    *,
    user: User = Depends(get_user_info),
) -> Any:
    """Get all kubernetes jobs in the namespace"""

    res = await client.get(
        f"{config.DEEPREEFMAP_API_URL}/v1/submissions/kubernetes/jobs",
    )

    return res.json()


@router.get("/download/{token}", response_class=StreamingResponse)
async def get_submission_output_file(
    client: httpx.AsyncClient = Depends(get_async_client),
    *,
    token: str,
    background_tasks: BackgroundTasks,
) -> StreamingResponse:
    """With the given submission ID and filename, returns the file from S3

    These details are embedded inside the token given to the user in the
    get_submission_output_file_token() endpoint at:

    `GET /submissions/{submission_id}/{filename}`
    """

    # Decode the token from the user
    decoded = jwt.decode(
        token, config.SERIALIZER_SECRET_KEY, algorithms=["HS256"]
    )

    submission_id, filename, exp = decoded.values()
    print("EXP", exp, datetime.datetime.fromtimestamp(exp))

    if datetime.datetime.fromtimestamp(
        exp, tz=datetime.timezone.utc
    ) < datetime.datetime.now(datetime.UTC):
        raise HTTPException(
            status_code=401,
            detail="Token has expired",
        )

    req = client.build_request(
        "GET",
        f"{config.DEEPREEFMAP_API_URL}/v1/submissions/"
        f"{submission_id}/{filename}",
    )
    r = await client.send(req, stream=True)

    return StreamingResponse(
        content=r.aiter_bytes(),
        media_type="application/octet-stream",
        background=background_tasks.add_task(r.aclose),
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


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


@router.get("/{submission_id}/{filename}", response_model=DownloadToken)
async def get_submission_output_file_token(
    client: httpx.AsyncClient = Depends(get_async_client),
    *,
    submission_id: UUID,
    user: User = Depends(get_user_info),
    filename: str,
    background_tasks: BackgroundTasks,
) -> DownloadToken:
    """With the given ID and filename, returns a token to download the file

    Necessary endpoint to allow the user to download the file but also
    providing some security by forcing authentication first.

    Token expires at a set time defined by config.SERIALIZER_EXPIRY_HOURS
    """

    payload = {
        "submission_id": str(submission_id),
        "filename": filename,
        "exp": datetime.datetime.now(datetime.UTC)
        + datetime.timedelta(hours=config.SERIALIZER_EXPIRY_HOURS),
    }
    token = jwt.encode(
        payload, config.SERIALIZER_SECRET_KEY, algorithm="HS256"
    )

    return DownloadToken(token=token)


@router.post("/{submission_id}/execute", response_model=Any)
async def execute_submission(
    submission_id: UUID,
    client: httpx.AsyncClient = Depends(get_async_client),
    admin_user: User = Depends(require_admin),
) -> Any:
    """Execute a submission by id"""

    res = await client.post(
        f"{config.DEEPREEFMAP_API_URL}/v1/submissions/{submission_id}/execute",
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
    submission: Any = Body(...),
    client: httpx.AsyncClient = Depends(get_async_client),
    admin_user: User = Depends(require_admin),
) -> Any:
    """Creates an submission

    Creates a new submission with the given files
    """

    res = await client.post(
        f"{config.DEEPREEFMAP_API_URL}/v1/submissions",
        json=submission,
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
