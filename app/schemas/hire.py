
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict, model_validator


# 1. CREATE PRIVATE VENUE HIRE REQUEST
class HireRequestCreate(BaseModel):

    venue_id: int = Field(gt=0)

    start_time: datetime

    end_time: datetime

    guest_count: int = Field(gt=0)

    purpose: str = Field(min_length=5, max_length=1000)

    @model_validator(mode="after")
    def validate_times(self):
        if self.end_time <= self.start_time:
            raise ValueError("End time must be after start time")

        return self


# 2. HIRE REQUEST RESPONSE
class HireRequestResponse(BaseModel):

    id: int
    user_id: int
    venue_id: int

    start_time: datetime
    end_time: datetime

    guest_count: int
    purpose: str

    status: str
    admin_note: str | None
    reviewed_by: int | None

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# 3. ADMIN REVIEW REQUEST
class HireRequestReview(BaseModel):

    status: str

    admin_note: str | None = Field(
        default=None,
        max_length=1000
    )

    @model_validator(mode="after")
    def validate_status(self):
        if self.status not in ["approved", "rejected"]:
            raise ValueError(
                "Status must be approved or rejected"
            )

        return self
