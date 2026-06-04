from fastapi import FastAPI, HTTPException, status

from app.observability import configure_request_observability
from app.schemas.schedule import ScheduleGenerateRequest, ScheduleGenerateResponse
from app.services.scheduler import ScheduleGenerationError, generate_schedule

SERVICE_NAME = "scheduler-service"
VERSION = "0.1.0"

app = FastAPI(title="OrdoStack Scheduler Service", version=VERSION)
configure_request_observability(app=app, service_name=SERVICE_NAME)


def build_health_payload() -> dict[str, str]:
    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "version": VERSION,
    }


def build_ready_payload() -> dict[str, object]:
    return {
        "status": "ready",
        "service": SERVICE_NAME,
        "version": VERSION,
        "checks": {
            "schedule_generator": "ok",
        },
    }


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return build_health_payload()


@app.get("/ready", tags=["health"])
def ready_check() -> dict[str, object]:
    return build_ready_payload()


@app.post("/schedule/generate", response_model=ScheduleGenerateResponse, tags=["schedule"])
def generate_daily_schedule(payload: ScheduleGenerateRequest) -> ScheduleGenerateResponse:
    try:
        return generate_schedule(payload)
    except ScheduleGenerationError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)) from error
