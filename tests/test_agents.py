
from datetime import timedelta

from app.agents.venue_agent import VenueAgent
from app.agents.booking_agent import BookingAgent
from app.agents.ticket_agent import TicketAgent
from app.agents.waitlist_agent import WaitlistAgent
from app.agents.notification_agent import NotificationAgent


# Fake Message Bus for BookingAgent testing
class FakeMessageBus:

    def send_message(self, message):

        if message["receiver"] == "VenueAgent":
            return {
                "status": "approved",
                "message": "Venue is available"
            }

        return {
            "status": "refused",
            "reason": "Unknown receiver"
        }


# TEST 1: VenueAgent rejects an already booked venue
def test_venue_agent_rejects_unavailable_venue(
    db_session, test_data, monkeypatch
):

    monkeypatch.setattr(
        "app.agents.venue_agent.SessionLocal",
        lambda: db_session
    )

    agent = VenueAgent("VenueAgent", None)

    event = test_data["event"]

    message = {
        "performative": "check_availability",
        "content": {
            "venue_id": test_data["venue"].id,
            "start_time": event.start_time.isoformat(),
            "end_time": event.end_time.isoformat()
        }
    }

    response = agent.receive_message(message)

    assert response["status"] == "refused"
    assert response["reason"] == "Venue is not available"


# TEST 2: BookingAgent checks venue availability
def test_booking_agent_checks_venue_availability():

    bus = FakeMessageBus()

    agent = BookingAgent("BookingAgent", bus)

    message = {
        "performative": "create_booking",
        "content": {
            "venue_id": 1,
            "start_time": "2027-02-10T09:00:00",
            "end_time": "2027-02-10T17:00:00"
        }
    }

    response = agent.receive_message(message)

    assert response["status"] == "approved"
    assert "Booking can proceed" in response["message"]


# TEST 3: TicketAgent rejects an invalid ticket
def test_ticket_agent_rejects_invalid_ticket(
    db_session, monkeypatch
):

    monkeypatch.setattr(
        "app.agents.ticket_agent.SessionLocal",
        lambda: db_session
    )

    agent = TicketAgent("TicketAgent", None)

    message = {
        "performative": "validate_ticket",
        "content": {
            "ticket_code": "INVALID-TEST-TICKET",
            "event_id": 1
        }
    }

    response = agent.receive_message(message)

    assert response["status"] == "refused"
    assert response["reason"] == "Invalid ticket"


# TEST 4: WaitlistAgent accepts a valid waitlist request
def test_waitlist_agent_accepts_request():

    agent = WaitlistAgent("WaitlistAgent", None)

    message = {
        "performative": "join_waitlist",
        "content": {
            "event_id": 1,
            "user_id": 10
        }
    }

    response = agent.receive_message(message)

    assert response["status"] == "approved"
    assert response["event_id"] == 1
    assert response["user_id"] == 10


# TEST 5: NotificationAgent processes a notification
def test_notification_agent_sends_notification(capsys):

    agent = NotificationAgent("NotificationAgent", None)

    message = {
        "performative": "send_notification",
        "content": {
            "user_id": 10,
            "message": "Your booking is confirmed."
        }
    }

    response = agent.receive_message(message)

    captured = capsys.readouterr()

    assert response["status"] == "approved"
    assert "Your booking is confirmed." in captured.out
