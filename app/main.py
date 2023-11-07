from typing import Union

from fastapi import FastAPI, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from config import config
from models.config import KeycloakConfig
from models.health import HealthCheck
from utils import get_async_client
import httpx

app = FastAPI()


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/config/keycloak")
async def get_keycloak_config() -> KeycloakConfig:
    return KeycloakConfig(
        clientId=config.KEYCLOAK_CLIENT_ID,
        realm=config.KEYCLOAK_REALM,
        url=config.KEYCLOAK_URL,
    )


@app.get("/api/areas/")
async def get_areas(
    client: httpx.AsyncClient = Depends(get_async_client),
) -> Union[dict, list]:
    # Fetch data from config.SOIL_API_URL/v1/areas/ and relay back to client

    res = await client.get(config.SOIL_API_URL + "/v1/areas/")

    return res.json()


@app.get(
    "/healthz",
    tags=["healthcheck"],
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=HealthCheck,
)
def get_health() -> HealthCheck:
    """
    ## Perform a Health Check
    Endpoint to perform a healthcheck on. This endpoint can primarily be used Docker
    to ensure a robust container orchestration and management is in place. Other
    services which rely on proper functioning of the API service will not deploy if this
    endpoint returns any other HTTP status code except 200 (OK).
    Returns:
        HealthCheck: Returns a JSON response with the health status
    """
    return HealthCheck(status="OK")
