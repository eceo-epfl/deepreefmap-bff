from pydantic import BaseModel


class KeycloakConfig(BaseModel):
    """Parameters for frontend access to Keycloak"""

    client_id: str
    realm: str
    url: str
