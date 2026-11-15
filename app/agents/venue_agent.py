
from datetime import datetime

from app.agents.base_agent import BaseAgent
from app.database.connection import SessionLocal
from app.database.models import Venue, Event, VenueHireRequest


class VenueAgent(BaseAgent):

    def receive_message(self, message):

        content = message["content"]

        if message["performative"] == "check_availability":

            venue_id = content.get("venue_id")

            # Convert ISO datetime strings into Python datetime objects
            start_time = datetime.fromisoformat(
                content.get("start_time")
            )

            end_time = datetime.fromisoformat(
                content.get("end_time")
            )

            db = SessionLocal()

            try:
                # Check whether the venue exists
                venue = db.query(Venue).filter(
                    Venue.id == venue_id
                ).first()

                if not venue:
                    return {
                        "status": "refused",
                        "reason": "Venue not found"
                    }

                # Check for existing event conflicts
                event_conflict = db.query(Event).filter(
                    Event.venue_id == venue_id,
                    Event.status != "cancelled",
                    Event.start_time < end_time,
                    Event.end_time > start_time
                ).first()

                # Check for approved private hire conflicts
                hire_conflict = db.query(VenueHireRequest).filter(
                    VenueHireRequest.venue_id == venue_id,
                    VenueHireRequest.status == "approved",
                    VenueHireRequest.start_time < end_time,
                    VenueHireRequest.end_time > start_time
                ).first()

                # Reject if another event or hire exists
                if event_conflict or hire_conflict:
                    return {
                        "status": "refused",
                        "reason": "Venue is not available"
                    }

                # Venue is available
                return {
                    "status": "approved",
                    "message": "Venue is available"
                }

            finally:
                db.close()

        return {
            "status": "refused",
            "reason": "Unsupported performative"
        }
