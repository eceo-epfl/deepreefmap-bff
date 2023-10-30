from typing import Union

from fastapi import FastAPI
from app.config import config
from app.models.config import KeycloakConfig

app = FastAPI()


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/config/keycloak")
async def get_keycloak_config() -> KeycloakConfig:
    return KeycloakConfig(
        client_id=config.KEYCLOAK_CLIENT_ID,
        realm=config.KEYCLOAK_REALM,
        url=config.KEYCLOAK_URL,
    )
