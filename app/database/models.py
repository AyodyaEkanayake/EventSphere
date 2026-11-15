
from datetime import datetime, timezone

from sqlalchemy import (
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    JSON
)

from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


# 1. USERS TABLE
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    full_name: Mapped[str] = mapped_column(String(100))

    email: Mapped[str] = mapped_column(
        String(150), unique=True, index=True
    )

    password_hash: Mapped[str] = mapped_column(String(255))

    role: Mapped[str] = mapped_column(
        String(20), default="attendee"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )


# 2. VENUES TABLE
class Venue(Base):
    __tablename__ = "venues"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    name: Mapped[str] = mapped_column(String(150))

    location: Mapped[str] = mapped_column(String(255))

    capacity: Mapped[int] = mapped_column(Integer)

    description: Mapped[str] = mapped_column(String(1000))

    image_url: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )

    hourly_hire_rate: Mapped[float] = mapped_column(Float)

    private_hire_available: Mapped[bool] = mapped_column(
        Boolean, default=True
    )


# 3. EVENTS TABLE
class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    title: Mapped[str] = mapped_column(String(200))

    category: Mapped[str] = mapped_column(String(100))

    venue_id: Mapped[int] = mapped_column(
        ForeignKey("venues.id")
    )

    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )

    end_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )

    description: Mapped[str] = mapped_column(String(2000))

    status: Mapped[str] = mapped_column(
        String(20), default="draft"
    )


# 4. TICKET CATEGORIES TABLE
class TicketCategory(Base):
    __tablename__ = "ticket_categories"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id")
    )

    name: Mapped[str] = mapped_column(String(100))

    price: Mapped[float] = mapped_column(Float)

    total_quantity: Mapped[int] = mapped_column(Integer)

    sold_quantity: Mapped[int] = mapped_column(
        Integer, default=0
    )


# 5. BOOKINGS TABLE
class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )

    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id")
    )

    ticket_category_id: Mapped[int] = mapped_column(
    ForeignKey("ticket_categories.id")
    )
    
    quantity: Mapped[int] = mapped_column(Integer)

    total_amount: Mapped[float] = mapped_column(Float)

    status: Mapped[str] = mapped_column(
        String(30), default="confirmed"
    )

    payment_reference: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )


# 6. TICKETS TABLE
class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    booking_id: Mapped[int] = mapped_column(
        ForeignKey("bookings.id")
    )

    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id")
    )

    ticket_code: Mapped[str] = mapped_column(
        String(100), unique=True, index=True
    )

    status: Mapped[str] = mapped_column(
        String(30), default="valid"
    )

    checked_in_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


# 7. AGENT MESSAGES TABLE
class AgentMessage(Base):
    __tablename__ = "agent_messages"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    sender: Mapped[str] = mapped_column(String(100))

    receiver: Mapped[str] = mapped_column(String(100))

    performative: Mapped[str] = mapped_column(String(30))

    content: Mapped[dict] = mapped_column(JSON)

    conversation_id: Mapped[str] = mapped_column(
        String(100), index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )



# 8. PRIVATE VENUE HIRE REQUESTS TABLE
class VenueHireRequest(Base):
    __tablename__ = "venue_hire_requests"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )

    venue_id: Mapped[int] = mapped_column(
        ForeignKey("venues.id")
    )

    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )

    end_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )

    guest_count: Mapped[int] = mapped_column(Integer)

    purpose: Mapped[str] = mapped_column(
        String(1000)
    )

    status: Mapped[str] = mapped_column(
        String(30), default="pending"
    )

    admin_note: Mapped[str | None] = mapped_column(
        String(1000), nullable=True
    )

    reviewed_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )



# 9. WAITLIST ENTRIES TABLE
class WaitlistEntry(Base):

    __tablename__ = "waitlist_entries"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )

    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id")
    )

    ticket_category_id: Mapped[int] = mapped_column(
        ForeignKey("ticket_categories.id")
    )

    quantity: Mapped[int] = mapped_column(Integer)

    status: Mapped[str] = mapped_column(
        String(30), default="waiting"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
