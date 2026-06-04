from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app.api.analytics import router as analytics_router
from app.api.auth import router as auth_router
from app.api.demo import router as demo_router
from app.api.execution_logs import router as execution_logs_router
from app.api.fixed_events import router as fixed_events_router
from app.api.predictions import router as predictions_router
from app.api.schedules import router as schedules_router
from app.api.tasks import router as tasks_router
from app.config import ConfigurationError, load_runtime_config
from app.observability import configure_request_observability

SERVICE_NAME = "backend-api"
VERSION = "0.1.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_runtime_config()
    yield


app = FastAPI(title="OrdoStack Backend API", version=VERSION, lifespan=lifespan)
configure_request_observability(app=app, service_name=SERVICE_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks_router)
app.include_router(auth_router)
app.include_router(fixed_events_router)
app.include_router(schedules_router)
app.include_router(execution_logs_router)
app.include_router(analytics_router)
app.include_router(predictions_router)
app.include_router(demo_router)


def build_health_payload() -> dict[str, str]:
    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "version": VERSION,
    }


def build_ready_payload() -> dict[str, object]:
    try:
        load_runtime_config()
    except ConfigurationError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "not_ready",
                "service": SERVICE_NAME,
                "reason": str(error),
            },
        ) from error

    return {
        "status": "ready",
        "service": SERVICE_NAME,
        "version": VERSION,
        "checks": {
            "configuration": "ok",
        },
    }


@app.get("/api/health", tags=["health"])
def api_health_check() -> dict[str, str]:
    return build_health_payload()


@app.get("/health", include_in_schema=False)
def health_check() -> dict[str, str]:
    return build_health_payload()


@app.get("/api/ready", tags=["health"])
def api_ready_check() -> dict[str, object]:
    return build_ready_payload()


@app.get("/ready", include_in_schema=False)
def ready_check() -> dict[str, object]:
    return build_ready_payload()
