
from app.agents.base_agent import BaseAgent


class BookingAgent(BaseAgent):

    def receive_message(self, message):

        if message["performative"] == "create_booking":

            content = message["content"]

            venue_response = self.send_message(
                receiver="VenueAgent",
                performative="check_availability",
                content={
                    "venue_id": content.get("venue_id"),
                    "start_time": content.get("start_time"),
                    "end_time": content.get("end_time")
                }
            )

            if venue_response.get("status") != "approved":
                return {
                    "status": "refused",
                    "reason": venue_response.get(
                        "reason",
                        "Venue availability check failed"
                    )
                }

            return {
                "status": "approved",
                "message": "Venue availability confirmed. Booking can proceed."
            }

        return {
            "status": "refused",
            "reason": "Unsupported performative"
        }
