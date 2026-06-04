from fastapi import FastAPI, HTTPException, status

from app.observability import configure_request_observability
from app.predict import get_active_model_metadata, predict_duration
from app.schemas import DurationPredictRequest, DurationPredictResponse

SERVICE_NAME = "ml-service"
VERSION = "0.1.0"

app = FastAPI(title="OrdoStack ML Service", version=VERSION)
configure_request_observability(app=app, service_name=SERVICE_NAME)


def build_health_payload() -> dict[str, str]:
    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "version": VERSION,
    }


def build_ready_payload() -> dict[str, object]:
    try:
        model_name, model_version, source = get_active_model_metadata()
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "not_ready",
                "service": SERVICE_NAME,
                "reason": "duration model metadata unavailable",
            },
        ) from error

    return {
        "status": "ready",
        "service": SERVICE_NAME,
        "version": VERSION,
        "checks": {
            "duration_model": "ok",
        },
        "model": {
            "model_name": model_name,
            "model_version": model_version,
            "source": source,
        },
    }


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return build_health_payload()


@app.get("/ready", tags=["health"])
def ready_check() -> dict[str, object]:
    return build_ready_payload()


@app.post("/duration/predict", response_model=DurationPredictResponse, tags=["duration"])
def predict_task_durations(payload: DurationPredictRequest) -> DurationPredictResponse:
    model_name, model_version, _ = get_active_model_metadata()
    return DurationPredictResponse(
        user_id=payload.user_id,
        model_name=model_name,
        model_version=model_version,
        predictions=[predict_duration(task) for task in payload.tasks],
    )


@app.get("/model/info", tags=["model"])
def model_info() -> dict[str, str]:
    model_name, model_version, source = get_active_model_metadata()
    return {
        "model_name": model_name,
        "model_version": model_version,
        "source": source,
    }
