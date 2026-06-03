from fastapi import APIRouter

from app.schemas.demo import DemoResetRead
from app.services import demo as demo_service

router = APIRouter(prefix="/api/demo", tags=["demo"])


@router.post("/reset", response_model=DemoResetRead)
def reset_demo_data(user_id: int = 1) -> DemoResetRead:
    return demo_service.reset_demo_data(user_id=user_id)
