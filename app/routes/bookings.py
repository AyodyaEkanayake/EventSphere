
import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import update

from app.database.connection import get_db
from app.database.models import (
    User,
    Event,
    TicketCategory,
    Booking
)
from app.schemas.booking import BookingCreate, BookingResponse
from app.routes.auth import require_roles


router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"]
)


# 1. CREATE A NEW BOOKING
@router.post(
    "/",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED
)
def create_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("attendee"))
):

    # Check whether the event exists and is published
    event = db.query(Event).filter(
        Event.id == booking_data.event_id,
        Event.status == "published"
    ).first()

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Published event not found"
        )

    # Check whether the selected ticket category belongs to this event
    category = db.query(TicketCategory).filter(
        TicketCategory.id == booking_data.ticket_category_id,
        TicketCategory.event_id == booking_data.event_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Ticket category not found for this event"
        )

    # Calculate total booking amount
    total_amount = category.price * booking_data.quantity

    # Atomically reserve available tickets
    result = db.execute(
        update(TicketCategory)
        .where(
            TicketCategory.id == booking_data.ticket_category_id,
            TicketCategory.event_id == booking_data.event_id,
            TicketCategory.total_quantity
            - TicketCategory.sold_quantity
            >= booking_data.quantity
        )
        .values(
            sold_quantity=(
                TicketCategory.sold_quantity
                + booking_data.quantity
            )
        )
    )

    # Check ticket availability
    if result.rowcount != 1:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Not enough tickets available"
        )

    # Create booking with pending payment status
    new_booking = Booking(
        user_id=current_user.id,
        event_id=booking_data.event_id,
        ticket_category_id=booking_data.ticket_category_id,
        quantity=booking_data.quantity,
        total_amount=total_amount,
        status="pending_payment"
    )

    try:
        db.add(new_booking)
        db.commit()
        db.refresh(new_booking)

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Booking could not be completed"
        )

    return new_booking


# 2. PROCESS SIMULATED PAYMENT
@router.post(
    "/{booking_id}/payment",
    response_model=BookingResponse
)
def process_payment(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("attendee"))
):

    # Find the booking belonging to the logged-in attendee
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.user_id == current_user.id
    ).first()

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    # Prevent duplicate payments
    if booking.payment_reference:
        return booking

    # Only pending or existing confirmed bookings can be paid
    if booking.status not in ["pending_payment", "confirmed"]:
        raise HTTPException(
            status_code=400,
            detail="This booking cannot be paid"
        )

    # Generate a unique simulated payment reference
    payment_reference = (
        "SIM-" + secrets.token_hex(6).upper()
    )

    # Update booking after simulated payment
    booking.payment_reference = payment_reference
    booking.status = "confirmed"

    try:
        db.commit()
        db.refresh(booking)

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Simulated payment could not be completed"
        )

    return booking


# 3. VIEW MY BOOKING HISTORY
@router.get(
    "/my-bookings",
    response_model=list[BookingResponse]
)
def get_my_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("attendee"))
):

    bookings = db.query(Booking).filter(
        Booking.user_id == current_user.id
    ).order_by(
        Booking.created_at.desc()
    ).all()

    return bookings
