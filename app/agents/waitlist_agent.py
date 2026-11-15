
from app.agents.base_agent import BaseAgent


class WaitlistAgent(BaseAgent):

    def receive_message(self, message):

        if message["performative"] == "join_waitlist":

            content = message["content"]

            event_id = content.get("event_id")
            user_id = content.get("user_id")

            if not event_id or not user_id:
                return {
                    "status": "refused",
                    "reason": "Event ID and User ID are required"
                }

            return {
                "status": "approved",
                "message": "Waitlist request received",
                "event_id": event_id,
                "user_id": user_id
            }

        return {
            "status": "refused",
            "reason": "Unsupported performative"
        }
