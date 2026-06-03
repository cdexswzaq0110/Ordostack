from fastapi import FastAPI, HTTPException, status

from app.schemas.schedule import ScheduleGenerateRequest, ScheduleGenerateResponse
from app.services.scheduler import ScheduleGenerationError, generate_schedule

SERVICE_NAME = "scheduler-service"
VERSION = "0.1.0"

app = FastAPI(title="OrdoStack Scheduler Service", version=VERSION)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "version": VERSION,
    }


@app.post("/schedule/generate", response_model=ScheduleGenerateResponse, tags=["schedule"])
def generate_daily_schedule(payload: ScheduleGenerateRequest) -> ScheduleGenerateResponse:
    try:
        return generate_schedule(payload)
    except ScheduleGenerationError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)) from error
