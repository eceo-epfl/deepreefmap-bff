from typing import Any
from fastapi import Depends, APIRouter, Query, Response, Body
from app.config import config
from app.utils import get_async_client
import httpx
from uuid import UUID
from app.models.user import User
from app.auth import require_admin, get_user_info

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
        f"{config.ECEO_API_URL}/v1/deepreef/submissions/{submission_id}",
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

    print(user)
    res = await client.get(
        f"{config.ECEO_API_URL}/v1/deepreef/submissions",
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
    """Creates an submission"""

    res = await client.post(
        f"{config.ECEO_API_URL}/v1/deepreef/submissions",
        json=submission,
    )

    return res.json()


@router.post("")
async def create_many_submissions(
    submission: Any = Body(...),
    client: httpx.AsyncClient = Depends(get_async_client),
    admin_user: User = Depends(require_admin),
) -> Any:
    """Creates an submission"""

    res = await client.post(
        f"{config.ECEO_API_URL}/v1/deepreef/submissions/many",
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
        f"{config.ECEO_API_URL}/v1/deepreef/submissions/{submission_id}",
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
        f"{config.ECEO_API_URL}/v1/deepreef/submissions/{submission_id}"
    )

    return res.json()
