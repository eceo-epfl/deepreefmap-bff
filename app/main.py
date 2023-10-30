from typing import Union

from fastapi import FastAPI
from config import config
from models.config import KeycloakConfig

app = FastAPI()


@app.get("/config/keycloak")
async def get_keycloak_config() -> KeycloakConfig:
    return KeycloakConfig(
        client_id=config.KEYCLOAK_CLIENT_ID,
        realm=config.KEYCLOAK_REALM,
        url=config.KEYCLOAK_URL,
    )
