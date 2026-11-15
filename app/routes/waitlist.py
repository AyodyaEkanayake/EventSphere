
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import (
    User,
    Event,
    TicketCategory,
    WaitlistEntry
)
from app.schemas.waitlist import (
    WaitlistCreate,
    WaitlistResponse,
    WaitlistStatusUpdate
)
from app.routes.auth import require_roles


router = APIRouter(
    prefix="/waitlist",
    tags=["Waitlist"]
)


# 1. ATTENDEE JOINS WAITLIST
@router.post("/", response_model=WaitlistResponse, status_code=201)
def join_waitlist(
    data: WaitlistCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("attendee"))
):

    event = db.query(Event).filter(
        Event.id == data.event_id,
        Event.status == "published"
    ).first()

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Published event not found"
        )

    category = db.query(TicketCategory).filter(
        TicketCategory.id == data.ticket_category_id,
        TicketCategory.event_id == data.event_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Ticket category not found"
        )

    available = category.total_quantity - category.sold_quantity

    if available > 0:
        raise HTTPException(
            status_code=400,
            detail="Tickets are still available. Please book directly."
        )

    existing = db.query(WaitlistEntry).filter(
        WaitlistEntry.user_id == current_user.id,
        WaitlistEntry.event_id == data.event_id,
        WaitlistEntry.ticket_category_id == data.ticket_category_id,
        WaitlistEntry.status == "waiting"
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="You are already in this waitlist."
        )

    entry = WaitlistEntry(
        user_id=current_user.id,
        event_id=data.event_id,
        ticket_category_id=data.ticket_category_id,
        quantity=data.quantity,
        status="waiting"
    )

    db.add(entry)
    db.commit()
    db.refresh(entry)

    return entry


# 2. ATTENDEE VIEWS OWN WAITLIST ENTRIES
@router.get("/my-entries", response_model=list[WaitlistResponse])
def my_waitlist_entries(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("attendee"))
):

    return db.query(WaitlistEntry).filter(
        WaitlistEntry.user_id == current_user.id
    ).order_by(
        WaitlistEntry.created_at.desc()
    ).all()


# 3. ADMIN VIEWS ALL WAITLIST ENTRIES
@router.get("/", response_model=list[WaitlistResponse])
def get_all_waitlist_entries(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):

    return db.query(WaitlistEntry).order_by(
        WaitlistEntry.created_at.asc()
    ).all()


# 4. ADMIN UPDATES WAITLIST STATUS
@router.patch("/{entry_id}/status", response_model=WaitlistResponse)
def update_waitlist_status(
    entry_id: int,
    data: WaitlistStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):

    if data.status not in ["notified", "fulfilled", "cancelled"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid waitlist status"
        )

    entry = db.query(WaitlistEntry).filter(
        WaitlistEntry.id == entry_id
    ).first()

    if not entry:
        raise HTTPException(
            status_code=404,
            detail="Waitlist entry not found"
        )

    if entry.status != "waiting":
        raise HTTPException(
            status_code=400,
            detail="This waitlist entry has already been processed"
        )

    entry.status = data.status

    db.commit()
    db.refresh(entry)

    return entry
