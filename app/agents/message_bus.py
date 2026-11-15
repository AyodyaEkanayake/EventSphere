
import json
from datetime import datetime, timezone

from app.database.connection import SessionLocal
from app.database.models import AgentMessage


class MessageBus:

    def __init__(self):
        self.agents = {}

    def register_agent(self, agent):
        self.agents[agent.name] = agent

    def send_message(self, message):

        required_fields = [
            "sender",
            "receiver",
            "performative",
            "content",
            "conversation_id"
        ]

        # Validate required message fields
        for field in required_fields:
            if field not in message:
                raise ValueError(
                    f"Missing message field: {field}"
                )

        # Convert datetime and other JSON-incompatible values
        # into JSON-compatible values.
        safe_message = json.loads(
            json.dumps(message, default=str)
        )

        # Save message to database
        db = SessionLocal()

        try:
            log = AgentMessage(
                sender=safe_message["sender"],
                receiver=safe_message["receiver"],
                performative=safe_message["performative"],
                content=safe_message["content"],
                conversation_id=safe_message["conversation_id"],
                created_at=datetime.now(timezone.utc)
            )

            db.add(log)
            db.commit()

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()

        # Find receiving agent
        receiver = self.agents.get(
            safe_message["receiver"]
        )

        if receiver is None:
            return {
                "status": "refused",
                "reason": "Receiver agent not found",
                "message": safe_message
            }

        # Deliver JSON-compatible message
        return receiver.receive_message(safe_message)
