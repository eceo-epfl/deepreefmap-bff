from typing import Any
from fastapi import Depends, APIRouter
from app.utils import _reverse_proxy
from uuid import UUID
from app.models.user import User
from app.auth import get_user_info


router = APIRouter()


@router.get("/{transect_id}")
async def get_transect(
    transect_id: UUID,
    reverse_proxy: Any = Depends(_reverse_proxy),
    user: User = Depends(get_user_info),
) -> Any:
    """Get a transect by id"""

    return reverse_proxy


@router.get("")
async def get_transects(
    reverse_proxy: Any = Depends(_reverse_proxy),
    user: User = Depends(get_user_info),
) -> Any:
    """Get all transects"""

    return reverse_proxy


@router.post("")
async def create_transect(
    reverse_proxy: Any = Depends(_reverse_proxy),
    user: User = Depends(get_user_info),
) -> Any:
    """Creates a transect"""

    return reverse_proxy


@router.post("/batch")
async def create_plot_batch(
    reverse_proxy: Any = Depends(_reverse_proxy),
    user: User = Depends(get_user_info),
) -> Any:
    """Creates plots from a batch import"""

    return reverse_proxy


@router.put("/{transect_id}")
async def update_transect(
    transect_id: UUID,
    reverse_proxy: Any = Depends(_reverse_proxy),
    user: User = Depends(get_user_info),
) -> Any:
    """ "Updates a transects by id"""

    return reverse_proxy


@router.delete("/{transect_id}")
async def delete_transect(
    transect_id: UUID,
    reverse_proxy: Any = Depends(_reverse_proxy),
    user: User = Depends(get_user_info),
) -> None:
    """Delete a transects by id"""

    return reverse_proxy
