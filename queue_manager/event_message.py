import json
import typing as t
from enum import Enum

from aiormq.abc import DeliveredMessage

from make_presentation.config import image_style_choice


class EventType(Enum):
    TELEGRAM = "telegram"
    WEB = "web"
    MAX = 'max'
    DOWNLOAD = "download"
    AUTOPAYMENT = "autopayment"


class PresentationType(Enum):
    TEXT = "text"
    TOPIC = "topic"


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
    def no_logo(self) -> bool:
        return self._generation_data.get("no_logo", False)

    @property
    def language(self) -> str:
        return self._generation_data.get("language", "ru")

    @property
    def context(self) -> t.Optional[str]:
        return self._generation_data.get("context")

    @property
    def save_presentation_path(self) -> t.Optional[str]:
        return self._generation_data.get("save_presentation_path")

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
    def number_of_slides(self) -> int:
        return self._generation_data.get("number_of_slides", 10)

    @property
    def image_style(self) -> str:
        return image_style_choice.get(self._generation_data.get("image_style", "DEFAULT"), "DEFAULT")

    @property
    def format_file(self) -> str:
        return self._generation_data.get("format_file", "pdf")

    @property
    def event_type(self) -> t.Optional[str]:
        return self._event_type if self._event_type in EventType._value2member_map_ else None

    @property
    def auto_pay(self) -> t.Optional[bool]:
        return self._generation_data.get("auto_pay")

    @property
    def auto_pay_id(self) -> t.Optional[str]:
        return self._generation_data.get("auto_pay_id")

    @property
    def username(self) -> t.Optional[bool]:
        return self._generation_data.get("username")

    @property
    def telegram_id(self) -> t.Optional[bool]:
        return self._generation_data.get("telegram_id")

    @property
    def email(self) -> t.Optional[bool]:
        return self._generation_data.get("email")


class RegenerateImageEventMessage:
    def __init__(self, message: DeliveredMessage):
        self._message_data = json.loads(message.body.decode('utf-8'))
        self._generation_data = self._message_data.get("generation_data")

    @property
    def current_image_uuid(self) -> t.Optional[str]:
        return self._generation_data.get("current_image_uuid")

    @property
    def candidate_image_uuid(self) -> t.Optional[str]:
        return self._generation_data.get("candidate_image_uuid")


class SendMessgeEventMessage:
    def __init__(self, message: DeliveredMessage):
        self._message_data = json.loads(message.body.decode('utf-8'))

    @property
    def from_source(self) -> t.Optional[str]:
        return self._message_data.get("from_source")

    @property
    def text(self) -> t.Optional[str]:
        return self._message_data.get("text")

    @property
    def telegram_id(self) -> t.Optional[str]:
        return self._message_data.get("telegram_id")

    @property
    def reply_markup(self) -> t.Optional[str]:
        return self._message_data.get("reply_markup")
