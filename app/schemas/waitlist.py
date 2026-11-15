
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class WaitlistCreate(BaseModel):

    event_id: int = Field(gt=0)

    ticket_category_id: int = Field(gt=0)

    quantity: int = Field(gt=0)


class WaitlistResponse(BaseModel):

    id: int
    user_id: int
    event_id: int
    ticket_category_id: int
    quantity: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WaitlistStatusUpdate(BaseModel):

    status: str

    def validate_status(self):
        if self.status not in ["notified", "fulfilled", "cancelled"]:
            raise ValueError("Invalid waitlist status")

        return self
