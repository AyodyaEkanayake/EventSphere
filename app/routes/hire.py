
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import (
    Venue,
    Event,
    User,
    VenueHireRequest
)
from app.schemas.hire import (
    HireRequestCreate,
    HireRequestResponse,
    HireRequestReview
)
from app.routes.auth import require_roles


router = APIRouter(
    prefix="/hire",
    tags=["Private Venue Hire"]
)


# CHECK WHETHER VENUE IS AVAILABLE
def check_venue_availability(
    db: Session,
    venue_id: int,
    start_time,
    end_time,
    exclude_request_id: int | None = None
):
    # Check existing non-cancelled events
    event_conflict = db.query(Event).filter(
        Event.venue_id == venue_id,
        Event.status != "cancelled",
        Event.start_time < end_time,
        Event.end_time > start_time
    ).first()

    if event_conflict:
        return False

    # Check already approved private hire requests
    hire_query = db.query(VenueHireRequest).filter(
        VenueHireRequest.venue_id == venue_id,
        VenueHireRequest.status == "approved",
        VenueHireRequest.start_time < end_time,
        VenueHireRequest.end_time > start_time
    )

    if exclude_request_id is not None:
        hire_query = hire_query.filter(
            VenueHireRequest.id != exclude_request_id
        )

    if hire_query.first():
        return False

    return True


# 1. ATTENDEE: SUBMIT PRIVATE VENUE HIRE REQUEST
@router.post(
    "/",
    response_model=HireRequestResponse,
    status_code=status.HTTP_201_CREATED
)
def create_hire_request(
    request: HireRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("attendee"))
):

    venue = db.query(Venue).filter(
        Venue.id == request.venue_id
    ).first()

    if venue is None:
        raise HTTPException(
            status_code=404,
            detail="Venue not found"
        )

    if not venue.private_hire_available:
        raise HTTPException(
            status_code=400,
            detail="Private hire is not available for this venue"
        )

    if request.guest_count > venue.capacity:
        raise HTTPException(
            status_code=400,
            detail="Guest count exceeds venue capacity"
        )

    available = check_venue_availability(
        db,
        request.venue_id,
        request.start_time,
        request.end_time
    )

    if not available:
        raise HTTPException(
            status_code=400,
            detail="Venue is not available during the requested time"
        )

    new_request = VenueHireRequest(
        user_id=current_user.id,
        venue_id=request.venue_id,
        start_time=request.start_time,
        end_time=request.end_time,
        guest_count=request.guest_count,
        purpose=request.purpose,
        status="pending"
    )

    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    return new_request


# 2. ATTENDEE: VIEW OWN HIRE REQUESTS
@router.get(
    "/my-requests",
    response_model=list[HireRequestResponse]
)
def get_my_hire_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("attendee"))
):

    return db.query(VenueHireRequest).filter(
        VenueHireRequest.user_id == current_user.id
    ).order_by(
        VenueHireRequest.created_at.desc()
    ).all()


# 3. ADMIN: VIEW ALL HIRE REQUESTS
@router.get(
    "/",
    response_model=list[HireRequestResponse]
)
def get_all_hire_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):

    return db.query(VenueHireRequest).order_by(
        VenueHireRequest.created_at.desc()
    ).all()


# 4. ADMIN: REVIEW AND APPROVE/REJECT REQUEST
@router.patch(
    "/{request_id}/review",
    response_model=HireRequestResponse
)
def review_hire_request(
    request_id: int,
    review: HireRequestReview,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):

    hire_request = db.query(VenueHireRequest).filter(
        VenueHireRequest.id == request_id
    ).first()

    if hire_request is None:
        raise HTTPException(
            status_code=404,
            detail="Hire request not found"
        )

    if hire_request.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="This hire request has already been reviewed"
        )

    if review.status == "approved":

        available = check_venue_availability(
            db,
            hire_request.venue_id,
            hire_request.start_time,
            hire_request.end_time,
            exclude_request_id=hire_request.id
        )

        if not available:
            raise HTTPException(
                status_code=400,
                detail="Venue is no longer available for this period"
            )

    hire_request.status = review.status
    hire_request.admin_note = review.admin_note
    hire_request.reviewed_by = current_user.id

    db.commit()
    db.refresh(hire_request)

    return hire_request


# 5. ADMIN: VIEW ONE HIRE REQUEST
@router.get(
    "/{request_id}",
    response_model=HireRequestResponse
)
def get_hire_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):

    hire_request = db.query(VenueHireRequest).filter(
        VenueHireRequest.id == request_id
    ).first()

    if hire_request is None:
        raise HTTPException(
            status_code=404,
            detail="Hire request not found"
        )

    return hire_request
