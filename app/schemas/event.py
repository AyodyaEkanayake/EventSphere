
from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class EventCreate(BaseModel):

    title: str = Field(min_length=3, max_length=200)

    category: str = Field(min_length=2, max_length=100)

    venue_id: int = Field(gt=0)

    start_time: datetime

    end_time: datetime

    description: str = Field(min_length=5, max_length=2000)

    @model_validator(mode="after")
    def validate_event_times(self):
        if self.end_time <= self.start_time:
            raise ValueError("End time must be later than start time")
        return self


class EventUpdate(EventCreate):
    pass


class EventResponse(BaseModel):

    id: int
    title: str
    category: str
    venue_id: int
    start_time: datetime
    end_time: datetime
    description: str
    status: str

    model_config = {"from_attributes": True}
