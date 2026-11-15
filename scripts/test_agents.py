
from uuid import uuid4
from datetime import datetime

from app.agents.message_bus import MessageBus
from app.agents.venue_agent import VenueAgent
from app.agents.booking_agent import BookingAgent
from app.agents.ticket_agent import TicketAgent
from app.agents.waitlist_agent import WaitlistAgent
from app.agents.notification_agent import NotificationAgent

from app.database.connection import SessionLocal
from app.database.models import AgentMessage


# 1. Create Message Bus
bus = MessageBus()


# 2. Create all five agents
venue_agent = VenueAgent("VenueAgent", bus)
booking_agent = BookingAgent("BookingAgent", bus)
ticket_agent = TicketAgent("TicketAgent", bus)
waitlist_agent = WaitlistAgent("WaitlistAgent", bus)
notification_agent = NotificationAgent("NotificationAgent", bus)


# 3. Register all agents
bus.register_agent(venue_agent)
bus.register_agent(booking_agent)
bus.register_agent(ticket_agent)
bus.register_agent(waitlist_agent)
bus.register_agent(notification_agent)

print("\n--- AGENT REGISTRATION ---")
print("Registered agents:", list(bus.agents.keys()))


# 4. Test BookingAgent -> VenueAgent communication
print("\n--- BOOKING AND VENUE AGENT TEST ---")

booking_message = {
    "sender": "TestClient",
    "receiver": "BookingAgent",
    "performative": "create_booking",
    "content": {
        "venue_id": 1,
        "start_time": datetime(2027, 1, 10, 9, 0),
        "end_time": datetime(2027, 1, 10, 17, 0)
    },
    "conversation_id": str(uuid4())
}

booking_response = booking_agent.receive_message(booking_message)
print("Booking response:", booking_response)


# 5. Test WaitlistAgent
print("\n--- WAITLIST AGENT TEST ---")

waitlist_response = bus.send_message({
    "sender": "TestClient",
    "receiver": "WaitlistAgent",
    "performative": "join_waitlist",
    "content": {
        "event_id": 2,
        "user_id": 1
    },
    "conversation_id": str(uuid4())
})

print("Waitlist response:", waitlist_response)


# 6. Test NotificationAgent
print("\n--- NOTIFICATION AGENT TEST ---")

notification_response = bus.send_message({
    "sender": "TestClient",
    "receiver": "NotificationAgent",
    "performative": "send_notification",
    "content": {
        "user_id": 1,
        "message": "Your EventSphere booking has been received."
    },
    "conversation_id": str(uuid4())
})

print("Notification response:", notification_response)


# 7. Test TicketAgent with an invalid ticket
print("\n--- TICKET AGENT TEST ---")

ticket_response = bus.send_message({
    "sender": "TestClient",
    "receiver": "TicketAgent",
    "performative": "validate_ticket",
    "content": {
        "ticket_code": "INVALID-TEST-CODE",
        "event_id": 2
    },
    "conversation_id": str(uuid4())
})

print("Ticket response:", ticket_response)


# 8. Check database message logs
print("\n--- DATABASE MESSAGE LOG TEST ---")

db = SessionLocal()

try:
    message_count = db.query(AgentMessage).count()
    print("Total stored agent messages:", message_count)
finally:
    db.close()


print("\n--- ALL AGENT TESTS COMPLETED ---")
