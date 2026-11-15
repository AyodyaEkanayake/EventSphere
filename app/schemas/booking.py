
from datetime import datetime

from pydantic import BaseModel, Field


# Data received when an attendee creates a booking
class BookingCreate(BaseModel):
    event_id: int = Field(gt=0)
    ticket_category_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


# Data returned after creating a booking
class BookingResponse(BaseModel):
    id: int
    user_id: int
    event_id: int
    ticket_category_id: int
    quantity: int
    total_amount: float
    status: str
    payment_reference: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
