
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import (
    Event,
    TicketCategory,
    Booking,
    Ticket,
    AgentMessage,
)
from app.routes.auth import require_roles


router = APIRouter(
    prefix="/dashboard",
    tags=["Admin Dashboard"]
)


@router.get("/")
def get_admin_dashboard(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin"))
):

    # 1. Total events
    total_events = db.query(Event).count()

    # 2. Total tickets sold
    total_tickets_sold = (
        db.query(TicketCategory.sold_quantity)
        .all()
    )

    tickets_sold = sum(
        item[0] for item in total_tickets_sold
    )

    # 3. Total confirmed booking revenue
    total_revenue = (
        db.query(Booking)
        .filter(
            Booking.status == "confirmed",
            Booking.payment_reference.isnot(None)
        )
        .with_entities(Booking.total_amount)
        .all()
    )

    revenue = sum(
        item[0] for item in total_revenue
    )

    # 4. Total check-ins
    total_check_ins = (
        db.query(Ticket)
        .filter(Ticket.status == "checked_in")
        .count()
    )

    # 5. Event capacity information
    categories = db.query(TicketCategory).all()

    event_capacity = []

    for category in categories:

        event = db.get(Event, category.event_id)

        event_capacity.append({
            "event_id": category.event_id,
            "event_title": event.title if event else None,
            "ticket_category": category.name,
            "total_quantity": category.total_quantity,
            "sold_quantity": category.sold_quantity,
            "available_quantity": (
                category.total_quantity -
                category.sold_quantity
            )
        })

    # 6. Recent agent communication logs
    agent_messages = (
        db.query(AgentMessage)
        .order_by(AgentMessage.id.desc())
        .limit(20)
        .all()
    )

    agent_logs = []

    for message in agent_messages:

        agent_logs.append({
            "id": message.id,
            "sender": message.sender,
            "receiver": message.receiver,
            "performative": message.performative,
            "content": message.content,
            "conversation_id": message.conversation_id,
            "created_at": message.created_at
        })

    return {
        "summary": {
            "total_events": total_events,
            "total_tickets_sold": tickets_sold,
            "total_revenue": revenue,
            "total_check_ins": total_check_ins
        },
        "event_capacity": event_capacity,
        "agent_logs": agent_logs
    }
