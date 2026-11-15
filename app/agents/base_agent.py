
from abc import ABC, abstractmethod
from uuid import uuid4


class BaseAgent(ABC):

    def __init__(self, name, message_bus):
        self.name = name
        self.message_bus = message_bus

    def send_message(self, receiver, performative, content):
        message = {
            "sender": self.name,
            "receiver": receiver,
            "performative": performative,
            "content": content,
            "conversation_id": str(uuid4())
        }

        return self.message_bus.send_message(message)

    @abstractmethod
    def receive_message(self, message):
        pass
