from typing import Any
from fastapi import Depends, APIRouter
from app.config import config
from app.utils import get_async_client
import httpx
from app.models.user import User
from app.auth import get_user_info


router = APIRouter()


@router.get("/{job_id}")
async def get_job_log(
    job_id: str,
    client: httpx.AsyncClient = Depends(get_async_client),
    *,
    user: User = Depends(get_user_info),
) -> Any:
    """Get all kubernetes jobs in the namespace"""

    res = await client.get(
        f"{config.DEEPREEFMAP_API_URL}/v1/submissions/logs/{job_id}",
    )

    return res.json()
