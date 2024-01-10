from pydantic_settings import BaseSettings
from functools import lru_cache


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
    ECEO_API_URL: str  # Full path to the ECEO API (eg: http://eceo-api-dev)


@lru_cache()
def get_config():
    return Config()


config = get_config()
