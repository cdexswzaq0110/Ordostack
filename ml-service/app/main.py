from fastapi import FastAPI

from app.predict import get_active_model_metadata, predict_duration
from app.schemas import DurationPredictRequest, DurationPredictResponse

SERVICE_NAME = "ml-service"
VERSION = "0.1.0"

app = FastAPI(title="OrdoStack ML Service", version=VERSION)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "version": VERSION,
    }


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
