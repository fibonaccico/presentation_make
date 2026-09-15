import uuid
from enum import Enum

from pydantic import BaseModel


class PresentationSchema(BaseModel):
    uuid: uuid.UUID
    status: str


class PaySchema(BaseModel):
    uuid: uuid.UUID
    paid_qty: int
    tariff_id: int


class PayStatus(str, Enum):
    SUCCEEDED = "succeeded"
    PENDING = "pending"
    CANCELED = "canceled"
    REFUND = "refund"
    NONE = "none"


class PaymentService(str, Enum):
    YOOKASSA = "yookassa"
    ROBOKASSA = "robokassa"
    DODOPAYMENTS = "dodopayments"


class TariffTitle(str, Enum):
    LITE = "LITE"
    TOP = "TOP"
    PROFI = "PROFI"
    NONE = "NONE"
    PROMOCODE = "PROMOCODE"
    USE_REF_CODE = "USE_REF_CODE"
    FRIEND_USE_REF_CODE = "FRIEND_USE_REF_CODE"
    FROM_ADMIN = "FROM_ADMIN"
    AFTER_REGISTRATION = "AFTER_REGISTRATION"
    TEST = "TEST"
