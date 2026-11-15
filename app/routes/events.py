
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Event, Venue, User
from app.schemas.event import EventCreate, EventUpdate, EventResponse
from app.routes.auth import require_roles


router = APIRouter(
    prefix="/events",
    tags=["Event Management"]
)


# Check whether the venue exists and has no overlapping event
def validate_venue_availability(
    db: Session,
    venue_id: int,
    start_time,
    end_time,
    exclude_event_id: int | None = None
):

    venue = db.get(Venue, venue_id)

    if venue is None:
        raise HTTPException(
            status_code=404,
            detail="Venue not found"
        )

    query = select(Event).where(
        Event.venue_id == venue_id,
        Event.status != "cancelled",
        Event.start_time < end_time,
        Event.end_time > start_time
    )

    if exclude_event_id is not None:
        query = query.where(Event.id != exclude_event_id)

    overlapping_event = db.scalar(query)

    if overlapping_event:
        raise HTTPException(
            status_code=409,
            detail="This venue already has an event during the selected time."
        )


# 1. CREATE EVENT
@router.post(
    "/",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED
)
def create_event(
    event_data: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):

    validate_venue_availability(
        db,
        event_data.venue_id,
        event_data.start_time,
        event_data.end_time
    )

    new_event = Event(
        title=event_data.title,
        category=event_data.category,
        venue_id=event_data.venue_id,
        start_time=event_data.start_time,
        end_time=event_data.end_time,
        description=event_data.description,
        status="draft"
    )

    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    return new_event


# 2. VIEW ALL EVENTS
@router.get(
    "/",
    response_model=list[EventResponse]
)
def get_all_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin", "attendee")
    )
):

    query = select(Event).order_by(Event.id)

    if current_user.role == "attendee":
        query = query.where(Event.status == "published")

    events = db.scalars(query).all()

    return events


# 3. VIEW ONE EVENT
@router.get(
    "/{event_id}",
    response_model=EventResponse
)
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin", "attendee")
    )
):

    event = db.get(Event, event_id)

    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    if current_user.role == "attendee" and event.status != "published":
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    return event


# 4. UPDATE EVENT
@router.put(
    "/{event_id}",
    response_model=EventResponse
)
def update_event(
    event_id: int,
    event_data: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):

    event = db.get(Event, event_id)

    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    if event.status == "cancelled":
        raise HTTPException(
            status_code=400,
            detail="Cancelled events cannot be updated"
        )

    validate_venue_availability(
        db,
        event_data.venue_id,
        event_data.start_time,
        event_data.end_time,
        exclude_event_id=event_id
    )

    event.title = event_data.title
    event.category = event_data.category
    event.venue_id = event_data.venue_id
    event.start_time = event_data.start_time
    event.end_time = event_data.end_time
    event.description = event_data.description

    db.commit()
    db.refresh(event)

    return event


# 5. CANCEL EVENT
@router.patch(
    "/{event_id}/cancel",
    response_model=EventResponse
)
def cancel_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):

    event = db.get(Event, event_id)

    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    if event.status == "cancelled":
        raise HTTPException(
            status_code=400,
            detail="Event is already cancelled"
        )

    event.status = "cancelled"

    db.commit()
    db.refresh(event)

    return event



# 6. PUBLISH EVENT
@router.patch(
    "/{event_id}/publish",
    response_model=EventResponse
)
def publish_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):

    event = db.get(Event, event_id)

    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    if event.status == "cancelled":
        raise HTTPException(
            status_code=400,
            detail="Cancelled events cannot be published"
        )

    if event.status == "published":
        raise HTTPException(
            status_code=400,
            detail="Event is already published"
        )

    venue = db.get(Venue, event.venue_id)

    from app.database.models import TicketCategory
    from sqlalchemy import func

    category_count = db.scalar(
        select(func.count(TicketCategory.id))
        .where(TicketCategory.event_id == event_id)
    )

    if category_count == 0:
        raise HTTPException(
            status_code=400,
            detail="At least one ticket category is required before publishing"
        )

    total_tickets = db.scalar(
        select(func.coalesce(func.sum(TicketCategory.total_quantity), 0))
        .where(TicketCategory.event_id == event_id)
    )

    if total_tickets > venue.capacity:
        raise HTTPException(
            status_code=400,
            detail="Ticket quantity exceeds venue capacity"
        )

    event.status = "published"

    db.commit()
    db.refresh(event)

    return event
