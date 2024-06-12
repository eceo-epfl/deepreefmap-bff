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


@router.get("")
async def get_status(
    reverse_proxy: Any = Depends(_reverse_proxy),
) -> Any:
    """Get status of k8s jobs, s3 bucket, etc"""

    return reverse_proxy
