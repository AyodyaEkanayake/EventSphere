
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Venue, User

from app.schemas.venue import (
    VenueCreate,
    VenueUpdate,
    VenueResponse
)

from app.routes.auth import require_roles


router = APIRouter(
    prefix="/venues",
    tags=["Venue Management"]
)


# 1. CREATE VENUE - ADMIN ONLY
@router.post(
    "/",
    response_model=VenueResponse,
    status_code=status.HTTP_201_CREATED
)
def create_venue(
    venue_data: VenueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):

    new_venue = Venue(
        name=venue_data.name,
        location=venue_data.location,
        capacity=venue_data.capacity,
        description=venue_data.description,
        image_url=venue_data.image_url,
        hourly_hire_rate=venue_data.hourly_hire_rate,
        private_hire_available=venue_data.private_hire_available
    )

    db.add(new_venue)
    db.commit()
    db.refresh(new_venue)

    return new_venue


# 2. VIEW ALL VENUES - ATTENDEE AND ADMIN
@router.get(
    "/",
    response_model=list[VenueResponse]
)
def get_all_venues(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("attendee", "admin")
    )
):

    venues = db.scalars(
        select(Venue).order_by(Venue.id)
    ).all()

    return venues


# 3. VIEW SINGLE VENUE - ATTENDEE AND ADMIN
@router.get(
    "/{venue_id}",
    response_model=VenueResponse
)
def get_venue(
    venue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("attendee", "admin")
    )
):

    venue = db.get(Venue, venue_id)

    if venue is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found"
        )

    return venue


# 4. UPDATE VENUE - ADMIN ONLY
@router.put(
    "/{venue_id}",
    response_model=VenueResponse
)
def update_venue(
    venue_id: int,
    venue_data: VenueUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):

    venue = db.get(Venue, venue_id)

    if venue is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found"
        )

    venue.name = venue_data.name
    venue.location = venue_data.location
    venue.capacity = venue_data.capacity
    venue.description = venue_data.description
    venue.image_url = venue_data.image_url
    venue.hourly_hire_rate = venue_data.hourly_hire_rate
    venue.private_hire_available = venue_data.private_hire_available

    db.commit()
    db.refresh(venue)

    return venue
