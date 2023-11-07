from typing import Union
from fastapi import Depends, APIRouter
from app.config import config
from app.utils import get_async_client
import httpx

router = APIRouter()


@router.get("/")
async def get_areas(
    client: httpx.AsyncClient = Depends(get_async_client),
) -> Union[dict, list]:
    # Fetch data from config.SOIL_API_URL/v1/areas/ and relay back to client

    res = await client.get(config.SOIL_API_URL + "/v1/areas/")

    return res.json()
