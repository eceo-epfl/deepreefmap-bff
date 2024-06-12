from typing import Any
from fastapi import Depends, APIRouter, Request, HTTPException
from app.config import config
from app.utils import get_async_client, _reverse_proxy
import httpx
from uuid import UUID
from app.models.user import User
from app.models.token import DownloadToken
from app.auth import require_admin, get_user_info
from fastapi import BackgroundTasks
from fastapi.responses import StreamingResponse
import jwt
import datetime

router = APIRouter()


@router.delete("/kubernetes/jobs/{job_id}")
async def delete_job(
    job_id: str,
    client: httpx.AsyncClient = Depends(get_async_client),
    *,
    user: User = Depends(get_user_info),
) -> Any:
    """Delete a kubernetes job by ID"""

    res = await client.delete(
        f"{config.DEEPREEFMAP_API_URL}/v1/submissions/kubernetes/jobs/{job_id}",
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
    submission_id: UUID,
    reverse_proxy: Any = Depends(_reverse_proxy),
) -> Any:
    """Get a submission by id"""

    return reverse_proxy


@router.get("/{submission_id}/{filename}", response_model=DownloadToken)
async def get_submission_output_file_token(
    request: Request,
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

    # Get the resource to validate that it exists and the user has access
    is_admin = "admin" in user.realm_roles
    headers = {
        key.decode(): value.decode() for key, value in request.headers.raw
    }
    headers.update(  # Add user ID and roles to the headers
        {
            "User-ID": user.id,
            "User-Is-Admin": str(is_admin),
        }
    )
    req = client.build_request(
        "GET",
        f"{config.DEEPREEFMAP_API_URL}/v1/submissions/{submission_id}",
        headers=headers,
    )
    r = await client.send(req)

    if r.status_code != 200:
        raise HTTPException(
            status_code=r.status_code,
            detail=r.text,
        )

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
    reverse_proxy: Any = Depends(_reverse_proxy),
) -> Any:
    """Execute a submission by id"""

    return reverse_proxy


@router.get("")
async def get_submissions(
    reverse_proxy: Any = Depends(_reverse_proxy),
) -> Any:
    """Get all submissions"""

    return reverse_proxy


@router.post("")
async def create_submission(
    reverse_proxy: Any = Depends(_reverse_proxy),
) -> Any:
    """Creates an submission

    Creates a new submission with the given files
    """

    return reverse_proxy


@router.put("/{submission_id}")
async def update_submission(
    submission_id: UUID,
    reverse_proxy: Any = Depends(_reverse_proxy),
) -> Any:
    """ "Updates an submission by id"""

    return reverse_proxy


@router.delete("/{submission_id}")
async def delete_submission(
    submission_id: UUID,
    reverse_proxy: Any = Depends(_reverse_proxy),
) -> None:
    """Delete an submission by id"""

    return reverse_proxy
