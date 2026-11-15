
from pydantic import BaseModel, Field


class VenueCreate(BaseModel):

    name: str = Field(min_length=2, max_length=150)

    location: str = Field(min_length=2, max_length=255)

    capacity: int = Field(gt=0)

    description: str = Field(max_length=1000)

    image_url: str | None = None

    hourly_hire_rate: float = Field(ge=0)

    private_hire_available: bool = True


class VenueUpdate(VenueCreate):
    pass


class VenueResponse(BaseModel):

    id: int
    name: str
    location: str
    capacity: int
    description: str
    image_url: str | None
    hourly_hire_rate: float
    private_hire_available: bool

    model_config = {"from_attributes": True}
