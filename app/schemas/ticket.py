
from pydantic import BaseModel, Field


# Data received when creating a ticket category
class TicketCategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    price: float = Field(ge=0)
    total_quantity: int = Field(gt=0)


# Data received when updating a ticket category
class TicketCategoryUpdate(TicketCategoryCreate):
    pass


# Data returned by the API
class TicketCategoryResponse(BaseModel):
    id: int
    event_id: int
    name: str
    price: float
    total_quantity: int
    sold_quantity: int
    available_quantity: int

    model_config = {"from_attributes": True}
