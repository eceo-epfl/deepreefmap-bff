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

    # SOIL-API settings
    SOIL_API_URL: str  # Full path to the Soil API (eg: http://soil-api-dev)


@lru_cache()
def get_config():
    return Config()


config = get_config()
