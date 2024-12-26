import json
from enum import Enum
import typing as t

from aiormq.abc import DeliveredMessage


class EventType(Enum):
    TELEGRAM = "telegram"
    WEB = "web"


class EventMessage:
    def __init__(self, message: DeliveredMessage):
        self._message_data = json.loads(message.body.decode('utf-8'))
        self._event_type = self._message_data.get("event_type")
        self._generation_data = self._message_data.get("generation_data")

    @property
    def gen_model(self) -> t.Optional[str]:
        return self._generation_data.get("text_generation_model")

    @property
    def template(self) -> t.Optional[str]:
        return self._generation_data.get("template")

    @property
    def context(self) -> t.Optional[str]:
        return self._generation_data.get("context")

    @property
    def save_path_for_images(self) -> t.Optional[str]:
        return self._generation_data.get("save_path_for_images")

    @property
    def presentation_type(self) -> t.Optional[str]:
        return self._generation_data.get("type")

    @property
    def user_uuid(self) -> t.Optional[str]:
        return self._generation_data.get("user_uuid")

    @property
    def presentation_uuid(self) -> t.Optional[str]:
        return self._generation_data.get("presentation_uuid")

    @property
    def event_type(self) -> t.Optional[str]:
        return self._event_type if self._event_type and self._event_type in EventType else None
