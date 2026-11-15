import io
import base64
import secrets

import qrcode

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func , update
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import (
    Event,
    Venue,
    TicketCategory,
    Booking,
    Ticket,
    User
)
from app.schemas.ticket import (
    TicketCategoryCreate,
    TicketCategoryUpdate,
    TicketCategoryResponse
)
from app.routes.auth import require_roles
from datetime import datetime, timezone

router = APIRouter(
    prefix="/tickets",
    tags=["Ticket Categories"]
)


# HELPER FUNCTION: CALCULATE AVAILABLE TICKETS
def format_ticket_category(category: TicketCategory):

    return {
        "id": category.id,
        "event_id": category.event_id,
        "name": category.name,
        "price": category.price,
        "total_quantity": category.total_quantity,
        "sold_quantity": category.sold_quantity,
        "available_quantity": (
            category.total_quantity - category.sold_quantity
        )
    }


# 1. CREATE TICKET CATEGORY
@router.post(
    "/events/{event_id}/categories",
    response_model=TicketCategoryResponse,
    status_code=status.HTTP_201_CREATED
)
def create_ticket_category(
    event_id: int,
    ticket_data: TicketCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):

    event = db.get(Event, event_id)

    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    if event.status != "draft":
        raise HTTPException(
            status_code=400,
            detail="Ticket categories can only be added to draft events"
        )

    venue = db.get(Venue, event.venue_id)

    current_quantity = db.scalar(
        select(func.coalesce(func.sum(TicketCategory.total_quantity), 0))
        .where(TicketCategory.event_id == event_id)
    )

    if current_quantity + ticket_data.total_quantity > venue.capacity:
        raise HTTPException(
            status_code=400,
            detail="Total ticket quantity cannot exceed venue capacity"
        )

    new_category = TicketCategory(
        event_id=event_id,
        name=ticket_data.name,
        price=ticket_data.price,
        total_quantity=ticket_data.total_quantity,
        sold_quantity=0
    )

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return format_ticket_category(new_category)


# 2. VIEW TICKET CATEGORIES FOR AN EVENT
@router.get(
    "/events/{event_id}/categories",
    response_model=list[TicketCategoryResponse]
)
def get_ticket_categories(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "attendee"))
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

    categories = db.scalars(
        select(TicketCategory)
        .where(TicketCategory.event_id == event_id)
        .order_by(TicketCategory.id)
    ).all()

    return [
        format_ticket_category(category)
        for category in categories
    ]


# 3. UPDATE TICKET CATEGORY
@router.put(
    "/categories/{category_id}",
    response_model=TicketCategoryResponse
)
def update_ticket_category(
    category_id: int,
    ticket_data: TicketCategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):

    category = db.get(TicketCategory, category_id)

    if category is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket category not found"
        )

    event = db.get(Event, category.event_id)

    if event.status != "draft":
        raise HTTPException(
            status_code=400,
            detail="Only draft event ticket categories can be updated"
        )

    if ticket_data.total_quantity < category.sold_quantity:
        raise HTTPException(
            status_code=400,
            detail="Total quantity cannot be less than tickets already sold"
        )

    venue = db.get(Venue, event.venue_id)

    other_quantity = db.scalar(
        select(func.coalesce(func.sum(TicketCategory.total_quantity), 0))
        .where(
            TicketCategory.event_id == event.id,
            TicketCategory.id != category_id
        )
    )

    if other_quantity + ticket_data.total_quantity > venue.capacity:
        raise HTTPException(
            status_code=400,
            detail="Total ticket quantity cannot exceed venue capacity"
        )

    category.name = ticket_data.name
    category.price = ticket_data.price
    category.total_quantity = ticket_data.total_quantity

    db.commit()
    db.refresh(category)

    return format_ticket_category(category)


# HELPER FUNCTION: GENERATE QR CODE AS BASE64
def create_qr_code(ticket_code: str):

    qr = qrcode.make(ticket_code)

    image_buffer = io.BytesIO()
    qr.save(image_buffer, format="PNG")

    image_buffer.seek(0)

    encoded_image = base64.b64encode(
        image_buffer.getvalue()
    ).decode("utf-8")

    return "data:image/png;base64," + encoded_image


# HELPER FUNCTION: FORMAT TICKET RESPONSE
def format_ticket(ticket: Ticket):

    return {
        "id": ticket.id,
        "booking_id": ticket.booking_id,
        "event_id": ticket.event_id,
        "ticket_code": ticket.ticket_code,
        "status": ticket.status,
        "qr_code": create_qr_code(ticket.ticket_code)
    }


# 4. GENERATE TICKETS FOR A CONFIRMED BOOKING
@router.post(
    "/bookings/{booking_id}/generate",
    status_code=status.HTTP_201_CREATED
)
def generate_booking_tickets(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("attendee"))
):

    # Find booking belonging to the logged-in attendee
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.user_id == current_user.id
    ).first()

    if booking is None:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    # Only paid and confirmed bookings can receive tickets
    if booking.status != "confirmed" or not booking.payment_reference:
        raise HTTPException(
            status_code=400,
            detail="Payment must be completed before ticket generation"
        )

    # Check whether tickets were already generated
    existing_tickets = db.query(Ticket).filter(
        Ticket.booking_id == booking_id
    ).all()

    if len(existing_tickets) >= booking.quantity:
        return {
            "message": "Tickets already generated",
            "tickets": [
                format_ticket(ticket)
                for ticket in existing_tickets
            ]
        }

    try:
        # Generate only the missing tickets
        missing_quantity = booking.quantity - len(existing_tickets)

        for _ in range(missing_quantity):

            ticket = Ticket(
                booking_id=booking.id,
                event_id=booking.event_id,
                ticket_code=secrets.token_urlsafe(32),
                status="valid"
            )

            db.add(ticket)

        db.commit()

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Ticket generation failed"
        )

    # Retrieve all tickets for this booking
    generated_tickets = db.query(Ticket).filter(
        Ticket.booking_id == booking_id
    ).all()

    return {
        "message": "Tickets generated successfully",
        "tickets": [
            format_ticket(ticket)
            for ticket in generated_tickets
        ]
    }


# 5. VIEW MY GENERATED TICKETS
@router.get("/my-tickets")
def get_my_tickets(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("attendee"))
):

    tickets = db.query(Ticket).join(
        Booking,
        Ticket.booking_id == Booking.id
    ).filter(
        Booking.user_id == current_user.id
    ).order_by(
        Ticket.id.desc()
    ).all()

    return {
        "total_tickets": len(tickets),
        "tickets": [
            format_ticket(ticket)
            for ticket in tickets
        ]
    }


# 6. SCAN TICKET AND CHECK IN ATTENDEE
@router.post("/scan/{event_id}/{ticket_code}")
def scan_ticket(
    event_id: int,
    ticket_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("gate_staff"))
):

    # Find ticket using its unique code
    ticket = db.query(Ticket).filter(
        Ticket.ticket_code == ticket_code
    ).first()

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    # Check whether ticket belongs to this event
    if ticket.event_id != event_id:
        raise HTTPException(
            status_code=400,
            detail="Ticket belongs to a different event"
        )

    # Check whether ticket was already used
    if ticket.status == "checked_in":
        raise HTTPException(
            status_code=400,
            detail="Ticket already checked in"
        )

    # Only valid tickets can be used
    if ticket.status != "valid":
        raise HTTPException(
            status_code=400,
            detail="Invalid or cancelled ticket"
        )

    # Atomically mark ticket as checked in
    result = db.execute(
        update(Ticket)
        .where(
            Ticket.id == ticket.id,
            Ticket.status == "valid"
        )
        .values(
            status="checked_in",
            checked_in_at=datetime.now(timezone.utc)
        )
    )

    if result.rowcount != 1:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Ticket already checked in"
        )

    db.commit()
    db.refresh(ticket)

    return {
        "message": "Ticket validated successfully. Entry allowed!",
        "ticket_id": ticket.id,
        "ticket_code": ticket.ticket_code,
        "event_id": ticket.event_id,
        "status": ticket.status,
        "checked_in_at": ticket.checked_in_at
    }
