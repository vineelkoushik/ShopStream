
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class NotificationOut(BaseModel):
    id: int
    user_id: int
    order_id: int
    type: str
    message: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
