from fastapi import HTTPException, status

from app.config import load_runtime_config
from app.repositories.memory_store import DEMO_USER_ID
from app.repositories.store import get_store
from app.schemas.demo import DemoResetRead


def reset_demo_data(user_id: int = DEMO_USER_ID) -> DemoResetRead:
    if load_runtime_config().ordostack_env == "production":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    if user_id != DEMO_USER_ID:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Demo reset is only available for the demo user",
        )

    reset_result = get_store().reset_demo_data(user_id=user_id)
    return DemoResetRead.model_validate(
        {
            "status": "ok",
            "user_id": user_id,
            "message": "Demo data was reset to the bundled seed dataset",
            **reset_result,
        }
    )
