
from app.agents.base_agent import BaseAgent
from app.database.connection import SessionLocal
from app.database.models import Ticket


class TicketAgent(BaseAgent):

    def receive_message(self, message):

        if message["performative"] == "validate_ticket":

            ticket_code = message["content"].get("ticket_code")
            event_id = message["content"].get("event_id")

            db = SessionLocal()

            try:
                ticket = db.query(Ticket).filter(
                    Ticket.ticket_code == ticket_code,
                    Ticket.event_id == event_id
                ).first()

                if not ticket:
                    return {
                        "status": "refused",
                        "reason": "Invalid ticket"
                    }

                if ticket.status != "valid":
                    return {
                        "status": "refused",
                        "reason": "Ticket already used or invalid"
                    }

                return {
                    "status": "approved",
                    "message": "Ticket is valid. Ready for check-in."
                }

            finally:
                db.close()

        return {
            "status": "refused",
            "reason": "Unsupported performative"
        }
