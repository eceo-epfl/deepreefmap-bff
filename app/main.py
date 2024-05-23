from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from app.config import config
from app.models.config import KeycloakConfig
from app.models.health import HealthCheck
from app.submissions import router as submissions_router
from app.users import router as users_router
from app.objects import router as objects_router
from app.submission_job_logs import router as submission_job_logs_router
from app.transects import router as transects_router
from app.utils import lifespan

app = FastAPI(lifespan=lifespan)


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(f"{config.API_PREFIX}/config/keycloak")
async def get_keycloak_config() -> KeycloakConfig:
    return KeycloakConfig(
        clientId=config.KEYCLOAK_CLIENT_ID,
        realm=config.KEYCLOAK_REALM,
        url=config.KEYCLOAK_URL,
    )


@app.get(
    "/healthz",
    tags=["healthcheck"],
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=HealthCheck,
)
def get_health() -> HealthCheck:
    """Perform a Health Check

    Useful for Kubernetes to check liveness and readiness probes
    """
    return HealthCheck(status="OK")


app.include_router(
    submissions_router,
    prefix=f"{config.API_PREFIX}/submissions",
    tags=["submissions"],
)
app.include_router(
    objects_router,
    prefix=f"{config.API_PREFIX}/objects",
    tags=["objects"],
)
app.include_router(
    users_router,
    prefix=f"{config.API_PREFIX}/users",
    tags=["users"],
)
app.include_router(
    submission_job_logs_router,
    prefix=f"{config.API_PREFIX}/submission_job_logs",
    tags=["submissions", "logs"],
)
app.include_router(
    transects_router,
    prefix=f"{config.API_PREFIX}/transects",
    tags=["transects"],
)
