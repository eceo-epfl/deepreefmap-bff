from pydantic_settings import BaseSettings
from functools import lru_cache
import httpx


class Config(BaseSettings):
    API_PREFIX: str = "/api"

    # Common Keycloaksettings
    KEYCLOAK_REALM: str
    KEYCLOAK_URL: str

    # Keycloak Admin settings
    KEYCLOAK_BFF_ID: str
    KEYCLOAK_BFF_SECRET: str

    # Keycloak UI settings
    KEYCLOAK_CLIENT_ID: str

    # ECEO-API settings
    DEEPREEFMAP_API_URL: str  # Path to API (eg: http://deepreefmap-api-dev)

    SERIALIZER_SECRET_KEY: str
    SERIALIZER_EXPIRY_HOURS: int = 6

    TIMEOUT: httpx.Timeout = httpx.Timeout(
        5.0,
        connect=2.0,
    )
    LIMITS: httpx.Limits = httpx.Limits(
        max_connections=500, max_keepalive_connections=50
    )

    VALID_ROLES: list[str] = ["admin", "user"]


@lru_cache()
def get_config():
    return Config()


config = get_config()
