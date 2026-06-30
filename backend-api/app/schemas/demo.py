from pydantic import BaseModel


class DemoResetRead(BaseModel):
    status: str
    user_id: int
    seeded_tasks: int
    seeded_fixed_events: int
    message: str
