
from app.agents.base_agent import BaseAgent


class NotificationAgent(BaseAgent):

    def receive_message(self, message):

        if message["performative"] == "send_notification":

            content = message["content"]

            user_id = content.get("user_id")
            notification = content.get("message")

            if not user_id or not notification:
                return {
                    "status": "refused",
                    "reason": "User ID and notification message are required"
                }

            print(
                f"NOTIFICATION for User {user_id}: {notification}"
            )

            return {
                "status": "approved",
                "message": "Notification processed successfully"
            }

        return {
            "status": "refused",
            "reason": "Unsupported performative"
        }
